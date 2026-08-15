"""Heteroatom-containing fragment factories (heterocycles, functional groups, acyclic N)."""

from ._fragment import MoleculeFragment


# === 5-ЧЛЕННЫЕ ГЕТЕРОЦИКЛЫ С АЗОТОМ ===
def create_pyrrolidine():
    return MoleculeFragment(
        "pyrrolidine",
        {"C": 4, "N": 1},
        1,
        ["C", "C", "C", "C", "N"],
        [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 1)],
        list(range(5)),
    )


def create_pyrroline():
    return MoleculeFragment(
        "pyrroline",
        {"C": 4, "N": 1},
        2,
        ["C", "C", "C", "C", "N"],
        [(0, 1, 2), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 1)],
        list(range(5)),
    )


def create_pyrrole():
    return MoleculeFragment(
        "pyrrole",
        {"C": 4, "N": 1},
        3,
        ["C", "C", "C", "C", "N"],
        [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 4, 1), (4, 0, 1)],
        list(range(5)),
    )


def create_imidazole():
    return MoleculeFragment(
        "imidazole",
        {"C": 3, "N": 2},
        3,
        ["C", "N", "C", "N", "C"],
        [(0, 1, 1), (1, 2, 2), (2, 3, 1), (3, 4, 2), (4, 0, 1)],
        list(range(5)),
    )


# === 5-ЧЛЕННЫЕ ГЕТЕРОЦИКЛЫ С КИСЛОРОДОМ ===
def create_tetrahydrofuran():
    return MoleculeFragment(
        "tetrahydrofuran",
        {"C": 4, "O": 1},
        1,
        ["C", "C", "C", "C", "O"],
        [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 1)],
        [0, 1, 2, 3],
    )


def create_dihydrofuran():
    return MoleculeFragment(
        "dihydrofuran",
        {"C": 4, "O": 1},
        2,
        ["C", "C", "C", "C", "O"],
        [(0, 1, 2), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 1)],
        [0, 1, 2, 3],
    )


def create_furan():
    return MoleculeFragment(
        "furan",
        {"C": 4, "O": 1},
        3,
        ["C", "C", "C", "C", "O"],
        [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 4, 1), (4, 0, 1)],
        [0, 1, 2, 3],
    )


# === 6-ЧЛЕННЫЕ ГЕТЕРОЦИКЛЫ С АЗОТОМ ===
def create_piperidine():
    return MoleculeFragment(
        "piperidine",
        {"C": 5, "N": 1},
        1,
        ["C"] * 5 + ["N"],
        [(i, (i + 1) % 6, 1) for i in range(6)],
        list(range(6)),
    )


def create_tetrahydropyridine():
    return MoleculeFragment(
        "tetrahydropyridine",
        {"C": 5, "N": 1},
        2,
        ["C"] * 5 + ["N"],
        [(0, 1, 2)] + [(i, (i + 1) % 6, 1) for i in range(1, 6)],
        list(range(6)),
    )


def create_dihydropyridine():
    return MoleculeFragment(
        "dihydropyridine",
        {"C": 5, "N": 1},
        3,
        ["C"] * 5 + ["N"],
        [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 4, 1), (4, 5, 1), (5, 0, 1)],
        list(range(6)),
    )


def create_pyridine():
    return MoleculeFragment(
        "pyridine",
        {"C": 5, "N": 1},
        4,
        ["C"] * 5 + ["N"],
        [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 4, 1), (4, 5, 2), (5, 0, 1)],
        list(range(6)),
    )


def create_pyrimidine():
    return MoleculeFragment(
        "pyrimidine",
        {"C": 4, "N": 2},
        4,
        ["C", "N", "C", "N", "C", "C"],
        [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 4, 1), (4, 5, 2), (5, 0, 1)],
        list(range(6)),
    )


def create_pyrazine():
    return MoleculeFragment(
        "pyrazine",
        {"C": 4, "N": 2},
        4,
        ["C", "N", "C", "C", "N", "C"],
        [(0, 1, 2), (1, 2, 1), (2, 3, 2), (3, 4, 1), (4, 5, 2), (5, 0, 1)],
        list(range(6)),
    )


# === 6-ЧЛЕННЫЕ ГЕТЕРОЦИКЛЫ С КИСЛОРОДОМ ===
def create_tetrahydropyran():
    return MoleculeFragment(
        "tetrahydropyran",
        {"C": 5, "O": 1},
        1,
        ["C"] * 5 + ["O"],
        [(i, (i + 1) % 6, 1) for i in range(6)],
        [0, 1, 2, 3, 4],
    )


def create_dihydropyran():
    return MoleculeFragment(
        "dihydropyran",
        {"C": 5, "O": 1},
        2,
        ["C"] * 5 + ["O"],
        [(0, 1, 2)] + [(i, (i + 1) % 6, 1) for i in range(1, 6)],
        [0, 1, 2, 3, 4],
    )


# === ФУНКЦИОНАЛЬНЫЕ ГРУППЫ ===
def create_cooh():
    return MoleculeFragment(
        "cooh", {"C": 1, "O": 2}, 1, ["C", "O", "O"], [(0, 1, 2), (0, 2, 1)], [0]
    )


def create_oh():
    return MoleculeFragment("oh", {"O": 1}, 0, ["O"], [], [0])


def create_cho():
    return MoleculeFragment("cho", {"C": 1, "O": 1}, 1, ["C", "O"], [(0, 1, 2)], [0])


def create_co():
    return MoleculeFragment("co", {"C": 1, "O": 1}, 1, ["C", "O"], [(0, 1, 2)], [0, 0])


def create_coo():
    return MoleculeFragment(
        "coo", {"C": 1, "O": 2}, 1, ["C", "O", "O"], [(0, 1, 2), (0, 2, 1)], [0, 2]
    )


def create_o_ether():
    return MoleculeFragment("o_ether", {"O": 1}, 0, ["O"], [], [0, 0])


def create_nh2():
    return MoleculeFragment("nh2", {"N": 1}, 0, ["N"], [], [0])


def create_nh():
    return MoleculeFragment("nh", {"N": 1}, 0, ["N"], [], [0, 0])


def create_n_tertiary():
    return MoleculeFragment("n_tertiary", {"N": 1}, 0, ["N"], [], [0, 0, 0])


def create_no2():
    return MoleculeFragment(
        "no2", {"N": 1, "O": 2}, 1, ["N", "O", "O"], [(0, 1, 2), (0, 2, 2)], [0]
    )


def create_cn():
    return MoleculeFragment("cn", {"C": 1, "N": 1}, 2, ["C", "N"], [(0, 1, 3)], [0])


def create_conh2():
    return MoleculeFragment(
        "conh2",
        {"C": 1, "O": 1, "N": 1},
        1,
        ["C", "O", "N"],
        [(0, 1, 2), (0, 2, 1)],
        [0],
    )


def create_sh():
    return MoleculeFragment("sh", {"S": 1}, 0, ["S"], [], [0])


def create_s_sulfide():
    return MoleculeFragment("s_sulfide", {"S": 1}, 0, ["S"], [], [0, 0])


def create_so2():
    return MoleculeFragment(
        "so2", {"S": 1, "O": 2}, 0, ["S", "O", "O"], [(0, 1, 2), (0, 2, 2)], [0, 0]
    )


def create_so3h():
    return MoleculeFragment(
        "so3h",
        {"S": 1, "O": 3},
        0,
        ["S", "O", "O", "O"],
        [(0, 1, 2), (0, 2, 2), (0, 3, 1)],
        [0],
    )


def create_f():
    return MoleculeFragment("f", {"F": 1}, 0, ["F"], [], [0])


def create_cl():
    return MoleculeFragment("cl", {"Cl": 1}, 0, ["Cl"], [], [0])


def create_br():
    return MoleculeFragment("br", {"Br": 1}, 0, ["Br"], [], [0])


def create_i():
    return MoleculeFragment("i", {"I": 1}, 0, ["I"], [], [0])


# ── Ациклические азот-содержащие фрагменты ─────────────────────────────────


def create_aminomethyl():
    """CH2-NH-  (первичный амин, 2 точки присоединения)."""
    return MoleculeFragment(
        "aminomethyl",
        {"C": 1, "N": 1},
        0,
        ["C", "N"],
        [(0, 1, 1)],
        [0, 1],
    )


def create_amide_link():
    """-CO-NH-  (амидный мостик, 2 точки присоединения)."""
    return MoleculeFragment(
        "amide_link",
        {"C": 1, "N": 1, "O": 1},
        1,
        ["C", "O", "N"],
        [(0, 1, 2), (0, 2, 1)],
        [0, 2],
    )


def create_ethylamine():
    """-CH2-CH2-NH-  (этиламиновый мостик, 2 точки)."""
    return MoleculeFragment(
        "ethylamine",
        {"C": 2, "N": 1},
        0,
        ["C", "C", "N"],
        [(0, 1, 1), (1, 2, 1)],
        [0, 2],
    )
