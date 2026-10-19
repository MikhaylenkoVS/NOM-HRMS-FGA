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
    run_pipeline_segmented,
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

    def _finish_run(self):
        """Снять блокировку кнопки запуска (после успеха или ошибки)."""
        self._run_in_progress = False
        if getattr(self, "_run_button", None) is not None:
            self._run_button.configure(state="normal")

    def _on_run_success_data(self, payload: dict):
        self.progress["value"] = 100
        result_df = payload.get("result")
        self.result_df = result_df
        stats = payload.get("stats")
        self._last_stats = stats
        n = len(result_df) if result_df is not None else 0
        stage_errors = list(getattr(stats, "errors", []) or [])
        if stage_errors:
            # Этапы конвейера могли упасть, а результат — частичный.
            self._set_status(
                f"Завершено с ошибками ({len(stage_errors)} этап(ов)). " f"Строк: {n}."
            )
            self._log(
                f"⚠️ Анализ завершён с ошибками этапов ({len(stage_errors)}):",
                color=WARN,
            )
            for msg in stage_errors[:10]:
                self._log(f"   • {str(msg).splitlines()[0][:300]}", color=WARN)
        else:
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
        self._finish_run()

    def _on_run_error_data(self, payload: dict):
        self.progress["value"] = 100
        self._finish_run()
        tb = payload["traceback"]
        self._set_status("Ошибка! Смотри лог.")
        self._log("[ОШИБКА ВЫПОЛНЕНИЯ]\n" + tb, color=WARN)
        messagebox.showerror("Ошибка выполнения", tb[:1200])

    def _on_paths_resolved(self, payload):
        """Обновляет поля путей после RAW/mzML-конвертации (главный поток)."""
        try:
            src, dmet, dacet = payload
        except Exception:
            return
        self.src_var.set(src)
        self.dmet_var.set(dmet)
        self.dacet_var.set(dacet)

    def _on_run_error_message(self, payload: dict):
        self._finish_run()
        """Показывает понятную ошибку подготовки входных файлов (главный поток)."""
        message = payload.get("message", "Неизвестная ошибка")
        self.progress["value"] = 100
        self._set_status("Ошибка! Смотри лог.")
        self._log(f"[ОШИБКА] {message}", color=WARN)
        messagebox.showerror("Ошибка", message)

    # ── ПОСТРОЕНИЕ ИНТЕРФЕЙСА ─────────────────────────────────────────────────

    def _resolve_path(self, path: str, rt_min_s: str, rt_max_s: str, label: str):
        """Return the actual CSV path, auto-detecting RAW/mzML→JSON if needed.

        Thread-safe: runs in the worker thread and communicates with the GUI
        exclusively through ``self._log_queue`` (never touches tkinter).
        """
        path = path.strip()
        if not path:
            raise ValueError(f"[{label}] Укажите файл (.csv, .mzML или .raw)")

        if not os.path.isfile(path):
            raise FileNotFoundError(f"[{label}] Файл не найден: {path}")

        # Автоопределение: если .raw → усреднить
        if path.lower().endswith(".raw"):
            try:
                rt_min = float(rt_min_s) if rt_min_s.strip() else 0.0
                rt_max = float(rt_max_s) if rt_max_s.strip() else 999.0
            except ValueError:
                raise ValueError(f"[{label}] Некорректный RT-диапазон")

            if not _RAW_LOADED:
                raise RuntimeError(
                    f"[{label}] Обработка RAW недоступна: {_RAW_ERROR}\n"
                    "Установите pythonnet и RawFileReader DLL в thermo/"
                )
            self._log_queue.put(
                (
                    "log",
                    f"[RAW] Усреднение {path} (RT {rt_min:.1f}–{rt_max:.1f} мин)…\n",
                )
            )
            self._log_queue.put(("progress", ("Усреднение RAW-спектра…", 0)))
            path = average_raw_to_json(path, rt_min, rt_max)
            self._log_queue.put(("progress", ("Готово", 100)))
            self._log_queue.put(("log", f"[RAW] → {path}\n"))

        # Автоопределение: если .mzML → конвертировать через mzml_bridge
        elif path.lower().endswith(".mzml"):
            try:
                rt_min = float(rt_min_s) if rt_min_s.strip() else 0.0
                rt_max = float(rt_max_s) if rt_max_s.strip() else 999.0
            except ValueError:
                raise ValueError(f"[{label}] Некорректный RT-диапазон")

            if _mzml_to_json is None:
                raise RuntimeError(
                    f"[{label}] Обработка mzML недоступна.\n"
                    "Установите pymzml: pip install pymzml"
                )
            self._log_queue.put(
                (
                    "log",
                    f"[mzML] Усреднение {path} (RT {rt_min:.1f}–{rt_max:.1f} мин)…\n",
                )
            )
            self._log_queue.put(("progress", ("Усреднение mzML-спектра…", 0)))
            path = _mzml_to_json(path, rt_min=rt_min, rt_max=rt_max)
            self._log_queue.put(("progress", ("Готово", 100)))
            self._log_queue.put(("log", f"[mzML] → {path}\n"))

        return path

    def _run(self):
        if getattr(self, "_run_in_progress", False):
            messagebox.showwarning(
                "Анализ уже выполняется",
                "Дождитесь завершения текущего прогона или остановите его.",
            )
            return
        if not CORE_LOADED:
            messagebox.showerror(
                "Ошибка", f"src.core не загружен:\n{_CORE_ERROR[:800]}"
            )
            return

        seg_opts = None
        if self.segment_mode_var.get():
            # Сегментный режим: усреднение по RT-отрезкам выполняет
            # run_pipeline_segmented (в фоновом потоке). Пути не разрешаем
            # заранее — функция сама обрабатывает RAW/mzML/CSV.
            try:
                seg_width = float(self.segment_width_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Ширина отрезка: ожидается число")
                return
            if seg_width <= 0:
                messagebox.showerror("Ошибка", "Ширина отрезка должна быть > 0")
                return
            rt_min = self._rt_float(self.src_rt_min, 0.0)
            rt_max = self._rt_float(self.src_rt_max, 20.0)
            seg_opts = {"segment_width": seg_width, "rt_min": rt_min, "rt_max": rt_max}

        # Быстрая валидация в главном потоке: только чтение StringVar,
        # без файловых операций и конвертации.
        inputs = []
        for label, spec_var, rt_min_var, rt_max_var in [
            ("Исходный", self.src_var, self.src_rt_min, self.src_rt_max),
            ("Дейтерометилирование", self.dmet_var, self.dmet_rt_min, self.dmet_rt_max),
            (
                "Дейтероацилирование",
                self.dacet_var,
                self.dacet_rt_min,
                self.dacet_rt_max,
            ),
        ]:
            path = spec_var.get().strip()
            if not path:
                messagebox.showerror(
                    "Ошибка", f"[{label}] Укажите файл (.csv, .mzML или .raw)"
                )
                return
            inputs.append((label, path, rt_min_var.get(), rt_max_var.get()))

        params = self._parse_params()
        if params is None:
            return
        self._last_params = params

        # Предупреждение о числе галогенных комбинаций выводится ДО старта
        # анализа: при полном переборе это заметно дольше.
        plan = getattr(self, "_halogen_plan_from_ui", lambda: None)()
        # Показ предупреждения управляется флагом halogen_search.show_warning
        # (сейчас выключен: замедление оказалось незначительным). Механика
        # сохранена — включить можно конфигом, без правки кода.
        if plan and plan.get("warn") and plan.get("warn_enabled"):
            messagebox.showwarning(
                "Проверка комбинаций галогенов",
                self._halogen_warning_text(plan),
            )

        self._run_in_progress = True
        if getattr(self, "_run_button", None) is not None:
            self._run_button.configure(state="disabled")
        self._clear_log()
        self._structure_cache.clear()  # сброс кэша структур
        self._structure_preloading = False
        self._log("[DEBUG] ═══ Запуск анализа ═══", color="info")
        if seg_opts:
            self._log(f"[DEBUG]   сегментный режим: {seg_opts}", color="info")
        self._log(f"[DEBUG]   params = {params}", color="info")

        self.progress["value"] = 0
        self._set_status("Выполняется анализ…")

        # RAW/mzML-конвертация и пайплайн выполняются в фоновом потоке.
        t = threading.Thread(
            target=self._run_worker,
            args=(inputs, params, seg_opts),
            daemon=True,
        )
        t.start()

    def _run_worker(self, inputs: list, params: dict, seg_opts=None):
        """
        Выполняется в фоновом потоке: разрешает пути (RAW/mzML → JSON) и
        запускает пайплайн.  Все print() из pipeline попадают в GUI-лог через
        _QueueWriter; tkinter из этого потока не вызывается.
        """
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        sys.stdout = _QueueWriter(self._log_queue, orig_stdout)
        sys.stderr = _QueueWriter(self._log_queue, orig_stderr)

        def _on_progress(stage_name, pct):
            """Передаёт этап и процент в GUI-очередь."""
            self._log_queue.put(("progress", (stage_name, pct)))

        try:
            if seg_opts:
                # Сегментный режим: RAW/mzML/CSV обрабатывает сама функция.
                spec_paths = [path for _, path, _, _ in inputs]
            else:
                spec_paths = []
                for label, path, rt_min_s, rt_max_s in inputs:
                    resolved = self._resolve_path(path, rt_min_s, rt_max_s, label)
                    spec_paths.append(resolved)
        except Exception as e:
            # Ошибка подготовки входных файлов (путь/RAW/mzML) — показываем
            # пользователю понятное сообщение без длинного traceback.
            self._log_queue.put(("log", f"[ОШИБКА] Подготовка входных файлов: {e}\n"))
            self._log_queue.put(("run_error", {"message": str(e)}))
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr
            return

        try:
            if not seg_opts:
                self._log_queue.put(("paths_resolved", tuple(spec_paths)))
            self._log_queue.put(("log", f"[DEBUG]   src   = {spec_paths[0]}\n"))
            self._log_queue.put(("log", f"[DEBUG]   dmet  = {spec_paths[1]}\n"))
            self._log_queue.put(("log", f"[DEBUG]   dacet = {spec_paths[2]}\n"))

            self._log_queue.put(("log", "[DEBUG] _run_worker: старт пайплайна\n"))
            if seg_opts:
                seg_params = {
                    k: v
                    for k, v in params.items()
                    if k not in ("output_csv", "visualize")
                }
                res = run_pipeline_segmented(
                    src_path=spec_paths[0],
                    dmet_path=spec_paths[1],
                    dacet_path=spec_paths[2],
                    progress_callback=_on_progress,
                    **seg_opts,
                    **seg_params,
                )
            else:
                res = run_pipeline(
                    src_path=spec_paths[0],
                    dmet_path=spec_paths[1],
                    dacet_path=spec_paths[2],
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
