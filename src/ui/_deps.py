"""Shared optional imports for the GUI (core, RAW/mzML bridges) with fallback.

The GUI mixins (``src/ui/_*.py``) import these names from here instead of
``app.py``, so each module is self-contained and the optional-dependency
fallback lives in exactly one place.
"""

from __future__ import annotations

import traceback

# ── Импорт пайплайна (опционально) ───────────────────────────────────────────
try:
    from src.core import (
        DELTA_CD3,
        DELTA_CD3CO,
        create_van_krevelen_plot,
        find_series,
        load_spectrum,
        run_pipeline,
        visualize_series,
    )

    CORE_LOADED = True
    _CORE_ERROR = ""
except Exception:
    CORE_LOADED = False
    _CORE_ERROR = traceback.format_exc()
    from src.configs import CHEM

    DELTA_CD3 = CHEM.derivatization_shifts["delta_cd3"]
    DELTA_CD3CO = CHEM.derivatization_shifts["delta_cd3co"]
    run_pipeline = load_spectrum = find_series = visualize_series = None
    create_van_krevelen_plot = None

# ── Импорт raw-бриджа (опционально) ──────────────────────────────────────────
try:
    from src.core.io.raw_bridge import average_raw_to_json

    _RAW_LOADED = True
    _RAW_ERROR = ""
except Exception as _raw_err:
    _RAW_LOADED = False
    _RAW_ERROR = str(_raw_err)
    average_raw_to_json = None

# ── Импорт mzML-бриджа (опционально) ─────────────────────────────────────────
try:
    from src.core.io.mzml_bridge import mzml_to_json as _mzml_to_json
except Exception:
    _mzml_to_json = None
