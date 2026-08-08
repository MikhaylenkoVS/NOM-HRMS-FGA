"""
app.py  —  GUI-интерфейс для пайплайна определения -COOH и -OH групп
           Запускать: python app.py
           Требует: tkinter (стандартная библиотека Python), matplotlib, pandas
"""

from __future__ import annotations
from src.core._safety import _safe_df
import ast
import io
import os
import queue
import threading
import traceback
import warnings
import sys
from pathlib import Path
from typing import Optional
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# RDKit CoordGen: sp3-зигзаги вместо линейных цепочек
try:
    from rdkit.Chem import rdDepictor

    rdDepictor.SetPreferCoordGen(True)
except Exception:
    pass

matplotlib.use("TkAgg")
# ── Импорт UI-утилит ─────────────────────────────────────────────────────────
try:
    from src.ui.plots import embed_figure
    from src.ui.theme import (
        ACCENT,
        BG,
        FG,
        IMG_H,
        IMG_W,
        MONO,
        OK,
        PANEL,
        WARN,
        _mpl_style,
        _style,
    )
    from src.structures.tab import StructureViewerTab

    _UI_LOADED = True
    _UI_ERROR = ""
except Exception as _ui_err:
    _UI_LOADED = False
    _UI_ERROR = traceback.format_exc()
    # Fallback-константы, чтобы GUI хотя бы запустился без src.ui
    BG = "#1e1e2e"
    ACCENT = "#89b4fa"
    PANEL = "#313244"
    WARN = "#f38ba8"
    FG = "#cdd6f4"
    OK = "#a6e3a1"
    BTN = "#45475a"
    FONT = ("Segoe UI", 10)
    MONO = ("Consolas", 9)
    IMG_H = 260
    IMG_W = 340

    def _mpl_style():
        pass

    def _style(root):
        pass

    StructureViewerTab = None

    def embed_figure(fig, parent, toolbar=True):
        """Минимальный fallback через FigureCanvasTkAgg."""
        try:
            from matplotlib.backends.backend_tkagg import (
                FigureCanvasTkAgg,
                NavigationToolbar2Tk,
            )

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            if toolbar:
                NavigationToolbar2Tk(canvas, parent)
        except Exception:
            plt.show()


# ── Импорт пайплайна ─────────────────────────────────────────────────────────
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
except Exception as _core_err:
    CORE_LOADED = False
    _CORE_ERROR = traceback.format_exc()
    from src.configs import CHEM

    DELTA_CD3 = CHEM.derivatization_shifts["delta_cd3"]
    DELTA_CD3CO = CHEM.derivatization_shifts["delta_cd3co"]
    run_pipeline = load_spectrum = find_series = visualize_series = None
    create_van_krevelen_plot = None

# ── Импорт raw-бриджа (опционально) ──────────────────────────────────────────
try:
    from src.core.io.raw_bridge import average_raw_to_csv

    _RAW_LOADED = True
    _RAW_ERROR = ""
except Exception as _raw_err:
    _RAW_LOADED = False
    _RAW_ERROR = str(_raw_err)
    average_raw_to_csv = None  # type: ignore[assignment]


# ── Импорт mzML-бриджа (опционально) ─────────────────────────────────────────
try:
    from src.core.io.mzml_bridge import mzml_to_csv as _mzml_to_csv
except Exception:
    _mzml_to_csv = None  # type: ignore[assignment]


# ── Импорт конфигурации ─────────────────────────────────────────────────────
from src.configs import PIPELINE as _PIPE_CFG, PATHS as _PATHS_CFG

_GUI_DEFAULTS = _PIPE_CFG.run_pipeline_defaults
_BRUTTO_DEFAULTS = _PIPE_CFG.default_brutto_dict
_FORMULA_RANGES = _PIPE_CFG.formula_search["ranges"]


# ═══════════════════════════════════════════════════════════════════════════════
#  Перехват stdout/stderr → thread-safe очередь → GUI-лог
# ═══════════════════════════════════════════════════════════════════════════════


class _QueueWriter:
    """Thread-safe stream shim that tees writes to a queue and a stream.

    Used to redirect ``sys.stdout``/``sys.stderr`` so that ``print``
    output from the pipeline (which may run in a worker thread) is
    delivered to the GUI log via a queue while still reaching the original
    stream.

    Parameters
    ----------
    q : queue.Queue
        Queue that receives ``("log", text)`` items.
    original : io.TextIOBase, optional
        Underlying stream to also forward writes to. Default ``None``.
    """

    def __init__(self, q: queue.Queue, original=None):
        self._q = q
        self._orig = original

    def write(self, data: str):
        if data:
            self._q.put(("log", data))
        if self._orig:
            try:
                self._orig.write(data)
            except Exception:
                pass

    def flush(self):
        if self._orig:
            try:
                self._orig.flush()
            except Exception:
                pass

    def fileno(self):
        if self._orig and hasattr(self._orig, "fileno"):
            return self._orig.fileno()
        raise io.UnsupportedOperation("fileno")


# ═══════════════════════════════════════════════════════════════════════════════
#  Импорт UI-миксинов (методы вынесены в src/ui/_*.py)
# ═══════════════════════════════════════════════════════════════════════════════

from src.ui._log import LogMixin
from src.ui._run import RunMixin
from src.ui._params import ParamsMixin
from src.ui._tabs import TabsMixin
from src.ui._results import ResultsMixin
from src.ui._structures import StructuresMixin
from src.ui._plots import PlotsMixin
from src.ui._presets import PresetsMixin
from src.ui._build import BuildMixin

# ═══════════════════════════════════════════════════════════════════════════════
#  ГЛАВНОЕ ОКНО
# ═══════════════════════════════════════════════════════════════════════════════


class App(
    tk.Tk,
    LogMixin,
    RunMixin,
    ResultsMixin,
    StructuresMixin,
    PlotsMixin,
    PresetsMixin,
    ParamsMixin,
    TabsMixin,
    BuildMixin,
):
    """Main Tkinter window for the -COOH/-OH functional-group analyzer.

    Provides a tabbed interface to load the three input spectra
    (underivatized, deuteromethylated, deuteroacylated), configure and run
    the deconvolution pipeline in a background thread, and inspect the
    results as spectra plots, homologous-series diagrams, per-compound
    histograms, a results table and (optionally) candidate structures.

    Notes
    -----
    The heavy work runs on a worker thread; ``stdout``/``stderr`` are
    redirected through :class:`_QueueWriter` so pipeline messages appear in
    the GUI log without blocking the Tk event loop.
    """

    # ── init ──────────────────────────────────────────────────────────────────

    def __init__(self):
        super().__init__()
        try:
            import os as _os
            import sys as _sys
            import logging as _logging

            # Inside PyInstaller one-file bundle, files are extracted to _MEIPASS
            if getattr(_sys, "frozen", False):
                _base = _sys._MEIPASS
            else:
                # __file__ lives in src/ — walk up to project root
                _base = _os.path.join(_os.path.dirname(__file__), "..")
            _icon = _os.path.join(_base, "assets", "icon.ico")
            _icon = _os.path.normpath(_icon)
            if _os.path.exists(_icon):
                self.iconbitmap(_icon)
                try:
                    import ctypes as _ctypes

                    _hwnd = self.winfo_id()
                    if _hwnd:
                        _hicon = _ctypes.windll.user32.LoadImageW(
                            0, _icon, 1, 0, 0, 0x10  # IMAGE_ICON, LR_LOADFROMFILE
                        )
                        if _hicon:
                            _ctypes.windll.user32.SendMessageW(
                                _hwnd, 0x0080, 1, _hicon  # WM_SETICON + ICON_BIG
                            )
                except Exception:
                    pass
            else:
                _logging.warning("Icon not found: %s", _icon)
        except Exception:
            _logging.exception("Failed to set application icon")
        self.title("NOM HRMS FGA")
        self.geometry("1200x760")
        self.configure(bg=BG)
        self.resizable(True, True)

        try:
            _style(self)
        except Exception as e:
            _logging.warning(f"_style failed: {e}")
        try:
            _mpl_style()
        except Exception as e:
            _logging.warning(f"_mpl_style failed: {e}")

        # ── данные ──
        self.result_df: Optional[pd.DataFrame] = None
        self._structure_cache: dict[str, list] = {}
        self._structure_preloading = False
        self.src_spec = None
        self.dmet_spec = None
        self.dacet_spec = None
        self.df_dmet_series = None
        self.df_dacet_series = None

        # ── очередь для потоко-безопасного логирования ──
        self._log_queue: queue.Queue = queue.Queue()

        # ── файловые переменные ──
        self.src_var = tk.StringVar()
        self.dmet_var = tk.StringVar()
        self.dacet_var = tk.StringVar()
        self.vk_color_var = tk.StringVar(value="N_COOH")

        # ── RT-диапазоны для усреднения RAW ──
        self.src_rt_min = tk.StringVar(value="")
        self.src_rt_max = tk.StringVar(value="")
        self.dmet_rt_min = tk.StringVar(value="")
        self.dmet_rt_max = tk.StringVar(value="")
        self.dacet_rt_min = tk.StringVar(value="")
        self.dacet_rt_max = tk.StringVar(value="")

        # ── параметры (значения из pipeline.json -> run_pipeline_defaults) ──
        self.sep_var = tk.StringVar(value=str(_GUI_DEFAULTS["sep"]))
        self.mass_min_var = tk.StringVar(value=str(_GUI_DEFAULTS["load_mass_min"]))
        self.mass_max_var = tk.StringVar(value=str(_GUI_DEFAULTS["load_mass_max"]))
        self.noise_force_var = tk.StringVar(value=str(_GUI_DEFAULTS["noise_force"]))
        self.noise_int_var = tk.StringVar(value=str(_GUI_DEFAULTS["noise_intensity"]))
        self.noise_method_var = tk.StringVar(value="auto")
        self.noise_value_var = tk.StringVar(value=str(_GUI_DEFAULTS["noise_force"]))
        self.rel_error_var = tk.StringVar(value=str(_GUI_DEFAULTS["rel_error"]))
        self.sign_var = tk.StringVar(value=str(_GUI_DEFAULTS["sign"]))
        self.ppm_tol_var = tk.StringVar(value=str(_GUI_DEFAULTS["ppm_tol"]))
        self.max_groups_var = tk.StringVar(value=str(_GUI_DEFAULTS["max_groups"]))
        self.allow_gaps_var = tk.BooleanVar(value=bool(_GUI_DEFAULTS["allow_gaps"]))
        self.isotope_filter_var = tk.BooleanVar(value=False)
        self.output_csv_var = tk.StringVar(value=str(_PATHS_CFG.default_output_csv))
        # Диапазоны элементов из pipeline.json -> formula_search.ranges
        _r = _FORMULA_RANGES
        self.c_min = tk.StringVar(value=str(_r["C"][0]))
        self.c_max = tk.StringVar(value=str(_r["C"][1]))
        self.h_min = tk.StringVar(value=str(_r["H"][0]))
        self.h_max = tk.StringVar(value=str(_r["H"][1]))
        self.o_min = tk.StringVar(value=str(_r["O"][0]))
        self.o_max = tk.StringVar(value=str(_r["O"][1]))
        self.n_min = tk.StringVar(value=str(_r["N"][0]))
        self.n_max = tk.StringVar(value=str(_r["N"][1]))

        self._build_ui()

        # Опрос очереди стартует после построения UI
        self._poll_log_queue()

        # Корректное завершение при закрытии окна (крестик)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Отложенные предупреждения об ошибках импорта
        if not CORE_LOADED:
            self._log(f"[ОШИБКА] src.core не загружен:\n{_CORE_ERROR}", color=WARN)
        if not _UI_LOADED:
            self._log(
                f"[WARN] src.ui / src.structures не загружены:\n{_UI_ERROR}", color=WARN
            )


# ═══════════════════════════════════════════════════════════════════════════════
#  ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    """Entry point for ``nom-hrms-fga`` CLI / ``python -m src``."""
    warnings.filterwarnings("always")
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
