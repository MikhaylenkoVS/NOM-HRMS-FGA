"""Fragment combination search and molecule assembly."""

from .fragments import (
    MoleculeFragment,
    FRAGMENT_LIBRARY,
    FUNCTIONAL_GROUPS,
    ALL_FRAGMENTS,
    create_cooh,
    create_oh,
)
from ..domain.molecule import add_formula


def filter_fragments(target_heavy, target_ihd, fragment_library):
    """Keep only fragments that can fit inside the target formula and IHD.

    Parameters
    ----------
    target_heavy : dict of {str: int}
        Heavy-atom element counts still available in the target.
    target_ihd : float
        Maximum allowed index of hydrogen deficiency for a fragment.
    fragment_library : dict
        Mapping of fragment name to its metadata (``heavy_formula``, ``ihd``).

    Returns
    -------
    dict
        Subset of ``fragment_library`` whose fragments do not exceed the
        target in IHD or in any element count.
    """
    filtered = {}
    for name, f in fragment_library.items():
        hf = f["heavy_formula"]
        ihd = f["ihd"]
        # отсев по IHD
        if ihd > target_ihd:
            continue
        # отсев по элементам
        bad = False
        for el, n in hf.items():
            if el not in target_heavy or n > target_heavy[el]:
                bad = True
                break
        if bad:
            continue
        filtered[name] = f
    return filtered


def find_fragment_combinations(
    target_heavy_formula,
    target_ihd,
    num_cooh=0,
    num_oh=0,
    max_bases=10,
    first_only=False,
):
    """Enumerate fragment multisets matching a target formula and IHD.

    Reserves the atoms and unsaturation contributed by the requested -COOH
    and -OH groups, then uses backtracking to find every combination of
    skeletal base fragments whose summed heavy formula and IHD exactly match
    the remainder.

    Parameters
    ----------
    target_heavy_formula : dict of {str: int}
        Heavy-atom element counts of the whole target molecule.
    target_ihd : float
        Target index of hydrogen deficiency.
    num_cooh : int, optional
        Number of carboxyl groups to place. Default 0.
    num_oh : int, optional
        Number of hydroxyl groups to place. Default 0.
    max_bases : int, optional
        Maximum total number of base fragments per combination. Default 10.

    Returns
    -------
    list of dict
        One entry per valid combination, each with keys ``bases``
        (fragment-name to count), ``cooh``, ``oh``, ``total_heavy_formula``
        and ``total_ihd``. Empty if the functional groups already exceed the
        target.
    """
    results = []

    # учёт функциональных групп
    func_heavy = {}
    func_ihd = 0
    if num_cooh:
        add_formula(func_heavy, FUNCTIONAL_GROUPS["cooh"]["heavy_formula"], num_cooh)
        func_ihd += FUNCTIONAL_GROUPS["cooh"]["ihd"] * num_cooh
    if num_oh:
        add_formula(func_heavy, FUNCTIONAL_GROUPS["oh"]["heavy_formula"], num_oh)
        func_ihd += FUNCTIONAL_GROUPS["oh"]["ihd"] * num_oh

    # скорректированная цель: что должны дать только базовые фрагменты
    base_target = target_heavy_formula.copy()
    for el, n in func_heavy.items():
        base_target[el] = base_target.get(el, 0) - n
        if base_target[el] < 0:
            # Функциональные группы «перерасходуют» атомы — пробуем без них
            if num_cooh > 0 or num_oh > 0:
                return find_fragment_combinations(
                    target_heavy_formula,
                    target_ihd,
                    num_cooh=0,
                    num_oh=0,
                    max_bases=max_bases,
                )
            return []

    base_target = {el: n for el, n in base_target.items() if n > 0}

    base_target_ihd = target_ihd - func_ihd
    if base_target_ihd < 0:
        return []

    # усечённая библиотека
    lib = filter_fragments(base_target, base_target_ihd, FRAGMENT_LIBRARY)

    # При first_only: ароматические фрагменты первыми — превью получает
    # химически осмысленные структуры с циклами
    _AROMATIC = {
        "benzene",
        "naphthalene",
        "anthracene",
        "pyridine",
        "pyrimidine",
        "pyrazine",
        "pyrrole",
        "imidazole",
        "furan",
    }
    if first_only:
        names = sorted(lib.keys(), key=lambda n: (0 if n in _AROMATIC else 1, n))
    else:
        names = sorted(lib.keys())

    def backtrack(idx, current_counts, current_heavy, current_ihd, used_bases):
        if used_bases > max_bases:
            return False
        for el, n in current_heavy.items():
            if n > base_target.get(el, 0):
                return False
        if current_ihd > base_target_ihd + 1e-6:
            return False

        if idx == len(names):
            if (
                current_heavy == base_target
                and abs(current_ihd - base_target_ihd) < 1e-6
            ):
                bases_dict = {
                    names[i]: c for i, c in enumerate(current_counts) if c > 0
                }
                results.append(
                    {
                        "bases": bases_dict,
                        "cooh": num_cooh,
                        "oh": num_oh,
                        "total_heavy_formula": target_heavy_formula.copy(),
                        "total_ihd": target_ihd,
                    }
                )
                if first_only:
                    return True
            return False

        name = names[idx]
        frag = lib[name]
        hf = frag["heavy_formula"]
        ihd_f = frag["ihd"]

        max_by_elem = float("inf")
        for el, n in hf.items():
            if n > 0:
                rem = base_target.get(el, 0) - current_heavy.get(el, 0)
                max_by_elem = min(max_by_elem, rem // n)
        if ihd_f > 0:
            max_by_ihd = int((base_target_ihd - current_ihd) // ihd_f)
            max_mult = min(max_by_elem, max_by_ihd)
        else:
            max_mult = max_by_elem

        if max_mult == float("inf"):
            max_mult = 0

        for k in range(max_mult + 1):
            new_heavy = current_heavy
            new_ihd = current_ihd
            if k > 0:
                new_heavy = current_heavy.copy()
                for el, n in hf.items():
                    new_heavy[el] = new_heavy.get(el, 0) + n * k
                new_ihd = current_ihd + ihd_f * k
            current_counts[idx] = k
            if backtrack(idx + 1, current_counts, new_heavy, new_ihd, used_bases + k):
                return True
        current_counts[idx] = 0
        return False

    current_counts = [0] * len(names)
    backtrack(0, current_counts, {}, 0.0, 0)

    return results


def assemble_molecule_from_combination(
    combination: dict, fragment_library_dict: dict = None
) -> MoleculeFragment:
    """Assemble one complete molecule from a fragment combination.

    Connects the base fragments sequentially, then attaches the requested
    -COOH and -OH groups to remaining free attachment points.

    Parameters
    ----------
    combination : dict
        A combination from :func:`find_fragment_combinations`, e.g.
        ``{'bases': {'benzene': 1}, 'cooh': 1, 'oh': 0, ...}``.
    fragment_library_dict : dict, optional
        Mapping of fragment name to factory function. Defaults to
        ``ALL_FRAGMENTS``.

    Returns
    -------
    MoleculeFragment
        The assembled molecule.

    Raises
    ------
    ValueError
        If a fragment name is unknown, the combination is empty, or there
        are not enough free attachment points to place all groups.
    """
    if fragment_library_dict is None:
        fragment_library_dict = ALL_FRAGMENTS

    # Извлекаем информацию из комбинации
    bases = combination.get("bases", {})
    num_cooh = combination.get("cooh", 0)
    num_oh = combination.get("oh", 0)

    # === ШАГ 1: Создаём базовые фрагменты ===
    base_fragments = []
    for name, count in bases.items():
        if name not in fragment_library_dict:
            raise ValueError(f"Фрагмент '{name}' не найден в библиотеке")
        for _ in range(count):
            base_fragments.append(fragment_library_dict[name]())

    if not base_fragments and not num_cooh and not num_oh:
        raise ValueError("Комбинация не содержит фрагментов")

    # === ШАГ 2: Последовательно соединяем базовые фрагменты ===
    current = []
    if base_fragments:
        current = base_fragments[0]

        for next_frag in base_fragments[1:]:
            # Находим свободные точки
            my_points = current.get_free_attachment_points()
            other_points = next_frag.get_free_attachment_points()

            if not my_points or not other_points:
                raise ValueError(
                    f"Нет свободных точек для соединения {current.name} и {next_frag.name}"
                )

            # Соединяем через первые доступные точки
            current = current.connect_to(
                next_frag, my_points[0], other_points[0], bond_order=1
            )
    if not base_fragments:
        if num_cooh > 0:
            current = create_cooh()
            num_cooh -= 1
        elif num_oh > 0:
            current = create_oh()
            num_oh -= 1
        else:
            raise ValueError("Combination contains no fragments to start with.")

    # === ШАГ 3: Добавляем COOH группы ===
    for i in range(num_cooh):
        free_points = current.get_free_attachment_points()
        if not free_points:
            raise ValueError(
                f"Не хватает свободных точек для добавления COOH группы #{i+1}"
            )

        cooh = create_cooh()
        current = current.connect_to(cooh, free_points[0], 0, bond_order=1)

    # === ШАГ 4: Добавляем OH группы ===
    for i in range(num_oh):
        free_points = current.get_free_attachment_points()
        if not free_points:
            raise ValueError(
                f"Не хватает свободных точек для добавления OH группы #{i+1}"
            )

        oh = create_oh()
        current = current.connect_to(oh, free_points[0], 0, bond_order=1)

    return current


def assemble_all_combinations(
    combinations: list, fragment_library_dict: dict = None
) -> list:
    """Assemble molecules from every combination, capturing failures.

    Parameters
    ----------
    combinations : list of dict
        Combinations from :func:`find_fragment_combinations`.
    fragment_library_dict : dict, optional
        Mapping of fragment name to factory function. Defaults to
        ``ALL_FRAGMENTS``.

    Returns
    -------
    list of dict
        One entry per combination with keys ``index``, ``combination``,
        ``molecule`` (a :class:`MoleculeFragment` or ``None``) and
        ``success``; failed entries additionally carry an ``error`` message.
    """
    if fragment_library_dict is None:
        fragment_library_dict = ALL_FRAGMENTS

    molecules = []
    for i, combo in enumerate(combinations):
        try:
            mol = assemble_molecule_from_combination(combo, fragment_library_dict)
            molecules.append(
                {"index": i, "combination": combo, "molecule": mol, "success": True}
            )
        except Exception as e:
            molecules.append(
                {
                    "index": i,
                    "combination": combo,
                    "molecule": None,
                    "success": False,
                    "error": str(e),
                }
            )

    return molecules
