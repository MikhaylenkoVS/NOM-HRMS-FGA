"""Оценка FDR через ансамбль decoy-сдвигов (P0).

Идея (target-decoy): для настоящих целей шаги ищутся на m0 + n·Δ; для decoy —
на m0 + n·(Δ+δ_j) при K случайных δ_j. Всё остальное (ppm, критерии серии)
идентично, поэтому число decoy-серий даёт ожидаемый фон:

    FDR(L) = (N_decoy(>= L) / K) / N_target(>= L)

FDR относится к группе серий выше порога, а не к отдельной серии; для серии
берётся q-value = минимум FDR по всем порогам, которые она проходит.
"""

from __future__ import annotations

import numpy as np

# Химически осмысленные сдвиги, которые нельзя использовать как decoy:
# изотопные разности, CH2, O, H2, а также сами дериватизационные Δ.
DECOY_SEED = 42  # фиксирован: FDR воспроизводим между прогонами

_EXCLUDE_DEFAULT = (
    0.0,
    1.003355,
    1.006277,
    2.00671,
    2.01565,
    14.01565,
    15.994915,
    17.03448,
    18.010565,
    45.02939,
    46.04186,
)


def decoy_shifts(
    delta: float,
    k: int = 30,
    seed: int = DECOY_SEED,
    lo: float = 0.05,
    hi: float = 0.9,
    exclude: tuple[float, ...] = _EXCLUDE_DEFAULT,
    min_gap: float = 0.05,
) -> list[float]:
    """K случайных сдвигов обоих знаков, не близких к химически значимым Δ.

    Parameters
    ----------
    delta : float
        Настоящий сдвиг дериватизации (он и его «родственники» исключаются).
    k : int
        Сколько decoy-сдвигов вернуть.
    seed : int
        Детерминированность (важно для воспроизводимости FDR).
    lo, hi : float
        Диапазон абсолютной величины сдвига, Да.
    exclude, min_gap : tuple, float
        Исключаемые значения и минимальный зазор до них, Да.

    Returns
    -------
    list of float
        Сдвиги со знаком (положительные и отрицательные).
    """
    if k <= 0:
        raise ValueError(f"k должно быть > 0, получено {k}")
    if not 0 < lo < hi:
        raise ValueError(f"нужно 0 < lo < hi, получено lo={lo}, hi={hi}")
    banned = [abs(v) for v in exclude] + [abs(delta)]
    rng = np.random.default_rng(seed)
    out: list[float] = []
    attempts = 0
    while len(out) < k and attempts < k * 200:
        attempts += 1
        mag = float(rng.uniform(lo, hi))
        sign = 1.0 if rng.random() < 0.5 else -1.0
        shift = sign * mag
        if any(abs(abs(shift) - b) < min_gap for b in banned):
            continue
        if any(abs(shift - s) < 1e-6 for s in out):
            continue
        out.append(round(shift, 6))
    if len(out) < k:
        raise RuntimeError(
            f"не удалось подобрать {k} сдвигов (получено {len(out)}) — ослабьте min_gap"
        )
    return out


def fdr_table(
    target_lengths,
    decoy_lengths_per_shift,
    min_length: int = 1,
    max_length: int | None = None,
) -> list[dict]:
    """FDR по порогам длины серии.

    Parameters
    ----------
    target_lengths : sequence of int
        Длины настоящих серий.
    decoy_lengths_per_shift : sequence of sequence of int
        Для каждого decoy-сдвига — длины найденных «серий».
    min_length, max_length : int
        Диапазон порогов.

    Returns
    -------
    list of dict
        ``[{"length": L, "n_target": ..., "n_decoy_mean": ..., "fdr": ...}, ...]``
    """
    t = np.asarray(list(target_lengths), dtype=int)
    k = len(decoy_lengths_per_shift)
    if k == 0:
        raise ValueError("нужен хотя бы один decoy-прогон")
    hi = int(
        max_length if max_length is not None else (t.max() if t.size else min_length)
    )
    rows = []
    for length in range(int(min_length), hi + 1):
        n_t = int((t >= length).sum())
        n_d = float(
            np.mean([sum(1 for v in d if v >= length) for d in decoy_lengths_per_shift])
        )
        fdr = (n_d / max(1, n_t)) if n_t else float("nan")
        rows.append(
            {
                "length": length,
                "n_target": n_t,
                "n_decoy_mean": round(n_d, 2),
                "fdr": round(min(1.0, fdr), 4) if n_t else float("nan"),
            }
        )
    return rows


def q_values(lengths, table: list[dict]) -> list[float]:
    """q-value каждой серии = минимальный FDR по порогам, которые она проходит."""
    by_len = {row["length"]: row["fdr"] for row in table}
    out = []
    for length in lengths:
        candidates = [
            by_len[L] for L in by_len if L <= int(length) and not np.isnan(by_len[L])
        ]
        out.append(float(min(candidates)) if candidates else float("nan"))
    return out
