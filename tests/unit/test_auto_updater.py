"""Тесты автообновления без сети."""

from pathlib import Path

from tools.auto_updater import is_newer, parse_version, pick_exe_asset, sha256_file


def test_parse_version():
    assert parse_version("v1.2.3") == (1, 2, 3)
    assert parse_version("1.2") == (1, 2)
    assert parse_version("v0.9.0-beta") == (0, 9, 0)


def test_is_newer():
    assert is_newer("v1.0.1", "1.0.0")
    assert not is_newer("v1.0.0", "1.0.0")
    assert not is_newer("v0.9.9", "1.0.0")


def test_pick_exe_asset():
    release = {
        "assets": [
            {"name": "readme.txt", "size": 10, "browser_download_url": "x"},
            {"name": "NOM_HRMS_FGA.exe", "size": 100, "browser_download_url": "a"},
            {"name": "other.exe", "size": 200, "browser_download_url": "b"},
        ]
    }
    asset = pick_exe_asset(release)
    assert asset is not None
    assert asset["name"] == "NOM_HRMS_FGA.exe"


def test_pick_exe_asset_none():
    assert pick_exe_asset({"assets": [{"name": "a.zip", "size": 1}]}) is None


def test_sha256_file(tmp_path: Path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"abc")
    assert (
        sha256_file(p)
        == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
