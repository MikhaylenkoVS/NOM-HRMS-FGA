"""Domain model: Peak, SpectrumMetadata, Spectrum.

Own implementation (MPL-2.0), clean-room design.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from src.configs import NOISE_CFG

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Iterable


# ===========================================================================
# Peak
# ===========================================================================


@dataclass(frozen=True, slots=True)
class Peak:
    """A single mass-spectrometric peak.

    Attributes
    ----------
    mass : float
        Observed m/z (Da).
    intensity : float
        Absolute or relative intensity.
    resolution : float or None
        Resolving power (FWHM) if available.
    baseline : float or None
        Local baseline level if computed.
    noise : float or None
        Local noise estimate if computed.
    charge : int or None
        Charge state if known (e.g. 1 for [M-H]⁻).
    rt : float or None
        Retention time (min) if the peak originated from an LC run.
    scan_number : int or None
        Index of the scan the peak belongs to.
    """

    mass: float
    intensity: float
    resolution: float | None = None
    baseline: float | None = None
    noise: float | None = None
    charge: int | None = None
    rt: float | None = None
    scan_number: int | None = None


# ===========================================================================
# SpectrumMetadata
# ===========================================================================


@dataclass
class SpectrumMetadata:
    """Metadata carried alongside a spectrum.

    All fields are optional — fill what the data source provides.
    """

    source_path: str | None = None
    sample_name: str | None = None
    rt_window: tuple[float, float] | None = None
    instrument: str | None = None
    ion_mode: str | None = None
    file_format: str | None = None
    scan_count: int | None = None


# ===========================================================================
# Spectrum
# ===========================================================================


class Spectrum:
    """An immutable collection of mass-spectral peaks with metadata.

    Core storage is a ``tuple[Peak, ...]`` — once created, the peaks cannot
    be mutated.  All operations that would modify the spectrum return a new
    ``Spectrum`` instance.

    For backward compatibility with the existing pipeline, the ``table``
    property provides a read / write view as a ``pandas.DataFrame``.

    Parameters
    ----------
    table : pd.DataFrame, optional
        Construct from a DataFrame (must have ``mass`` and ``intensity``
        columns).  Mutually exclusive with ``peaks``.
    peaks : iterable of Peak, optional
        Construct from Peak objects.  Mutually exclusive with ``table``.
    metadata : dict or SpectrumMetadata or None, optional
        Metadata.  A plain dict is converted to ``SpectrumMetadata``.
    """

    __slots__ = ("_peaks", "_table_cache", "metadata")

    @staticmethod
    def _df_to_peaks(df: pd.DataFrame) -> tuple[Peak, ...]:
        """Convert a DataFrame to a tuple of Peak objects.

        Only the mandatory columns (*mass*, *intensity*) are used; optional
        columns (*resolution*, *baseline*, *noise*, *charge*, *rt*,
        *scan_number*) are picked up when present.

        If *intensity* column is missing, it is filled with 0.0 (the caller
        should have called ``validate()`` beforehand).
        """
        cols = df.columns
        masses = df["mass"]
        intensities = (
            df["intensity"] if "intensity" in cols else pd.Series(0.0, index=df.index)
        )
        # optional — use None when column is missing
        resolution = df["resolution"] if "resolution" in cols else None
        baseline = df["baseline"] if "baseline" in cols else None
        noise = df["noise"] if "noise" in cols else None
        charge = df["charge"] if "charge" in cols else None
        rt = df["rt"] if "rt" in cols else None
        scan_number = df["scan_number"] if "scan_number" in cols else None

        def _opt_float(series, i):
            """Значение необязательной колонки как float; NaN/None → None."""
            if series is None:
                return None
            value = series.iloc[i]
            return None if pd.isna(value) else float(value)

        def _opt_int(series, i):
            """Значение необязательной колонки как int; NaN/None → None."""
            if series is None:
                return None
            value = series.iloc[i]
            return None if pd.isna(value) else int(value)

        peaks: list[Peak] = []
        for i in range(len(df)):
            peaks.append(
                Peak(
                    mass=float(masses.iloc[i]),
                    intensity=float(intensities.iloc[i]),
                    resolution=_opt_float(resolution, i),
                    baseline=_opt_float(baseline, i),
                    noise=_opt_float(noise, i),
                    charge=_opt_int(charge, i),
                    rt=_opt_float(rt, i),
                    scan_number=_opt_int(scan_number, i),
                )
            )
        return tuple(peaks)

    def __init__(
        self,
        *,
        table: pd.DataFrame | None = None,
        peaks: Iterable[Peak] | None = None,
        metadata: dict | SpectrumMetadata | None = None,
    ):
        if table is not None and peaks is not None:
            raise ValueError(
                "Only one of 'table' or 'peaks' may be provided, not both."
            )

        # ── metadata ──────────────────────────────────────────────────
        if metadata is None:
            self.metadata = SpectrumMetadata()
        elif isinstance(metadata, dict):
            from dataclasses import fields as _fields

            known = {f.name for f in _fields(SpectrumMetadata)}
            # map legacy key 'name' → 'sample_name' if the latter not set
            meta = dict(metadata)
            if "name" in meta and "sample_name" not in meta:
                meta["sample_name"] = meta.pop("name")
            filtered = {k: v for k, v in meta.items() if k in known}
            self.metadata = SpectrumMetadata(**filtered)
        elif isinstance(metadata, SpectrumMetadata):
            self.metadata = metadata
        else:
            raise TypeError(
                f"metadata must be dict or SpectrumMetadata, got {type(metadata)}"
            )

        # ── peaks / table ─────────────────────────────────────────────
        if peaks is not None:
            self._peaks = tuple(peaks)
            self._table_cache = None  # built lazily on first access
        elif table is not None:
            self._peaks = self._df_to_peaks(table)
            self._table_cache = table.copy()
        else:
            self._peaks = ()
            self._table_cache = None

    # ------------------------------------------------------------------
    # Properties (backward-compatible with the legacy Spectrum API)
    # ------------------------------------------------------------------

    @property
    def table(self) -> pd.DataFrame:
        """The spectrum as a pandas DataFrame (mass, intensity, …)."""
        if self._table_cache is not None:
            return self._table_cache
        # Build from peaks
        df = pd.DataFrame(
            {
                "mass": [p.mass for p in self._peaks],
                "intensity": [p.intensity for p in self._peaks],
            }
        )
        # Carry over optional columns when ALL peaks have non-None values
        for attr in ("resolution", "baseline", "noise", "charge", "rt", "scan_number"):
            values = [getattr(p, attr) for p in self._peaks]
            if all(v is not None for v in values):
                df[attr] = values
        self._table_cache = df
        return df

    @table.setter
    def table(self, df: pd.DataFrame):
        """Replace the underlying peaks with those from *df*."""
        self._peaks = self._df_to_peaks(df)
        self._table_cache = df.copy()

    @property
    def mass(self) -> np.ndarray:
        """Array of m/z values (Da)."""
        return self.table["mass"].values

    @property
    def intensity(self) -> np.ndarray:
        """Array of intensity values."""
        return self.table["intensity"].values

    @property
    def n_peaks(self) -> int:
        """Number of peaks in the spectrum."""
        return len(self._peaks)

    @property
    def peaks(self) -> tuple[Peak, ...]:
        """Immutable tuple of Peak objects."""
        return self._peaks

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def copy(self) -> Spectrum:
        """Return a deep copy of the spectrum."""
        new = Spectrum.__new__(Spectrum)
        new._peaks = self._peaks  # frozen objects — shallow copy is safe
        new.metadata = SpectrumMetadata(
            source_path=self.metadata.source_path,
            sample_name=self.metadata.sample_name,
            rt_window=self.metadata.rt_window,
            instrument=self.metadata.instrument,
            ion_mode=self.metadata.ion_mode,
            file_format=self.metadata.file_format,
            scan_count=self.metadata.scan_count,
        )
        new._table_cache = (
            self._table_cache.copy() if self._table_cache is not None else None
        )
        return new

    def __len__(self) -> int:
        return self.n_peaks

    def __repr__(self) -> str:
        n = self.n_peaks
        mz_range = f"{self.mass[0]:.2f}–{self.mass[-1]:.2f}" if n else "—"
        return f"Spectrum(n={n}, m/z={mz_range})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Spectrum):
            return NotImplemented
        return self._peaks == other._peaks and self.metadata == other.metadata

    def __hash__(self) -> int:
        return hash((self._peaks, self.metadata))

    # ------------------------------------------------------------------
    # noise_filter (clean-room GMM-based auto-mode, MPL-2.0)
    # ------------------------------------------------------------------

    def noise_filter(
        self,
        *,
        force: float = 2.0,
        intensity: float | None = None,
        quantile: float | None = None,
        max_components: int = NOISE_CFG.max_components,
    ) -> Spectrum:
        """Remove noise peaks from the spectrum.

        Parameter priority: ``intensity`` > ``quantile`` > auto (GMM + BIC).

        The **auto** mode fits a 1-D Gaussian mixture model to
        ``log10(intensities)``, selects the number of components via BIC,
        and sets the threshold at the intersection of the two lowest-mean
        Gaussians — the noise / signal boundary.  The result is multiplied
        by *force* (default 2.0; use 1.0 for the exact boundary).

        Returns a **new** Spectrum; does not mutate ``self``.
        """
        if quantile is not None and not 0.0 <= quantile <= 1.0:
            raise ValueError(
                f"quantile должен быть в диапазоне [0, 1], получено {quantile!r}"
            )

        if intensity is not None:
            threshold = intensity
        elif quantile is not None:
            threshold = float(self.table["intensity"].quantile(quantile))
        else:
            from src.core.spectrum import compute_noise_threshold

            intens = self.intensity[self.intensity > 0]
            if len(intens) < 3:
                return self.copy()
            result = compute_noise_threshold(intens, max_components=max_components)
            threshold = result.threshold * force

        # ── Предохранители ─────────────────────────────────────────────────
        # Нечисловой порог (вырожденный GMM: одна популяция, одинаковые
        # интенсивности и т.п.) — спектр не фильтруем.
        if threshold is None or not np.isfinite(threshold):
            logger.warning(
                "Шумоподавление: порог не определён (%r) — спектр оставлен "
                "без изменений",
                threshold,
            )
            return self.copy()

        keep = [p for p in self._peaks if p.intensity > threshold]
        n_total = len(self._peaks)
        if n_total:
            removed_ratio = 1.0 - len(keep) / n_total
            max_removed = float(getattr(NOISE_CFG, "max_removed_ratio", 0.9))
            if removed_ratio > max_removed:
                logger.warning(
                    "Шумоподавление: порог %.3g отсекает %.0f%% пиков "
                    "(> %.0f%%) — похоже, шумовой популяции в файле нет или "
                    "пиклист уже отфильтрован; фильтр не применён",
                    threshold,
                    100 * removed_ratio,
                    100 * max_removed,
                )
                return self.copy()
        return Spectrum(peaks=keep, metadata=self.metadata)
