"""StructuresMixin — extracted from app.py."""

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


class StructuresMixin:
    """Extracted from app.py."""

    # Автоматический прогрев кэша структур ОТКЛЮЧЁН.
    #
    # Причина: find_fragment_combinations() для тяжёлых формул комбинаторно
    # взрывается — замерено ~140 млн обращений к dict.get и ~49 млн min() на
    # несколько формул, т.е. десятки секунд чистого Python на одну формулу.
    # Такой фоновый поток держит GIL, и главный поток, который перерисовывает
    # вкладки («Спектры», «Van Krevelen», «Серии», «Гистограммы»), замедляется
    # в десятки раз: замерено 73.8 с против 0.21 с при выключенном прогреве.
    #
    # Структуры и так генерируются по запросу: клик по строке таблицы
    # результатов (_load_structure_preview) или выбор пика во вкладке
    # «Структуры» — в отдельном потоке, со статусом «Поиск структуры…».
    # Чтобы вернуть прогрев, достаточно поставить PRELOAD_ENABLED = True.
    PRELOAD_ENABLED = False
    MAX_PRELOAD_FORMULAS = 100

    def _start_structure_preload(self, df: pd.DataFrame):
        """Прогрев кэша структур. По умолчанию выключен (см. PRELOAD_ENABLED)."""
        if not self.PRELOAD_ENABLED:
            return
        if self._structure_preloading:
            return  # уже идёт
        formulas = list(
            dict.fromkeys(
                str(r.get("brutto", "")) for _, r in df.iterrows() if r.get("brutto")
            )
        )
        if not formulas:
            return
        total = len(formulas)
        if total > self.MAX_PRELOAD_FORMULAS:
            formulas = formulas[: self.MAX_PRELOAD_FORMULAS]
        self._structure_preloading = True
        if total > len(formulas):
            self._log(
                f"🔍 Предзагрузка структур: {len(formulas)} из {total} формул "
                f"(остальные — по клику на строку результатов)…",
                color="info",
            )
        else:
            self._log(f"🔍 Предзагрузка структур для {total} формул…", color="info")
        t = threading.Thread(
            target=self._preload_structures_worker,
            args=(formulas,),
            daemon=True,
        )
        t.start()

    def _preload_structures_worker(self, formulas: list[str]):
        """Фоновый поток: генерация структур для списка формул.

        tkinter из этого потока не трогаем — только ``_log_queue``.
        """
        try:
            from src.core import find_and_visualize_molecules
        except Exception:
            self._structure_preloading = False
            return

        done = 0
        for brutto in formulas:
            if brutto in self._structure_cache:
                done += 1
                continue
            try:
                result = find_and_visualize_molecules(
                    brutto,
                    num_cooh=0,
                    num_oh=0,
                    max_bases=8,
                    show_images=False,
                    first_only=True,
                )
                self._structure_cache[brutto] = result.get("molecules", [])
            except Exception:
                self._structure_cache[brutto] = []
            done += 1

        self._structure_preloading = False
        self._log_queue.put(
            ("log", f"✅ Предзагрузка структур завершена ({done}/{len(formulas)}).\n")
        )

    # ── Выбор строки таблицы → структура ──────────────────────────────────────

    def _load_structure_preview(self, brutto: str, n_cooh: int, n_oh: int):
        """Фоновый поток: поиск структуры (first_only). Кэширует результат."""
        try:
            from src.core import find_and_visualize_molecules

            result = find_and_visualize_molecules(
                brutto,
                num_cooh=n_cooh,
                num_oh=n_oh,
                max_bases=8,
                show_images=False,
                first_only=True,
            )
            molecules = result.get("molecules", [])
            self._structure_cache[brutto] = molecules  # сохраняем в кэш
            self.after(0, lambda: self._show_structure_preview(molecules, brutto))
        except Exception:
            self.after(
                0,
                lambda: (
                    self.progress.configure(value=100),
                    self._structure_preview_label.configure(
                        text=f"Не удалось найти\nструктуру для {brutto}"
                    ),
                ),
            )

    def _show_structure_preview(self, molecules: list, brutto: str):
        """Отображение первой найденной структуры в панели превью."""
        self.progress["value"] = 100
        if not molecules:
            self._structure_preview_label.configure(
                text=f"Структуры не найдены\n{brutto}"
            )
            return

        try:
            from src.structures.rdkit_utils import fragment_to_rdkit, RDKIT_OK
            from io import BytesIO
            from PIL import Image, ImageTk

            mol_info = molecules[0]
            frag = mol_info.get("fragment_object")
            rdmol = fragment_to_rdkit(frag) if frag is not None else None

            if rdmol is not None:
                from rdkit import Chem
                from rdkit.Chem import Draw, AllChem, rdDepictor

                # 2D-координаты (CoordGen — зигзаги sp3)
                rdDepictor.SetPreferCoordGen(True)
                AllChem.Compute2DCoords(rdmol)
                rdmol = Chem.AddHs(rdmol, explicitOnly=True)
                final_mol = Chem.RWMol(rdmol)
                atoms_to_remove = []
                for atom in final_mol.GetAtoms():
                    if atom.GetAtomicNum() == 1:
                        for nbr in atom.GetNeighbors():
                            if nbr.GetAtomicNum() == 6:
                                atoms_to_remove.append(atom.GetIdx())
                                break
                for idx in reversed(sorted(atoms_to_remove)):
                    final_mol.RemoveAtom(idx)
                rdmol = final_mol.GetMol()
                try:
                    Chem.SanitizeMol(rdmol)
                except Exception:
                    pass
                img = Draw.MolToImage(rdmol, size=(300, 200))
                buf = BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                pil_img = Image.open(buf)
                self._structure_preview_img = ImageTk.PhotoImage(pil_img)
                self._structure_preview_label.configure(
                    image=self._structure_preview_img, text=""
                )
            else:
                name = mol_info.get("name", brutto)
                self._structure_preview_label.configure(
                    text=f"{name}\n(нет RDKit-изображения)", image=""
                )
        except Exception:
            self._structure_preview_label.configure(
                text=f"Ошибка отрисовки\n{brutto}", image=""
            )

    def _refresh_structures_tab(self):
        """Обновить выпадающий список во вкладке Структуры."""
        if hasattr(self, "tab_struct") and self.tab_struct is not None:
            try:
                self.tab_struct._refresh_peak_list()
            except Exception:
                pass
