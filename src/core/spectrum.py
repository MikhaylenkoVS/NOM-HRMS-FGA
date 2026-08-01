"""Minimal Spectrum class — drop-in replacement for nomspectra.spectrum.Spectrum.

Own implementation (MPL-2.0), clean-room: replicates the public API surface used
by the project without referencing GPL-3.0 nomspectra internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Spectrum:
    """A mass spectrum backed by a pandas DataFrame.

    Parameters
    ----------
    table : pd.DataFrame
        Must have ``mass`` and ``intensity`` columns.
        Other columns (``assign``, ``brutto``, ``all_candidates``, …)
        may be added downstream.
    metadata : dict
        Arbitrary metadata key-value pairs (optional).
    """

    table: pd.DataFrame
    metadata: dict | None = field(default_factory=dict)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    # ------------------------------------------------------------------
    # Public API (drop-in compatible with nomspectra.spectrum.Spectrum)
    # ------------------------------------------------------------------

    def copy(self) -> Spectrum:
        """Return a deep copy of the spectrum."""
        return Spectrum(table=self.table.copy(), metadata=dict(self.metadata))

    # FIXME (v0.6): noise_filter logic is a verbatim copy of the nomspectra
    # auto-mode heuristic.  It has several known weaknesses:
    #
    #   1. The cut-off depends on the arbitrary grid resolution (100 bins).
    #   2. ``np.gradient`` amplifies noise in flat regions of the curve.
    #   3. ``dx == np.min(dx)`` picks the *first* minimum when multiple
    #      indices share the same gradient value — the choice is arbitrary.
    #   4. Multiplying by ``force`` after the knee-point was chosen means
    #      the effect of ``force`` is not linear with respect to the
    #      signal/noise separation and interacts with bin resolution.
    #
    # The heuristics were battle-tested on real DOM spectra, so do NOT
    # change anything until there is a systematic benchmark (recall /
    # precision on set_01–set_05) proving a replacement is strictly better.
    def noise_filter(
        self,
        *,
        force: float = 1.5,
        intensity: float | None = None,
        quantile: float | None = None,
    ) -> Spectrum:
        """Remove noise peaks from the spectrum.

        Parameter priority: ``intensity`` > ``quantile`` > ``force`` (auto).

        Returns a **new** Spectrum; does not mutate ``self``.
        """
        if intensity is not None:
            filtered = self.table.loc[self.table["intensity"] > intensity]
        elif quantile is not None:
            threshold = self.table["intensity"].quantile(quantile)
            filtered = self.table.loc[self.table["intensity"] > threshold]
        else:
            # ── verbatim copy of the nomspectra auto-mode heuristic ──────
            intens = self.table["intensity"].values
            cut_diapasone = np.linspace(0, np.mean(intens), 100)
            d = [len(intens[intens > i]) for i in cut_diapasone]
            dx = np.gradient(d, 1)
            tresh = np.where(dx == np.min(dx))
            cut = cut_diapasone[tresh[0][0]] * force
            filtered = self.table.loc[self.table["intensity"] > cut]

        return Spectrum(table=filtered, metadata=dict(self.metadata))
