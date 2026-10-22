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
except Exception:
    _UI_LOADED = False
    _UI_ERROR = traceback.format_exc()
    # Fallback-константы, чтобы GUI хотя бы запустился без src.ui
    BG = "#1e1e2e"
    ACCENT = "#89b4fa"
    PANEL = "#313244"
    WARN = "#f38ba8"
    FG = "#cdd6f4"
    OK = "#a6e3a1"
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


# ── Импорт пайплайна / мостов (с fallback) ────────────────────────────────────
from src.ui._deps import (
    DELTA_CD3,
    DELTA_CD3CO,
    create_van_krevelen_plot,
    find_series,
    load_spectrum,
    run_pipeline,
    visualize_series,
    CORE_LOADED,
    _CORE_ERROR,
    average_raw_to_json,
    _RAW_LOADED,
    _RAW_ERROR,
    _mzml_to_json,
)

# ── Импорт конфигурации ─────────────────────────────────────────────────────
from src.configs import (
    FORMULA_SEARCH_CFG as _FORMULA_SEARCH_CFG,
    PIPELINE as _PIPE_CFG,
    PATHS as _PATHS_CFG,
)

_GUI_DEFAULTS = _PIPE_CFG.run_pipeline_defaults
_FORMULA_RANGES = _FORMULA_SEARCH_CFG["ranges"]


# ═══════════════════════════════════════════════════════════════════════════════
#  Импорт UI-миксинов (методы вынесены в src/ui/_*.py)
# ═══════════════════════════════════════════════════════════════════════════════

from src.ui._log import LogMixin, _QueueWriter
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
        self.noise_method_var = tk.StringVar(value="auto")
        self.noise_value_var = tk.StringVar(value=str(_GUI_DEFAULTS["noise_force"]))
        self.rel_error_var = tk.StringVar(value=str(_GUI_DEFAULTS["rel_error"]))
        self.sign_var = tk.StringVar(value=str(_GUI_DEFAULTS["sign"]))
        self.ppm_tol_var = tk.StringVar(value=str(_GUI_DEFAULTS["ppm_tol"]))
        self.max_groups_var = tk.StringVar(value=str(_GUI_DEFAULTS["max_groups"]))
        # По умолчанию пропуски запрещены; число задаётся пользователем.
        self.max_gaps_var = tk.StringVar(value=str(_GUI_DEFAULTS.get("max_gaps", 0)))
        self.require_first_step_var = tk.BooleanVar(
            value=bool(_GUI_DEFAULTS.get("require_first_step", False))
        )
        self.ratios_enabled_var = tk.BooleanVar(value=True)
        self.nom_dbe_enabled_var = tk.BooleanVar(value=True)
        # Изотопные проверки включены по умолчанию: паттерн M+1/M+2 учитывается
        # при выборе формулы, а для найденных формул ищутся изотопные варианты.
        self.isotope_filter_var = tk.BooleanVar(value=True)
        self.isotope_variants_var = tk.BooleanVar(value=True)
        # Фильтр X/C — пользовательская настройка, по умолчанию выключен.
        self.max_xc_enabled_var = tk.BooleanVar(value=False)
        self.max_xc_var = tk.StringVar(value="0.1")
        # Предел числа атомов галогенов в брутто-формуле (пользовательский).
        self.halogen_max_atoms_var = tk.StringVar(value="5")
        # Полный перебор комбинаций галогенов (по умолчанию выключен:
        # в обычном режиме проверяются самые приоритетные комбинации).
        # По требованию заказчика полный перебор комбинаций включён по
        # умолчанию; значение по умолчанию берётся из formula_search.json
        # (halogen_search.exhaustive).
        try:
            from src.configs import FORMULA_SEARCH_CFG as _FS

            _hs = getattr(_FS, "halogen_search", None) or {}
            _exh_default = bool(_hs.get("exhaustive", True))
        except Exception:
            _exh_default = True
        self.halogen_exhaustive_var = tk.BooleanVar(value=_exh_default)
        # Шумоподавление дериватизатов: по умолчанию выключено (пики
        # продуктов низкоинтенсивные и теряются вместе с шумом).
        self.denoise_derivatives_var = tk.BooleanVar(value=False)
        # Шумоподавление исходного спектра (можно выключить, если пиклист
        # уже отфильтрован прибором/исследователем).
        self.denoise_source_var = tk.BooleanVar(value=True)
        self.segment_mode_var = tk.BooleanVar(value=False)
        self.segment_width_var = tk.StringVar(value="2.0")
        self.output_csv_var = tk.StringVar(value=str(_PATHS_CFG.default_output_csv))
        # Диапазоны элементов из configs/constants/formula_search.json -> ranges.
        # Список элементов берётся из того же конфига, поэтому добавление
        # элемента (S, P, галогены) не требует правки GUI.
        _r = _FORMULA_RANGES
        self.el_vars: dict[str, tuple[tk.StringVar, tk.StringVar]] = {}
        for _el, (_lo, _hi) in _r.items():
            self.el_vars[_el] = (
                tk.StringVar(value=str(_lo)),
                tk.StringVar(value=str(_hi)),
            )
        # Совместимые атрибуты для C/H/O/N (используются тестами и старым кодом)
        _zero = lambda: tk.StringVar(value="0")  # noqa: E731
        self.c_min, self.c_max = self.el_vars["C"]
        self.h_min, self.h_max = self.el_vars["H"]
        self.o_min, self.o_max = self.el_vars.get("O", (_zero(), _zero()))
        self.n_min, self.n_max = self.el_vars.get("N", (_zero(), _zero()))

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
