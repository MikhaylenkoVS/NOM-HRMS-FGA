"""Carbon-skeleton fragment factories (chains, carbon rings, condensed aromatics)."""

from ._fragment import MoleculeFragment


def create_methylene():
    return MoleculeFragment("methylene", {"C": 1}, 0, ["C"], [], [0, 0])


def create_ethylene():
    return MoleculeFragment("ethylene", {"C": 2}, 0, ["C", "C"], [(0, 1, 1)], [0, 1])


def create_propylene():
    return MoleculeFragment(
        "propylene", {"C": 3}, 0, ["C"] * 3, [(0, 1, 1), (1, 2, 1)], [0, 2]
    )


def create_alkene():
    return MoleculeFragment("alkene", {"C": 2}, 1, ["C", "C"], [(0, 1, 2)], [0, 1])


def create_propenyl():
    return MoleculeFragment(
        "propenyl", {"C": 3}, 1, ["C"] * 3, [(0, 1, 2), (1, 2, 1)], [0, 2]
    )


def create_alkyne():
    return MoleculeFragment("alkyne", {"C": 2}, 2, ["C", "C"], [(0, 1, 3)], [0, 1])


def create_propynyl():
    return MoleculeFragment(
        "propynyl", {"C": 3}, 2, ["C"] * 3, [(0, 1, 3), (1, 2, 1)], [0, 2]
    )


# === 5-ЧЛЕННЫЕ УГЛЕРОДНЫЕ ЦИКЛЫ ===
def create_cyclopentane():
    return MoleculeFragment(
        "cyclopentane",
        {"C": 5},
        1,
        ["C"] * 5,
        [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 1)],
        list(range(5)),
    )


def create_cyclopentene():
    return MoleculeFragment(
        "cyclopentene",
        {"C": 5},
        2,
        ["C"] * 5,
        [(0, 1, 2), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 1)],
        list(range(5)),
    )


def create_cyclopentadiene():
    return MoleculeFragment(
        "cyclopentadiene",
        {"C": 5},
        3,
        ["C"] * 5,
        [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 4, 1), (4, 0, 1)],
        list(range(5)),
    )


# === 6-ЧЛЕННЫЕ УГЛЕРОДНЫЕ ЦИКЛЫ ===
def create_cyclohexane():
    return MoleculeFragment(
        "cyclohexane",
        {"C": 6},
        1,
        ["C"] * 6,
        [(i, (i + 1) % 6, 1) for i in range(6)],
        list(range(6)),
    )


def create_cyclohexene():
    return MoleculeFragment(
        "cyclohexene",
        {"C": 6},
        2,
        ["C"] * 6,
        [(0, 1, 2)] + [(i, (i + 1) % 6, 1) for i in range(1, 6)],
        list(range(6)),
    )


def create_cyclohexadiene():
    return MoleculeFragment(
        "cyclohexadiene",
        {"C": 6},
        3,
        ["C"] * 6,
        [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 4, 1), (4, 5, 1), (5, 0, 1)],
        list(range(6)),
    )


def create_benzene():
    return MoleculeFragment(
        "benzene",
        {"C": 6},
        4,
        ["C"] * 6,
        [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 4, 1), (4, 5, 2), (5, 0, 1)],
        list(range(6)),
    )


# === 8-ЧЛЕННЫЕ УГЛЕРОДНЫЕ ЦИКЛЫ ===
def create_cyclooctane():
    return MoleculeFragment(
        "cyclooctane",
        {"C": 8},
        1,
        ["C"] * 8,
        [(i, (i + 1) % 8, 1) for i in range(8)],
        list(range(8)),
    )


def create_cyclooctene():
    return MoleculeFragment(
        "cyclooctene",
        {"C": 8},
        2,
        ["C"] * 8,
        [(0, 1, 2)] + [(i, (i + 1) % 8, 1) for i in range(1, 8)],
        list(range(8)),
    )


def create_cyclooctadiene():
    return MoleculeFragment(
        "cyclooctadiene",
        {"C": 8},
        3,
        ["C"] * 8,
        [
            (0, 1, 2),
            (1, 2, 1),
            (2, 3, 2),
            (3, 4, 1),
            (4, 5, 1),
            (5, 6, 1),
            (6, 7, 1),
            (7, 0, 1),
        ],
        list(range(8)),
    )


def create_cyclooctatriene():
    return MoleculeFragment(
        "cyclooctatriene",
        {"C": 8},
        4,
        ["C"] * 8,
        [
            (0, 1, 2),
            (1, 2, 1),
            (2, 3, 2),
            (3, 4, 1),
            (4, 5, 2),
            (5, 6, 1),
            (6, 7, 1),
            (7, 0, 1),
        ],
        list(range(8)),
    )


def create_cyclooctatetraene():
    return MoleculeFragment(
        "cyclooctatetraene",
        {"C": 8},
        5,
        ["C"] * 8,
        [
            (0, 1, 2),
            (1, 2, 1),
            (2, 3, 2),
            (3, 4, 1),
            (4, 5, 2),
            (5, 6, 1),
            (6, 7, 2),
            (7, 0, 1),
        ],
        list(range(8)),
    )


# === 10-ЧЛЕННЫЕ УГЛЕРОДНЫЕ ЦИКЛЫ ===
def create_cyclodecane():
    return MoleculeFragment(
        "cyclodecane",
        {"C": 10},
        1,
        ["C"] * 10,
        [(i, (i + 1) % 10, 1) for i in range(10)],
        list(range(10)),
    )


def create_cyclodecene():
    return MoleculeFragment(
        "cyclodecene",
        {"C": 10},
        2,
        ["C"] * 10,
        [(0, 1, 2)] + [(i, (i + 1) % 10, 1) for i in range(1, 10)],
        list(range(10)),
    )


def create_cyclodecadiene():
    return MoleculeFragment(
        "cyclodecadiene",
        {"C": 10},
        3,
        ["C"] * 10,
        [(0, 1, 2), (2, 3, 2)]
        + [(i, (i + 1) % 10, 1) for i in [1] + list(range(3, 10))],
        list(range(10)),
    )


def create_cyclodecatriene():
    return MoleculeFragment(
        "cyclodecatriene",
        {"C": 10},
        4,
        ["C"] * 10,
        [(0, 1, 2), (2, 3, 2), (4, 5, 2)]
        + [(i, (i + 1) % 10, 1) for i in [1, 3] + list(range(5, 10))],
        list(range(10)),
    )


def create_cyclodecatetraene():
    return MoleculeFragment(
        "cyclodecatetraene",
        {"C": 10},
        5,
        ["C"] * 10,
        [(0, 1, 2), (2, 3, 2), (4, 5, 2), (6, 7, 2)]
        + [(i, (i + 1) % 10, 1) for i in [1, 3, 5] + list(range(7, 10))],
        list(range(10)),
    )


def create_cyclodecapentaene():
    return MoleculeFragment(
        "cyclodecapentaene",
        {"C": 10},
        6,
        ["C"] * 10,
        [(i, (i + 1) % 10, 2 if i % 2 == 0 else 1) for i in range(10)],
        list(range(10)),
    )


# === КОНДЕНСИРОВАННЫЕ СИСТЕМЫ ===
def create_naphthalene():
    return MoleculeFragment(
        "naphthalene",
        {"C": 10},
        7,
        ["C"] * 10,
        [
            (0, 1, 2),
            (1, 2, 1),
            (2, 3, 2),
            (3, 4, 1),
            (4, 5, 2),
            (5, 6, 1),
            (6, 7, 2),
            (7, 8, 1),
            (8, 9, 2),
            (9, 0, 1),
            (4, 9, 1),
        ],
        [0, 1, 2, 3, 5, 6, 7, 8],
    )


def create_anthracene():
    return MoleculeFragment(
        "anthracene",
        {"C": 14},
        10,
        ["C"] * 14,
        [
            (0, 1, 2),
            (1, 2, 1),
            (2, 3, 2),
            (3, 4, 1),
            (4, 5, 2),
            (5, 6, 1),
            (6, 7, 2),
            (7, 8, 1),
            (8, 9, 2),
            (9, 10, 1),
            (10, 11, 2),
            (11, 12, 1),
            (12, 13, 2),
            (13, 0, 1),
            (4, 13, 1),
            (8, 12, 1),
        ],
        [0, 1, 2, 3, 5, 6, 7, 9, 10, 11],
    )
