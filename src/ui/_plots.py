"""PlotsMixin — extracted from app.py."""

import ast
import threading, queue, os, sys, traceback, io
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from src.core._safety import _safe_df
from src.ui._deps import create_van_krevelen_plot, DELTA_CD3, DELTA_CD3CO
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


class PlotsMixin:
    """Extracted from app.py."""

    def _plot_van_krevelen(self):
        if self.result_df is None or self.result_df.empty:
            messagebox.showinfo(
                "Нет данных",
                "Сначала запустите анализ, чтобы получить таблицу результатов.",
            )
            return
        if create_van_krevelen_plot is None:
            messagebox.showerror(
                "Ошибка", "Модуль Van Krevelen не загружен (core import failed)."
            )
            return

        self._log("[DEBUG] _plot_van_krevelen: построение диаграммы...", color="info")
        self._clear_frame(self.vk_canvas_frame)
        try:
            # Закрываем предыдущую фигуру, если она есть
            if self._vk_figure is not None:
                plt.close(self._vk_figure)

            fig = create_van_krevelen_plot(
                self.result_df, color_by=self.vk_color_var.get()
            )
            self._vk_figure = fig
            embed_figure(fig, self.vk_canvas_frame)
            self._log("[DEBUG] _plot_van_krevelen: диаграмма построена", color=OK)
        except Exception:
            self._log(
                f"[ОШИБКА] _plot_van_krevelen:\n{traceback.format_exc()}",
                color=WARN,
            )
            plt.close("all")
            messagebox.showerror(
                "Ошибка", "Не удалось построить диаграмму Ван Кревелена."
            )

    def _save_van_krevelen_png(self):
        if self._vk_figure is None:
            messagebox.showinfo(
                "Нет диаграммы",
                "Сначала постройте диаграмму, нажав «Построить диаграмму Ван Кревелена».",
            )
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            self._vk_figure.savefig(path, dpi=300)
            self._log(f"Van Krevelen диаграмма сохранена: {path}", color=OK)
        except Exception as e:
            self._log(f"[ОШИБКА] Сохранение Van Krevelen PNG: {e}", color=WARN)
            messagebox.showerror("Ошибка", str(e))

    # ── Графики спектров ──────────────────────────────────────────────────────

    def _plot_spectra(self):
        paths = [self.src_var.get(), self.dmet_var.get(), self.dacet_var.get()]
        if not all(paths):
            messagebox.showwarning("Нет файлов", "Укажите все три файла.")
            return
        for p in paths:
            if not os.path.exists(p):
                messagebox.showerror("Файл не найден", p)
                return

        sep = self.sep_var.get()
        if sep in ("\\t", "tab", "TAB"):
            sep = "\t"

        self._log("[DEBUG] _plot_spectra: загрузка...", color="info")
        try:
            dfs = {}
            for key, path in zip(
                ["Исходный", "Дейтерометилирование", "Дейтероацилирование"], paths
            ):
                df = pd.read_csv(path, sep=sep)
                df.columns = [c.strip() for c in df.columns]
                # Единый маппинг из spectrum_ops
                from src.core.spectrum import CSV_COLUMN_MAPPER

                df = df.rename(columns=CSV_COLUMN_MAPPER)
                if "mass" not in df.columns or "intensity" not in df.columns:
                    raise ValueError(
                        f"{key}: колонки mass/intensity не найдены. "
                        f"Доступны: {list(df.columns)}"
                    )
                dfs[key] = df
                self._log(f"[DEBUG]   {key}: {len(df)} строк", color="info")
        except Exception as e:
            self._log(f"[ОШИБКА] _plot_spectra: {traceback.format_exc()}", color=WARN)
            messagebox.showerror("Ошибка чтения", str(e))
            return

        self._clear_frame(self.spectra_canvas_frame)
        try:
            fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
            colors = [ACCENT, "#a6e3a1", "#fab387"]
            for ax, (title, df), color in zip(axes, dfs.items(), colors):
                ax.vlines(
                    df["mass"],
                    0,
                    df["intensity"],
                    colors=color,
                    linewidth=0.8,
                    alpha=0.8,
                )
                ax.set_ylabel("Intensity", fontsize=8)
                ax.set_title(title, fontsize=9, loc="left", color=FG)
                ax.grid(True, alpha=0.3)
            axes[-1].set_xlabel("m/z", fontsize=9)
            fig.suptitle("Три масс-спектра", color=ACCENT, fontsize=11)
            fig.tight_layout()
            embed_figure(fig, self.spectra_canvas_frame)
            self._log("[DEBUG] _plot_spectra: успешно", color=OK)
        except Exception:
            self._log(f"[ОШИБКА] _plot_spectра: {traceback.format_exc()}", color=WARN)
            plt.close("all")

    # ── Графики серий ─────────────────────────────────────────────────────────

    def _plot_series(self, which: str):
        if self.result_df is None:
            messagebox.showinfo("Нет данных", "Сначала запустите анализ.")
            return

        # build_result_table возвращает N_OH (не N_OH_total) — исправлено
        col_n = "N_COOH" if which == "dmet" else "N_OH"
        col_m = "missing_dmet" if which == "dmet" else "missing_dacet"
        delta = DELTA_CD3 if which == "dmet" else DELTA_CD3CO
        label = "CD₃ (dmet)" if which == "dmet" else "CD₃CO (dacet)"

        self._log(f"[DEBUG] _plot_series({which}): col_n={col_n}", color="info")

        if col_n not in self.result_df.columns:
            self._log(
                f"[WARN] '{col_n}' нет в result_df. "
                f"Есть: {list(self.result_df.columns)}",
                color=WARN,
            )
            messagebox.showwarning("Нет данных", f"Колонка '{col_n}' отсутствует.")
            return

        df = _safe_df(self.result_df)[self.result_df[col_n] > 0].copy()
        self._log(f"[DEBUG] Соединений с {col_n}>0: {len(df)}", color="info")
        if df.empty:
            self._log(f"Серии {label}: нет соединений с n>0.", color=WARN)
            return

        n_plots = min(len(df), 9)
        ncols = 3
        nrows = (n_plots + ncols - 1) // ncols

        self._clear_frame(self.series_canvas_frame)
        try:
            fig, axes = plt.subplots(nrows, ncols, figsize=(9, nrows * 2.8))
            if nrows * ncols == 1:
                axes_flat = [axes]
            elif nrows == 1:
                axes_flat = list(axes)
            else:
                axes_flat = list(axes.flatten())

            last_i = -1
            for last_i, (_, row) in enumerate(df.head(n_plots).iterrows()):
                ax = axes_flat[last_i]
                m0 = row["mass"]
                n = int(row[col_n])
                steps = list(range(1, n + 1))

                missing = row.get(col_m, [])
                if isinstance(missing, str):
                    try:
                        missing = ast.literal_eval(missing)
                    except Exception:
                        missing = []
                if not isinstance(missing, list):
                    missing = []

                colors_bars = [WARN if s in missing else OK for s in steps]
                ax.bar(steps, [1] * len(steps), color=colors_bars, alpha=0.8, width=0.6)
                ax.set_xticks(steps)
                ax.set_xticklabels([str(s) for s in steps], fontsize=7)
                ax.set_yticks([])
                ax.set_title(
                    f"m/z={m0:.3f}\n{row.get('brutto','')}, n={n}", fontsize=7, color=FG
                )
                if missing:
                    ax.set_xlabel(f"⚠ пропуски: {missing}", fontsize=6, color=WARN)

            for j in range(last_i + 1, len(axes_flat)):
                axes_flat[j].set_visible(False)

            fig.suptitle(
                f"Серии {label}  (зелёный=найден, красный=пропущен)",
                color=ACCENT,
                fontsize=10,
            )
            fig.tight_layout()
            embed_figure(fig, self.series_canvas_frame)
            self._log(f"[DEBUG] _plot_series: {n_plots} графиков построено", color=OK)
        except Exception:
            self._log(f"[ОШИБКА] _plot_series: {traceback.format_exc()}", color=WARN)
            plt.close("all")

    # ── Гистограммы ───────────────────────────────────────────────────────────

    def _auto_plot_hist(self):
        if self.result_df is None:
            return
        self._plot_histograms()

    def _plot_hist(self, col: str):
        if self.result_df is None:
            messagebox.showinfo("Нет данных", "Сначала запустите анализ.")
            return
        if col not in self.result_df.columns:
            self._log(
                f"[WARN] _plot_hist: нет '{col}'. "
                f"Есть: {list(self.result_df.columns)}",
                color=WARN,
            )
            messagebox.showwarning("Нет данных", f"Колонка '{col}' отсутствует.")
            return
        self._clear_frame(self.series_canvas_frame)
        try:
            fig, ax = plt.subplots(figsize=(7, 4))
            vals = _safe_df(self.result_df)[col].dropna().astype(int)
            if vals.empty:
                ax.text(
                    0.5,
                    0.5,
                    "Нет данных",
                    transform=ax.transAxes,
                    ha="center",
                    color=FG,
                )
            else:
                ax.hist(
                    vals,
                    bins=range(vals.max() + 2),
                    color=ACCENT,
                    alpha=0.85,
                    edgecolor=BG,
                    rwidth=0.7,
                )
            ax.set_xlabel(col)
            ax.set_ylabel("Количество соединений")
            ax.set_title(f"Распределение {col}")
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            embed_figure(fig, self.series_canvas_frame)
        except Exception:
            self._log(
                f"[ОШИБКА] _plot_hist({col}): {traceback.format_exc()}", color=WARN
            )
            plt.close("all")

    def _plot_histograms(self):
        if self.result_df is None or self.result_df.empty:
            messagebox.showinfo("Нет данных", "Сначала запустите анализ.")
            return
        try:
            from src.core.statistics import create_histograms_plot
        except Exception as e:
            messagebox.showerror("Ошибка", f"Модуль статистики не загружен: {e}")
            return
        self._clear_frame(self.histograms_canvas_frame)
        try:
            self._histograms_figure = create_histograms_plot(self.result_df)
            embed_figure(
                self._histograms_figure, self.histograms_canvas_frame, toolbar=False
            )
            self._log("[DEBUG] _plot_histograms: построено", color=OK)
        except Exception:
            self._log(
                f"[ОШИБКА] _plot_histograms:\n{traceback.format_exc()}", color=WARN
            )
            plt.close("all")
            messagebox.showerror("Ошибка", "Не удалось построить гистограммы.")

    def _save_histograms(self):
        fig = getattr(self, "_histograms_figure", None)
        if fig is None:
            messagebox.showinfo("Нет гистограмм", "Сначала постройте гистограммы.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("SVG image", "*.svg"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            fig.savefig(path, dpi=300)
            self._log(f"Гистограммы сохранены: {path}", color=OK)
        except Exception as e:
            self._log(f"[ОШИБКА] Сохранение гистограмм: {e}", color=WARN)
            messagebox.showerror("Ошибка", str(e))


# ═══════════════════════════════════════════════════════════════════════════════
#  ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════════════════════
