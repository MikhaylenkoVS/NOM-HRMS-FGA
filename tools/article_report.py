"""Материалы для научной статьи: картинки, таблицы, графики (не текст).

Единая точка генерации того, что идёт в статью:

  * рисунки (PNG 300 dpi): спектры, диаграмма Ван-Кревелена, распределения,
    групповой состав (N_COOH / N_OH), статусы изотопного подтверждения,
    технические характеристики (таблица-картинка);
  * таблицы (XLSX): результаты назначения, технические характеристики,
    сводка по группам;
  * при желании — структуры (SDF) для схемы.

Запуск из корня проекта:

    python -m tools.article_report --result result.xlsx --outdir reports/article \\
        --original orig.csv --dmet cd3.csv --dacet cd3co.csv

Модуль сознательно не пишет текстовых отчётов: только изображения и таблицы.
"""

from __future__ import annotations

import argparse
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ── Служебное ─────────────────────────────────────────────────────────────────


def _mpl():
    """matplotlib в безоконном режиме + шрифт с кириллицей."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False
    return plt


def _read_result(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if p.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(p)
    return pd.read_csv(p, sep=None, engine="python")


def _safe_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in name)


# ── Рисунок 1: спектры ────────────────────────────────────────────────────────


#: Подписи и цвета трёх панелей спектров.
_SPECTRA_LABELS = {
    "original": ("Исходный", "#1f77b4"),
    "dmet": ("Дейтерометилирование", "#2ca02c"),
    "dacet": ("Дейтероацилирование", "#d62728"),
}


def load_peaks(path: str | Path, sep: str = ",") -> pd.DataFrame:
    """Пики из любого поддерживаемого входа (CSV/XLSX/JSON) → DataFrame."""
    from src.core.spectrum import load_spectrum

    spec = load_spectrum(str(path), sep=sep)
    df = spec.table[["mass", "intensity"]].copy()
    return df


def plot_spectra_panels(
    series: list[tuple[str, pd.DataFrame, str]],
    out_png: Path,
    max_points: int = 8000,
):
    """Три (или меньше) масс-спектра на одной картинке."""
    plt = _mpl()
    n = len(series)
    fig, axes = plt.subplots(n, 1, figsize=(11, 2.7 * n), sharex=True)
    if n == 1:
        axes = [axes]
    for ax, (label, df, color) in zip(axes, series):
        total = len(df)
        plot_df = df
        if total > max_points:
            step = max(1, total // max_points)
            plot_df = df.iloc[::step]
        ax.vlines(
            plot_df["mass"],
            0,
            plot_df["intensity"],
            colors=color,
            linewidth=0.7,
            alpha=0.85,
        )
        ax.set_ylabel("Интенсивность", fontsize=9)
        ax.set_title(
            f"{label}  ({total:,} пиков, прорежено до {len(plot_df):,})".replace(
                ",", " "
            ),
            fontsize=10,
            loc="left",
        )
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("m/z", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_png


def fig_spectra(paths: dict[str, str | None], out_png: Path, max_points: int = 8000):
    """Спектры: исходный и производные (панели друг под другом)."""
    series = []
    for key, path in paths.items():
        if not path:
            continue
        label, color = _SPECTRA_LABELS.get(key, (key, "#555555"))
        try:
            df = load_peaks(path)
        except Exception:
            # JSON от RAW-конвертера (список объектов mass/intensity)
            import json

            data = json.loads(Path(path).read_text(encoding="utf-8"))
            df = pd.DataFrame(data)
        series.append((label, df[["mass", "intensity"]], color))
    if not series:
        return None
    return plot_spectra_panels(series, out_png, max_points=max_points)


# ── Рисунок 2: Ван-Кревелен ───────────────────────────────────────────────────


def fig_van_krevelen(df: pd.DataFrame, out_png: Path, color_by: str = "N_COOH"):
    from src.core.van_krevelen import create_van_krevelen_plot

    if "brutto" not in df.columns:
        return None
    if color_by not in df.columns:
        color_by = "N_OH" if "N_OH" in df.columns else None
    fig = create_van_krevelen_plot(df, str(out_png), color_by=color_by or "N_COOH")
    plt = _mpl()
    plt.close(fig)
    return out_png


# ── Рисунок 3: распределения (штатная статистика) ─────────────────────────────


def fig_histograms(df: pd.DataFrame, out_png: Path):
    from src.core.statistics import create_histograms_plot

    fig = create_histograms_plot(df)
    if fig is None:
        return None
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt = _mpl()
    plt.close(fig)
    return out_png


# ── Рисунок 4: групповой состав (N_COOH / N_OH) ───────────────────────────────


def fig_groups(df: pd.DataFrame, out_png: Path):
    """Сколько соединений в каждой группе по числу –COOH и –OH."""
    cols = [c for c in ("N_COOH", "N_OH") if c in df.columns]
    if not cols:
        return None
    plt = _mpl()
    fig, axes = plt.subplots(1, len(cols), figsize=(5 * len(cols), 4))
    if len(cols) == 1:
        axes = [axes]
    for ax, col in zip(axes, cols):
        counts = df[col].fillna(0).astype(int).value_counts().sort_index()
        ax.bar(counts.index.astype(str), counts.to_numpy(), color="#3b6ea5")
        ax.set_title(f"Распределение {col}")
        ax.set_xlabel("число групп")
        ax.set_ylabel("число соединений")
        for i, v in enumerate(counts.to_numpy()):
            ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_png


# ── Рисунок 5: изотопное подтверждение ────────────────────────────────────────


def fig_isotope(df: pd.DataFrame, out_png: Path):
    cols = [c for c in ("iso_status", "iso_halogen_unconfirmed") if c in df.columns]
    if not cols:
        return None
    plt = _mpl()
    fig, axes = plt.subplots(1, len(cols), figsize=(5 * len(cols), 4))
    if len(cols) == 1:
        axes = [axes]
    for ax, col in zip(axes, cols):
        series = df[col]
        if col == "iso_halogen_unconfirmed":
            series = series.astype(bool).map(
                {True: "галоген без подтверждения", False: "подтверждён/нет галогена"}
            )
        counts = series.fillna("—").value_counts()
        ax.bar(counts.index.astype(str), counts.to_numpy(), color="#a5533b")
        ax.set_title(col)
        ax.set_ylabel("число соединений")
        ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_png


# ── Технические характеристики ────────────────────────────────────────────────


def technical_characteristics(
    df: pd.DataFrame | None = None,
    timing: dict | None = None,
    extra: dict | None = None,
) -> pd.DataFrame:
    """Ключевые технические характеристики кода (для статьи)."""
    rows: list[tuple[str, str]] = []

    def add(name: str, value) -> None:
        rows.append((name, "" if value is None else str(value)))

    try:
        import src as pkg

        add("Версия программы", getattr(pkg, "__version__", "—"))
    except Exception:
        add("Версия программы", "—")
    add("Python", sys.version.split()[0])
    add("Платформа", f"{platform.system()} {platform.release()}")
    add("Процессор", platform.processor() or "—")

    # База формул
    try:
        from src.configs import FORMULA_SEARCH_CFG
        from src.core.formula_db._reader import FormulaDatabaseReader
        from src.core.spectrum._formula_source import open_formula_db

        db = open_formula_db()
        if db is not None:
            fdb = Path(getattr(db, "_fdb", ""))
            add("Формул в базе", f"{db.total_formulas:,}".replace(",", " "))
            add("Файл базы", fdb.name)
            add(
                "Размер базы, МБ",
                f"{fdb.stat().st_size / 1e6:.1f}" if fdb.exists() else "—",
            )
            add("Макс. масса базы, Да", f"{db.max_mass:.0f}")
            db.close()
        else:
            add("База формул", "недоступна (используется перебор)")
        add(
            "Окна элементов",
            ", ".join(
                f"{el}:{lo}-{hi}"
                for el, (lo, hi) in (FORMULA_SEARCH_CFG.ranges or {}).items()
            ),
        )
    except Exception as exc:  # pragma: no cover
        add("База формул", f"ошибка: {exc}")

    # Изотопы / галогены
    try:
        from src.configs import FORMULA_SEARCH_CFG as _FS
        from src.core.spectrum._formula_source import (
            halogen_search_plan,
            select_halogen_combos,
        )

        hs = getattr(_FS, "halogen_search", {}) or {}
        add(
            "Режим галогенов",
            (
                "все комбинации"
                if hs.get("exhaustive")
                else f"до {hs.get('max_combinations', 16)} комбинаций"
            ),
        )
        plan = halogen_search_plan(
            _FS_ranges_cfg(), 16, bool(hs.get("exhaustive", True)), 5
        )
        add("Комбинаций галогенов", f"{plan['selected']} из {plan['allowed']}")
    except Exception:
        pass

    # Результаты
    if df is not None and len(df):
        add("Соединений в отчёте", len(df))
        add(
            "Диапазон масс, Да",
            f"{df['mass'].min():.1f}–{df['mass'].max():.1f}" if "mass" in df else "—",
        )
        if "brutto" in df:
            add("Уникальных брутто-формул", int(df["brutto"].nunique()))
            hal = df["brutto"].astype(str).str.contains("F|Cl|Br|I", regex=True)
            add("Формул с галогенами", int(hal.sum()))
        for col in ("N_COOH", "N_OH"):
            if col in df.columns:
                add(f"Среднее {col}", f"{df[col].fillna(0).mean():.2f}")

    if timing:
        for k, v in timing.items():
            add(k, f"{v:.2f} c" if isinstance(v, (int, float)) else v)
    if extra:
        for k, v in extra.items():
            add(k, v)
    return pd.DataFrame(rows, columns=["Характеристика", "Значение"])


def _FS_ranges_cfg():
    from src.core.spectrum._constants import FormulaSearchConfig

    return FormulaSearchConfig()


# ── Рисунок 6: технические характеристики таблицей ───────────────────────────


def fig_technical_table(df: pd.DataFrame, out_png: Path, title: str = ""):
    plt = _mpl()
    n = len(df)
    height = max(3.0, 0.32 * n + 1.2)
    fig, ax = plt.subplots(figsize=(11, height))
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=13, pad=12)
    tbl = ax.table(
        cellText=df.to_numpy(),
        colLabels=list(df.columns),
        loc="center",
        cellLoc="left",
        colWidths=[0.42, 0.58],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.25)
    for (row, _col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#eef2f7")
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_png


# ── Таблицы ───────────────────────────────────────────────────────────────────


def table_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Сводка по группам: сколько соединений с данным числом –COOH / –OH."""
    out = []
    for col in ("N_COOH", "N_OH"):
        if col not in df.columns:
            continue
        for value, sub in df.groupby(df[col].fillna(0).astype(int)):
            g = {"группа": col, "число групп": int(value), "соединений": len(sub)}
            if "mass" in sub:
                g["средняя масса"] = round(float(sub["mass"].mean()), 2)
            if "intensity" in sub:
                g["средняя интенсивность"] = round(float(sub["intensity"].mean()), 1)
            out.append(g)
    return pd.DataFrame(out)


def write_tables(df: pd.DataFrame, technical: pd.DataFrame, outdir: Path) -> list[Path]:
    written = []
    p1 = outdir / "table_01_results.xlsx"
    df.to_excel(p1, index=False)
    written.append(p1)
    p2 = outdir / "table_02_technical.xlsx"
    technical.to_excel(p2, index=False)
    written.append(p2)
    groups = table_groups(df)
    if len(groups):
        p3 = outdir / "table_03_groups.xlsx"
        groups.to_excel(p3, index=False)
        written.append(p3)
    return written


# ── Главная функция ───────────────────────────────────────────────────────────


def generate_article_report(
    result: str | Path | None = None,
    *,
    outdir: str | Path = "reports/article",
    original: str | None = None,
    dmet: str | None = None,
    dacet: str | None = None,
    df: pd.DataFrame | None = None,
    timing: dict | None = None,
    extra_technical: dict | None = None,
    structures_sdf: str | None = None,
    progress=None,
) -> dict:
    """Собрать все материалы для статьи (рисунки + таблицы)."""
    log = progress or (lambda msg: print(msg))
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    if df is None:
        if result is None:
            raise ValueError("нужен result или df")
        df = _read_result(result)
    log(f"Результатов: {len(df)} строк")

    made: dict[str, list[str]] = {"figures": [], "tables": []}

    def _try(fn, label: str):
        try:
            p = fn()
            if p is not None:
                made["figures"].append(str(p))
                log(f"  рисунок: {Path(p).name}")
        except Exception as exc:
            log(f"  {label}: не построен ({exc})")

    _try(
        lambda: fig_spectra(
            {"original": original, "dmet": dmet, "dacet": dacet},
            out / "fig_01_spectra.png",
        ),
        "спектры",
    )
    _try(lambda: fig_van_krevelen(df, out / "fig_02_van_krevelen.png"), "Ван-Кревелен")
    _try(lambda: fig_histograms(df, out / "fig_03_histograms.png"), "распределения")
    _try(lambda: fig_groups(df, out / "fig_04_groups.png"), "группы")
    _try(lambda: fig_isotope(df, out / "fig_05_isotope_status.png"), "изотопы")

    if structures_sdf:
        try:
            made["tables"].append(str(structures_sdf))
            log(f"  структуры: {Path(structures_sdf).name}")
        except Exception as exc:
            log(f"  структуры: {exc}")

    made["tables"].extend(
        str(p)
        for p in write_tables(
            df, technical_characteristics(df, timing=timing, extra=extra_technical), out
        )
    )
    for p in made["tables"]:
        if p.endswith(".xlsx"):
            log(f"  таблица: {Path(p).name}")

    tech = technical_characteristics(df, timing=timing, extra=extra_technical)
    _try(
        lambda: fig_technical_table(
            tech, out / "fig_06_technical.png", "Технические характеристики"
        ),
        "тех. таблица",
    )

    elapsed = time.perf_counter() - t0
    log(
        f"Готово за {elapsed:.1f} c: {len(made['figures'])} рисунков, "
        f"{len(made['tables'])} таблиц → {out}"
    )
    return {
        "outdir": str(out),
        "figures": made["figures"],
        "tables": made["tables"],
        "seconds": elapsed,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Материалы для статьи (рисунки и таблицы)")
    ap.add_argument("--result", required=True, help="таблица результатов (.xlsx/.csv)")
    ap.add_argument("--outdir", default="reports/article")
    ap.add_argument("--original", default=None)
    ap.add_argument("--dmet", default=None)
    ap.add_argument("--dacet", default=None)
    ap.add_argument("--structures", default=None, help="SDF со структурами (если есть)")
    a = ap.parse_args(argv)
    res = generate_article_report(
        a.result,
        outdir=a.outdir,
        original=a.original,
        dmet=a.dmet,
        dacet=a.dacet,
        structures_sdf=a.structures,
    )
    print(f"рисунков: {len(res['figures'])}, таблиц: {len(res['tables'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
