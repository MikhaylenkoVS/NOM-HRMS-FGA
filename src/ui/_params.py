"""ParamsMixin — extracted from app.py."""

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


class ParamsMixin:
    """Extracted from app.py."""

    def _build_params_tab(self):
        p = self.tab_params
        p.columnconfigure(0, weight=1)
        p.rowconfigure(0, weight=1)  # подвкладки растягиваются

        sub_nb = ttk.Notebook(p)
        sub_nb.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self._build_params_files(sub_nb)
        self._build_params_processing(sub_nb)
        self._build_params_formulas(sub_nb)
        self._build_params_series(sub_nb)
        self._build_params_advanced(sub_nb)

        try:
            run_btn = ttk.Button(
                p, text="▶  Запустить анализ", style="Accent.TButton", command=self._run
            )
        except Exception:
            run_btn = ttk.Button(p, text="▶  Запустить анализ", command=self._run)
        run_btn.grid(row=1, column=0, pady=12, ipadx=20, ipady=4)

    def _build_params_files(self, nb: ttk.Notebook):
        frame = ttk.Frame(nb)
        nb.add(frame, text="📂  Файлы")
        frame.columnconfigure(0, weight=1)
        files_lf = ttk.LabelFrame(frame, text="Входные спектры")
        files_lf.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        files_lf.columnconfigure(1, weight=1)

        rt_configs = [
            (self.src_var, self.src_rt_min, self.src_rt_max),
            (self.dmet_var, self.dmet_rt_min, self.dmet_rt_max),
            (self.dacet_var, self.dacet_rt_min, self.dacet_rt_max),
        ]
        for i, (label, (spec_var, rt_min_var, rt_max_var)) in enumerate(
            [
                ("Исходный спектр:", rt_configs[0]),
                ("Дейтерометилирование:", rt_configs[1]),
                ("Дейтероацилирование:", rt_configs[2]),
            ]
        ):
            base_row = i * 2
            ttk.Label(files_lf, text=label).grid(
                row=base_row, column=0, sticky="w", padx=6, pady=4
            )
            ttk.Entry(files_lf, textvariable=spec_var, width=55).grid(
                row=base_row, column=1, sticky="ew", padx=4, pady=4
            )
            ttk.Button(
                files_lf, text="...", command=lambda v=spec_var: self._browse(v)
            ).grid(row=base_row, column=2, padx=4, pady=4)
            # RT-диапазон (под полем ввода, для .raw)
            rt_frame = ttk.Frame(files_lf)
            rt_frame.grid(
                row=base_row + 1,
                column=1,
                columnspan=2,
                sticky="w",
                padx=4,
                pady=(0, 6),
            )
            ttk.Label(rt_frame, text="RT, мин:").pack(side="left")
            ttk.Entry(rt_frame, textvariable=rt_min_var, width=5).pack(
                side="left", padx=2
            )
            ttk.Label(rt_frame, text="–").pack(side="left")
            ttk.Entry(rt_frame, textvariable=rt_max_var, width=5).pack(
                side="left", padx=2
            )
            ttk.Label(rt_frame, text="(если .raw)", foreground="gray").pack(
                side="left", padx=4
            )
        out_lf = ttk.LabelFrame(frame, text="💾  Выходной файл")
        out_lf.grid(row=1, column=0, sticky="ew", padx=8, pady=6)
        out_lf.columnconfigure(0, weight=1)
        ttk.Entry(out_lf, textvariable=self.output_csv_var, width=50).grid(
            row=0, column=0, sticky="ew", padx=6, pady=4
        )
        ttk.Button(
            out_lf, text="...", command=lambda: self._save_browse(self.output_csv_var)
        ).grid(row=0, column=1, padx=4, pady=4)

        # ── Пресеты ──
        preset_lf = ttk.LabelFrame(frame, text="🎯  Пресеты параметров")
        preset_lf.grid(row=2, column=0, sticky="ew", padx=8, pady=6)
        self.preset_var = tk.StringVar(value="")
        try:
            from src.configs.presets_loader import list_presets

            presets = list_presets()
            preset_names = [f"{p['name']}" for p in presets]
        except Exception:
            presets = []
            preset_names = ["(пресеты недоступны)"]
        cb = ttk.Combobox(
            preset_lf,
            textvariable=self.preset_var,
            values=preset_names,
            state="readonly",
            width=40,
        )
        cb.pack(side="left", padx=6, pady=4)
        ttk.Button(
            preset_lf,
            text="Применить",
            command=lambda: self._apply_preset(presets),
        ).pack(side="left", padx=4, pady=4)
        self._presets_data = presets

        # Кнопка импорта целой папки
        ttk.Button(
            frame, text="📁 Импорт папки со спектрами", command=self._import_folder
        ).grid(row=3, column=0, sticky="w", padx=8, pady=(4, 2))
        self._folder_path_var = tk.StringVar()
        tk.Label(
            frame,
            textvariable=self._folder_path_var,
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 8),
            anchor="w",
        ).grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 2))

    def _build_params_processing(self, nb: ttk.Notebook):
        frame = ttk.Frame(nb)
        nb.add(frame, text="📏  Обработка")
        frame.columnconfigure(0, weight=1)
        load_lf = ttk.LabelFrame(frame, text="Загрузка и фильтрация")
        load_lf.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        for row, (lbl, var) in enumerate(
            [
                ("Разделитель CSV:", self.sep_var),
                ("m/z min:", self.mass_min_var),
                ("m/z max:", self.mass_max_var),
            ]
        ):
            ttk.Label(load_lf, text=lbl).grid(
                row=row, column=0, sticky="w", padx=6, pady=3
            )
            ttk.Entry(load_lf, textvariable=var, width=12).grid(
                row=row, column=1, sticky="w", padx=4, pady=3
            )
        ttk.Label(load_lf, text="Шумоподавление:").grid(
            row=3, column=0, sticky="w", padx=6, pady=3
        )
        noise_methods = ["auto", "intensity", "quantile"]
        noise_names = {
            "auto": "GMM (авто, force 1.0-3.0)",
            "intensity": "Абс. интенсивность (100+)",
            "quantile": "Квантиль (0.01)",
        }
        self._noise_cb = ttk.Combobox(
            load_lf,
            textvariable=self.noise_method_var,
            values=[noise_names[m] for m in noise_methods],
            width=28,
            state="readonly",
        )
        self._noise_cb.grid(row=3, column=1, sticky="w", padx=4, pady=3)
        self._noise_cb.bind("<<ComboboxSelected>>", self._on_noise_method_change)
        self._noise_cb.current(0)  # default = GMM auto
        ttk.Label(load_lf, text="Значение:").grid(
            row=4, column=0, sticky="w", padx=6, pady=3
        )
        ttk.Entry(load_lf, textvariable=self.noise_value_var, width=12).grid(
            row=4, column=1, sticky="w", padx=4, pady=3
        )

    def _build_params_formulas(self, nb: ttk.Notebook):
        frame = ttk.Frame(nb)
        nb.add(frame, text="🔬  Формулы")
        frame.columnconfigure(0, weight=1)
        lf = ttk.LabelFrame(frame, text="Назначение брутто-формул")
        lf.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        ttk.Label(lf, text="Знак иона:").grid(
            row=0, column=0, sticky="w", padx=6, pady=3
        )
        ttk.Combobox(
            lf, textvariable=self.sign_var, values=["-", "+"], width=5, state="readonly"
        ).grid(row=0, column=1, sticky="w", padx=4, pady=3)
        ttk.Label(lf, text="Погрешность (ppm):").grid(
            row=1, column=0, sticky="w", padx=6, pady=3
        )
        ttk.Entry(lf, textvariable=self.rel_error_var, width=8).grid(
            row=1, column=1, sticky="w", padx=4, pady=3
        )
        ttk.Label(lf, text="Диапазоны элементов:").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=6, pady=(10, 2)
        )
        for i, (sym, mn, mx) in enumerate(
            [
                ("C", self.c_min, self.c_max),
                ("H", self.h_min, self.h_max),
                ("O", self.o_min, self.o_max),
                ("N", self.n_min, self.n_max),
            ]
        ):
            r = 3 + i
            ttk.Label(lf, text=f"{sym}:").grid(
                row=r, column=0, sticky="w", padx=20, pady=2
            )
            ef = ttk.Frame(lf)
            ef.grid(row=r, column=1, sticky="w", padx=4, pady=2)
            ttk.Entry(ef, textvariable=mn, width=5).pack(side="left")
            ttk.Label(ef, text="-").pack(side="left", padx=2)
            ttk.Entry(ef, textvariable=mx, width=5).pack(side="left")

    def _build_params_series(self, nb: ttk.Notebook):
        frame = ttk.Frame(nb)
        nb.add(frame, text="🔍  Серии")
        frame.columnconfigure(0, weight=1)
        lf = ttk.LabelFrame(frame, text="Поиск гомологических серий")
        lf.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        ttk.Label(lf, text="Допуск поиска (ppm):").grid(
            row=0, column=0, sticky="w", padx=6, pady=3
        )
        ttk.Entry(lf, textvariable=self.ppm_tol_var, width=8).grid(
            row=0, column=1, sticky="w", padx=4, pady=3
        )
        ttk.Label(lf, text="Макс. число групп:").grid(
            row=1, column=0, sticky="w", padx=6, pady=3
        )
        ttk.Entry(lf, textvariable=self.max_groups_var, width=8).grid(
            row=1, column=1, sticky="w", padx=4, pady=3
        )
        ttk.Checkbutton(
            lf, text="Разрешить пропуски в сериях", variable=self.allow_gaps_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=4)

    def _build_params_advanced(self, nb: ttk.Notebook):
        frame = ttk.Frame(nb)
        nb.add(frame, text="🧪  Фильтры")
        frame.columnconfigure(0, weight=1)
        lf = ttk.LabelFrame(frame, text="Дополнительные фильтры")
        lf.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        cb = ttk.Checkbutton(
            lf,
            text="🔬 Изотопный фильтр ¹³C (формула Бейнона)",
            variable=self.isotope_filter_var,
        )
        cb.grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(
            lf,
            text="Штрафует формулы, чей изотопный паттерн M+1/M\n"
            "отличается от теоретического более чем на 20%.\n"
            "Проверка — по исходному спектру до шумоподавления.",
            font=("Segoe UI", 8),
            foreground="#888",
        ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 6))

    def _browse(self, var: tk.StringVar):
        path = filedialog.askopenfilename(
            filetypes=[
                ("CSV / RAW files", "*.csv;*.raw"),
                ("CSV files", "*.csv"),
                ("RAW files", "*.raw"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ]
        )
        if path:
            var.set(path)

    def _save_browse(self, var: tk.StringVar):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            var.set(path)

    # ── Денойз: обновление значения при смене метода ──────────────────────────

    def _on_noise_method_change(self, event=None):
        """Update the parameter field to a suggested default for the selected method."""
        defaults = {"auto": "2.0", "intensity": "100", "quantile": "0.01"}
        method = self.noise_method_var.get()
        for key, name in {
            "auto": "GMM",
            "intensity": "Абс. интенсивность",
            "quantile": "Квантиль",
        }.items():
            if name in method:
                self.noise_value_var.set(defaults[key])
                return

    # ── Валидация и парсинг параметров ────────────────────────────────────────

    def _parse_params(self) -> Optional[dict]:
        """
        Читает все параметры из виджетов и валидирует типы.
        При ошибке логирует, показывает messagebox и возвращает None.
        """
        errors = []

        def _float(var, name, default=None):
            try:
                return float(var.get())
            except ValueError:
                errors.append(f"  • {name}: ожидается число, получено «{var.get()}»")
                return default

        def _int(var, name, default=None):
            try:
                return int(var.get())
            except ValueError:
                errors.append(f"  • {name}: ожидается целое, получено «{var.get()}»")
                return default

        sep = self.sep_var.get()
        if sep in ("\\t", "tab", "TAB"):
            sep = "\t"

        mass_min = _float(self.mass_min_var, "m/z min", 0.0)
        mass_max = _float(self.mass_max_var, "m/z max", 1000.0)
        # Денойз: взаимоисключающие параметры (intensity > quantile > auto/GMM)
        noise_method = self.noise_method_var.get()
        noise_value = _float(self.noise_value_var, "Шум значение", 1.5)
        if "intensity" in noise_method or "Абс. интенсивность" in noise_method:
            noise_force, noise_int, noise_quantile = None, noise_value, None
        elif "quantile" in noise_method or "Квантиль" in noise_method:
            noise_force, noise_int, noise_quantile = None, None, noise_value
        else:
            # GMM auto — noise_value = force multiplier
            noise_force, noise_int, noise_quantile = noise_value, None, None
        rel_error = _float(self.rel_error_var, "Погрешность ppm", 0.5)
        ppm_tol = _float(self.ppm_tol_var, "Допуск поиска ppm", 0.5)
        max_groups = _int(self.max_groups_var, "Макс. групп", 20)

        try:
            c_min = int(self.c_min.get())
            c_max = int(self.c_max.get())
            h_min = int(self.h_min.get())
            h_max = int(self.h_max.get())
            o_min = int(self.o_min.get())
            o_max = int(self.o_max.get())
            n_min = int(self.n_min.get())
            n_max = int(self.n_max.get())
        except ValueError as e:
            errors.append(f"  • Диапазон элементов: {e}")
            _r = _FORMULA_RANGES
            c_min = _r["C"][0]
            c_max = _r["C"][1]
            h_min = _r["H"][0]
            h_max = _r["H"][1]
            o_min = _r["O"][0]
            o_max = _r["O"][1]
            n_min = _r["N"][0]
            n_max = _r["N"][1]

        if mass_min is not None and mass_max is not None and mass_min >= mass_max:
            errors.append(f"  • m/z min ({mass_min}) ≥ m/z max ({mass_max})")

        if errors:
            msg = "Ошибки в параметрах:\n" + "\n".join(errors)
            self._log("[DEBUG] Ошибки валидации:\n" + msg, color=WARN)
            messagebox.showerror("Ошибки параметров", msg)
            return None

        brutto_dict = {
            "C": (c_min, c_max),
            "H": (h_min, h_max),
            "O": (o_min, o_max),
            "N": (n_min, n_max),
        }

        return dict(
            sep=sep,
            load_mass_min=mass_min,
            load_mass_max=mass_max,
            noise_force=noise_force,
            noise_intensity=noise_int,
            noise_quantile=noise_quantile,
            rel_error=rel_error,
            sign=self.sign_var.get(),
            assign_mass_min=_GUI_DEFAULTS["assign_mass_min"],
            assign_mass_max=_GUI_DEFAULTS["assign_mass_max"],
            ppm_tol=ppm_tol,
            max_groups=max_groups,
            allow_gaps=self.allow_gaps_var.get(),
            isotope_filter=self.isotope_filter_var.get(),
            brutto_dict=brutto_dict,
            output_csv=self.output_csv_var.get() or None,
            visualize=False,  # визуализацию делаем через GUI-вкладку
        )

    # ── Запуск ────────────────────────────────────────────────────────────────
