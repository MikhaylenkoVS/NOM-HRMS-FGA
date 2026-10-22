"""Тесты загрузчика баз формул (без сети)."""

import hashlib
import json
from pathlib import Path

import pytest

from src.core.formula_db import _manager
from src.core.formula_db._variants import DB_VARIANTS, find_variant_path


class _Resp:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)

    def json(self):
        return json.loads(self.content.decode("utf-8"))

    def iter_content(self, chunk_size=1 << 20):
        for i in range(0, len(self.content), chunk_size):
            yield self.content[i : i + chunk_size]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_download_writes_fdb_idx_and_manifest(tmp_path, monkeypatch):
    fdb = b"fdb-data"
    idx = b"idx-data"
    manifest = b'{"format_version": 3}'
    release = {
        "databases": [
            {
                "id": "test_db",
                "manifest_url": "http://test/manifest",
                "manifest_sha256": _sha(manifest),
                "fdb_url": "http://test/fdb",
                "fdb_size_bytes": len(fdb),
                "fdb_sha256": _sha(fdb),
                "idx_url": "http://test/idx",
                "idx_size_bytes": len(idx),
                "idx_sha256": _sha(idx),
            }
        ]
    }
    responses = {
        "http://test/release": _Resp(json.dumps(release).encode()),
        "http://test/manifest": _Resp(manifest),
        "http://test/fdb": _Resp(fdb),
        "http://test/idx": _Resp(idx),
    }
    monkeypatch.setattr(
        _manager.requests,
        "get",
        lambda url, **kwargs: responses[url],
    )

    mgr = _manager.DatabaseManager(
        data_dir=tmp_path, release_manifest_url="http://test/release"
    )
    mgr.download("test_db")

    assert (tmp_path / "test_db.fdb").read_bytes() == fdb
    assert (tmp_path / "test_db.idx").read_bytes() == idx
    meta = json.loads((tmp_path / "test_db.manifest.json").read_text(encoding="utf-8"))
    assert meta["format_version"] == 3
    assert meta["fdb_sha256"] == _sha(fdb)
    assert meta["idx_sha256"] == _sha(idx)


def test_download_rejects_bad_sha(tmp_path, monkeypatch):
    fdb = b"bad"
    release = {
        "databases": [
            {
                "id": "test_db",
                "manifest_url": "http://test/manifest",
                "fdb_url": "http://test/fdb",
                "fdb_size_bytes": len(fdb),
                "fdb_sha256": "0" * 64,
            }
        ]
    }
    responses = {
        "http://test/release": _Resp(json.dumps(release).encode()),
        "http://test/manifest": _Resp(b"{}"),
        "http://test/fdb": _Resp(fdb),
    }
    monkeypatch.setattr(
        _manager.requests,
        "get",
        lambda url, **kwargs: responses[url],
    )
    mgr = _manager.DatabaseManager(
        data_dir=tmp_path, release_manifest_url="http://test/release"
    )
    with pytest.raises(RuntimeError, match="SHA-256"):
        mgr.download("test_db")
    assert not (tmp_path / "test_db.fdb").exists()
    assert not (tmp_path / "test_db.manifest.json").exists()


def test_find_variant_requires_fdb(tmp_path):
    variant = next(v for v in DB_VARIANTS if v.id == "chorsphal")
    stem = variant.manifest[: -len(".manifest.json")]
    (tmp_path / variant.manifest).write_text("{}", encoding="utf-8")
    assert find_variant_path(variant, dirs=[tmp_path]) is None
    (tmp_path / f"{stem}.fdb").write_bytes(b"x")
    assert find_variant_path(variant, dirs=[tmp_path]) == tmp_path / variant.manifest
