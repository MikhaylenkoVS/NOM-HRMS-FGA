"""ParamsMixin — extracted from app.py."""

import threading, queue, os, sys, traceback, io
from typing import Optional
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


def _to_float(raw, default=None):
    """Разобрать число из поля ввода (запятая или точка)."""
    try:
        return float(str(raw).replace(",", ".").strip())
    except (TypeError, ValueError):
        return default


def _to_int(raw, default=0):
    """Разобрать целое из поля ввода (запятая или точка)."""
    try:
        return int(float(str(raw).replace(",", ".").strip()))
    except (TypeError, ValueError):
        return default


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
        self._run_button = run_btn  # для блокировки во время прогона

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
            ttk.Label(rt_frame, text="(если .raw/.mzML)", foreground="gray").pack(
                side="left", padx=4
            )
            if i == 0:
                # Для исходного спектра: опциональное разбиение диапазона
                # на отрезки (шаг = ширина отрезка в минутах).
                ttk.Label(rt_frame, text="Шаг, мин:").pack(side="left", padx=(12, 2))
                ttk.Entry(rt_frame, textvariable=self.segment_width_var, width=5).pack(
                    side="left", padx=2
                )
                ttk.Checkbutton(
                    rt_frame,
                    text="разбить на отрезки",
                    variable=self.segment_mode_var,
                ).pack(side="left", padx=4)
                ttk.Label(
                    frame,
                    text=(
                        "⚠ Режим отрезков: исходный спектр делится по RT, а "
                        "дериватизаты усредняются по всему файлу. Сопоставление "
                        "по RT для дериватизатов не делается (у продукта и "
                        "исходного соединения RT может различаться), поэтому "
                        "возможны ложные совпадения — режим экспериментальный."
                    ),
                    font=("Segoe UI", 8),
                    foreground="#b07000",
                    wraplength=760,
                    justify="left",
                ).grid(row=0, column=0, sticky="w", padx=10, pady=(0, 4))
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
        # Элементы берём из self.el_vars (созданы по configs/constants/
        # formula_search.json -> ranges), поэтому список не дублируется в коде.
        # C, H, O, N — базовая химия; S, P, F, Cl, Br, I — расширение
        # (см. _ratio_limits_note в том же конфиге про время поиска).
        for i, (sym, (mn, mx)) in enumerate(
            sorted(
                self.el_vars.items(),
                key=lambda kv: (
                    ["C", "H", "O", "N", "S", "P", "F", "Cl", "Br", "I"].index(kv[0])
                    if kv[0] in ["C", "H", "O", "N", "S", "P", "F", "Cl", "Br", "I"]
                    else 99
                ),
            )
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
        ttk.Label(lf, text="Макс. длина серии:").grid(
            row=1, column=0, sticky="w", padx=6, pady=3
        )
        ttk.Entry(lf, textvariable=self.max_groups_var, width=8).grid(
            row=1, column=1, sticky="w", padx=4, pady=3
        )
        # По умолчанию пропуски запрещены; число можно задать вручную.
        ttk.Label(lf, text="Пропусков в серии (0 = запрещены):").grid(
            row=2, column=0, sticky="w", padx=6, pady=3
        )
        ttk.Entry(lf, textvariable=self.max_gaps_var, width=8).grid(
            row=2, column=1, sticky="w", padx=4, pady=3
        )
        ttk.Checkbutton(
            lf,
            text="Шумоподавление спектров дериватизации",
            variable=self.denoise_derivatives_var,
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=2)
        ttk.Checkbutton(
            lf,
            text="Требовать первую ступень серии",
            variable=self.require_first_step_var,
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=6, pady=2)

    def _build_params_advanced(self, nb: ttk.Notebook):
        frame = ttk.Frame(nb)
        nb.add(frame, text="🧪  Фильтры")
        frame.columnconfigure(0, weight=1)
        lf = ttk.LabelFrame(frame, text="Дополнительные фильтры")
        lf.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        cb = ttk.Checkbutton(
            lf,
            text="🔬 Изотопный фильтр (M+1/M+2 по таблице изотопов)",
            variable=self.isotope_filter_var,
        )
        cb.grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(
            lf,
            text="Сравнивает изотопный паттерн M+1/M+2 кандидата с исходным\n"
            "спектром (до шумоподавления): расхождение — штраф, совпадение\n"
            "M+2 для S/Cl/Br — бонус (изотопное подтверждение состава).",
            font=("Segoe UI", 8),
            foreground="#888",
        ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 6))

        cb2 = ttk.Checkbutton(
            lf,
            text="🧬 Искать изотопные варианты (13C, 34S, 37Cl, 81Br, …)",
            variable=self.isotope_variants_var,
        )
        cb2.grid(row=2, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(
            lf,
            text="Для каждой найденной формулы ищутся её изотопные варианты,\n"
            "а пики-сателлиты помечаются и не попадают в отчёт как\n"
            "самостоятельные соединения.",
            font=("Segoe UI", 8),
            foreground="#888",
        ).grid(row=3, column=0, sticky="w", padx=12, pady=(0, 6))

        ttk.Separator(lf, orient="horizontal").grid(
            row=4, column=0, sticky="ew", padx=6, pady=6
        )

        # X/C — пользовательский фильтр (по умолчанию выключен)
        xc_row = ttk.Frame(lf)
        xc_row.grid(row=5, column=0, sticky="w", padx=6, pady=(0, 2))
        ttk.Checkbutton(
            xc_row,
            text="Ограничивать X/C (F+Cl+Br+I)/C",
            variable=self.max_xc_enabled_var,
        ).pack(side="left")
        ttk.Entry(xc_row, textvariable=self.max_xc_var, width=8).pack(
            side="left", padx=6
        )
        ttk.Label(
            lf,
            text=(
                "Жёсткий фильтр отношения галогенов к углероду. По умолчанию "
                "выключен: галогенные формулы подтверждаются изотопным "
                "паттерном, а не отношением. Включайте, если нужен явный предел."
            ),
            font=("Segoe UI", 8),
            foreground="#888",
            wraplength=560,
            justify="left",
        ).grid(row=6, column=0, sticky="w", padx=12, pady=(0, 6))

        # Предел числа атомов галогенов
        hal_row = ttk.Frame(lf)
        hal_row.grid(row=7, column=0, sticky="w", padx=6, pady=(0, 2))
        ttk.Label(hal_row, text="Максимум атомов галогенов в формуле:").pack(
            side="left"
        )
        ttk.Entry(hal_row, textvariable=self.halogen_max_atoms_var, width=6).pack(
            side="left", padx=6
        )
        ttk.Label(
            lf,
            text="По умолчанию 5. Большие значения увеличивают время поиска.",
            font=("Segoe UI", 8),
            foreground="#888",
        ).grid(row=8, column=0, sticky="w", padx=12, pady=(0, 6))

        ttk.Label(lf, text="Шумоподавление спектров:").grid(
            row=9, column=0, sticky="w", padx=6, pady=(4, 0)
        )
        ttk.Checkbutton(
            lf,
            text="Фильтровать дериватизаты (по умолчанию выключено)",
            variable=self.denoise_derivatives_var,
        ).grid(row=10, column=0, sticky="w", padx=6)
        ttk.Checkbutton(
            lf,
            text="Шумоподавление исходного спектра (по умолчанию включено)",
            variable=self.denoise_source_var,
        ).grid(row=10, column=0, sticky="e", padx=6, pady=(24, 0))
        ttk.Label(
            lf,
            text=(
                "Пики продуктов дериватизации низкоинтенсивные: шумоподавление "
                "может вырезать их вместе с шумом, поэтому по умолчанию выключено."
            ),
            font=("Segoe UI", 8),
            foreground="#888",
            wraplength=560,
            justify="left",
        ).grid(row=11, column=0, sticky="w", padx=12, pady=(0, 6))

        ttk.Button(
            lf,
            text="📋 Список изотопов…",
            command=self._show_isotope_table,
        ).grid(row=12, column=0, sticky="w", padx=6, pady=(2, 4))
        ttk.Button(
            lf,
            text="⚙ Настройки поиска по галогенам…",
            command=self._show_halogen_settings,
        ).grid(row=13, column=0, sticky="w", padx=6, pady=(2, 4))
        ttk.Button(
            lf,
            text="📦 База формул…",
            command=self._show_db_variants,
        ).grid(row=14, column=0, sticky="w", padx=6, pady=(2, 8))

        limits_row = ttk.Frame(lf)
        limits_row.grid(row=15, column=0, sticky="w", padx=6, pady=(4, 2))
        ttk.Checkbutton(
            limits_row,
            text="NOM-ratio limits (H/C, O/C, N/C, S/C, P/C)",
            variable=self.ratios_enabled_var,
        ).pack(side="left")
        ttk.Checkbutton(
            limits_row,
            text="NOM DBE limit",
            variable=self.nom_dbe_enabled_var,
        ).pack(side="left", padx=12)

    # Элементы галогенов в порядке отображения в окне настроек.
    _HALOGEN_ORDER = ("F", "Cl", "Br", "I")
    #: Сколько комбинаций проверять в обычном режиме (по приоритету).
    HALOGEN_MAX_COMBINATIONS = 16

    def _halogen_plan_from_ui(self) -> dict | None:
        """План галогенного поиска по текущим настройкам интерфейса."""
        try:
            from src.core.spectrum._constants import FormulaSearchConfig
            from src.core.spectrum._formula_source import halogen_search_plan

            cfg = FormulaSearchConfig()
            ranges = dict(cfg.ranges or {})
            for el, (_mn, mx_var) in self.el_vars.items():
                ranges[el] = (0, _to_int(mx_var.get(), 0))
            cfg.ranges = ranges
            return halogen_search_plan(
                cfg,
                max_combinations=self.HALOGEN_MAX_COMBINATIONS,
                exhaustive=bool(self.halogen_exhaustive_var.get()),
                max_atoms_total=_to_int(self.halogen_max_atoms_var.get(), 5),
            )
        except Exception:
            return None

    def _halogen_warning_text(self, plan: dict) -> str:
        """Текст предупреждения о числе комбинаций и замедлении."""
        limits = plan.get("limits", {})
        window = (
            ", ".join(
                f"{el}≤{limits[el]}" for el in ("F", "Cl", "Br", "I") if limits.get(el)
            )
            or "галогены выключены"
        )
        return (
            f"Будет проверено комбинаций галогенов: {plan['selected']} "
            f"(допустимо в заданных окнах: {plan['allowed']}).\n"
            f"Окна: {window}.\n\n"
            f"Ориентировочное замедление назначения формул: "
            f"×{plan['slowdown']:.2f} (за базу принято 16 комбинаций).\n\n"
            "Уменьшить число комбинаций или сузить окна можно в окне "
            "«⚙ Настройки поиска по галогенам…» — вкладка «Параметры», блок "
            "«Фильтры», сразу под кнопкой «📋 Список изотопов…».\n"
            "Там же снимается галочка «Проверить все комбинации галогенов»."
        )

    def _show_db_variants(self):
        """Информация о базе формул (и о правиле инсталлера).

        Инсталлер ставит CHNOSP всегда — выключать её незачем. Переключатель
        «или одно, или другое» появится только если объём CHNOSPHal станет
        сопоставим с CHNOSP; сейчас CHNOSPHal не предлагается, но программа
        подхватит его автоматически, если файл положить рядом.
        """
        from src.core.formula_db._variants import (
            describe_choice,
            installer_plan,
            variants_report,
        )

        plan = installer_plan()
        win = tk.Toplevel(self)
        win.title("База формул")
        win.transient(self)
        win.resizable(False, False)

        ttk.Label(
            win,
            text=(
                "Сжатая база формул ускоряет работу. Базовая (CHNOSP) ставится "
                "всегда: она занимает десятки мегабайт и ускоряет пайплайн "
                "примерно в 19 раз."
            ),
            wraplength=680,
            justify="left",
        ).grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(10, 4))

        head = ("вариант", "объём", "ускорение", "установлен", "в инсталлере")
        for col, text in enumerate(head):
            ttk.Label(win, text=text, font=("Segoe UI", 9, "bold")).grid(
                row=1, column=col, sticky="w", padx=(10 if col == 0 else 6, 6), pady=2
            )
        for i, row in enumerate(variants_report(), start=2):
            if row["id"] == "chnosp":
                note = "ставится всегда"
            elif row["id"] in plan["choice"]:
                note = "по выбору"
            else:
                note = "не предлагается"
            cells = (
                row["title"],
                f"{row['size_mb']:.1f} МБ" if row["size_mb"] else "—",
                row["speedup"],
                "да" if row["installed"] else "нет",
                note,
            )
            for col, text in enumerate(cells):
                ttk.Label(win, text=text).grid(
                    row=i,
                    column=col,
                    sticky="w",
                    padx=(10 if col == 0 else 6, 6),
                    pady=1,
                )
        base_row = 2 + len(variants_report())
        ttk.Label(
            win,
            text=f"Сейчас используется: {describe_choice()}",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=base_row, column=0, columnspan=5, sticky="w", padx=10, pady=(8, 2))
        ttk.Label(
            win,
            text=f"Инсталлер: {plan['summary']}",
            font=("Segoe UI", 9),
        ).grid(
            row=base_row + 1, column=0, columnspan=5, sticky="w", padx=10, pady=(0, 2)
        )
        ttk.Label(
            win,
            text=(
                "CHNOSPHal (с галогенами) пока не предлагается: он примерно в 15 "
                "раз больше. Его можно положить вручную в data/formula_db — "
                "программа подхватит его автоматически как более быстрый.\n"
                "Принудительный выбор: переменная окружения "
                "NOM_FORMULA_DB = chnosp | chorsphal | none."
            ),
            font=("Segoe UI", 8),
            foreground="#666",
            justify="left",
            wraplength=680,
        ).grid(
            row=base_row + 2, column=0, columnspan=5, sticky="w", padx=10, pady=(0, 10)
        )

    def _show_halogen_settings(self):
        """Окно с настройками поиска по галогенам.

        Обычный режим: проверяется ограниченное число комбинаций, выбранных
        ДИНАМИЧЕСКИ по окнам пользователя (сначала варианты с большим числом
        атомов одного галогена). Галочка сверху включает полный перебор.
        """
        win = tk.Toplevel(self)
        win.title("Настройки поиска по галогенам")
        win.transient(self)
        win.resizable(False, False)
        win.columnconfigure(0, weight=1)

        ttk.Checkbutton(
            win,
            text=(
                "Проверить все комбинации галогенов "
                "(значительно замедляет обработку)"
            ),
            variable=self.halogen_exhaustive_var,
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))

        note = ttk.Label(
            win,
            text=(
                "Обычный режим: проверяются только самые приоритетные комбинации "
                "— сначала варианты с большим числом атомов одного галогена "
                "(например, F5 или Cl4F важнее, чем F2ClBrI). Набор зависит от "
                "пределов ниже: окна выбирают, какие комбинации вообще допустимы."
            ),
            font=("Segoe UI", 8),
            foreground="#666",
            wraplength=520,
            justify="left",
        )
        note.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 6))

        limits = ttk.LabelFrame(win, text="Пределы по галогенам (макс. атомов)")
        limits.grid(row=2, column=0, sticky="ew", padx=10, pady=4)
        spin_vars = {}
        for i, el in enumerate(self._HALOGEN_ORDER):
            ttk.Label(limits, text=f"{el} не более:").grid(
                row=i, column=0, sticky="w", padx=6, pady=2
            )
            max_var = self.el_vars.get(el, (None, None))[1]
            spin = ttk.Spinbox(limits, from_=0, to=5, width=5, textvariable=max_var)
            spin.grid(row=i, column=1, sticky="w", padx=6, pady=2)
            spin_vars[el] = max_var

        ttk.Label(limits, text="всего атомов галогенов:").grid(
            row=len(self._HALOGEN_ORDER), column=0, sticky="w", padx=6, pady=2
        )
        ttk.Spinbox(
            limits,
            from_=1,
            to=8,
            width=5,
            textvariable=self.halogen_max_atoms_var,
        ).grid(row=len(self._HALOGEN_ORDER), column=1, sticky="w", padx=6, pady=2)

        preview = ttk.Label(win, text="", font=("Segoe UI", 9), justify="left")
        preview.grid(row=3, column=0, sticky="w", padx=10, pady=(6, 2))

        listing = tk.Text(win, height=8, width=58, font=("Consolas", 9))
        listing.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        listing.configure(state="disabled")

        def _current_cfg():
            """Текущие настройки как FormulaSearchConfig (для предпросмотра)."""
            from src.core.spectrum._constants import FormulaSearchConfig

            cfg = FormulaSearchConfig()
            ranges = dict(cfg.ranges or {})
            for el, (_mn, mx_var) in self.el_vars.items():
                ranges[el] = (0, _to_int(mx_var.get(), 0))
            cfg.ranges = ranges
            return cfg

        def _update(*_args):
            try:
                from src.core.spectrum._formula_source import (
                    combo_priority,
                    select_halogen_combos,
                )
            except Exception as exc:  # pragma: no cover - база/ядро недоступны
                preview.configure(text=f"Предпросмотр недоступен: {exc}")
                return
            cfg = _current_cfg()
            total = _to_int(self.halogen_max_atoms_var.get(), 5)
            exhaustive = bool(self.halogen_exhaustive_var.get())
            combos, allowed = select_halogen_combos(
                cfg,
                max_combinations=self.HALOGEN_MAX_COMBINATIONS,
                exhaustive=exhaustive,
                max_atoms_total=total,
            )
            shown = sorted(combos, key=combo_priority, reverse=True)[:12]

            def _name(combo):
                return "".join(el + (str(n) if n > 1 else "") for el, n in combo) or "—"

            if exhaustive:
                head = (
                    f"Полный перебор: будет проверено ВСЕХ {allowed} комбинаций "
                    f"(из них {self.HALOGEN_MAX_COMBINATIONS} в обычном режиме)."
                )
            else:
                head = (
                    f"Будет проверено {len(combos)} из {allowed} допустимых "
                    f"комбинаций (приоритет по числу атомов одного галогена)."
                )
            preview.configure(text=head)
            listing.configure(state="normal")
            listing.delete("1.0", "end")
            listing.insert(
                "end", "Первые по приоритету: " + ", ".join(map(_name, shown))
            )
            if not exhaustive and allowed > len(combos):
                listing.insert(
                    "end",
                    "\n\nОстальные комбинации не проверяются: включите галочку "
                    "выше, чтобы перебрать все.",
                )
            listing.configure(state="disabled")

        for var in list(spin_vars.values()) + [self.halogen_max_atoms_var]:
            var.trace_add("write", _update)
        self.halogen_exhaustive_var.trace_add("write", _update)
        _update()

    def _show_isotope_table(self):
        """Отдельное окно со списком изотопов элементов поиска.

        Таблица не висит в основной вкладке: её открывают кнопкой, когда
        нужно посмотреть массы и природные распространённости изотопов,
        которые использует изотопный фильтр и поиск вариантов.
        """
        from src.core.spectrum._isotopes import ISOTOPE_TABLE, isotope_label

        win = tk.Toplevel(self)
        win.title("Список изотопов")
        win.transient(self)
        win.geometry("620x620")

        ttk.Label(
            win,
            text="Изотопы элементов поиска (масса и природная распространённость)",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 2))
        ttk.Label(
            win,
            text="M+1/M+2 считаются по этой таблице; моноизотопные элементы "
            "(P, F, I) имеют один изотоп.",
            font=("Segoe UI", 8),
            foreground="#888",
        ).pack(anchor="w", padx=12, pady=(0, 8))

        holder = ttk.Frame(win)
        holder.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        cols = ("el", "iso", "mass", "abund")
        tv = ttk.Treeview(holder, columns=cols, show="headings", height=22)
        widths = {"el": 90, "iso": 90, "mass": 170, "abund": 200}
        titles = {
            "el": "Элемент",
            "iso": "Изотоп",
            "mass": "Масса, Да",
            "abund": "Распространённость, %",
        }
        for c in cols:
            tv.heading(c, text=titles[c])
            tv.column(c, width=widths[c], anchor="center")
        for el, pairs in ISOTOPE_TABLE.items():
            for i, (mass, abundance) in enumerate(pairs):
                tv.insert(
                    "",
                    "end",
                    values=(
                        el,
                        isotope_label(el, i),
                        f"{mass:.8f}",
                        f"{abundance * 100:.4f}",
                    ),
                )
        scroll = ttk.Scrollbar(holder, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=scroll.set)
        tv.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        ttk.Button(win, text="Закрыть", command=win.destroy).pack(pady=(0, 12))

    def _browse(self, var: tk.StringVar):
        path = filedialog.askopenfilename(
            filetypes=[
                ("CSV / RAW files", "*.csv;*.raw"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
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
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*"),
            ],
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

        # Диапазоны всех элементов из GUI (C, H, O, N, S, P, F, Cl, Br, I).
        brutto_dict: dict[str, tuple[int, int]] = {}
        for el, (mn_var, mx_var) in self.el_vars.items():
            try:
                lo_v = int(mn_var.get())
                hi_v = int(mx_var.get())
            except ValueError:
                errors.append(
                    f"  • {el}: ожидаются целые числа, "
                    f"получено «{mn_var.get()}»-«{mx_var.get()}»"
                )
                _rng = _FORMULA_RANGES.get(el, [0, 0])
                lo_v, hi_v = int(_rng[0]), int(_rng[1])
            if hi_v < lo_v:
                errors.append(f"  • {el}: максимум ({hi_v}) меньше минимума ({lo_v})")
            brutto_dict[el] = (lo_v, hi_v)

        if mass_min is not None and mass_max is not None and mass_min >= mass_max:
            errors.append(f"  • m/z min ({mass_min}) ≥ m/z max ({mass_max})")

        if errors:
            msg = "Ошибки в параметрах:\n" + "\n".join(errors)
            self._log("[DEBUG] Ошибки валидации:\n" + msg, color=WARN)
            messagebox.showerror("Ошибки параметров", msg)
            return None

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
            max_gaps=int(_to_float(self.max_gaps_var.get()) or 0),
            denoise_derivatives=self.denoise_derivatives_var.get(),
            require_first_step=self.require_first_step_var.get(),
            ratios_enabled=self.ratios_enabled_var.get(),
            nom_dbe_enabled=self.nom_dbe_enabled_var.get(),
            isotope_filter=self.isotope_filter_var.get(),
            isotope_variants=self.isotope_variants_var.get(),
            max_xc=(
                _to_float(self.max_xc_var.get())
                if self.max_xc_enabled_var.get()
                else None
            ),
            halogen_max_atoms=_to_int(self.halogen_max_atoms_var.get(), 5),
            halogen_exhaustive=bool(self.halogen_exhaustive_var.get()),
            halogen_max_combinations=self.HALOGEN_MAX_COMBINATIONS,
            denoise_source=self.denoise_source_var.get(),
            brutto_dict=brutto_dict,
            output_csv=self.output_csv_var.get() or None,
            visualize=False,  # визуализацию делаем через GUI-вкладку
        )

    # ── Запуск ────────────────────────────────────────────────────────────────
