"""BuildMixin — extracted from app.py."""

import threading, queue, os, sys, traceback, io
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from src.ui._config import (
    BG,
    FG,
    ACCENT,
    PANEL,
    WARN,
    OK,
    IMG_W,
    IMG_H,
    MONO,
    _GUI_DEFAULTS,
    _FORMULA_RANGES,
)
from src.ui.plots import embed_figure


class BuildMixin:
    """Extracted from app.py."""

    def _build_ui(self):
        hdr = tk.Label(
            self,
            text="⚗  NOM HRMS FGA",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 16, "bold"),
        )
        hdr.pack(fill="x", padx=16, pady=(12, 4))
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=16, pady=2)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=8)

        self.tab_params = ttk.Frame(nb)
        self.tab_spectra = ttk.Frame(nb)
        self.tab_series = ttk.Frame(nb)
        self.tab_result = ttk.Frame(nb)
        self.tab_van_krevelen = ttk.Frame(nb)
        self.tab_log = ttk.Frame(nb)

        nb.add(self.tab_params, text="⚙  Параметры")
        nb.add(self.tab_spectra, text="📈  Спектры")
        nb.add(self.tab_series, text="🔗  Серии")
        nb.add(self.tab_result, text="📊  Результаты")
        nb.add(self.tab_van_krevelen, text="🌿  Van Krevelen")
        nb.add(self.tab_log, text="📋  Лог")

        if StructureViewerTab is not None:
            try:
                self.tab_struct = StructureViewerTab(nb, app=self)
                nb.add(self.tab_struct, text="🧪  Структуры")
            except Exception as e:
                self._log_queue.put(
                    ("log", f"[WARN] StructureViewerTab init failed: {e}\n")
                )

        self._build_params_tab()
        self._build_spectra_tab()
        self._build_series_tab()
        self._build_result_tab()
        self._build_van_krevelen_tab()
        self._build_log_tab()

        self.status_var = tk.StringVar(value="Готов к работе")
        tk.Label(
            self,
            textvariable=self.status_var,
            bg=PANEL,
            fg=FG,
            font=("Segoe UI", 9),
            anchor="w",
            padx=8,
        ).pack(fill="x", side="bottom")
        self.progress = ttk.Progressbar(self, mode="determinate", length=200)
        self.progress.pack(fill="x", side="bottom")

    # ── ВКЛАДКА ПАРАМЕТРОВ ────────────────────────────────────────────────────
