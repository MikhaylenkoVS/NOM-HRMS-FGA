#!/usr/bin/env python3
"""Headless-дополнение к CLI: PNG со спектрами и SDF со структурами.

Что делает
----------
1. ``--spectra-png`` — рисует три спектра (исходный / дейтерометилированный /
   дейтероацилированный) в один PNG. Пики прореживаются до ``--max-points``,
   поэтому файл строится за доли секунды даже на профильных спектрах.
2. ``--structures-sdf`` — для каждой уникальной комбинации
   ``(brutto, N_OH, N_COOH)`` из таблицы результатов генерирует одну структуру
   (как предпросмотр в GUI: ``first_only=True``, ``max_bases=8``) и пишет всё
   в один SDF. Имя молекулы — ``"<brutto> - <N_OH> - <N_COOH>"``.

Таблицу результатов делает CLI (она же — вход для SDF):

    python -m src.cli --input original.csv --dmet d.csv --dacet a.csv \\
        --sep , --output result.xlsx

Затем:

    python tools/make_outputs.py \\
        --input data/test_sets/set_01/original.csv \\
        --dmet  data/test_sets/set_01/deutermethylated.csv \\
        --dacet data/test_sets/set_01/deuteroacylated.csv \\
        --result result.xlsx --outdir out --sep ,

Поиск структур для «тяжёлых» формул может комбинаторно взрываться, поэтому
на каждую молекулу есть бюджет времени ``--mol-timeout`` (по умолчанию 15 с):
не успевшие формулы пропускаются и перечисляются в отчёте.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# ─────────────────────────────────────────────────────────────────────────────
#  1. Картинка спектров
# ─────────────────────────────────────────────────────────────────────────────


def plot_spectra(paths: list[str], sep: str, out_png: str, max_points: int = 8000) -> None:
    """Построить три масс-спектра в один PNG (без GUI)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from src.core.spectrum import CSV_COLUMN_MAPPER

    labels = ["Исходный", "Дейтерометилирование", "Дейтероацилирование"]
    colors = ["#89b4fa", "#a6e3a1", "#fab387"]

    dfs = []
    for label, path in zip(labels, paths):
        df = pd.read_csv(path, sep=sep)
        df.columns = [c.strip() for c in df.columns]
        df = df.rename(columns=CSV_COLUMN_MAPPER)
        missing = [c for c in ("mass", "intensity") if c not in df.columns]
        if missing:
            raise ValueError(
                f"{label} ({path}): нет колонок {missing}; доступны {list(df.columns)}"
            )
        df = df[["mass", "intensity"]]
        total = len(df)
        if total > max_points:
            step = total // max_points
            df = df.iloc[::step]
        dfs.append((label, df, total))
        print(f"  {label:24s} {total:>9,} пиков → {len(df):>6,} на графике")

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    for i, (ax, (label, df, total)) in enumerate(zip(axes, dfs)):
        ax.vlines(df["mass"], 0, df["intensity"], colors=colors[i],
                  linewidth=0.7, alpha=0.85)
        ax.set_ylabel("Intensity", fontsize=9)
        ax.set_title(f"{label}  ({total:,} пиков, прорежено до {len(df):,})".replace(",", " "),
                     fontsize=10, loc="left")
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("m/z", fontsize=10)
    fig.suptitle("Три масс-спектра", fontsize=13)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    print(f"  сохранено: {out_png}")


# ─────────────────────────────────────────────────────────────────────────────
#  2. Структуры → один SDF (с бюджетом времени на молекулу)
# ─────────────────────────────────────────────────────────────────────────────


def _structure_worker(in_q, out_q) -> None:
    """Процесс-исполнитель: ищет структуры по формулам из очереди.

    Работает отдельным процессом, чтобы родитель мог его убить, если
    ``find_fragment_combinations`` для какой-то формулы уйдёт в комбинаторный
    перебор на десятки секунд.
    """
    from src.core import find_and_visualize_molecules
    from src.structures.rdkit_utils import fragment_to_rdkit

    while True:
        item = in_q.get()
        if item is None:
            return
        brutto, n_cooh, n_oh = item
        try:
            res = find_and_visualize_molecules(
                brutto,
                num_cooh=n_cooh,
                num_oh=n_oh,
                max_bases=8,
                show_images=False,
                first_only=True,
            )
            mols = res.get("molecules", [])
            if not mols:
                out_q.put((brutto, n_cooh, n_oh, None, "нет комбинаций"))
                continue
            rdmol = fragment_to_rdkit(mols[0]["fragment_object"])
            if rdmol is None:
                out_q.put((brutto, n_cooh, n_oh, None, "конвертация в RDKit не удалась"))
                continue
            from rdkit import Chem

            try:
                Chem.SanitizeMol(rdmol)
            except Exception:
                pass
            block = Chem.MolToMolBlock(rdmol)
            out_q.put((brutto, n_cooh, n_oh, block, None))
        except Exception as exc:  # noqa: BLE001 — причина уходит в отчёт
            out_q.put((brutto, n_cooh, n_oh, None, f"{type(exc).__name__}: {exc}"))


def export_structures(
    df: pd.DataFrame,
    out_sdf: str,
    *,
    mol_timeout: float = 15.0,
    max_structures: int = 0,
    smiles_tsv: str | None = None,
) -> dict:
    """Сгенерировать по одной структуре на (brutto, N_OH, N_COOH) и записать в SDF."""
    mass_col = "mass" if "mass" in df.columns else None
    triples: list[tuple[str, int, int, float | None]] = []
    seen: set[tuple[str, int, int]] = set()
    for _, row in df.iterrows():
        brutto = str(row.get("brutto", "") or "").strip()
        if not brutto:
            continue
        try:
            n_cooh = int(row.get("N_COOH", 0) or 0)
            n_oh = int(row.get("N_OH", 0) or 0)
        except (TypeError, ValueError):
            n_cooh, n_oh = 0, 0
        key = (brutto, n_oh, n_cooh)
        if key in seen:
            continue
        seen.add(key)
        mass = float(row[mass_col]) if mass_col and pd.notna(row.get(mass_col)) else None
        triples.append((brutto, n_cooh, n_oh, mass))

    if max_structures and len(triples) > max_structures:
        print(f"  ограничение --max-structures={max_structures}: "
              f"беру первые {max_structures} из {len(triples)}")
        triples = triples[:max_structures]

    print(f"  уникальных (brutto, N_OH, N_COOH): {len(triples)}")
    if not triples:
        return {"total": 0, "ok": 0, "skipped": 0, "timeout": 0}

    import multiprocessing as mp

    ctx = mp.get_context("spawn")
    in_q = ctx.Queue()
    out_q = ctx.Queue()

    def _spawn():
        p = ctx.Process(target=_structure_worker, args=(in_q, out_q), daemon=True)
        p.start()
        return p

    proc = _spawn()
    Path(out_sdf).write_text("", encoding="utf-8")  # начинаем SDF с нуля
    report = {"total": len(triples), "ok": 0, "skipped": 0, "timeout": 0}
    problems: list[str] = []
    t_start = time.time()

    for i, (brutto, n_cooh, n_oh, mass) in enumerate(triples, 1):
        in_q.put((brutto, n_cooh, n_oh))
        try:
            b, c, o, block, err = out_q.get(timeout=mol_timeout)
        except Exception:
            # Процесс ушёл в комбинаторный перебор — убиваем и поднимаем новый.
            proc.terminate()
            proc.join(timeout=5)
            proc = _spawn()
            report["timeout"] += 1
            problems.append(f"{brutto} (N_OH={n_oh}, N_COOH={n_cooh}): > {mol_timeout:g} с")
            print(f"  [{i}/{len(triples)}] {brutto}: пропуск (> {mol_timeout:g} с)")
            continue

        if block:
            # Пишем mol-блок как есть (не пересобирая через RDKit): часть
            # структур не проходит санитизацию (например, валентность N=4),
            # но именно они показываются в предпросмотре GUI.
            name = f"{brutto} - {n_oh} - {n_cooh}"
            lines = block.rstrip("\n").splitlines()
            if lines:
                lines[0] = name  # первая строка mol-блока — название молекулы
            props = [f">  <brutto>\n{brutto}", f">  <N_OH>\n{n_oh}",
                     f">  <N_COOH>\n{n_cooh}"]
            if mass is not None:
                props.append(f">  <mass>\n{mass:.5f}")
            with open(out_sdf, "a", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + "\n")
                for prop in props:
                    fh.write(prop + "\n\n")
                fh.write("$$$$\n")
            report["ok"] += 1
            print(f"  [{i}/{len(triples)}] {name}: OK")
            continue
        report["skipped"] += 1
        problems.append(f"{brutto} (N_OH={n_oh}, N_COOH={n_cooh}): {err}")
        print(f"  [{i}/{len(triples)}] {brutto}: без структуры ({err})")

    in_q.put(None)
    proc.join(timeout=5)
    if proc.is_alive():
        proc.terminate()

    report["elapsed"] = round(time.time() - t_start, 1)
    report["problems"] = problems
    print(f"  SDF: {out_sdf} — молекул {report['ok']}, "
          f"без структуры {report['skipped']}, по таймауту {report['timeout']}, "
          f"за {report['elapsed']} с")
    return report


# ─────────────────────────────────────────────────────────────────────────────
#  3. CLI
# ─────────────────────────────────────────────────────────────────────────────


def _read_result(path: str) -> pd.DataFrame:
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    return pd.read_csv(path, sep=";")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="make_outputs.py",
        description="PNG со спектрами и SDF со структурами (headless, без GUI).",
    )
    p.add_argument("--input", "-i", required=True, help="исходный спектр (.csv)")
    p.add_argument("--dmet", required=True, help="дейтерометилированный спектр (.csv)")
    p.add_argument("--dacet", required=True, help="дейтероацилированный спектр (.csv)")
    p.add_argument("--result", required=True, help="таблица результатов от CLI (.xlsx/.csv)")
    p.add_argument("--outdir", "-o", required=True, help="куда складывать файлы")
    p.add_argument("--sep", default=",", help="разделитель входных CSV (по умолчанию ',')")
    p.add_argument("--max-points", type=int, default=8000,
                   help="максимум точек на спектр при отрисовке")
    p.add_argument("--mol-timeout", type=float, default=15.0,
                   help="бюджет времени на одну молекулу, секунды")
    p.add_argument("--max-structures", type=int, default=0,
                   help="сколько молекул максимум писать в SDF (0 = все)")
    p.add_argument("--spectra-png", action="store_true", help="сделать картинку спектров")
    p.add_argument("--structures-sdf", action="store_true", help="сделать SDF со структурами")
    args = p.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")

    if args.spectra_png:
        print("[1/2] Картинка спектров")
        png = os.path.join(args.outdir, f"spectra_{stamp}.png")
        plot_spectra([args.input, args.dmet, args.dacet], args.sep, png,
                     max_points=args.max_points)

    if args.structures_sdf:
        print("[2/2] Структуры → SDF")
        df = _read_result(args.result)
        print(f"  таблица результатов: {len(df)} строк, колонки {list(df.columns)}")
        sdf = os.path.join(args.outdir, f"structures_{stamp}.sdf")
        report = export_structures(df, sdf, mol_timeout=args.mol_timeout,
                                   max_structures=args.max_structures)
        if report.get("problems"):
            rep = os.path.join(args.outdir, f"structures_{stamp}_problems.txt")
            Path(rep).write_text("\n".join(report["problems"]), encoding="utf-8")
            print(f"  спорные формулы: {rep}")

    return 0


if __name__ == "__main__":
    import multiprocessing as _mp

    _mp.freeze_support()
    raise SystemExit(main())
