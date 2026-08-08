"""RunMixin — extracted from app.py."""

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


class RunMixin:
    """Extracted from app.py."""

    def _on_run_success_data(self, payload: dict):
        self.progress["value"] = 100
        result_df = payload.get("result")
        self.result_df = result_df
        n = len(result_df) if result_df is not None else 0
        self._set_status(f"Готово. Найдено {n} соединений.")
        self._log("✅ Анализ завершён успешно.", color=OK)
        if result_df is not None and not result_df.empty:
            self._fill_result_table(result_df)
            self._auto_plot_hist()
            # Автообновление списка соединений во вкладке Структуры
            self._refresh_structures_tab()
            # Предзагрузка структур для всех уникальных формул (фон)
            self._start_structure_preload(result_df)
        else:
            self._log("[WARN] Результирующая таблица пуста.", color=WARN)

    def _on_run_error_data(self, payload: dict):
        self.progress["value"] = 100
        tb = payload["traceback"]
        self._set_status("Ошибка! Смотри лог.")
        self._log("[ОШИБКА ВЫПОЛНЕНИЯ]\n" + tb, color=WARN)
        messagebox.showerror("Ошибка выполнения", tb[:1200])

    # ── ПОСТРОЕНИЕ ИНТЕРФЕЙСА ─────────────────────────────────────────────────

    def _resolve_path(self, spec_var, rt_min_var, rt_max_var, label):
        """Return the actual CSV path, auto-detecting RAW→CSV if needed."""
        path = spec_var.get().strip()
        if not path:
            raise ValueError(f"[{label}] Укажите файл (.csv, .mzML или .raw)")

        if not os.path.isfile(path):
            raise FileNotFoundError(f"[{label}] Файл не найден: {path}")

        # Автоопределение: если .raw → усреднить
        if path.lower().endswith(".raw"):
            try:
                rt_min = float(rt_min_var.get()) if rt_min_var.get().strip() else 0.0
                rt_max = float(rt_max_var.get()) if rt_max_var.get().strip() else 999.0
            except ValueError:
                raise ValueError(f"[{label}] Некорректный RT-диапазон")

            if not _RAW_LOADED:
                raise RuntimeError(
                    f"[{label}] Обработка RAW недоступна: {_RAW_ERROR}\n"
                    "Установите pythonnet и RawFileReader DLL в thermo/"
                )
            self._log(
                f"[RAW] Усреднение {path} (RT {rt_min:.1f}–{rt_max:.1f} мин)…",
                color=FG,
            )
            self._set_status("Усреднение RAW-спектра…")
            self.progress["value"] = 0
            self.update_idletasks()
            path = average_raw_to_csv(path, rt_min, rt_max)
            self.progress["value"] = 100
            self._set_status("Готово")
            self._log(f"[RAW] → {path}", color=OK)

        # Автоопределение: если .mzML → конвертировать через mzml_bridge
        elif path.lower().endswith(".mzml"):
            try:
                rt_min = float(rt_min_var.get()) if rt_min_var.get().strip() else 0.0
                rt_max = float(rt_max_var.get()) if rt_max_var.get().strip() else 999.0
            except ValueError:
                raise ValueError(f"[{label}] Некорректный RT-диапазон")

            if _mzml_to_csv is None:
                raise RuntimeError(
                    f"[{label}] Обработка mzML недоступна.\n"
                    "Установите pymzml: pip install pymzml"
                )
            self._log(
                f"[mzML] Усреднение {path} (RT {rt_min:.1f}–{rt_max:.1f} мин)…",
                color=FG,
            )
            self._set_status("Усреднение mzML-спектра…")
            self.progress["value"] = 0
            self.update_idletasks()
            path = _mzml_to_csv(path, rt_min=rt_min, rt_max=rt_max)
            self.progress["value"] = 100
            self._set_status("Готово")
            self._log(f"[mzML] → {path}", color=OK)

        return path

    def _run(self):
        if not CORE_LOADED:
            messagebox.showerror(
                "Ошибка", f"src.core не загружен:\n{_CORE_ERROR[:800]}"
            )
            return

        spec_paths = []
        for label, spec_var, rt_min, rt_max in [
            ("Исходный", self.src_var, self.src_rt_min, self.src_rt_max),
            ("Дейтерометилирование", self.dmet_var, self.dmet_rt_min, self.dmet_rt_max),
            (
                "Дейтероацилирование",
                self.dacet_var,
                self.dacet_rt_min,
                self.dacet_rt_max,
            ),
        ]:
            try:
                path = self._resolve_path(spec_var, rt_min, rt_max, label)
                spec_var.set(path)  # записываем результат для лога
                spec_paths.append(path)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                return

        params = self._parse_params()
        if params is None:
            return

        self._clear_log()
        self._structure_cache.clear()  # сброс кэша структур
        self._structure_preloading = False
        self._log("[DEBUG] ═══ Запуск анализа ═══", color="info")
        self._log(f"[DEBUG]   src   = {spec_paths[0]}", color="info")
        self._log(f"[DEBUG]   dmet  = {spec_paths[1]}", color="info")
        self._log(f"[DEBUG]   dacet = {spec_paths[2]}", color="info")
        self._log(f"[DEBUG]   params = {params}", color="info")

        self.progress["value"] = 0
        self._set_status("Выполняется анализ…")

        t = threading.Thread(
            target=self._run_worker,
            args=(spec_paths[0], spec_paths[1], spec_paths[2], params),
            daemon=True,
        )
        t.start()

    def _run_worker(self, src_path: str, dmet_path: str, dacet_path: str, params: dict):
        """
        Выполняется в фоновом потоке.
        Все print() из pipeline автоматически попадают в GUI-лог через _QueueWriter.
        """
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        sys.stdout = _QueueWriter(self._log_queue, orig_stdout)
        sys.stderr = _QueueWriter(self._log_queue, orig_stderr)

        def _on_progress(stage_name, pct):
            """Передаёт этап и процент в GUI-очередь."""
            self._log_queue.put(("progress", (stage_name, pct)))

        try:
            self._log_queue.put(("log", "[DEBUG] _run_worker: старт пайплайна\n"))
            res = run_pipeline(
                src_path=src_path,
                dmet_path=dmet_path,
                dacet_path=dacet_path,
                progress_callback=_on_progress,
                **params,
            )

            # res — PipelineRunResult
            table = getattr(res, "table", None)
            n = len(table) if table is not None else "None"
            self._log_queue.put(
                ("log", f"[DEBUG] _run_worker: pipeline завершён, строк={n}\n")
            )
            self._log_queue.put(
                ("success", {"result": table, "stats": getattr(res, "stats", None)})
            )
        except Exception:
            tb = traceback.format_exc()
            self._log_queue.put(("log", f"[DEBUG] _run_worker: EXCEPTION\n{tb}\n"))
            self._log_queue.put(("error", {"traceback": tb}))
        finally:
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr

    # ── Таблица результатов ───────────────────────────────────────────────────
