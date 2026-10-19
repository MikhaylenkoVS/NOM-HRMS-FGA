"""Химическая проверка формулы продукта дериватизации (P2).

Для исходной формулы F0 и n модифицированных групп продукт имеет состав
F0 + n·ΔF. Известны точные изменения (дейтерий учитывается в массе, но не в
элементном балансе — в базе элементов его нет):

  * CD3 (метилирование COOH):      ΔF = +1 C, +2 H, 0 O,  DBE не меняется;
  * CD3CO (ацетилирование OH):     ΔF = +2 C, +2 H, +1 O, DBE +1 за группу.

Проверки:
  * число групп не превышает число атомов O (каждая группа требует кислорода);
  * H ≤ 2C + 2 + N + P (валентность);
  * DBE ≥ 0;
  * число групп не больше числа гетероатомов, способных нести группу.

Модуль не заменяет поиск по массе, а отсекает химически невозможные варианты,
которые могли совпасть по m/z.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from src.core.domain.molecule import parse_formula


@dataclass(frozen=True)
class DerivatizationGroup:
    """Чистое изменение состава на одну группу (дейтерий не учитывается)."""

    name: str
    dc: int
    dh: int
    do: int
    d_dbe: int


CD3 = DerivatizationGroup("cd3", dc=1, dh=2, do=0, d_dbe=0)
CD3CO = DerivatizationGroup("cd3co", dc=2, dh=2, do=1, d_dbe=1)
GROUPS = {"cd3": CD3, "cd3co": CD3CO}


def product_counts(
    counts: dict[str, int], n_groups: int, group: DerivatizationGroup
) -> dict[str, int]:
    """Состав продукта после n модификаций (тяжёлые элементы + H)."""
    out = dict(counts)
    out["C"] = out.get("C", 0) + n_groups * group.dc
    out["H"] = out.get("H", 0) + n_groups * group.dh
    out["O"] = out.get("O", 0) + n_groups * group.do
    return out


def counts_valid(
    counts: dict[str, int], *, min_o_for_groups: int = 0
) -> tuple[bool, str]:
    """Проверить валентность/DBE состава. Возвращает (ok, причина)."""
    c = int(counts.get("C", 0))
    h = int(counts.get("H", 0))
    n = int(counts.get("N", 0))
    o = int(counts.get("O", 0))
    p = int(counts.get("P", 0))
    x = sum(int(counts.get(el, 0)) for el in ("F", "Cl", "Br", "I"))

    if c < 1:
        return False, "C<1"
    if h < 0 or o < 0:
        return False, "отрицательное число атомов"
    if h > 2 * c + 2 + n + p:
        return False, "нарушена валентность (H > 2C+2+N+P)"
    dbe = (2 * c + 2 + n + p - h - x) / 2.0
    if dbe < 0:
        return False, "DBE < 0"
    if min_o_for_groups and o < min_o_for_groups:
        return False, "групп больше, чем атомов O"
    return True, "ok"


#: Пределы «правдоподобной» NOM-формулы (CHNOPS, без галогенов).
#: Используются только для разрешения конфликтов: неправдоподобная формула
#: не может претендовать на пик, но остаётся в выдаче как отдельная серия.
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
    """Правдоподобна ли брутто-формула для природного органического вещества.

    Критерий: только CHNOPS, без галогенов; S ≤ 2, P ≤ 1, N ≤ 5;
    H/C 0.3–2.5, O/C ≤ 1.2, N/C ≤ 0.5, S/C ≤ 0.1, P/C ≤ 0.05; DBE ≥ 0.
    """
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


def check_series_formula(
    counts: dict[str, int],
    n_groups: int,
    group_name: str,
    *,
    max_groups_by_oxygen: bool = True,
) -> dict:
    """Проверить, что серия из n групп химически допустима.

    Returns
    -------
    dict
        ``{ok, reason, product}``: ``ok`` — все проверки пройдены; ``product`` —
        состав последней ступени.
    """
    group = GROUPS.get(str(group_name).lower())
    if group is None:
        raise ValueError(f"неизвестная группа дериватизации: {group_name}")
    n = int(n_groups)
    if n < 0:
        return {"ok": False, "reason": " отрицательное число групп", "product": {}}

    product = product_counts(counts, n, group)
    min_o = n if max_groups_by_oxygen else 0
    ok, reason = counts_valid(product, min_o_for_groups=min_o)
    if not ok:
        return {"ok": False, "reason": reason, "product": product}

    # Каждая группа требует «своего» кислорода: n <= O исходной формулы
    if max_groups_by_oxygen and n > int(counts.get("O", 0)):
        return {
            "ok": False,
            "reason": f"групп {n} > атомов O {int(counts.get('O', 0))}",
            "product": product,
        }

    # DBE продукта должно быть неотрицательным (проверено выше) и расти
    # ожидаемым образом — это уже следствие состава, отдельная проверка не нужна.
    return {"ok": True, "reason": "ok", "product": product}
