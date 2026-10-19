"""uint64-упаковка брутто-формул CHNOSPHal (C, H, N, O, S, P, F, Cl, Br, I).

Отличие от прежнего формата (``_packed.py``, uint32 CHNOSP с выводом H из
границ блока): здесь водород и галогены хранятся **явно**, поэтому одна
запись = полная брутто-формула без восстановления по контексту.

Раскладка битов (всего 55 из 64 — есть запас):

======  ======  =====
поле    бит     сдвиг
======  ======  =====
C       8       0
H       8       8
N       7       16
O       7       23
S       6       30
P       7       36
F       3       43
Cl      3       46
Br      3       49
I       3       52
======  ======  =====

Диапазоны: C, H <= 255; N, O, P <= 127; S <= 63; F..I <= 7.

Массы — в целочисленном масштабе 1e11 Да (как в ``_packed.MASS_SCALE``).
"""

# ВНИМАНИЕ: модуль НЕ ИСПОЛЬЗУЕТСЯ текущей версией программы.
# Это формат записей для базы формул v3 (явные H и галогены); он
# понадобится при сборке такой базы (tools/diagnostics/build_halogen_db.py).
# В сборку exe не попадает, так как никем не импортируется.


from __future__ import annotations

from ._packed import MASS_SCALE

#: Элементы в порядке упаковки (H и галогены — явно).
ELEMENTS64 = ("C", "H", "N", "O", "S", "P", "F", "Cl", "Br", "I")

#: (сдвиг, ширина) для каждого элемента.
_FIELDS: dict[str, tuple[int, int]] = {
    "C": (0, 8),
    "H": (8, 8),
    "N": (16, 7),
    "O": (23, 7),
    "S": (30, 6),
    "P": (36, 7),
    "F": (43, 3),
    "Cl": (46, 3),
    "Br": (49, 3),
    "I": (52, 3),
}

#: Атомные моноизотопные массы в масштабе 1e11 (целые).
MASS_U64: dict[str, int] = {
    "C": 1_200_000_000_000,
    "H": 100_782_503_223,
    "N": 1_400_307_400_443,
    "O": 1_599_491_461_957,
    "S": 3_197_207_117_440,
    "P": 3_097_376_199_842,
    "F": 1_899_840_316_273,
    "Cl": 3_496_885_268_200,
    "Br": 7_891_833_760_000,
    "I": 12_690_447_190_000,
}

MASS64: dict[str, float] = {el: u / MASS_SCALE for el, u in MASS_U64.items()}

_MAX = {el: (1 << width) - 1 for el, (_, width) in _FIELDS.items()}


def pack_formula64(counts: dict[str, int]) -> int:
    """Упаковать брутто-формулу в uint64.

    Parameters
    ----------
    counts : dict
        Количества атомов по элементам (отсутствующие = 0).

    Raises
    ------
    ValueError
        Если количество выходит за отведённые биты.
    """
    code = 0
    for el, (shift, width) in _FIELDS.items():
        n = int(counts.get(el, 0))
        if n < 0 or n > _MAX[el]:
            raise ValueError(
                f"{el}={n} не помещается в {width} бит (максимум {_MAX[el]})"
            )
        code |= n << shift
    return code


def unpack_formula64(code: int) -> dict[str, int]:
    """Распаковать uint64 в словарь количеств (без нулевых элементов)."""
    counts: dict[str, int] = {}
    for el, (shift, width) in _FIELDS.items():
        n = (code >> shift) & ((1 << width) - 1)
        if n:
            counts[el] = n
    return counts


def exact_mass_u64(code: int) -> int:
    """Моноизотопная масса в единицах 1e-11 Да."""
    total = 0
    for el, (shift, width) in _FIELDS.items():
        n = (code >> shift) & ((1 << width) - 1)
        if n:
            total += n * MASS_U64[el]
    return total


def exact_mass64(code: int) -> float:
    """Моноизотопная масса в Да."""
    return exact_mass_u64(code) / MASS_SCALE


def dbe64(code: int) -> float:
    """DBE = (2C + 2 + N + P - H - X) / 2, где X = F + Cl + Br + I."""
    c = (code >> 0) & _MAX["C"]
    h = (code >> 8) & _MAX["H"]
    n = (code >> 16) & _MAX["N"]
    p = (code >> 36) & _MAX["P"]
    x = sum((code >> _FIELDS[el][0]) & _MAX[el] for el in ("F", "Cl", "Br", "I"))
    return (2 * c + 2 + n + p - h - x) / 2.0


def is_valid_closed_shell64(code: int) -> bool:
    """Проверка Льюиса: целочисленный неотрицательный DBE."""
    c = (code >> 0) & _MAX["C"]
    h = (code >> 8) & _MAX["H"]
    n = (code >> 16) & _MAX["N"]
    p = (code >> 36) & _MAX["P"]
    x = sum((code >> _FIELDS[el][0]) & _MAX[el] for el in ("F", "Cl", "Br", "I"))
    numerator = 2 * c + 2 + n + p - h - x
    return numerator >= 0 and numerator % 2 == 0


def formula_to_string64(code: int) -> str:
    """Строка формулы в порядке Хилла (C, H, далее по алфавиту)."""
    counts = unpack_formula64(code)
    if not counts.get("C"):
        # Без углерода — алфавитный порядок всех элементов
        return "".join(
            el + (str(counts[el]) if counts[el] > 1 else "") for el in sorted(counts)
        )
    order = ["C", "H"] + sorted(el for el in counts if el not in ("C", "H"))
    return "".join(
        el + (str(counts[el]) if counts[el] > 1 else "")
        for el in order
        if counts.get(el)
    )


def halogen_counts64(code: int) -> dict[str, int]:
    """Количества галогенов в записи."""
    return {
        el: (code >> _FIELDS[el][0]) & _MAX[el]
        for el in ("F", "Cl", "Br", "I")
        if (code >> _FIELDS[el][0]) & _MAX[el]
    }


def halogen_total64(code: int) -> int:
    """Суммарное число атомов галогенов."""
    return sum(halogen_counts64(code).values())


# ── Композиции галогенов (шарды) ────────────────────────────────────────────
def halogen_shards(max_atoms: int = 5) -> list[tuple[tuple[str, int], ...]]:
    """Все композиции галогенов до ``max_atoms`` (мультимножества над F..I).

    Каждая композиция — кортеж пар ``(элемент, количество)``; порядок
    стабильный (F, Cl, Br, I). Используется как список шардов базы.
    """
    import itertools

    elements = ("F", "Cl", "Br", "I")
    shards: list[tuple[tuple[str, int], ...]] = []
    for size in range(1, max_atoms + 1):
        for combo in itertools.combinations_with_replacement(elements, size):
            collapsed = tuple(
                (el, combo.count(el)) for el in elements if combo.count(el)
            )
            if collapsed not in shards:
                shards.append(collapsed)
    return shards


def shard_name(combo: tuple[tuple[str, int], ...]) -> str:
    """Имя шарда: ``Cl1Br1``, ``F2`` и т. п."""
    return "".join(f"{el}{n}" if n > 1 else el for el, n in combo) or "CHNOSP"
