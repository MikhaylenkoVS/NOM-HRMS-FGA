"""Исключение сигналов, дублирующихся между исходным и производным спектрами.

Модель — **один к одному**: каждый пик исходника вычитает не более одного пика
производного спектра (ближайшего по массе в пределах ppm-окна). Основание: если
пик исходника накладывается на пик дериватизата, такой пик и так не является
подтверждением дериватизации, поэтому потенциальные дериватизаты не теряются.

Сопоставление — только по m/z (интенсивности не учитываются). Пары выбираются
«жадно»: сначала самые точные совпадения (минимальное отклонение в ppm), каждая
пара используется один раз. Отсюда: удаляется не больше пиков, чем есть в
исходнике, и один пик дериватизата не может быть вычтен дважды.
"""

from __future__ import annotations

import logging

import numpy as np

from src.core.domain.spectrum import Spectrum

logger = logging.getLogger(__name__)


def _sorted_mz(spectrum: Spectrum) -> np.ndarray:
    mz = np.asarray(spectrum.table["mass"].to_numpy(), dtype=float)
    return np.sort(mz) if mz.size else mz


def match_mask(
    deriv_mz: np.ndarray, src_mz_sorted: np.ndarray, ppm_tol: float
) -> np.ndarray:
    """bool-маска: ``True`` — у пика производного спектра есть совпадение.

    Вспомогательная (для диагностики): не учитывает правило «один к одному».
    """
    deriv_mz = np.asarray(deriv_mz, dtype=float)
    if deriv_mz.size == 0 or src_mz_sorted.size == 0:
        return np.zeros(deriv_mz.shape, dtype=bool)

    pos = np.searchsorted(src_mz_sorted, deriv_mz)
    left = np.clip(pos - 1, 0, src_mz_sorted.size - 1)
    right = np.clip(pos, 0, src_mz_sorted.size - 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        dev_left = np.abs(src_mz_sorted[left] - deriv_mz) / deriv_mz * 1e6
        dev_right = np.abs(src_mz_sorted[right] - deriv_mz) / deriv_mz * 1e6
    dev = np.minimum(dev_left, dev_right)
    return dev <= float(ppm_tol)


def matched_pairs(
    src_mz: np.ndarray, deriv_mz: np.ndarray, ppm_tol: float
) -> np.ndarray:
    """Индексы пиков дериватизата, вычтенных по правилу «один к одному».

    Строятся все пары (пик исходника, пик дериватизата) в пределах ``ppm_tol``,
    затем они разбираются по возрастанию отклонения в ppm: пара принимается,
    если оба её участника ещё не использованы.

    Returns
    -------
    numpy.ndarray
        Индексы (в исходном порядке ``deriv_mz``) вычитаемых пиков.
    """
    src_mz = np.asarray(src_mz, dtype=float)
    deriv_mz = np.asarray(deriv_mz, dtype=float)
    if src_mz.size == 0 or deriv_mz.size == 0:
        return np.empty(0, dtype=int)

    order = np.argsort(deriv_mz)
    deriv_sorted = deriv_mz[order]
    tol = float(ppm_tol)

    pairs: list[tuple[float, int, int]] = []
    for i, m in enumerate(src_mz):
        lo = int(np.searchsorted(deriv_sorted, m * (1.0 - tol * 1e-6), side="left"))
        hi = int(np.searchsorted(deriv_sorted, m * (1.0 + tol * 1e-6), side="right"))
        for j in range(lo, hi):
            dev = abs(deriv_sorted[j] - m) / m * 1e6
            if dev <= tol:
                pairs.append((dev, i, j))

    if not pairs:
        return np.empty(0, dtype=int)

    pairs.sort()
    used_src = np.zeros(src_mz.size, dtype=bool)
    used_deriv = np.zeros(deriv_mz.size, dtype=bool)
    matched: list[int] = []
    for _dev, i, j in pairs:
        if used_src[i] or used_deriv[j]:
            continue
        used_src[i] = True
        used_deriv[j] = True
        matched.append(int(order[j]))

    return np.asarray(matched, dtype=int)


def anchor_masses(
    src_mz: np.ndarray, deriv_mz: np.ndarray, ppm_tol: float
) -> np.ndarray:
    """Для каждого пика исходника — m/z соответствующего пика дериватизата.

    Ищется ближайший пик производного спектра в пределах ``ppm_tol``.
    Если пика нет — ``NaN``. Нужно для режима ``series_anchor="observed"``:
    сдвиг ступеней считается от наблюдаемого пика, а не от теоретической массы.
    """
    src_mz = np.asarray(src_mz, dtype=float)
    deriv_mz = np.asarray(deriv_mz, dtype=float)
    out = np.full(src_mz.shape, np.nan, dtype=float)
    if src_mz.size == 0 or deriv_mz.size == 0:
        return out
    order = np.argsort(deriv_mz)
    sorted_mz = deriv_mz[order]
    pos = np.searchsorted(sorted_mz, src_mz)
    best_dev = np.full(src_mz.shape, np.inf)
    for shift in (-1, 0):
        idx = np.clip(pos + shift, 0, sorted_mz.size - 1)
        cand = sorted_mz[idx]
        with np.errstate(invalid="ignore", divide="ignore"):
            dev = np.abs(cand - src_mz) / src_mz * 1e6
        take = dev < best_dev
        best_dev = np.where(take, dev, best_dev)
        out = np.where(take, cand, out)
    out[best_dev > float(ppm_tol)] = np.nan
    return out


def subtract_matching_peaks(
    deriv: Spectrum,
    src: Spectrum,
    ppm_tol: float = 5.0,
    one_to_one: bool = True,
) -> tuple[Spectrum, dict]:
    """Удалить из ``deriv`` пики, которые объясняются исходным спектром.

    Parameters
    ----------
    deriv : Spectrum
        Производный спектр (после шумоподавления).
    src : Spectrum
        Исходный спектр (после шумоподавления).
    ppm_tol : float, optional
        Окно совпадения по m/z в ppm. Интенсивности не учитываются. Default 5.0.
    one_to_one : bool, optional
        ``True`` (модель по умолчанию) — каждый пик исходника вычитает не более
        одного (ближайшего) пика дериватизата. ``False`` — удаляются все
        совпавшие пики (прежнее поведение, для сравнения). Default ``True``.

    Returns
    -------
    tuple of (Spectrum, dict)
        Новый спектр и статистика: ``total``, ``removed``, ``kept``,
        ``removed_frac``, ``ppm_tol``, ``one_to_one``, ``src_peaks``.
    """
    if ppm_tol <= 0:
        raise ValueError(f"ppm_tol должно быть > 0, получено {ppm_tol}")

    table = deriv.table
    src_table = src.table
    src_n = int(len(src_table)) if src_table is not None else 0
    if table is None or len(table) == 0:
        return deriv, {
            "total": 0,
            "removed": 0,
            "kept": 0,
            "removed_frac": 0.0,
            "ppm_tol": float(ppm_tol),
            "one_to_one": bool(one_to_one),
            "src_peaks": src_n,
        }

    deriv_mz = np.asarray(table["mass"].to_numpy(), dtype=float)
    src_mz_sorted = _sorted_mz(src)

    if one_to_one:
        src_mz = np.asarray(src_table["mass"].to_numpy(), dtype=float)
        removed_idx = matched_pairs(src_mz, deriv_mz, ppm_tol)
        dup = np.zeros(deriv_mz.size, dtype=bool)
        if removed_idx.size:
            dup[removed_idx] = True
    else:
        dup = match_mask(deriv_mz, src_mz_sorted, ppm_tol)

    # Сохраняем исходный порядок строк (важно для прогресса/визуализации)
    keep = ~dup
    new_table = table.loc[keep].reset_index(drop=True)
    new_spectrum = Spectrum(table=new_table, metadata=deriv.metadata)

    total = int(len(table))
    removed = int(dup.sum())
    stats = {
        "total": total,
        "removed": removed,
        "kept": total - removed,
        "removed_frac": (removed / total) if total else 0.0,
        "ppm_tol": float(ppm_tol),
        "one_to_one": bool(one_to_one),
        "src_peaks": src_n,
    }
    logger.debug(
        "Вычитание исходника (%s): удалено %d из %d пиков (%.1f %%) при %g ppm",
        "1:1" if one_to_one else "все совпадения",
        removed,
        total,
        stats["removed_frac"] * 100,
        ppm_tol,
    )
    return new_spectrum, stats
