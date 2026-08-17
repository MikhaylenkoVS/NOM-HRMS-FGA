"""LogMixin — extracted from app.py."""

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


class LogMixin:
    """Extracted from app.py."""

    def _poll_log_queue(self):
        """Вызывается из главного потока каждые 50 мс."""
        try:
            while True:
                kind, data = self._log_queue.get_nowait()
                if kind == "log":
                    self._append_log_raw(data)
                elif kind == "success":
                    self._on_run_success_data(data)
                elif kind == "error":
                    self._on_run_error_data(data)
                elif kind == "progress":
                    stage, pct = data
                    self.progress["value"] = pct
                    if stage:
                        self._set_status(stage)
                elif kind == "batch_done":
                    self._on_batch_done(data)
        except queue.Empty:
            pass
        finally:
            self._poll_id = self.after(50, self._poll_log_queue)

    def _on_close(self):
        """Корректное завершение: остановка poll, закрытие matplotlib, выход."""
        try:
            self.after_cancel(self._poll_id)
        except Exception:
            pass
        try:
            import sys as _sys

            _sys.stdout = _sys.__stdout__
            _sys.stderr = _sys.__stderr__
        except Exception:
            pass
        try:
            import matplotlib.pyplot as _plt

            _plt.close("all")
        except Exception:
            pass
        self.destroy()
        import os as _os

        _os._exit(0)

    # ── методы лога ───────────────────────────────────────────────────────────

    def _append_log_raw(self, text: str):
        """Вставка сырого текста без тега (безопасна из любого контекста)."""
        if not hasattr(self, "log_text") or self.log_text is None:
            return
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _log(self, msg: str, color: str = FG):
        """Вставка строки с цветовым тегом. Только из главного потока."""
        if not hasattr(self, "log_text") or self.log_text is None:
            return
        tag = "ok" if color == OK else ("warn" if color == WARN else "info")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        if not hasattr(self, "log_text"):
            return
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _save_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text", "*.txt"), ("All", "*.*")]
        )
        if path:
            content = self.log_text.get("1.0", "end")
            try:
                Path(path).write_text(content, encoding="utf-8")
                self._log(f"Лог сохранён: {path}", color=OK)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    # ── статус ────────────────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        if hasattr(self, "status_var"):
            self.status_var.set(msg)
        self.update_idletasks()

    def _clear_frame(self, parent):
        for child in parent.winfo_children():
            child.destroy()

    # ── коллбеки воркера (всегда в главном потоке) ───────────────────────────
