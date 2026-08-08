"""PresetsMixin — extracted from app.py."""

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


class PresetsMixin:
    """Extracted from app.py."""

    def _import_csv(self):
        """Загрузить result_table.csv, заполнить таблицу и структуры."""
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
        except Exception:
            # пробуем другие разделители
            try:
                df = pd.read_csv(path, sep=",", encoding="utf-8")
            except Exception as e:
                messagebox.showerror("Ошибка импорта", str(e))
                return

        self.result_df = df
        self._log(f"[INFO] Импортировано: {path} ({len(df)} строк)", color=OK)
        self._set_status(f"Импортировано {len(df)} соединений.")
        self._fill_result_table(df)
        self._auto_plot_hist()
        self._refresh_structures_tab()

    # ── Импорт папки ──────────────────────────────────────────────────

    _SPECTRUM_PATTERNS = {
        "src": ["original", "src", "source", "исходный", "orig"],
        "dmet": ["deutermethyl", "dmet", "cd3", "дейтерометил"],
        "dacet": ["deuteroacyl", "dacet", "cd3co", "дейтероацил"],
    }

    def _apply_preset(self, presets: list):
        """Применить выбранный пресет параметров."""
        name = self.preset_var.get()
        preset = next((p for p in presets if p["name"] == name), None)
        if not preset:
            return
        params = preset.get("params", {})
        # Масс-фильтр
        for var, key in [
            (self.mass_min_var, "load_mass_min"),
            (self.mass_max_var, "load_mass_max"),
        ]:
            if key in params:
                var.set(str(params[key]))
        # Шумоподавление
        if "noise_intensity" in params:
            self.noise_int_var.set(str(params["noise_intensity"]))
        if "noise_force" in params:
            self.noise_force_var.set(str(params["noise_force"]))
        # Формулы
        if "rel_error" in params:
            self.rel_error_var.set(str(params["rel_error"]))
        if "ppm_tol" in params:
            self.ppm_tol_var.set(str(params["ppm_tol"]))
        if "max_groups" in params:
            self.max_groups_var.set(str(params["max_groups"]))
        # Диапазоны элементов
        er = params.get("element_ranges", {})
        for el, (var_min, var_max) in [
            ("C", (self.c_min, self.c_max)),
            ("H", (self.h_min, self.h_max)),
            ("O", (self.o_min, self.o_max)),
            ("N", (self.n_min, self.n_max)),
        ]:
            if el in er:
                var_min.set(str(er[el][0]))
                var_max.set(str(er[el][1]))
        self._log(f"[PRESET] Применён: {name}", color="info")

    def _import_folder(self):
        """Автоопределение трёх спектров в папке по шаблонам имён."""
        folder = filedialog.askdirectory(title="Выберите папку со спектрами")
        if not folder:
            return

        import os, glob

        csv_files = glob.glob(os.path.join(folder, "*.csv"))
        raw_files = glob.glob(os.path.join(folder, "*.raw"))
        all_files = csv_files + raw_files
        if not all_files:
            messagebox.showwarning(
                "Нет файлов", f"В папке нет .csv или .raw файлов: {folder}"
            )
            return

        found = {"src": None, "dmet": None, "dacet": None}
        for f in all_files:
            name = os.path.basename(f).lower()
            for key, patterns in self._SPECTRUM_PATTERNS.items():
                if found[key] is None and any(p in name for p in patterns):
                    found[key] = f
                    break

        missing = [k for k, v in found.items() if v is None]
        if missing:
            # пробуем по порядку: первый — src, второй — dmet, третий — dacet
            all_files.sort()
            for key in missing:
                for f in all_files:
                    if f not in found.values():
                        found[key] = f
                        break

        self.src_var.set(found["src"] or "")
        self.dmet_var.set(found["dmet"] or "")
        self.dacet_var.set(found["dacet"] or "")
        if hasattr(self, "_folder_path_var"):
            self._folder_path_var.set(folder)

        found_count = sum(1 for v in found.values() if v)
        self._log(
            f"[INFO] Папка: {folder} → найдено {found_count}/3 спектров", color=OK
        )
        if found_count < 3:
            messagebox.showwarning(
                "Не все спектры",
                f"Автоматически найдено {found_count} из 3 спектров. Проверьте оставшиеся поля вручную.",
            )

    def _export_csv(self):
        if self.result_df is None:
            messagebox.showinfo("Нет данных", "Сначала запустите анализ.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("All", "*.*")]
        )
        if path:
            try:
                self.result_df.to_csv(path, index=False, sep=";", encoding="utf-8-sig")
                self._log(f"Таблица сохранена: {path}", color=OK)
            except Exception as e:
                self._log(f"[ОШИБКА] Сохранение не удалось: {e}", color=WARN)
                messagebox.showerror("Ошибка", str(e))

    # ── Van Krevelen ──────────────────────────────────────────────────────────
