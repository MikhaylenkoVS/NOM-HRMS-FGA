"""ResultsMixin — extracted from app.py."""

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


class ResultsMixin:
    """Extracted from app.py."""

    def _fill_result_table(self, df: pd.DataFrame):
        self._log(
            f"[DEBUG] _fill_result_table: {len(df)} строк, "
            f"колонки={list(df.columns)}",
            color="info",
        )
        for row in self.result_tree.get_children():
            self.result_tree.delete(row)

        for col, fill in [
            ("N_COOH", 0),
            ("N_OH", 0),
            ("missing_dmet", []),
            ("missing_dacet", []),
            ("brutto", ""),
            ("all_candidates", []),
        ]:
            if col not in df.columns:
                df[col] = fill
                self._log(
                    f"[WARN] Колонка '{col}' отсутствует → заполнено {fill!r}",
                    color=WARN,
                )

        warn_count = 0
        for i, (_, r) in enumerate(df.iterrows()):
            try:
                n_cooh = int(r.get("N_COOH", 0))
                n_oh = int(r.get("N_OH", 0))
            except (ValueError, TypeError):
                n_cooh = 0
                n_oh = 0

            missing_d = r.get("missing_dmet", [])
            missing_a = r.get("missing_dacet", [])
            has_missing = (isinstance(missing_d, list) and len(missing_d) > 0) or (
                isinstance(missing_a, list) and len(missing_a) > 0
            )

            # Визуальный индикатор: если есть альтернативные формулы-кандидаты
            brutto = r.get("brutto", "")
            candidates = r.get("all_candidates", None)
            has_alternatives = isinstance(candidates, list) and len(candidates) > 1
            brutto_display = f"{brutto}  ▾" if has_alternatives else brutto

            vals = (
                f"{r['mass']:.5f}" if pd.notna(r.get("mass")) else "?",
                brutto_display,
                n_cooh,
                n_oh,
            )
            tags = []
            if has_missing:
                tags.append("warn")
            if has_alternatives:
                tags.append("has_alt")
            tag = tuple(tags) if tags else ""
            if has_missing:
                warn_count += 1
            self.result_tree.insert("", "end", iid=str(i), values=vals, tags=tag)

        self.result_tree.tag_configure("warn", foreground=WARN)
        self.result_tree.tag_configure("has_alt", font=("Consolas", 9, "bold"))
        self._log(
            f"[DEBUG] Таблица: {len(df)} строк, {warn_count} с пропусками.",
            color="info",
        )

    # ── Выбор альтернативной формулы (фича #2) ──────────────────────────────

    # ── Превью структуры при клике на строку ─────────────────────────────

    # ── Предзагрузка структур (фоновая) ────────────────────────────────────────

    def _on_result_row_select(self, event):
        """Один клик по строке — показать структуру из кэша (мгновенно)."""
        selection = self.result_tree.selection()
        if not selection:
            return
        iid = selection[0]
        try:
            idx = int(iid)
        except ValueError:
            return
        if self.result_df is None or idx >= len(self.result_df):
            return

        row = self.result_df.iloc[idx]
        brutto = row.get("brutto", "")
        n_cooh = int(row.get("N_COOH", 0))
        n_oh = int(row.get("N_OH", 0))

        if not brutto:
            self._structure_preview_label.configure(text="Нет формулы\nдля этого пика")
            return

        # ── мгновенная выдача из кэша ──
        brutto_str = str(brutto)
        if brutto_str in self._structure_cache:
            molecules = self._structure_cache[brutto_str]
            self._show_structure_preview(molecules, brutto_str)
            return

        # ── fallback: генерация на лету (если предзагрузка не завершена) ──
        self._structure_preview_label.configure(
            text=f"Поиск структуры...\n{brutto_str}"
        )
        self.progress["value"] = 0

        t = threading.Thread(
            target=self._load_structure_preview,
            args=(brutto_str, n_cooh, n_oh),
            daemon=True,
        )
        t.start()

    def _on_formula_double_click(self, event):
        """Двойной клик по строке таблицы — выбор формулы из кандидатов."""
        selection = self.result_tree.selection()
        if not selection:
            return
        iid = selection[0]
        try:
            idx = int(iid)
        except ValueError:
            return

        if self.result_df is None or idx >= len(self.result_df):
            return

        row = self.result_df.iloc[idx]
        candidates = row.get("all_candidates", None)
        if not isinstance(candidates, list) or len(candidates) <= 1:
            return  # только один кандидат — нечего выбирать

        current_brutto = row.get("brutto", "")

        # Диалоговое окно с выпадающим списком
        dialog = tk.Toplevel(self)
        dialog.title("Выбор брутто-формулы")
        dialog.geometry("380x160")
        dialog.configure(bg=BG)
        dialog.transient(self)
        dialog.grab_set()

        # Центрируем относительно родителя
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 160) // 2
        dialog.geometry(f"+{x}+{y}")

        tk.Label(
            dialog,
            text=f"m/z = {row['mass']:.5f}  —  выберите формулу:",
            bg=BG,
            fg=FG,
            font=("Segoe UI", 10),
        ).pack(padx=12, pady=(12, 8))

        combo_var = tk.StringVar(value=current_brutto)
        combo = ttk.Combobox(
            dialog,
            textvariable=combo_var,
            values=candidates,
            state="readonly",
            width=30,
        )
        combo.pack(padx=12, pady=4)

        def _on_ok():
            new_formula = combo_var.get()
            if new_formula and new_formula != current_brutto:
                self._apply_formula_change(idx, new_formula)
            dialog.destroy()

        def _on_cancel():
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=12)
        ttk.Button(btn_frame, text="OK", command=_on_ok).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Отмена", command=_on_cancel).pack(
            side="left", padx=4
        )

        combo.bind("<Return>", lambda e: _on_ok())
        combo.focus_set()

    def _apply_formula_change(self, idx: int, new_formula: str):
        """Применяет выбор новой формулы: обновляет result_df, таблицу, графики."""
        old_formula = self.result_df.at[idx, "brutto"]
        self.result_df.at[idx, "brutto"] = new_formula
        self._log(
            f"[INFO] Строка {idx}: формула изменена «{old_formula}» → «{new_formula}»",
            color=OK,
        )

        # Обновить отображение в Treeview
        row = self.result_df.iloc[idx]
        candidates = row.get("all_candidates", None)
        has_alternatives = isinstance(candidates, list) and len(candidates) > 1
        brutto_display = f"{new_formula}  ▾" if has_alternatives else new_formula

        vals = list(self.result_tree.item(str(idx), "values"))
        vals[1] = brutto_display  # индекс 1 = колонка «Формула»
        self.result_tree.item(str(idx), values=vals)

        # Перестроить Van Krevelen, если уже был построен
        if self._vk_figure is not None:
            try:
                self._plot_van_krevelen()
            except Exception:
                pass

        self._refresh_structures_tab()

        # Обновить превью структуры для новой формулы
        if new_formula in self._structure_cache:
            self._show_structure_preview(
                self._structure_cache[new_formula], new_formula
            )
        else:
            n_cooh = int(row.get("N_COOH", 0))
            n_oh = int(row.get("N_OH", 0))
            self._structure_preview_label.configure(
                text=f"Поиск структуры...\n{new_formula}"
            )
            self.progress["value"] = 0
            t = threading.Thread(
                target=self._load_structure_preview,
                args=(new_formula, n_cooh, n_oh),
                daemon=True,
            )
            t.start()

    def _sort_tree(self, col: str):
        if self.result_df is None:
            return
        if col not in self.result_df.columns:
            self._log(f"[WARN] Сортировка: колонка '{col}' не найдена", color=WARN)
            return
        ascending = getattr(self, f"_sort_{col}_asc", True)
        try:
            self.result_df = self.result_df.sort_values(
                col, ascending=ascending, na_position="last"
            )
        except Exception as e:
            self._log(f"[WARN] Сортировка по '{col}': {e}", color=WARN)
            return
        setattr(self, f"_sort_{col}_asc", not ascending)
        self._fill_result_table(self.result_df)

    # ── Импорт CSV ────────────────────────────────────────────────────
