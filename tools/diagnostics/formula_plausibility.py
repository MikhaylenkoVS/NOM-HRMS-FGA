"""Экспериментальная NOM-проверка правдоподобия брутто-формулы.

Не входит в рабочий пайплайн: используется только диагностикой
(конфликты, отчёты). В `src` оставлены только проверки, которые реально
применяются программой.
"""

from __future__ import annotations

from functools import lru_cache

from src.core.domain.molecule import parse_formula
from src.core.spectrum._formula_check import counts_valid

NOM_MAX_S = 2
NOM_MAX_P = 1
NOM_MAX_N = 5
NOM_HC = (0.3, 2.5)
NOM_OC_MAX = 1.2
NOM_NC_MAX = 0.5
NOM_SC_MAX = 0.1
NOM_PC_MAX = 0.05


@lru_cache(maxsize=200_000)
def is_plausible_brutto(brutto: str) -> tuple[bool, str]:
    """Правдоподобна ли брутто-формула для природного органического вещества."""
    try:
        counts = parse_formula(str(brutto))
    except Exception:
        return False, "не разобрана формула"
    return is_plausible_nom(counts)


def is_plausible_nom(counts: dict[str, int]) -> tuple[bool, str]:
    """Проверить CHNOPS-правдоподобие состава. Возвращает (ok, причина)."""
    if any(int(counts.get(el, 0)) > 0 for el in ("F", "Cl", "Br", "I")):
        return False, "галогены"
    if int(counts.get("S", 0)) > NOM_MAX_S:
        return False, f"S > {NOM_MAX_S}"
    if int(counts.get("P", 0)) > NOM_MAX_P:
        return False, f"P > {NOM_MAX_P}"
    if int(counts.get("N", 0)) > NOM_MAX_N:
        return False, f"N > {NOM_MAX_N}"

    ok, reason = counts_valid(counts)
    if not ok:
        return False, reason

    c = int(counts.get("C", 0))
    h = int(counts.get("H", 0))
    o = int(counts.get("O", 0))
    n = int(counts.get("N", 0))
    s = int(counts.get("S", 0))
    p = int(counts.get("P", 0))
    if c < 1 or h < 1:
        return False, "C/H < 1"
    if not (NOM_HC[0] <= h / c <= NOM_HC[1]):
        return False, "H/C вне диапазона"
    if o / c > NOM_OC_MAX:
        return False, "O/C слишком велико"
    if n / c > NOM_NC_MAX:
        return False, "N/C слишком велико"
    if s / c > NOM_SC_MAX:
        return False, "S/C слишком велико"
    if p / c > NOM_PC_MAX:
        return False, "P/C слишком велико"
    return True, "ok"
