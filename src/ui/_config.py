"""Shared configuration constants for UI mixins."""

from src.configs import PIPELINE as _PIPE_CFG, PATHS as _PATHS_CFG

_GUI_DEFAULTS = _PIPE_CFG.run_pipeline_defaults
_BRUTTO_DEFAULTS = _PIPE_CFG.default_brutto_dict
_FORMULA_RANGES = _PIPE_CFG.formula_search["ranges"]

# Theme constants — imported from theme.py, with fallback if UI not loaded
try:
    from src.ui.theme import (  # noqa: F811
        BG,
        FG,
        ACCENT,
        PANEL,
        WARN,
        OK,
        IMG_W,
        IMG_H,
        MONO,
        _mpl_style,
        _style,
    )
except ImportError:
    BG = "#1e1e2e"
    FG = "#cdd6f4"
    ACCENT = "#89b4fa"
    PANEL = "#313244"
    WARN = "#f38ba8"
    OK = "#a6e3a1"
    IMG_W = 340
    IMG_H = 260
    MONO = ("Consolas", 9)

    def _mpl_style():
        pass

    def _style(root):
        pass
