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

    def _center_dialog(self, win: tk.Toplevel, width: int, height: int) -> None:
        """Поставить дочернее окно по центру родителя."""
        win.transient(self)
        win.resizable(True, True)
        x = self.winfo_rootx() + max(0, (self.winfo_width() - width) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - height) // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def _scrollable_tab(self, nb: ttk.Notebook, title: str) -> ttk.Frame:
        """Вкладка с вертикальной прокруткой: контент не обрезается."""
        outer = ttk.Frame(nb)
        nb.add(outer, text=title)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        inner = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(window_id, width=e.width),
        )

        def _wheel(event):
            canvas.yview_scroll(int(-event.delta / 120), "units")

        canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", _wheel))
        canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))
        return inner

    def _build_params_files(self, nb: ttk.Notebook):
        frame = self._scrollable_tab(nb, "📂  Файлы")
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
        frame = self._scrollable_tab(nb, "📏  Обработка")
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
        frame = self._scrollable_tab(nb, "🔬  Формулы")
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
        frame = self._scrollable_tab(nb, "🔍  Серии")
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
            text="Требовать первую ступень серии",
            variable=self.require_first_step_var,
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=2)

    def _build_params_advanced(self, nb: ttk.Notebook):
        frame = self._scrollable_tab(nb, "🧪  Фильтры")
        frame.columnconfigure(0, weight=1)

        # ── Изотопы ──────────────────────────────────────────────────
        iso = ttk.LabelFrame(frame, text="Изотопы")
        iso.grid(row=0, column=0, sticky="ew", padx=8, pady=(4, 2))
        iso.columnconfigure(0, weight=1)
        ttk.Checkbutton(
            iso,
            text="Изотопный фильтр M+1/M+2",
            variable=self.isotope_filter_var,
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))
        ttk.Checkbutton(
            iso,
            text="Искать изотопные варианты (13C, 34S, 37Cl, 81Br, …)",
            variable=self.isotope_variants_var,
        ).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 2))
        ttk.Button(
            iso,
            text="📋 Список изотопов…",
            command=self._show_isotope_table,
        ).grid(row=2, column=0, sticky="w", padx=8, pady=(4, 8))

        # ── Галогены ─────────────────────────────────────────────────
        hal = ttk.LabelFrame(frame, text="Галогены")
        hal.grid(row=1, column=0, sticky="ew", padx=8, pady=2)
        hal.columnconfigure(1, weight=1)
        ttk.Checkbutton(
            hal,
            text="Ограничивать X/C (F+Cl+Br+I)/C:",
            variable=self.max_xc_enabled_var,
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))
        ttk.Entry(hal, textvariable=self.max_xc_var, width=8).grid(
            row=0, column=1, sticky="w", padx=4, pady=(6, 2)
        )
        ttk.Label(hal, text="Максимум атомов галогенов:").grid(
            row=1, column=0, sticky="w", padx=8, pady=2
        )
        ttk.Spinbox(
            hal,
            from_=0,
            to=8,
            width=7,
            textvariable=self.halogen_max_atoms_var,
        ).grid(row=1, column=1, sticky="w", padx=4, pady=2)
        ttk.Button(
            hal,
            text="⚙ Настройки поиска по галогенам…",
            command=self._show_halogen_settings,
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 8))

        # ── Шумоподавление ───────────────────────────────────────────
        den = ttk.LabelFrame(frame, text="Шумоподавление")
        den.grid(row=2, column=0, sticky="ew", padx=8, pady=2)
        den.columnconfigure(0, weight=1)
        den.columnconfigure(1, weight=1)
        ttk.Checkbutton(
            den,
            text="Исходный спектр",
            variable=self.denoise_source_var,
        ).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Checkbutton(
            den,
            text="Спектры дериватизации",
            variable=self.denoise_derivatives_var,
        ).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        # ── Ограничения NOM ──────────────────────────────────────────
        lim = ttk.LabelFrame(frame, text="Ограничения NOM")
        lim.grid(row=3, column=0, sticky="ew", padx=8, pady=2)
        ttk.Checkbutton(
            lim,
            text="H/C, O/C, N/C, S/C, P/C",
            variable=self.ratios_enabled_var,
        ).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Checkbutton(
            lim,
            text="DBE limit",
            variable=self.nom_dbe_enabled_var,
        ).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        # ── База формул ──────────────────────────────────────────────
        db = ttk.LabelFrame(frame, text="База формул")
        db.grid(row=4, column=0, sticky="ew", padx=8, pady=2)
        ttk.Button(
            db,
            text="📦 База формул…",
            command=self._show_db_variants,
        ).grid(row=0, column=0, sticky="w", padx=8, pady=8)

        # ── Справка ──────────────────────────────────────────────────
        help_row = ttk.Frame(frame)
        help_row.grid(row=5, column=0, sticky="ew", padx=8, pady=(4, 4))
        ttk.Button(
            help_row,
            text="📖 Руководство пользователя",
            command=self._open_user_guide,
        ).pack(side="left")
        ttk.Label(
            help_row,
            text="Подробности по параметрам — в документации.",
            foreground="#777",
        ).pack(side="left", padx=10)

    def _open_user_guide(self) -> None:
        """Открыть пользовательскую документацию из GUI."""
        import webbrowser

        doc = Path(__file__).resolve().parents[2] / "docs" / "user_guide.md"
        if doc.is_file():
            try:
                os.startfile(str(doc))  # type: ignore[attr-defined]
                return
            except Exception:
                pass
        webbrowser.open(
            "https://github.com/MikhaylenkoVS/NOM-HRMS-FGA/blob/main/docs/user_guide.md"
        )

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
        """Компактное окно управления базами формул."""
        from src.core.formula_db._variants import (
            DB_VARIANTS,
            describe_choice,
            find_variant_path,
            variants_report,
        )

        win = tk.Toplevel(self)
        win.title("База формул")
        win.minsize(620, 360)
        self._center_dialog(win, 760, 460)

        body = ttk.Frame(win)
        body.pack(fill="both", expand=True, padx=12, pady=12)
        ttk.Label(body, text="База формул", font=("Segoe UI", 11, "bold")).pack(
            anchor="w"
        )
        ttk.Label(
            body,
            text="CHNOSP уже включена в сборку. CHNOSPHal можно скачать отдельно — "
            "она ускоряет назначение формул и будет использована после перезапуска.",
            foreground="#777",
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        table = ttk.Frame(body)
        table.pack(fill="both", expand=True)
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=1)
        cols = ("variant", "size", "speed", "state")
        tv = ttk.Treeview(table, columns=cols, show="headings", height=3)
        headings = {
            "variant": "Вариант",
            "size": "Объём",
            "speed": "Ускорение",
            "state": "Статус",
        }
        widths = {"variant": 340, "size": 100, "speed": 110, "state": 120}
        for c in cols:
            tv.heading(c, text=headings[c])
            tv.column(c, width=widths[c], anchor="w" if c == "variant" else "center")
        for i, row in enumerate(variants_report()):
            tv.insert(
                "",
                "end",
                tags=("odd",) if i % 2 else (),
                values=(
                    row["title"],
                    f"{row['size_mb']:.1f} МБ" if row["size_mb"] else "—",
                    row["speedup"],
                    "установлена" if row["installed"] else "нет",
                ),
            )
        tv.tag_configure("odd", background="#f5f5f5")
        scroll = ttk.Scrollbar(table, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=scroll.set)
        tv.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        ttk.Label(
            body,
            text=f"Сейчас используется: {describe_choice()}",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(10, 6))

        actions = ttk.Frame(body)
        actions.pack(fill="x")
        for v in [v for v in DB_VARIANTS if not find_variant_path(v)]:
            ttk.Button(
                actions,
                text=f"Скачать {v.title.split(' — ')[0]} ({v.size_mb:.0f} МБ)…",
                command=lambda v=v: self._download_db_variant(v),
            ).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Закрыть", command=win.destroy).pack(side="right")

    def _download_db_variant(self, variant) -> None:
        """Скачать опциональную базу формул в пользовательский каталог."""
        from src.core.formula_db._manager import DatabaseManager
        from src.core.formula_db._variants import find_variant_path

        if find_variant_path(variant):
            messagebox.showinfo("База формул", "Эта база уже установлена.", parent=self)
            return
        if not messagebox.askyesno(
            "Скачать базу формул?",
            f"Будет скачано {variant.size_mb:.0f} МБ ({variant.title}).\n"
            "База сохранится отдельно от exe и будет использована после перезапуска.",
            parent=self,
        ):
            return

        win = tk.Toplevel(self)
        win.title("Загрузка базы формул")
        self._center_dialog(win, 560, 240)
        win.resizable(False, False)
        body = ttk.Frame(win)
        body.pack(fill="both", expand=True, padx=14, pady=14)
        ttk.Label(
            body,
            text=variant.title,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            body,
            text="Скачивание отдельной базы формул. После завершения перезапустите программу.",
            foreground="#777",
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(2, 10))
        stage_var = tk.StringVar(value="Подготовка…")
        ttk.Label(body, textvariable=stage_var).pack(anchor="w")
        progress = ttk.Progressbar(body, length=520, maximum=100)
        progress.pack(fill="x", pady=8)

        state = {
            "cancel": False,
            "done": False,
            "error": None,
            "stage": "",
            "frac": 0.0,
        }

        def on_cancel() -> None:
            state["cancel"] = True
            stage_var.set("Отмена…")

        ttk.Button(win, text="Отмена", command=on_cancel).pack(
            anchor="e", padx=12, pady=(0, 10)
        )
        win.protocol("WM_DELETE_WINDOW", on_cancel)

        def progress_cb(stage: str, frac: float) -> None:
            state["stage"] = stage
            state["frac"] = float(frac)

        def worker() -> None:
            try:
                mgr = DatabaseManager()
                mgr.download_variant(
                    variant,
                    progress_callback=progress_cb,
                    cancel_check=lambda: state["cancel"],
                )
                state["done"] = True
            except Exception as exc:  # noqa: BLE001 - показываем пользователю
                state["error"] = exc

        threading.Thread(target=worker, daemon=True).start()

        def poll() -> None:
            if state["done"]:
                win.destroy()
                messagebox.showinfo(
                    "База формул",
                    "База скачана. Перезапустите программу, чтобы она стала активной.",
                    parent=self,
                )
                return
            if state["error"] is not None:
                win.destroy()
                if state["cancel"]:
                    messagebox.showinfo(
                        "База формул", "Загрузка отменена.", parent=self
                    )
                else:
                    messagebox.showerror(
                        "Ошибка загрузки базы",
                        f"Не удалось скачать базу:\n{state['error']}",
                        parent=self,
                    )
                return
            stage_var.set(state["stage"] or "Загрузка…")
            progress["value"] = max(0.0, min(100.0, state["frac"] * 100.0))
            win.after(150, poll)

        win.after(150, poll)

    def _show_halogen_settings(self):
        """Окно настроек поиска по галогенам."""
        win = tk.Toplevel(self)
        win.title("Настройки поиска по галогенам")
        win.minsize(680, 480)
        self._center_dialog(win, 760, 560)

        body = ttk.Frame(win)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        top = ttk.Frame(body)
        top.pack(fill="x")
        ttk.Checkbutton(
            top,
            text="Проверить все комбинации галогенов (медленно)",
            variable=self.halogen_exhaustive_var,
        ).pack(side="left")
        ttk.Label(
            top,
            text="Подробнее — в руководстве пользователя.",
            foreground="#777",
        ).pack(side="right")

        content = ttk.Frame(body)
        content.pack(fill="both", expand=True, pady=(10, 8))
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        limits = ttk.LabelFrame(content, text="Пределы (макс. атомов)")
        limits.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        spin_vars = {}
        for i, el in enumerate(self._HALOGEN_ORDER):
            ttk.Label(limits, text=f"{el}:").grid(
                row=i, column=0, sticky="w", padx=8, pady=3
            )
            max_var = self.el_vars.get(el, (None, None))[1]
            ttk.Spinbox(limits, from_=0, to=5, width=5, textvariable=max_var).grid(
                row=i, column=1, sticky="w", padx=8, pady=3
            )
            spin_vars[el] = max_var
        ttk.Separator(limits, orient="horizontal").grid(
            row=len(self._HALOGEN_ORDER), column=0, columnspan=2, sticky="ew", pady=6
        )
        ttk.Label(limits, text="Всего:").grid(
            row=len(self._HALOGEN_ORDER) + 1, column=0, sticky="w", padx=8, pady=3
        )
        ttk.Spinbox(
            limits,
            from_=1,
            to=8,
            width=5,
            textvariable=self.halogen_max_atoms_var,
        ).grid(
            row=len(self._HALOGEN_ORDER) + 1,
            column=1,
            sticky="w",
            padx=8,
            pady=3,
        )

        preview_lf = ttk.LabelFrame(content, text="Предпросмотр")
        preview_lf.grid(row=0, column=1, sticky="nsew")
        preview_lf.columnconfigure(0, weight=1)
        preview_lf.rowconfigure(1, weight=1)

        preview = ttk.Label(
            preview_lf, text="", font=("Segoe UI", 9), justify="left", wraplength=420
        )
        preview.grid(row=0, column=0, sticky="w", padx=8, pady=(6, 4))

        listing_holder = ttk.Frame(preview_lf)
        listing_holder.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        listing_holder.columnconfigure(0, weight=1)
        listing_holder.rowconfigure(0, weight=1)
        listing = tk.Text(
            listing_holder,
            height=12,
            width=50,
            font=("Consolas", 9),
            wrap="word",
            relief="flat",
        )
        listing_scroll = ttk.Scrollbar(
            listing_holder, orient="vertical", command=listing.yview
        )
        listing.configure(yscrollcommand=listing_scroll.set)
        listing.grid(row=0, column=0, sticky="nsew")
        listing_scroll.grid(row=0, column=1, sticky="ns")
        listing.configure(state="disabled")

        def _current_cfg():
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
            except Exception as exc:  # pragma: no cover
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
                head = f"Полный перебор: {allowed} комбинаций."
            else:
                head = f"Будет проверено {len(combos)} из {allowed} комбинаций."
            preview.configure(text=head)
            listing.configure(state="normal")
            listing.delete("1.0", "end")
            listing.insert("end", ", ".join(map(_name, shown)))
            if not exhaustive and allowed > len(combos):
                listing.insert(
                    "end",
                    "\n\nОстальные не проверяются: включите полный перебор.",
                )
            listing.configure(state="disabled")

        for var in list(spin_vars.values()) + [self.halogen_max_atoms_var]:
            var.trace_add("write", _update)
        self.halogen_exhaustive_var.trace_add("write", _update)
        _update()

        ttk.Button(body, text="Закрыть", command=win.destroy).pack(anchor="e")

    def _show_isotope_table(self):
        """Отдельное окно со списком изотопов элементов поиска."""
        from src.core.spectrum._isotopes import ISOTOPE_TABLE, isotope_label

        win = tk.Toplevel(self)
        win.title("Список изотопов")
        win.minsize(560, 420)
        self._center_dialog(win, 640, 560)

        body = ttk.Frame(win)
        body.pack(fill="both", expand=True, padx=12, pady=12)
        ttk.Label(
            body,
            text="Изотопы элементов поиска",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            body,
            text="Массы и природная распространённость; моноизотопные элементы — P, F, I.",
            foreground="#777",
        ).pack(anchor="w", pady=(0, 8))

        holder = ttk.Frame(body)
        holder.pack(fill="both", expand=True)
        holder.columnconfigure(0, weight=1)
        holder.rowconfigure(0, weight=1)

        cols = ("el", "iso", "mass", "abund")
        tv = ttk.Treeview(holder, columns=cols, show="headings")
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
        tv.tag_configure("odd", background="#f5f5f5")
        for idx, (el, pairs) in enumerate(ISOTOPE_TABLE.items()):
            for i, (mass, abundance) in enumerate(pairs):
                tv.insert(
                    "",
                    "end",
                    tags=("odd",) if idx % 2 else (),
                    values=(
                        el,
                        isotope_label(el, i),
                        f"{mass:.8f}",
                        f"{abundance * 100:.4f}",
                    ),
                )
        scroll = ttk.Scrollbar(holder, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=scroll.set)
        tv.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(body, text="Закрыть", command=win.destroy).pack(
            anchor="e", pady=(10, 0)
        )

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
