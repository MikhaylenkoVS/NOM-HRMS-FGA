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
from src.ui._deps import (
    run_pipeline,
    CORE_LOADED,
    _CORE_ERROR,
    average_raw_to_json,
    _RAW_LOADED,
    _RAW_ERROR,
    _mzml_to_json,
)
from src.ui._log import _QueueWriter


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
            path = average_raw_to_json(path, rt_min, rt_max)
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

            if _mzml_to_json is None:
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
            path = _mzml_to_json(path, rt_min=rt_min, rt_max=rt_max)
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

    # ── Batch-обработка ────────────────────────────────────────────────────────

    def _select_batch_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку с наборами образцов")
        if not folder:
            return
        from src.core.batch import detect_sample_triples

        self._batch_folder = folder
        self._batch_triples = detect_sample_triples(folder)
        n = len(self._batch_triples)
        if not n:
            messagebox.showwarning(
                "Нет троек",
                "В папке не найдено троек файлов (исходный / CD₃ / CD₃CO).",
            )
            return
        self._log(f"[INFO] Batch: {folder} → {n} наборов", color=OK)
        messagebox.showinfo(
            "Batch", f"Найдено наборов: {n}.\nНажмите «Запустить batch»."
        )

    def _run_batch(self):
        triples = getattr(self, "_batch_triples", None)
        if not triples:
            messagebox.showinfo("Batch", "Сначала выберите папку с наборами.")
            return
        params = self._parse_params()
        if params is None:
            return
        rt_min = self._rt_float(self.src_rt_min, 0.0)
        rt_max = self._rt_float(self.src_rt_max, 999.0)
        self._clear_log()
        self.progress["value"] = 0
        self._set_status(f"Batch: {len(triples)} наборов…")
        threading.Thread(
            target=self._batch_worker,
            args=(triples, params, rt_min, rt_max),
            daemon=True,
        ).start()

    def _rt_float(self, var, default):
        try:
            val = var.get().strip()
            return float(val) if val else default
        except (ValueError, tk.TclError):
            return default

    def _batch_worker(self, triples, params, rt_min, rt_max):
        from src.core import run_pipeline, build_batch_summary, compute_sample_summary
        from src.core.io.raw_bridge import average_raw_to_json
        from src.core.io.mzml_bridge import mzml_to_json

        orig_stdout, orig_stderr = sys.stdout, sys.stderr
        sys.stdout = _QueueWriter(self._log_queue, orig_stdout)
        sys.stderr = _QueueWriter(self._log_queue, orig_stderr)

        def _progress(stage, pct):
            self._log_queue.put(("progress", (stage, pct)))

        rows = []
        total = len(triples)
        try:
            for i, tp in enumerate(triples, 1):
                sample = tp["sample"]
                self._log_queue.put(
                    ("log", f"\n═══ [Batch {i}/{total}] {sample} ═══\n")
                )
                paths, ok = [], True
                for role in ("src", "dmet", "dacet"):
                    p = tp.get(role, "")
                    if not p:
                        self._log_queue.put(
                            ("log", f"  [WARN] {role}: файл не найден\n")
                        )
                        ok = False
                        break
                    try:
                        paths.append(
                            _resolve_batch_path(
                                p, rt_min, rt_max, average_raw_to_json, mzml_to_json
                            )
                        )
                    except Exception as e:
                        self._log_queue.put(("log", f"  [ОШИБКА] {role}: {e}\n"))
                        ok = False
                        break
                if not ok:
                    rows.append(compute_sample_summary(None, sample))
                    continue
                try:
                    res = run_pipeline(
                        src_path=paths[0],
                        dmet_path=paths[1],
                        dacet_path=paths[2],
                        progress_callback=_progress,
                        **params,
                    )
                    rows.append(
                        compute_sample_summary(
                            getattr(res, "table", None),
                            sample,
                            getattr(res, "stats", None),
                        )
                    )
                except Exception as e:
                    self._log_queue.put(("log", f"  [ОШИБКА] pipeline: {e}\n"))
                    rows.append(compute_sample_summary(None, sample))
                self._log_queue.put(("progress", ("", int(100 * i / total))))
            self._log_queue.put(("batch_done", {"summary": build_batch_summary(rows)}))
        except Exception:
            self._log_queue.put(
                ("log", f"[ОШИБКА] _batch_worker:\n{traceback.format_exc()}\n")
            )
        finally:
            sys.stdout, sys.stderr = orig_stdout, orig_stderr

    def _on_batch_done(self, payload):
        summary = payload["summary"]
        self.batch_summary_df = summary
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)
        for _, r in summary.iterrows():
            self.batch_tree.insert(
                "",
                "end",
                values=(
                    r.get("sample", ""),
                    r.get("n_compounds", 0),
                    r.get("N_COOH_total", 0),
                    r.get("N_OH_total", 0),
                    r.get("avg_mass", ""),
                ),
            )
        self.progress["value"] = 100
        self._set_status("Batch завершён.")
        self._log("✅ Batch-обработка завершена.", color=OK)

    def _export_batch_summary(self):
        summary = getattr(self, "batch_summary_df", None)
        if summary is None or summary.empty:
            messagebox.showinfo("Нет сводки", "Сначала запустите batch.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx"),
                ("JSON", "*.json"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            from src.core.pipeline._export import export_result_table

            export_result_table(summary, path)
            self._log(f"Сводка сохранена: {path}", color=OK)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ── Таблица результатов ───────────────────────────────────────────────────


def _resolve_batch_path(path, rt_min, rt_max, average_raw_to_json, mzml_to_json):
    """Resolve a batch input path: RAW/mzML → JSON, otherwise unchanged."""
    if path.lower().endswith(".raw"):
        return average_raw_to_json(path, rt_min, rt_max)
    if path.lower().endswith(".mzml"):
        return mzml_to_json(path, rt_min=rt_min, rt_max=rt_max)
    return path
