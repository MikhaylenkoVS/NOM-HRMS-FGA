"""Тесты весов штрафов."""

from src.core.spectrum._penalty import PenaltyWeights


def test_source_overlap_scales_and_caps():
    w = PenaltyWeights()
    assert w.source_overlap(1) == 20.0
    assert w.source_overlap(2) == 30.0
    assert w.source_overlap(10) == 30.0


def test_o_excess_scales_and_caps():
    w = PenaltyWeights()
    assert w.o_excess(1) == 20.0
    assert w.o_excess(2) == 40.0
    assert w.o_excess(5) == 40.0


def test_isotope_scales_and_caps():
    w = PenaltyWeights()
    assert w.isotope(0.0) == 5.0
    assert w.isotope(0.5) == 15.0
    assert w.isotope(2.0) == 30.0
    assert w.isotope(float("nan")) == 30.0


def test_gap_scales_and_caps():
    w = PenaltyWeights()
    assert w.gap(1) == 15.0
    assert w.gap(2) == 30.0
    assert w.gap(10) == 45.0


def test_persistence_linear_threshold():
    w = PenaltyWeights()
    assert w.persistence(0.8) == 0.0
    assert w.persistence(0.4) == 5.0
    assert w.persistence(0.0) == 10.0


def test_intensity_capped():
    w = PenaltyWeights()
    assert w.intensity(2.0) == 2.0
    assert w.intensity(50.0) == 5.0
