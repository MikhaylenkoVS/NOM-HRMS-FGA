"""Candidate-structure visualization: parse -> combine -> assemble -> draw."""

import logging

from rdkit import Chem
from rdkit.Chem import Draw, AllChem
from ..domain.molecule import parse_formula
from .fragment_combinations import find_fragment_combinations, assemble_all_combinations

logger = logging.getLogger(__name__)


def find_and_visualize_molecules(
    brutto_formula: str,
    num_cooh: int = 0,
    num_oh: int = 0,
    max_bases: int = 10,
    show_images: bool = True,
    image_size: tuple = (400, 300),
    first_only: bool = False,
):
    """Go from a brutto formula to assembled (and optionally drawn) molecules.

    Runs the full candidate-structure cycle: parse the formula, compute IHD,
    enumerate fragment combinations, assemble molecules, and optionally render
    2D depictions with RDKit.

    Parameters
    ----------
    brutto_formula : str
        Molecular formula, e.g. ``"C7H6O2"``.
    num_cooh : int, optional
        Number of carboxyl groups. Default 0.
    num_oh : int, optional
        Number of hydroxyl groups. Default 0.
    max_bases : int, optional
        Maximum number of base fragments per combination. Default 10.
    show_images : bool, optional
        Whether to render RDKit images. Default ``True``.
    image_size : tuple of (int, int), optional
        Image size in pixels ``(width, height)``. Default ``(400, 300)``.

    Returns
    -------
    dict
        Keys: ``input`` (echoed arguments), ``heavy_formula``, ``ihd``,
        ``combinations``, ``molecules`` (assembled structures with metadata),
        and ``images`` (PIL images when ``show_images`` is True).

    Notes
    -----
    IHD is computed as ``(2*C + 2 - H + N - X) / 2`` where ``X`` is the total
    halogen count. Progress is printed to stdout.
    """

    # === ШАГ 2: Вычисление тяжёлой формулы и IHD ===
    full_formula = parse_formula(brutto_formula)
    X = (
        full_formula.get("F", 0)
        + full_formula.get("Cl", 0)
        + full_formula.get("Br", 0)
        + full_formula.get("I", 0)
    )

    # Убираем водороды для тяжёлой формулы
    heavy_formula = {k: v for k, v in full_formula.items() if k != "H"}

    # Вычисляем IHD по формуле: IHD = (2C + 2 - H + N) / 2
    C = full_formula.get("C", 0)
    H = full_formula.get("H", 0)
    N = full_formula.get("N", 0)

    ihd = (2 * C + 2 - H + N - X) / 2

    logger.info("📋 Исходные данные:")
    logger.info(f"   Брутто-формула: {brutto_formula}")
    logger.info(f"   Тяжёлая формула: {heavy_formula}")
    logger.info(f"   IHD: {ihd}")
    logger.info(f"   COOH групп: {num_cooh}")
    logger.info(f"   OH групп: {num_oh}")

    # === ШАГ 3: Поиск комбинаций ===
    logger.info("🔍 Поиск возможных комбинаций фрагментов...")

    combinations = find_fragment_combinations(
        target_heavy_formula=heavy_formula,
        target_ihd=ihd,
        num_cooh=num_cooh,
        num_oh=num_oh,
        max_bases=max_bases,
        first_only=first_only,
    )
    logger.info(f"✅ Найдено {len(combinations)} комбинаций")

    if not combinations:
        logger.warning("⚠️  Подходящих комбинаций не найдено")
        return {
            "input": {"brutto": brutto_formula, "cooh": num_cooh, "oh": num_oh},
            "heavy_formula": heavy_formula,
            "ihd": ihd,
            "combinations": [],
            "molecules": [],
            "images": [],
        }

    # === ШАГ 4: Сборка молекул ===
    logger.info("🔧 Сборка молекул из комбинаций...")
    assembled = assemble_all_combinations(combinations)

    successful = [r for r in assembled if r["success"]]
    failed = [r for r in assembled if not r["success"]]

    logger.info(f"✅ Успешно собрано: {len(successful)}")
    if failed:
        logger.warning(f"❌ Не удалось собрать: {len(failed)}")

    # === ШАГ 5: Подготовка результата ===
    molecules_data = []
    images = []

    for result in successful:
        mol = result["molecule"]
        combo = result["combination"]

        mol_info = {
            "index": result["index"],
            "name": mol.name,
            "formula": mol.heavy_formula,
            "ihd": mol.ihd,
            "num_atoms": mol.get_num_atoms(),
            "num_bonds": len(mol.bonds),
            "free_points": len(mol.get_free_attachment_points()),
            "combination": combo,
            "fragment_object": mol,
        }
        molecules_data.append(mol_info)

    # === ШАГ 6: Визуализация (если требуется) ===
    if show_images:
        logger.info("🎨 Визуализация структур...")
        for mol_data in molecules_data:
            mol_obj = mol_data["fragment_object"]

            # Создаём RDKit молекулу
            rdkit_mol = Chem.RWMol()
            for symbol in mol_obj.atoms:
                rdkit_mol.AddAtom(Chem.Atom(symbol))

            for i, j, order in mol_obj.bonds:
                bond_types = [
                    Chem.BondType.SINGLE,
                    Chem.BondType.DOUBLE,
                    Chem.BondType.TRIPLE,
                    Chem.BondType.AROMATIC,
                ]
                idx = min(order - 1, len(bond_types) - 1)
                rdkit_mol.AddBond(i, j, bond_types[idx])

            rdkit_mol = rdkit_mol.GetMol()

            # Санитизация
            try:
                Chem.SanitizeMol(rdkit_mol)
            except Exception:
                try:
                    Chem.SanitizeMol(
                        rdkit_mol,
                        sanitizeOps=Chem.SANITIZE_ALL ^ Chem.SANITIZE_PROPERTIES,
                    )
                except Exception:
                    pass

            # Генерируем 2D-координаты (CoordGen для зигзагов sp3)
            from rdkit.Chem import rdDepictor

            rdDepictor.SetPreferCoordGen(True)
            AllChem.Compute2DCoords(rdkit_mol)
            # Добавляем только полярные водороды (на гетероатомах)
            rdkit_mol = Chem.AddHs(rdkit_mol, explicitOnly=True)
            # Убираем H с углерода, оставляем на N, O, S
            final_mol = Chem.RWMol(rdkit_mol)
            atoms_to_remove = []
            for atom in final_mol.GetAtoms():
                if atom.GetAtomicNum() == 1:  # водород
                    # Найти соседа
                    for nbr in atom.GetNeighbors():
                        if nbr.GetAtomicNum() == 6:  # углерод
                            atoms_to_remove.append(atom.GetIdx())
                            break
            for idx in reversed(sorted(atoms_to_remove)):
                final_mol.RemoveAtom(idx)
            rdkit_mol = final_mol.GetMol()
            try:
                Chem.SanitizeMol(rdkit_mol)
            except Exception:
                pass

            # Генерируем изображение
            img = Draw.MolToImage(rdkit_mol, size=image_size)
            images.append(img)
            mol_data["image"] = img

        logger.info(f"✅ Создано {len(images)} изображений")

    # === ШАГ 7: Вывод результатов ===
    sep = "=" * 60
    logger.info(sep)
    logger.info(
        f"📊 ИТОГО: найдено {len(molecules_data)} структур для {brutto_formula}"
    )
    logger.info(sep)

    for i, mol_data in enumerate(molecules_data, 1):
        logger.info(f"{i}. {mol_data['name']}")
        logger.info(f"   Формула: {mol_data['formula']}")
        logger.info(f"   IHD: {mol_data['ihd']}")
        logger.info(f"   Фрагменты: {mol_data['combination']['bases']}")
        logger.info(
            f"   COOH: {mol_data['combination']['cooh']}, OH: {mol_data['combination']['oh']}"
        )

    logger.info(sep)

    return {
        "input": {
            "brutto": brutto_formula,
            "cooh": num_cooh,
            "oh": num_oh,
            "max_bases": max_bases,
        },
        "heavy_formula": heavy_formula,
        "ihd": ihd,
        "combinations": combinations,
        "molecules": molecules_data,
        "images": images,
    }
