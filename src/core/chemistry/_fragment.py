"""MoleculeFragment — a reusable structural building block for NOM structure enumeration."""

from collections import defaultdict
from typing import Dict, List, Tuple


class MoleculeFragment:
    """A structural building block with labelled attachment points.

    Represents a connected sub-structure (ring, chain or functional group)
    whose free valences (attachment points) can be bonded to other fragments
    to assemble whole molecules.

    Parameters
    ----------
    name : str
        Fragment name (e.g. ``"benzene"``).
    heavy_formula : dict of {str: int}
        Heavy-atom (non-hydrogen) element counts.
    ihd : int
        Index of hydrogen deficiency contributed by the fragment.
    atoms : list of str
        Element symbol of each atom, indexed by position.
    bonds : list of tuple of (int, int, int)
        Internal bonds as ``(atom_i, atom_j, bond_order)``.
    attachment_points : list of int
        Atom indices exposing a free valence; repeated entries mean multiple
        free bonds on the same atom.

    Attributes
    ----------
    attachment_counts : dict of {int: int}
        Number of free attachment bonds per atom index.
    adjacency : dict of {int: list of (int, int)}
        Neighbour list mapping each atom to ``(neighbour, bond_order)`` pairs.
    """

    def __init__(self, name, heavy_formula, ihd, atoms, bonds, attachment_points):
        self.name = name
        self.heavy_formula = heavy_formula
        self.ihd = ihd
        self.atoms = atoms
        self.bonds = bonds
        # Convert list of attachment points to a counts dictionary
        self.attachment_counts = {}
        for idx in attachment_points:
            self.attachment_counts[idx] = self.attachment_counts.get(idx, 0) + 1
        self.adjacency = self._build_adjacency()

    def _build_adjacency(self) -> Dict[int, List[Tuple[int, int]]]:
        adj = defaultdict(list)
        for i, j, order in self.bonds:
            adj[i].append((j, order))
            adj[j].append((i, order))
        return dict(adj)  # or simply return adj if a defaultdict is acceptable

    def get_num_atoms(self) -> int:
        """Return the number of (heavy) atoms in the fragment.

        Returns
        -------
        int
            Count of atoms.
        """
        return len(self.atoms)

    def get_free_attachment_points(self) -> List[int]:
        """List all free attachment points, with multiplicity.

        Returns
        -------
        list of int
            Atom indices with a free valence; an atom with two free bonds
            appears twice.
        """
        return [idx for idx, cnt in self.attachment_counts.items() for _ in range(cnt)]

    def has_free_attachment_point(self, idx: int) -> bool:
        """Test whether an atom still has a free attachment point.

        Parameters
        ----------
        idx : int
            Atom index to check.

        Returns
        -------
        bool
            ``True`` if atom ``idx`` has at least one free bond available.
        """
        return self.attachment_counts.get(idx, 0) > 0

    def connect_to(
        self,
        other: "MoleculeFragment",
        my_point: int,
        other_point: int,
        bond_order: int = 1,
    ) -> "MoleculeFragment":
        """Join this fragment to another at given attachment points.

        Parameters
        ----------
        other : MoleculeFragment
            Fragment to attach.
        my_point : int
            Atom index on this fragment exposing a free valence.
        other_point : int
            Atom index on ``other`` exposing a free valence.
        bond_order : int, optional
            Order of the new inter-fragment bond. Default is 1.

        Returns
        -------
        MoleculeFragment
            A new fragment combining both, with atom indices of ``other``
            offset, the connecting bond added, and the two consumed
            attachment points removed. Neither input is modified.

        Raises
        ------
        ValueError
            If either attachment point has no free valence left.
        """
        if not self.has_free_attachment_point(my_point):
            raise ValueError(f"Точка {my_point} в {self.name} уже занята")
        if not other.has_free_attachment_point(other_point):
            raise ValueError(f"Точка {other_point} в {other.name} уже занята")

        # Имя и суммарная формула
        new_name = f"{self.name}+{other.name}"
        new_heavy = self.heavy_formula.copy()
        for el, count in other.heavy_formula.items():
            new_heavy[el] = new_heavy.get(el, 0) + count

        new_ihd = self.ihd + other.ihd

        # Атомы
        offset = len(self.atoms)
        new_atoms = self.atoms + other.atoms

        # Связи
        new_bonds = self.bonds.copy()
        for i, j, order in other.bonds:
            new_bonds.append((i + offset, j + offset, order))
        new_bonds.append((my_point, other_point + offset, bond_order))

        # --- Слияние точек присоединения ---
        # Копируем и уменьшаем self
        counts = dict(self.attachment_counts)
        if my_point in counts:
            counts[my_point] -= 1
            if counts[my_point] == 0:
                del counts[my_point]

        # Копируем и уменьшаем other (со сдвигом)
        other_counts = {k + offset: v for k, v in other.attachment_counts.items()}
        shifted_other_point = other_point + offset
        if shifted_other_point in other_counts:
            other_counts[shifted_other_point] -= 1
            if other_counts[shifted_other_point] == 0:
                del other_counts[shifted_other_point]

        # Сливаем два словаря
        merged = counts.copy()
        for k, v in other_counts.items():
            merged[k] = merged.get(k, 0) + v

        # Преобразуем обратно в список для конструктора
        new_attachment_points = [idx for idx, cnt in merged.items() for _ in range(cnt)]

        return MoleculeFragment(
            name=new_name,
            heavy_formula=new_heavy,
            ihd=new_ihd,
            atoms=new_atoms,
            bonds=new_bonds,
            attachment_points=new_attachment_points,
        )

    def __repr__(self) -> str:
        return (
            f"MoleculeFragment(name='{self.name}', "
            f"formula={self.heavy_formula}, ihd={self.ihd}, "
            f"atoms={len(self.atoms)}, bonds={len(self.bonds)}, "
            f"free_points={sum(self.attachment_counts.values())})"
        )
