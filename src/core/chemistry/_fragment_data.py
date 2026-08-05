"""Fragment library and functional groups data.

Pure data dicts — no MoleculeFragment instances.
ALL_FRAGMENTS (which requires factory functions) stays in fragments.py.
"""

FRAGMENT_LIBRARY = {
    # === АЦИКЛИЧЕСКИЕ ФРАГМЕНТЫ ===
    # Одинарные связи C-C
    "methylene": {
        "heavy_formula": {"C": 1},
        "ihd": 0,
        "attachment_points": 2,
        "description": "CH2",
    },
    # Двойные связи C=C
    "alkene": {
        "heavy_formula": {"C": 2},
        "ihd": 1,
        "attachment_points": 2,
        "description": "CH=CH",
    },
    "propenyl": {
        "heavy_formula": {"C": 3},
        "ihd": 1,
        "attachment_points": 2,
        "description": "CH=CH-CH2",
    },
    # Тройные связи C≡C
    # === 5-ЧЛЕННЫЕ УГЛЕРОДНЫЕ ЦИКЛЫ ===
    "cyclopentane": {
        "heavy_formula": {"C": 5},
        "ihd": 1,
        "attachment_points": 5,
        "description": "Циклопентан",
    },
    "cyclopentene": {
        "heavy_formula": {"C": 5},
        "ihd": 2,
        "attachment_points": 5,
        "description": "Циклопентен",
    },
    "cyclopentadiene": {
        "heavy_formula": {"C": 5},
        "ihd": 3,
        "attachment_points": 5,
        "description": "Циклопентадиен",
    },
    # === 6-ЧЛЕННЫЕ УГЛЕРОДНЫЕ ЦИКЛЫ ===
    "cyclohexane": {
        "heavy_formula": {"C": 6},
        "ihd": 1,
        "attachment_points": 6,
        "description": "Циклогексан",
    },
    "cyclohexene": {
        "heavy_formula": {"C": 6},
        "ihd": 2,
        "attachment_points": 6,
        "description": "Циклогексен",
    },
    "cyclohexadiene": {
        "heavy_formula": {"C": 6},
        "ihd": 3,
        "attachment_points": 6,
        "description": "Циклогексадиен",
    },
    "benzene": {
        "heavy_formula": {"C": 6},
        "ihd": 4,
        "attachment_points": 6,
        "description": "Бензол",
    },
    # === 8-ЧЛЕННЫЕ УГЛЕРОДНЫЕ ЦИКЛЫ ===
    # === 10-ЧЛЕННЫЕ УГЛЕРОДНЫЕ ЦИКЛЫ ===
    # === КОНДЕНСИРОВАННЫЕ СИСТЕМЫ ===
    "naphthalene": {
        "heavy_formula": {"C": 10},
        "ihd": 7,
        "attachment_points": 8,
        "description": "Нафталин",
    },
    "anthracene": {
        "heavy_formula": {"C": 14},
        "ihd": 10,
        "attachment_points": 10,
        "description": "Антрацен",
    },
    # === 5-ЧЛЕННЫЕ ГЕТЕРОЦИКЛЫ С АЗОТОМ ===
    "pyrrolidine": {
        "heavy_formula": {"C": 4, "N": 1},
        "ihd": 1,
        "attachment_points": 5,
        "description": "Пирролидин",
    },
    "pyrroline": {
        "heavy_formula": {"C": 4, "N": 1},
        "ihd": 2,
        "attachment_points": 5,
        "description": "Пирролин",
    },
    "pyrrole": {
        "heavy_formula": {"C": 4, "N": 1},
        "ihd": 3,
        "attachment_points": 5,
        "description": "Пиррол",
    },
    "imidazole": {
        "heavy_formula": {"C": 3, "N": 2},
        "ihd": 3,
        "attachment_points": 5,
        "description": "Имидазол",
    },
    # === 5-ЧЛЕННЫЕ ГЕТЕРОЦИКЛЫ С КИСЛОРОДОМ ===
    "tetrahydrofuran": {
        "heavy_formula": {"C": 4, "O": 1},
        "ihd": 1,
        "attachment_points": 4,
        "description": "Тетрагидрофуран",
    },
    "dihydrofuran": {
        "heavy_formula": {"C": 4, "O": 1},
        "ihd": 2,
        "attachment_points": 4,
        "description": "Дигидрофуран",
    },
    "furan": {
        "heavy_formula": {"C": 4, "O": 1},
        "ihd": 3,
        "attachment_points": 4,
        "description": "Фуран",
    },
    # === 6-ЧЛЕННЫЕ ГЕТЕРОЦИКЛЫ С АЗОТОМ ===
    "piperidine": {
        "heavy_formula": {"C": 5, "N": 1},
        "ihd": 1,
        "attachment_points": 6,
        "description": "Пиперидин",
    },
    "tetrahydropyridine": {
        "heavy_formula": {"C": 5, "N": 1},
        "ihd": 2,
        "attachment_points": 6,
        "description": "Тетрагидропиридин",
    },
    "dihydropyridine": {
        "heavy_formula": {"C": 5, "N": 1},
        "ihd": 3,
        "attachment_points": 6,
        "description": "Дигидропиридин",
    },
    "pyridine": {
        "heavy_formula": {"C": 5, "N": 1},
        "ihd": 4,
        "attachment_points": 6,
        "description": "Пиридин",
    },
    "pyrimidine": {
        "heavy_formula": {"C": 4, "N": 2},
        "ihd": 4,
        "attachment_points": 6,
        "description": "Пиримидин",
    },
    "pyrazine": {
        "heavy_formula": {"C": 4, "N": 2},
        "ihd": 4,
        "attachment_points": 6,
        "description": "Пиразин",
    },
    # === 6-ЧЛЕННЫЕ ГЕТЕРОЦИКЛЫ С КИСЛОРОДОМ ===
    "tetrahydropyran": {
        "heavy_formula": {"C": 5, "O": 1},
        "ihd": 1,
        "attachment_points": 5,
        "description": "Тетрагидропиран",
    },
    "dihydropyran": {
        "heavy_formula": {"C": 5, "O": 1},
        "ihd": 2,
        "attachment_points": 5,
        "description": "Дигидропиран",
    },
    # === АЦИКЛИЧЕСКИЕ АЗОТ-СОДЕРЖАЩИЕ ФРАГМЕНТЫ ===
    "aminomethyl": {
        "heavy_formula": {"C": 1, "N": 1},
        "ihd": 0,
        "attachment_points": 2,
        "description": "CH2-NH (первичный амин)",
    },
    "amide_link": {
        "heavy_formula": {"C": 1, "N": 1, "O": 1},
        "ihd": 1,
        "attachment_points": 2,
        "description": "CO-NH (амидный линкер)",
    },
    "ethylamine": {
        "heavy_formula": {"C": 2, "N": 1},
        "ihd": 0,
        "attachment_points": 2,
        "description": "CH2-CH2-NH (этиламиновый мостик)",
    },
}
# === ФУНКЦИОНАЛЬНЫЕ ГРУППЫ ===

FUNCTIONAL_GROUPS = {
    "cooh": {
        "heavy_formula": {"C": 1, "O": 2},
        "ihd": 1,
        "description": "Карбоксильная группа",
    },
    "oh": {"heavy_formula": {"O": 1}, "ihd": 0, "description": "Гидроксильная группа"},
    "cho": {
        "heavy_formula": {"C": 1, "O": 1},
        "ihd": 1,
        "description": "Альдегидная группа",
    },
    "co": {
        "heavy_formula": {"C": 1, "O": 1},
        "ihd": 1,
        "description": "Кетонная группа",
    },
    "coo": {
        "heavy_formula": {"C": 1, "O": 2},
        "ihd": 1,
        "description": "Сложноэфирная группа",
    },
    "o_ether": {
        "heavy_formula": {"O": 1},
        "ihd": 0,
        "description": "Простая эфирная связь",
    },
    "nh2": {"heavy_formula": {"N": 1}, "ihd": 0, "description": "Аминогруппа"},
    "nh": {"heavy_formula": {"N": 1}, "ihd": 0, "description": "Вторичная аминогруппа"},
    "n_tertiary": {
        "heavy_formula": {"N": 1},
        "ihd": 0,
        "description": "Третичная аминогруппа",
    },
    "no2": {"heavy_formula": {"N": 1, "O": 2}, "ihd": 1, "description": "Нитрогруппа"},
    "cn": {
        "heavy_formula": {"C": 1, "N": 1},
        "ihd": 2,
        "description": "Нитрильная группа",
    },
    "conh2": {
        "heavy_formula": {"C": 1, "O": 1, "N": 1},
        "ihd": 1,
        "description": "Амидная группа",
    },
    "sh": {"heavy_formula": {"S": 1}, "ihd": 0, "description": "Тиольная группа"},
    "s_sulfide": {
        "heavy_formula": {"S": 1},
        "ihd": 0,
        "description": "Сульфидная связь",
    },
    "so2": {
        "heavy_formula": {"S": 1, "O": 2},
        "ihd": 0,
        "description": "Сульфонильная группа",
    },
    "so3h": {
        "heavy_formula": {"S": 1, "O": 3},
        "ihd": 0,
        "description": "Сульфоновая кислота",
    },
    "f": {"heavy_formula": {"F": 1}, "ihd": 0, "description": "Фтор"},
    "cl": {"heavy_formula": {"Cl": 1}, "ihd": 0, "description": "Хлор"},
    "br": {"heavy_formula": {"Br": 1}, "ihd": 0, "description": "Бром"},
    "i": {"heavy_formula": {"I": 1}, "ihd": 0, "description": "Йод"},
}


# === АЦИКЛИЧЕСКИЕ ФРАГМЕНТЫ ===
