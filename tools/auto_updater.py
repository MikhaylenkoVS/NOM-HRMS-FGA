"""Автообновление NOM HRMS FGA по GitHub Releases.

Примеры:
    python tools/auto_updater.py --check
    python tools/auto_updater.py --update
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = "MikhaylenkoVS/NOM-HRMS-FGA"
API_LATEST = f"https://api.github.com/repos/{REPO}/releases/latest"
USER_AGENT = "NOM-HRMS-FGA-updater"


def parse_version(value: str) -> tuple[int, ...]:
    """'v1.2.3' / '1.2.3' -> (1, 2, 3)."""
    text = str(value).strip().lstrip("vV")
    parts: list[int] = []
    for chunk in text.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) or (0,)


def is_newer(latest: str, current: str) -> bool:
    return parse_version(latest) > parse_version(current)


def _get_json(url: str, timeout: float = 10.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def latest_release(timeout: float = 10.0) -> dict:
    return _get_json(API_LATEST, timeout=timeout)


def pick_exe_asset(release: dict) -> dict | None:
    assets = release.get("assets") or []
    candidates = [
        a
        for a in assets
        if str(a.get("name", "")).lower().endswith(".exe")
        and "nom" in str(a.get("name", "")).lower()
    ]
    if not candidates:
        candidates = [
            a for a in assets if str(a.get("name", "")).lower().endswith(".exe")
        ]
    if not candidates:
        return None
    return max(candidates, key=lambda a: int(a.get("size", 0)))


def download(url: str, dest: Path, timeout: float = 60.0) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as fh:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)
    return dest


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def apply_update(downloaded: Path, current_exe: Path | None = None) -> None:
    """Заменить текущий exe после выхода процесса и перезапустить."""
    current_exe = Path(current_exe or sys.executable).resolve()
    downloaded = Path(downloaded).resolve()
    if not downloaded.is_file():
        raise FileNotFoundError(downloaded)
    if downloaded.suffix.lower() != ".exe":
        raise ValueError("ожидается .exe")

    bat = Path(tempfile.gettempdir()) / "nom_hrms_fga_update.bat"
    log = Path(tempfile.gettempdir()) / "nom_hrms_fga_update.log"
    bat.write_text(
        "@echo off\r\n"
        "chcp 65001 >nul\r\n"
        f"timeout /t 2 /nobreak >nul\r\n"
        f'move /y "{downloaded}" "{current_exe}" >>"{log}" 2>&1\r\n'
        f'start "" "{current_exe}"\r\n'
        'del "%~f0"\r\n',
        encoding="utf-8",
    )
    flags = 0
    if os.name == "nt":
        flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        )
    subprocess.Popen(
        ["cmd", "/c", str(bat)],
        creationflags=flags,
        close_fds=True,
    )


def check_and_prompt(current_version: str | None = None) -> bool:
    """Проверить релиз и спросить пользователя; True — обновление запущено."""
    if os.environ.get("NOM_HRMS_DISABLE_UPDATE") == "1":
        return False
    if current_version is None:
        try:
            from src import __version__ as current_version
        except Exception:
            current_version = "0.0.0"

    release = latest_release()
    latest = str(release.get("tag_name") or release.get("name") or "")
    if not latest or not is_newer(latest, current_version):
        return False
    asset = pick_exe_asset(release)
    if asset is None:
        return False

    question = (
        f"Доступна новая версия {latest} (у вас {current_version}).\n\n"
        "Скачать и установить сейчас? Приложение будет перезапущено."
    )
    if not _ask_yes_no(question):
        return False

    downloaded = Path(tempfile.gettempdir()) / f"NOM_HRMS_FGA_{latest}.exe"
    download(str(asset["browser_download_url"]), downloaded)
    apply_update(downloaded)
    return True


def _ask_yes_no(text: str) -> bool:
    if os.name == "nt":
        try:
            import ctypes

            res = ctypes.windll.user32.MessageBoxW(
                0, text, "NOM HRMS FGA — обновление", 0x04 | 0x40
            )
            return res == 6  # IDYES
        except Exception:
            pass
    try:
        import tkinter.messagebox as mb

        return bool(mb.askyesno("NOM HRMS FGA — обновление", text))
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="только проверить наличие")
    ap.add_argument("--update", action="store_true", help="скачать и установить")
    ap.add_argument("--current", default=None, help="текущая версия")
    args = ap.parse_args()

    try:
        from src import __version__ as current_version
    except Exception:
        current_version = "0.0.0"
    current_version = args.current or current_version

    release = latest_release()
    latest = str(release.get("tag_name") or "")
    newer = is_newer(latest, current_version)
    asset = pick_exe_asset(release)
    print(f"current={current_version} latest={latest} newer={newer}")
    if asset:
        print(f"asset={asset.get('name')} size={asset.get('size')}")

    if args.check or not args.update:
        return 0
    if not newer or asset is None:
        return 0
    dest = Path(tempfile.gettempdir()) / f"NOM_HRMS_FGA_{latest}.exe"
    download(str(asset["browser_download_url"]), dest)
    print(f"downloaded={dest} sha256={sha256_file(dest)}")
    apply_update(dest)
    print("update scheduled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
