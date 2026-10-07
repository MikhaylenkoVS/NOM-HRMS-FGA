"""Unit tests for the headless CLI (CLI-01)."""

from pathlib import Path

import pytest

from src.cli import main
from src.configs import PATHS

THIS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = THIS_DIR.parent
TEST_SETS_ROOT = PROJECT_ROOT / PATHS.test_sets_dir


def _set01():
    root = TEST_SETS_ROOT / "set_01"
    return (
        str(root / "original.csv"),
        str(root / "deutermethylated.csv"),
        str(root / "deuteroacylated.csv"),
    )


@pytest.mark.unit
def test_cli_writes_output_file(tmp_path):
    src, dmet, dacet = _set01()
    out = tmp_path / "result.csv"
    code = main(
        [
            "--input",
            src,
            "--dmet",
            dmet,
            "--dacet",
            dacet,
            "--preset",
            "soil",
            "--output",
            str(out),
        ]
    )
    assert code == 0
    assert out.exists()
    content = out.read_text(encoding="utf-8-sig")
    assert "mass" in content and "brutto" in content


@pytest.mark.unit
def test_cli_stdout(capsys):
    src, dmet, dacet = _set01()
    code = main(["--input", src, "--dmet", dmet, "--dacet", dacet])
    assert code == 0
    out = capsys.readouterr().out
    assert "mass" in out and "brutto" in out


@pytest.mark.unit
def test_cli_missing_file_exit_1(tmp_path):
    code = main(
        [
            "--input",
            str(tmp_path / "nonexistent.csv"),
            "--dmet",
            "x.csv",
            "--dacet",
            "y.csv",
        ]
    )
    assert code == 1


# ── --element-ranges: разбор и обработка ошибок (S-07) ────────────────────────


@pytest.mark.unit
def test_parse_element_ranges_valid():
    from src.cli import _parse_element_ranges

    assert _parse_element_ranges("C:5-60,H:4-120,O:1-30,N:0-3") == {
        "C": (5, 60),
        "H": (4, 120),
        "O": (1, 30),
        "N": (0, 3),
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    "spec",
    [
        "C:abc",  # границы не целые
        "C5-60",  # нет ':'
        "C:60",  # нет '-'
        "C:60-5",  # нижняя больше верхней
        ",,",  # не задано ни одного элемента
    ],
)
def test_parse_element_ranges_invalid(spec):
    from src.cli import _parse_element_ranges

    with pytest.raises(ValueError):
        _parse_element_ranges(spec)


@pytest.mark.unit
def test_cli_invalid_element_ranges_exit_1(capsys):
    """Некорректный --element-ranges → код 1 и понятное сообщение, без traceback."""
    src, dmet, dacet = _set01()
    code = main(
        [
            "--input",
            src,
            "--dmet",
            dmet,
            "--dacet",
            dacet,
            "--element-ranges",
            "C:abc",
        ]
    )
    assert code == 1
    err = capsys.readouterr().err
    assert "element-ranges" in err
    assert "Traceback" not in err
