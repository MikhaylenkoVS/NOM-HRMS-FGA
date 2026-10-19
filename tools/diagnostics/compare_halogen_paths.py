"""Почему «слой подстановок» (v2 CHNOSP) и база CHNOSPHal (v3) дают разное.

Сравнение идёт на уровне кандидатов — то есть ровно тем вызовом, который делает
пайплайн (`db_candidates`), но для каждого пути отдельно:

  * ``layer``  — v2 CHNOSP + слой галогенных подстановок (include_halogens=True);
  * ``chnosp`` — v2 CHNOSP без подстановок (что пайплайн использует для пиков БЕЗ
    изотопного свидетельства M+2 — см. gating в ``_assign.py``);
  * ``base``   — v3 CHNOSPHal (галогены материализованы, слой не применяется).

Для каждого пика сравниваются множества формул (в порядке ``cfg.elements``) и
классифицируются расхождения:

  * ``only_in_base``   — есть в базе v3, нет в слое (слой не догенерировал);
  * ``only_in_layer``  — есть в слое, нет в базе (база не содержит);
  * ``mass_mismatch``  — формула есть в обоих, но массы различаются.

Запуск:
  python tools/diagnostics/compare_halogen_paths.py --datasets set_01,set_02 \
      --json D:/Temp/User/halogen_paths.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.core.formula_db._reader import FormulaDatabaseReader
from src.core.formula_db._reader_v3 import FormulaDatabaseReaderV3
from src.core.spectrum._constants import FormulaSearchConfig
from src.core.spectrum._formula_source import db_candidates

V2_MANIFEST = Path("data/formula_db/chposp_1000_zstd9_v2.manifest.json")
V3_MANIFEST = Path("data/formula_db/chorsphal_1000_v3.manifest.json")
BIN_TOL_PPM = 5.0


def _peak_masses(dataset: str, limit: int) -> list[float]:
    """НЕЙТРАЛЬНЫЕ массы пиков датасета (после загрузки и шумоподавления).

    В спектре хранятся m/z ионов, а база формул — нейтральные массы, поэтому
    переводим: ``neutral = m/z − _ion_shift(mode)`` (для [M-H]- сдвиг
    отрицательный, то есть neutral = m/z + m(H) − m(e)).
    """
    from src.core.spectrum._denoise import denoise
    from src.core.spectrum._generate import _ion_shift
    from src.core.spectrum._load import load_spectrum

    if dataset.startswith("set_"):
        path = f"data/test_sets/{dataset}/original.csv"
    else:
        raw = f"data/real_sets/{dataset}/" + _real_original(dataset)
        # RAW предварительно усредняем в таблицу (как делает CLI)
        from src.core.io.raw_bridge import average_raw_to_json

        path = average_raw_to_json(raw, 0.0, 999.0)
    spec = load_spectrum(path, sep=",")
    spec = denoise(spec)
    # режим ионизации по умолчанию берём из конфига (модуль _chem отдаёт
    # атрибуты динамически, поэтому читаем JSON напрямую)
    import json

    chem_cfg = json.loads(
        Path("src/configs/chemistry.json").read_text(encoding="utf-8")
    )
    shift = _ion_shift(chem_cfg.get("default_ion_mode", "[M-H]-"))
    masses = [float(m) - shift for m in spec.table["mass"].to_numpy()]
    if limit and len(masses) > limit:
        step = max(1, len(masses) // limit)
        masses = masses[::step][:limit]
    return masses


def _real_original(dataset: str) -> str:
    return {
        "SRFA": "SRFA_ESI_480k_128_m-s.raw",
        "Fulvagra F14": "Fulvagra_prep HPLC_Fr14_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra F16": "Fulvagra_prep HPLC_FR16_ESI_1e6_480k_128_m-s.raw",
    }[dataset]


def _candidates(reader, cfg, mass: float, *, halogens: bool) -> dict[tuple, float]:
    half = mass * BIN_TOL_PPM * 1e-6
    rows, masses = db_candidates(
        reader, cfg, mass, half, include_halogens=halogens, halogen_exhaustive=True
    )
    return {tuple(int(v) for v in row): float(m) for row, m in zip(rows, masses)}


def _explain_missing(
    v2, cfg, peak_mass: float, cand_mass: float, key: tuple, combos: list
) -> tuple[str, float]:
    """Почему слой не догенерировал формулу ``key``.

    Возвращает ``(причина, смещение_ppm)``, где смещение — расстояние от центра
    поиска слоя (``масса пика − Δ``) до истинной массы родителя. Категории:

    * ``combo_not_selected`` — комбинация галогенов не входит в список слоя;
    * ``parent_outside_window`` — родитель существует, но из-за того, что слой
      ищет его от массы ПИКА (а допуск ppm применяется и к родителю, и к
      конечной формуле), родитель выпадает из окна;
    * ``no_parent_in_v2`` — родительской формулы нет в базе v2;
    * ``other`` — иное.
    """
    from src.core.formula_db._reader_v3 import FORMULA_ELEMENT_ORDER as ORDER
    from src.core.formula_db._reader_v3 import MASS_U

    idx = {el: i for i, el in enumerate(ORDER)}
    x_counts = tuple(key[idx[el]] for el in ("F", "Cl", "Br", "I"))
    x_total = sum(x_counts)
    layer_combos = {tuple(sorted((el, n) for el, n in combo)) for combo in combos}
    mine = tuple(
        sorted((el, n) for el, n in zip(("F", "Cl", "Br", "I"), x_counts) if n)
    )
    if x_total and mine not in layer_combos:
        return "combo_not_selected", 0.0

    delta_u = sum(
        n_x * (MASS_U[el] - MASS_U["H"])
        for el, n_x in zip(("F", "Cl", "Br", "I"), x_counts)
    )
    parent = (
        key[idx["C"]],
        key[idx["H"]] + x_total,
        key[idx["O"]],
        key[idx["N"]],
        key[idx["S"]],
        key[idx["P"]],
    )
    # истинная масса родителя (в единицах 1e-11 Да)
    parent_mass_u = (
        parent[0] * MASS_U["C"]
        + parent[1] * MASS_U["H"]
        + parent[2] * MASS_U["O"]
        + parent[3] * MASS_U["N"]
        + parent[4] * MASS_U["S"]
        + parent[5] * MASS_U["P"]
    )
    parent_mass = parent_mass_u / 1e11
    # центр поиска слоя — от массы пика (так делает db_candidates)
    layer_center = peak_mass - delta_u / 1e11
    offset_ppm = abs(layer_center - parent_mass) / parent_mass * 1e6

    res = v2.search(parent_mass, ppm=BIN_TOL_PPM, max_results=20000)
    for r in res:
        c = r.counts
        row = (
            c.get("C", 0),
            c.get("H", 0),
            c.get("O", 0),
            c.get("N", 0),
            c.get("S", 0),
            c.get("P", 0),
        )
        if row == parent:
            if offset_ppm > BIN_TOL_PPM:
                return "parent_outside_window", round(offset_ppm, 3)
            return "other", round(offset_ppm, 3)
    return "no_parent_in_v2", round(offset_ppm, 3)


def compare(datasets: list[str], limit: int) -> dict:
    if not V2_MANIFEST.is_file():
        raise SystemExit(f"нет базовой базы: {V2_MANIFEST}")
    if not V3_MANIFEST.is_file():
        raise SystemExit(
            f"нет базы v3: {V3_MANIFEST} (установите chorsphal в data/formula_db)"
        )

    cfg = FormulaSearchConfig()
    v2 = FormulaDatabaseReader(V2_MANIFEST, cache_size=64)
    v3 = FormulaDatabaseReaderV3(V3_MANIFEST, cache_size=64)

    reasons: dict[str, int] = {}
    offsets: dict[str, list[float]] = {}
    report: dict = {"datasets": {}, "totals": {}}
    tot = {
        "peaks": 0,
        "only_in_base": 0,
        "only_in_layer": 0,
        "mass_mismatch": 0,
        "only_in_base_vs_pipeline": 0,
        "identical": 0,
    }
    examples: dict[str, list] = {
        "only_in_base": [],
        "only_in_layer": [],
        "mass_mismatch": [],
        "gating": [],
    }

    for ds in datasets:
        masses = _peak_masses(ds, limit)
        stats = {
            "peaks": len(masses),
            "layer": 0,
            "chnosp": 0,
            "base": 0,
            "only_in_base": 0,
            "only_in_layer": 0,
            "mass_mismatch": 0,
            "identical_layer_base": 0,
            "gating_lost_vs_base": 0,
        }
        for m in masses:
            layer = _candidates(v2, cfg, m, halogens=True)
            chnosp = _candidates(v2, cfg, m, halogens=False)
            base = _candidates(v3, cfg, m, halogens=True)
            stats["layer"] += len(layer)
            stats["chnosp"] += len(chnosp)
            stats["base"] += len(base)

            only_base = set(base) - set(layer)
            only_layer = set(layer) - set(base)
            stats["only_in_base"] += len(only_base)
            stats["only_in_layer"] += len(only_layer)
            if not only_base and not only_layer:
                stats["identical_layer_base"] += 1
            if only_base:
                from src.core.spectrum._formula_source import select_halogen_combos

                combos, _allowed = select_halogen_combos(cfg, 16, True, None)
                for key in sorted(only_base)[:4]:
                    reason, off_ppm = _explain_missing(
                        v2, cfg, m, base[key], key, combos
                    )
                    reasons[reason] = reasons.get(reason, 0) + 1
                    offsets.setdefault(reason, []).append(off_ppm)
                    if len(examples["only_in_base"]) < 12:
                        examples["only_in_base"].append(
                            {
                                "dataset": ds,
                                "mass": m,
                                "counts": key,
                                "mass_cand": base[key],
                                "reason": reason,
                                "offset_ppm": off_ppm,
                            }
                        )
            for key in list(only_layer)[:2]:
                if len(examples["only_in_layer"]) < 12:
                    examples["only_in_layer"].append(
                        {
                            "dataset": ds,
                            "mass": m,
                            "counts": key,
                            "mass_cand": layer[key],
                        }
                    )
            for key in set(base) & set(layer):
                if abs(base[key] - layer[key]) > 1e-9:
                    stats["mass_mismatch"] += 1
                    if len(examples["mass_mismatch"]) < 6:
                        examples["mass_mismatch"].append(
                            {
                                "dataset": ds,
                                "mass": m,
                                "counts": key,
                                "base": base[key],
                                "layer": layer[key],
                            }
                        )
            # что теряется из-за gating: пики, где слой не применялся бы
            # (в пайплайне галогены включаются по M+2 или при пустом CHNOSP)
            if chnosp:
                gating_lost = set(base) - set(chnosp)
                stats["gating_lost_vs_base"] += len(gating_lost)
                if gating_lost and len(examples["gating"]) < 6:
                    examples["gating"].append(
                        {
                            "dataset": ds,
                            "mass": m,
                            "n_base": len(base),
                            "n_chnosp": len(chnosp),
                            "lost": len(gating_lost),
                        }
                    )

        report["datasets"][ds] = stats
        for k in (
            "peaks",
            "only_in_base",
            "only_in_layer",
            "mass_mismatch",
            "identical_layer_base",
            "gating_lost_vs_base",
        ):
            tot[k] = tot.get(k, 0) + stats[k]
        print(
            f"{ds:14s} пиков {stats['peaks']:4d} | кандидатов слой {stats['layer']:7d} "
            f"chnosp {stats['chnosp']:7d} база {stats['base']:7d} | "
            f"только в базе {stats['only_in_base']:7d} только в слое {stats['only_in_layer']:7d} "
            f"расхождение масс {stats['mass_mismatch']:4d} | "
            f"совпало наборов {stats['identical_layer_base']:4d}/{stats['peaks']}"
        )

    report["totals"] = tot
    report["missing_reasons_sampled"] = reasons
    report["missing_reasons_offset_ppm"] = {
        k: {
            "n": len(v),
            "min": min(v),
            "mean": round(sum(v) / len(v), 3),
            "max": max(v),
        }
        for k, v in offsets.items()
        if v
    }
    report["examples"] = examples
    v2.close()
    v3.close()
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default="set_01,set_02,set_03,set_04,set_05")
    ap.add_argument("--limit", type=int, default=200, help="пиков на датасет")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    ds = [s.strip() for s in a.datasets.split(",") if s.strip()]
    report = compare(ds, a.limit)
    if a.json:
        Path(a.json).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nзаписано: {a.json}")


if __name__ == "__main__":
    main()
