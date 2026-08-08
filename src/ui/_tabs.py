"""TabsMixin — extracted from app.py."""

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


class TabsMixin:
    """Extracted from app.py."""

    def _build_spectra_tab(self):
        frame = self.tab_spectra
        ctrl = ttk.Frame(frame)
        ctrl.pack(fill="x", pady=4, padx=8)
        ttk.Button(ctrl, text="📈 Построить спектры", command=self._plot_spectra).pack(
            side="left", padx=4
        )
        ttk.Button(
            ctrl,
            text="🗑 Очистить",
            command=lambda: self._clear_frame(self.spectra_canvas_frame),
        ).pack(side="left", padx=4)
        self.spectra_canvas_frame = ttk.Frame(frame)
        self.spectra_canvas_frame.pack(fill="both", expand=True)

    # ── ВКЛАДКА СЕРИИ ─────────────────────────────────────────────────────────

    def _build_series_tab(self):
        frame = self.tab_series
        ctrl = ttk.Frame(frame)
        ctrl.pack(fill="x", pady=4, padx=8)
        ttk.Button(
            ctrl,
            text="🔗 Показать серии CD₃",
            command=lambda: self._plot_series("dmet"),
        ).pack(side="left", padx=4)
        ttk.Button(
            ctrl,
            text="🔗 Показать серии CD₃CO",
            command=lambda: self._plot_series("dacet"),
        ).pack(side="left", padx=4)
        ttk.Button(
            ctrl,
            text="🗑 Очистить",
            command=lambda: self._clear_frame(self.series_canvas_frame),
        ).pack(side="left", padx=4)
        self.series_canvas_frame = ttk.Frame(frame)
        self.series_canvas_frame.pack(fill="both", expand=True)

    # ── ВКЛАДКА РЕЗУЛЬТАТОВ ───────────────────────────────────────────────────

    def _build_result_tab(self):
        frame = self.tab_result
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        ctrl = ttk.Frame(frame)
        ctrl.grid(row=0, column=0, columnspan=2, sticky="ew", pady=4, padx=8)
        ttk.Button(
            ctrl,
            text="📊 Гистограмма N_COOH",
            command=lambda: self._plot_hist("N_COOH"),
        ).pack(side="left", padx=4)
        ttk.Button(
            ctrl, text="📊 Гистограмма N_OH", command=lambda: self._plot_hist("N_OH")
        ).pack(side="left", padx=4)
        ttk.Button(ctrl, text="💾 Экспорт CSV", command=self._export_csv).pack(
            side="left", padx=4
        )
        ttk.Button(ctrl, text="📂 Импорт CSV", command=self._import_csv).pack(
            side="left", padx=4
        )

        # Левая часть — таблица (без колонок пропусков)
        tbl_frame = ttk.Frame(frame)
        tbl_frame.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=4)

        cols = ("mass", "brutto", "N_COOH", "N_OH")
        col_labels = ["m/z", "Формула", "N_COOH", "N_OH"]
        col_widths = [120, 180, 90, 90]

        self.result_tree = ttk.Treeview(
            tbl_frame, columns=cols, show="headings", height=18
        )
        for c, lbl, w in zip(cols, col_labels, col_widths):
            self.result_tree.heading(
                c, text=lbl, command=lambda _c=c: self._sort_tree(_c)
            )
            self.result_tree.column(c, width=w, anchor="center")

        vsb = ttk.Scrollbar(
            tbl_frame, orient="vertical", command=self.result_tree.yview
        )
        hsb = ttk.Scrollbar(
            tbl_frame, orient="horizontal", command=self.result_tree.xview
        )
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.result_tree.pack(fill="both", expand=True)
        self.result_tree.bind("<Double-1>", self._on_formula_double_click)
        self.result_tree.bind("<<TreeviewSelect>>", self._on_result_row_select)

        # Правая часть — превью структуры
        preview_frame = ttk.LabelFrame(frame, text="🧪  Структура")
        preview_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=4)
        self._structure_preview_label = tk.Label(
            preview_frame,
            text="Кликните на строку\nтаблицы для просмотра",
            bg=PANEL,
            fg=FG,
            font=("Segoe UI", 10),
            justify="center",
        )
        self._structure_preview_label.pack(expand=True, fill="both", padx=8, pady=8)
        self._structure_preview_img = None

        self.hist_frame = ttk.Frame(frame)
        self.hist_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=4)

    # ── ВКЛАДКА VAN KREVELEN ─────────────────────────────────────────────────

    def _build_van_krevelen_tab(self):
        frame = self.tab_van_krevelen
        ctrl = ttk.Frame(frame)
        ctrl.pack(fill="x", pady=4, padx=8)
        ttk.Button(
            ctrl,
            text="📈 Построить диаграмму Ван Кревелена",
            command=self._plot_van_krevelen,
        ).pack(side="left", padx=4)
        ttk.Button(
            ctrl,
            text="💾 Скачать PNG",
            command=self._save_van_krevelen_png,
        ).pack(side="left", padx=4)
        ttk.Button(
            ctrl,
            text="🗑 Очистить",
            command=lambda: self._clear_frame(self.vk_canvas_frame),
        ).pack(side="left", padx=4)
        ttk.Label(ctrl, text="  Цвет по:").pack(side="left", padx=(12, 2))
        self._vk_color_cb = ttk.Combobox(
            ctrl,
            textvariable=self.vk_color_var,
            values=["N_COOH", "N_OH"],
            width=8,
            state="readonly",
        )
        self._vk_color_cb.pack(side="left", padx=4)
        self._vk_color_cb.bind(
            "<<ComboboxSelected>>", lambda e: self._plot_van_krevelen()
        )
        self.vk_canvas_frame = ttk.Frame(frame)
        self.vk_canvas_frame.pack(fill="both", expand=True)
        # Храним ссылку на последнюю построенную фигуру для сохранения
        self._vk_figure = None

    # ── ВКЛАДКА ЛОГ ──────────────────────────────────────────────────────────

    def _build_log_tab(self):
        frame = self.tab_log
        ctrl = ttk.Frame(frame)
        ctrl.pack(fill="x", pady=4, padx=8)
        ttk.Button(ctrl, text="🗑 Очистить лог", command=self._clear_log).pack(
            side="left", padx=4
        )
        ttk.Button(ctrl, text="💾 Сохранить лог", command=self._save_log).pack(
            side="left", padx=4
        )

        self.log_text = scrolledtext.ScrolledText(
            frame,
            bg=PANEL,
            fg=FG,
            font=MONO,
            relief="flat",
            insertbackground=FG,
            state="disabled",
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=4)
        self.log_text.tag_config("ok", foreground=OK)
        self.log_text.tag_config("warn", foreground=WARN)
        self.log_text.tag_config("info", foreground=ACCENT)

    # ═══════════════════════════════════════════════════════════════════════════
    #  ДЕЙСТВИЯ
    # ═══════════════════════════════════════════════════════════════════════════
