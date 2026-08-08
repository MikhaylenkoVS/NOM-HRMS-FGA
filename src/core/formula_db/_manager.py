"""Formula database download manager.

Handles: discovery, download with resume, SHA-256 verification, atomic replace.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Callable, Optional

import requests

logger = logging.getLogger(__name__)

# Default release manifest URL — configured by developer, not hardcoded
_RELEASE_MANIFEST_URL_DEFAULT: str = (
    "https://raw.githubusercontent.com/MikhaylenkoVS/NOM-HRMS-FGA/"
    "main/data/formula_db/release_manifest.json"
)


class DatabaseManager:
    """Manages the lifecycle of the pre-built formula database.

    - Finds the user-writable data directory.
    - Checks for existing valid local DB.
    - Downloads DB files from a remote release manifest.
    - Verifies SHA-256.
    - Provides a :class:`FormulaDatabaseReader` when ready.
    """

    def __init__(
        self,
        data_dir: Optional[str | Path] = None,
        release_manifest_url: Optional[str] = None,
    ):
        import platformdirs

        self._data_dir = Path(data_dir or platformdirs.user_data_dir("NOM-HRMS-FGA"))
        self._release_url = release_manifest_url or _RELEASE_MANIFEST_URL_DEFAULT
        self._data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    def _local_manifest_path(self, db_id: str) -> Path:
        return self._data_dir / f"{db_id}.manifest.json"

    def _local_fdb_path(self, db_id: str) -> Path:
        return self._data_dir / f"{db_id}.fdb"

    def is_available(self, db_id: str = "chposp_1000") -> bool:
        """Check if a valid local database exists."""
        mp = self._local_manifest_path(db_id)
        fdb = self._local_fdb_path(db_id)
        if not mp.exists() or not fdb.exists():
            return False
        try:
            self._verify_local(db_id)
            return True
        except Exception:
            return False

    def _verify_local(self, db_id: str) -> None:
        """Verify SHA-256 of local .fdb against manifest."""
        mp = self._local_manifest_path(db_id)
        fdb = self._local_fdb_path(db_id)
        with open(mp, encoding="utf-8") as mf:
            manifest = json.load(mf)
        expected = manifest["fdb_sha256"]
        actual = hashlib.sha256(fdb.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(
                f"Local DB SHA-256 mismatch: expected {expected}, got {actual}"
            )

    def get_reader(self, db_id: str = "chposp_1000", cache_size: int = 8) -> object:
        """Return a FormulaDatabaseReader for the local DB.

        Raises FileNotFoundError if DB not available.
        """
        from ._reader import FormulaDatabaseReader

        mp = self._local_manifest_path(db_id)
        if not mp.exists():
            raise FileNotFoundError(
                f"Formula database '{db_id}' not found. Download it first "
                "or run: python -m src.core.formula_db build"
            )
        self._verify_local(db_id)
        return FormulaDatabaseReader(mp, cache_size=cache_size)

    def fetch_release_info(self) -> dict:
        """Fetch the remote release manifest.

        Returns the JSON dict or raises on network/parse error.
        """
        resp = requests.get(self._release_url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def download(
        self,
        db_id: str = "chposp_1000",
        progress_callback: Optional[Callable[[str, float], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> None:
        """Download the formula database from the remote release manifest.

        Steps:
        1. Fetch release manifest to get file URLs and sizes.
        2. Download .manifest.json + .fdb to .part files.
        3. Verify SHA-256 of .fdb.
        4. Atomically rename .part → final.
        """
        info = self.fetch_release_info()

        entry = None
        for db in info.get("databases", []):
            if db.get("id") == db_id:
                entry = db
                break
        if entry is None:
            raise ValueError(
                f"Database '{db_id}' not found in release manifest. "
                f"Available: {[d.get('id') for d in info.get('databases', [])]}"
            )

        total_size = entry["fdb_size_bytes"] + 1024  # + manifest overhead
        downloaded = 0

        def _report(stage: str):
            if progress_callback:
                progress_callback(stage, min(downloaded / max(total_size, 1), 0.99))

        # Download manifest
        mp = self._local_manifest_path(db_id)
        mp_part = mp.with_suffix(".manifest.json.part")
        self._download_file(entry["manifest_url"], mp_part)
        os.replace(mp_part, mp)

        # Download .fdb with resume support
        fdb = self._local_fdb_path(db_id)
        fdb_part = fdb.with_suffix(".fdb.part")
        fdb_url = entry["fdb_url"]
        fdb_size = entry["fdb_size_bytes"]

        # Check for partial download
        resume_pos = 0
        if fdb_part.exists():
            resume_pos = fdb_part.stat().st_size
            downloaded = resume_pos

        headers = {}
        if resume_pos > 0 and resume_pos < fdb_size:
            headers["Range"] = f"bytes={resume_pos}-"
            _report(f"Возобновление загрузки ({resume_pos / 1e6:.0f} MB)...")

        _report(f"Загрузка базы формул ({fdb_size / 1e6:.1f} MB)...")

        with requests.get(fdb_url, stream=True, timeout=300, headers=headers) as r:
            if resume_pos > 0 and r.status_code == 206:
                mode = "ab"
                r.raise_for_status()
            elif resume_pos > 0:
                # Server doesn't support resume, start over
                resume_pos = 0
                mode = "wb"
            else:
                r.raise_for_status()
                mode = "wb"

            with open(fdb_part, mode) as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if cancel_check and cancel_check():
                            raise InterruptedError("Download cancelled by user")
                        _report(f"Загрузка... {downloaded / 1e6:.1f} MB")

        # Verify SHA-256
        _report("Проверка целостности...")
        actual = hashlib.sha256(fdb_part.read_bytes()).hexdigest()
        expected = entry["fdb_sha256"]
        if actual != expected:
            fdb_part.unlink(missing_ok=True)
            raise RuntimeError(
                f"Downloaded DB SHA-256 mismatch.\n"
                f"  Expected: {expected}\n"
                f"  Got:      {actual}"
            )

        # Atomic replace
        os.replace(fdb_part, fdb)
        _report("Готово")

    @staticmethod
    def _download_file(url: str, dest: Path) -> None:
        """Download a single file, writing to dest."""
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
