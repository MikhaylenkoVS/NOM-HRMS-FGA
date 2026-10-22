"""Веса штрафов политики серий v3."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PenaltyWeights:
    """Максимальные вклады штрафов; сумма ограничена 100."""

    source_overlap_base: float = 10.0
    source_overlap_per_src: float = 10.0
    source_overlap_max: float = 30.0
    o_excess_per: float = 20.0
    o_excess_max: float = 40.0
    isotope_min: float = 5.0
    isotope_max: float = 30.0
    gap_per: float = 15.0
    gap_cap: float = 45.0
    conflict_overlap: float = 10.0
    conflict_no_prev: float = 30.0
    persistence_max: float = 10.0
    peak_profile: float = 10.0
    poor_resolution_max: float = 25.0
    multi_resolution: float = 15.0
    intensity_max: float = 5.0

    def source_overlap(self, n_src: int) -> float:
        return min(
            float(self.source_overlap_max),
            float(self.source_overlap_base)
            + float(self.source_overlap_per_src) * int(n_src),
        )

    def o_excess(self, extra_steps: int) -> float:
        return min(
            float(self.o_excess_max),
            float(self.o_excess_per) * max(0, int(extra_steps)),
        )

    def isotope(self, iso_dev: float) -> float:
        if iso_dev != iso_dev:  # NaN
            return float(self.isotope_max)
        return min(
            float(self.isotope_max),
            max(float(self.isotope_min), float(self.isotope_max) * float(iso_dev)),
        )

    def gap(self, n_missing: int) -> float:
        return min(float(self.gap_cap), float(self.gap_per) * max(1, int(n_missing)))

    def persistence(self, persistence: float, min_persistence: float = 0.8) -> float:
        if persistence >= min_persistence:
            return 0.0
        return float(self.persistence_max) * (
            (min_persistence - float(persistence)) / max(1e-12, min_persistence)
        )

    def intensity(self, excess: float) -> float:
        return min(float(self.intensity_max), max(0.0, float(excess)))
