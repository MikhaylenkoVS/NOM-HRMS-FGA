"""Pipeline test mode."""

import logging
from pathlib import Path

from src.configs import PIPELINE, PATHS
from src.core.spectrum import DELTA_CD3, DELTA_CD3CO
from ._stats import TestSetResult
from ._test_set import _run_single_test_set

logger = logging.getLogger(__name__)


#: Конфигурация дериватизации для тест-режима:
#: имена файлов из paths.json, сдвиги масс из chemistry.json.
_DERIV_SPECS = [
    (
        PATHS.spectrum_files["deutermethylated"],
        DELTA_CD3,
        "deutermethylated",
    ),
    (
        PATHS.spectrum_files["deuteroacylated"],
        DELTA_CD3CO,
        "deuteroacylated",
    ),
]
_TEST_MATCH_PPM = PIPELINE.test_mode["match_ppm"]


def _run_test_mode(
    test_sets_root=None,
    noise_force=10.0,
    noise_intensity=100,
    noise_quantile=None,
    assign_mass_min=None,
    assign_mass_max=None,
    rel_error=0.5,
    sign="-",
    ppm_tol=0.5,
    max_groups=20,
    allow_gaps=True,
) -> list[TestSetResult]:
    """Run the pipeline over every ``set_0N`` and print detailed statistics.

    Parameters
    ----------
    test_sets_root : str, path-like or None, optional
        Root directory holding the ``set_0*`` folders. If ``None``, it is
        auto-detected relative to the repository, falling back to
        ``<cwd>/data/test_sets``.
    noise_force, noise_intensity, noise_quantile : optional
        Denoising parameters.
    assign_mass_min, assign_mass_max : float or None, optional
        Mass window for formula assignment.
    rel_error : float, optional
        Mass tolerance (ppm) for assignment. Default 0.5.
    sign : {'-', '+'}, optional
        Ionization sign. Default ``'-'``.
    ppm_tol : float, optional
        Series-matching tolerance (ppm). Default 0.5.
    max_groups : int, optional
        Maximum functional groups probed per molecule. Default 20.
    allow_gaps : bool, optional
        Whether to tolerate gaps within a series. Default ``True``.

    Returns
    -------
    list of TestSetResult
        One result per test set; empty if the root or sets are missing.
    """

    # Resolve roots
    if test_sets_root is None:
        # Автоопределение: ищем через paths.json относительно текущего файла
        candidate = Path(__file__).resolve().parents[2] / PATHS.test_sets_dir
        if candidate.exists():
            test_sets_root = candidate
        else:
            # fallback: текущая рабочая директория
            test_sets_root = Path.cwd() / PATHS.test_sets_dir
    test_sets_root = Path(test_sets_root)

    print("=" * 70)
    print("ТЕСТ-РЕЖИМ pipeline.py")
    print(f"  test_sets_root = {test_sets_root}")
    print(f"  exists         = {test_sets_root.exists()}")
    print("=" * 70)

    if not test_sets_root.exists():
        logger.error(
            f"[TEST] ОШИБКА: директория тест-сетов не найдена: {test_sets_root}",
        )
        return []

    test_sets = sorted(p for p in test_sets_root.glob("set_0*") if p.is_dir())
    if not test_sets:
        logger.error(
            f"[TEST] ОШИБКА: не найдено ни одного set* в {test_sets_root}",
        )
        return []

    print(f"  Найдено сетов: {len(test_sets)} → {[p.name for p in test_sets]}")
    print()

    results: list[TestSetResult] = []
    all_errors: list[str] = []

    for set_dir in test_sets:
        res = _run_single_test_set(
            set_dir=set_dir,
            noise_force=noise_force,
            noise_intensity=noise_intensity,
            noise_quantile=noise_quantile,
            assign_mass_min=assign_mass_min,
            assign_mass_max=assign_mass_max,
            rel_error=rel_error,
            sign=sign,
            ppm_tol=ppm_tol,
            max_groups=max_groups,
            allow_gaps=allow_gaps,
        )
        results.append(res)
        if res.errors:
            all_errors.extend([f"[{res.set_name}] {e}" for e in res.errors])

    # -----------------------------------------------------------------------
    # Итоговая сводная статистика
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("ИТОГОВАЯ СВОДНАЯ СТАТИСТИКА (тест-режим)")
    print("=" * 70)
    header = (
        f"{'Set':<8}"
        f"{'Signals':>8}"
        f"{'Denoised':>10}"
        f"{'D-Rec%':>8}"
        f"{'Assigned':>10}"
        f"{'A-Rec%':>8}"
        f"{'DmetFnd':>9}"
        f"{'DmetOk':>8}"
        f"{'DacetFnd':>10}"
        f"{'DacetOk':>9}"
        f"{'Errors':>7}"
    )
    print(header)
    print("-" * 97)
    for r in results:
        dr = r.denoise_recall * 100
        ar = r.assign_recall * 100
        errs = len(r.errors)
        print(
            f"{r.set_name:<8}"
            f"{r.total_signals:>8}"
            f"{r.denoised_kept:>10}"
            f"{dr:>7.1f}%"
            f"{r.assigned_ok:>10}"
            f"{ar:>7.1f}%"
            f"{r.dmet_found:>9}"
            f"{r.dmet_matched:>8}"
            f"{r.dacet_found:>10}"
            f"{r.dacet_matched:>9}"
            f"{errs:>7}"
        )
    print("-" * 97)

    if all_errors:
        print()
        print(f"НАКОПЛЕННЫЕ ОШИБКИ ({len(all_errors)} шт.):")
        for e in all_errors:
            print(f"  {e}")

    # Проверки на пороги
    print()
    print("ПРОВЕРКА ПОРОГОВ:")
    # Pass/fail thresholds (single source of truth: pipeline.json -> thresholds).
    MIN_DENOISE_RECALL = PIPELINE.thresholds["min_denoise_recall"]
    MIN_ASSIGN_RECALL = PIPELINE.thresholds["min_assign_recall"]
    MAX_WRONG_RATIO = PIPELINE.thresholds["max_wrong_ratio"]
    any_fail = False
    for r in results:
        if r.denoise_recall < MIN_DENOISE_RECALL:
            print(
                f"  FAIL denoise  {r.set_name}: {r.denoise_recall:.3f} < {MIN_DENOISE_RECALL}"
            )
            any_fail = True
        if r.assign_recall < MIN_ASSIGN_RECALL:
            print(
                f"  FAIL assign   {r.set_name}: {r.assign_recall:.3f} < {MIN_ASSIGN_RECALL}"
            )
            any_fail = True
        total = r.total_signals
        dmet_wrong_ratio = r.dmet_wrong / total if total else 0
        dacet_wrong_ratio = r.dacet_wrong / total if total else 0
        if dmet_wrong_ratio > MAX_WRONG_RATIO:
            print(
                f"  FAIL dmet_wrong {r.set_name}: {dmet_wrong_ratio:.3f} > {MAX_WRONG_RATIO}"
            )
            any_fail = True
        if dacet_wrong_ratio > MAX_WRONG_RATIO:
            print(
                f"  FAIL dacet_wrong {r.set_name}: {dacet_wrong_ratio:.3f} > {MAX_WRONG_RATIO}"
            )
            any_fail = True
    if not any_fail:
        print("  Все пороги пройдены ✓")

    return results


# ---------------------------------------------------------------------------
# Точка входа командной строки
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="pipeline.py – анализ масс-спектров гуминовых веществ"
    )
    parser.add_argument(
        "--test", action="store_true", help="Запустить тест-режим по set_01..set_05"
    )
    parser.add_argument(
        "--sets-root", type=str, default=None, help="Путь к директории с тест-сетами"
    )
    args = parser.parse_args()

    if args.test:
        run_pipeline(test_mode=True, test_sets_root=args.sets_root)
    else:
        print(
            "Используйте --test для запуска тест-режима, или импортируйте run_pipeline() из кода."
        )
