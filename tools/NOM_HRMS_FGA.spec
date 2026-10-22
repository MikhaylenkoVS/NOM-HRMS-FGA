# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for NOM HRMS FGA — single-file Windows .exe.

Usage:
    pyinstaller tools/NOM_HRMS_FGA.spec

Result:  ``dist/NOM_HRMS_FGA.exe``  (≈200–400 MB, self-contained).
"""
from __future__ import annotations

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# ---------------------------------------------------------------------------
# Spec file directory (= tools/); project root is _PROJECT.parent
# ---------------------------------------------------------------------------
_PROJECT = Path(SPECPATH)  # type: ignore[name-defined]  # noqa: F821
_ROOT = _PROJECT.parent     # actual project root

# ---------------------------------------------------------------------------
# Hidden imports — modules imported lazily, dynamically, or via __import__
# ---------------------------------------------------------------------------
_hidden: list[str] = [
    # tkinter & friends
    "tkinter", "tkinter.ttk", "tkinter.filedialog", "tkinter.messagebox",
    "tkinter.scrolledtext", "_tkinter",
    # matplotlib
    "matplotlib.backends.backend_tkagg",
    "matplotlib.backends._tkagg",
    # numpy
    "numpy.core._methods", "numpy.lib.format",
    # pandas
    "pandas._libs.tslibs",
    # Excel: подключается динамически через engine="openpyxl"
    "openpyxl", "openpyxl.utils", "openpyxl.styles",
    # misc
    "queue", "threading", "warnings", "logging",
    "json", "csv", "io", "ast", "re", "math",
    "ctypes",
    # Материалы для статьи (кнопка в панели результатов): модуль
    # подключается лениво внутри обработчика, поэтому указываем явно.
    "tools.article_report", "tools.make_outputs", "tools.auto_updater",
    # Сжатая база формул: читатель подключается лениво из
    # src/core/spectrum/_formula_source.open_formula_db, поэтому PyInstaller
    # не видит импорт при статическом анализе.
    "src.core.formula_db._reader",
    "src.core.formula_db._packed",
    "zstandard",
]

# ---------------------------------------------------------------------------
# Collect-all for complex native-extension packages
# ---------------------------------------------------------------------------
_collect_packages = ["rdkit", "matplotlib", "PIL", "scipy"]
_collected_datas: list[tuple[str, str]] = []
_collected_binaries: list[tuple[str, str]] = []

for _pkg in _collect_packages:
    _d, _b, _h = collect_all(_pkg)
    _collected_datas.extend(_d)
    _collected_binaries.extend(_b)
    _hidden.extend(_h)

# ---------------------------------------------------------------------------
# Data files: config JSONs
# ---------------------------------------------------------------------------
_added_datas: list[tuple[str, str]] = []
_config_dir = _ROOT / "src" / "configs"
if _config_dir.is_dir():
    for _jf in _config_dir.glob("*.json"):
        _added_datas.append((str(_jf), os.path.join("src", "configs")))
    # Subdirectories: loader.py reads constants/*.json at import time,
    # presets/*.json feed the GUI preset list.
    for _sub in ("constants", "presets"):
        _sub_dir = _config_dir / _sub
        if _sub_dir.is_dir():
            for _jf in _sub_dir.glob("*.json"):
                _added_datas.append(
                    (str(_jf), os.path.join("src", "configs", _sub))
                )

# Also collect matplotlib's mpl-data
_added_datas.extend(collect_data_files("matplotlib"))

# Include app icon for runtime use (window icon in taskbar via iconbitmap)
_icon_path = _ROOT / "assets" / "icon.ico"
if _icon_path.is_file():
    _added_datas.append((str(_icon_path), "assets"))

# Сжатая база формул (data/formula_db): *.fdb + манифест.
# Используется назначением формул через src/core/spectrum/_formula_source.py
# (ищется в sys._MEIPASS/data/formula_db). Без неё назначение работает
# перебором — медленнее, но корректно.
_db_dir = _ROOT / "data" / "formula_db"
if _db_dir.is_dir():
    for _f in sorted(_db_dir.glob("*.fdb")) + sorted(_db_dir.glob("*.manifest.json")):
        _added_datas.append((str(_f), "data/formula_db"))

# Merge all datas
_all_datas: list[tuple[str, str]] = []
_all_datas.extend(_added_datas)
_all_datas.extend(_collected_datas)

# ---------------------------------------------------------------------------
# Exclusions
# ---------------------------------------------------------------------------
_excludes: list[str] = [
    "IPython", "ipykernel", "jupyter", "notebook",
    "PyQt5", "PyQt6", "PySide2", "PySide6", "wx",
    "zmq", "tornado", "sqlalchemy",
    # ВНИМАНИЕ: openpyxl НЕ исключается — он нужен для XLSX-экспорта
    # (src/core/pipeline/_export.py) и загрузки .xlsx (src/core/spectrum/_load.py).
    "sympy", "xlrd", "xlsxwriter",
    "lxml", "html5lib", "bs4", "sphinx",
    "pytest", "setuptools", "pip", "wheel", "Cython",
    # "distutils" НЕ исключается: на Python >=3.12 PyInstaller-хук
    # hook-distutils алиасит setuptools._distutils -> distutils, и исключение
    # приводит к ValueError: Target module "distutils" already imported
    # as ExcludedModule('distutils').
]

# ---------------------------------------------------------------------------
# Icon (embedded into EXE for Explorer — _icon_path defined above in Data files)
# ---------------------------------------------------------------------------
_icon = str(_icon_path) if _icon_path.is_file() else None

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    [str(_PROJECT / "launcher.py")],
    pathex=[str(_PROJECT), str(_PROJECT.parent)],
    binaries=_collected_binaries,
    datas=_all_datas,
    hiddenimports=list(dict.fromkeys(_hidden)),  # deduplicate
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=_excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ---------------------------------------------------------------------------
# PYZ + EXE
# ---------------------------------------------------------------------------
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="NOM_HRMS_FGA",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)
