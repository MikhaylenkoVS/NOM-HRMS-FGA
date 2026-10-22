"""CHO-приоритет в NOM-like области Ван-Кревелена."""

import numpy as np

from src.core.spectrum._assign import _candidate_scores
from src.core.spectrum._constants import FormulaSearchConfig


def _row(counts: dict[str, int], elements: tuple[str, ...]) -> list[int]:
    return [counts.get(el, 0) for el in elements]


def test_cho_nom_candidate_beats_halogen_candidate():
    cfg = FormulaSearchConfig()
    elements = cfg.elements
    idx = {el: i for i, el in enumerate(elements)}
    counts = np.array(
        [
            _row({"C": 13, "H": 16, "O": 8}, elements),
            _row({"C": 11, "H": 18, "O": 5, "S": 1, "F": 2}, elements),
        ],
        dtype=np.int32,
    )
    scores = _candidate_scores(counts, elements, idx, 1.0, cfg)
    assert int(np.argmin(scores)) == 0
    assert scores[0] < scores[1]


def test_cho_outside_nom_does_not_get_bonus():
    cfg = FormulaSearchConfig()
    elements = cfg.elements
    idx = {el: i for i, el in enumerate(elements)}
    counts = np.array(
        [
            _row({"C": 13, "H": 1, "O": 1}, elements),
            _row({"C": 13, "H": 16, "O": 8}, elements),
        ],
        dtype=np.int32,
    )
    scores = _candidate_scores(counts, elements, idx, 1.0, cfg)
    assert int(np.argmin(scores)) == 1
