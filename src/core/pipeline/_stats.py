"""Pipeline statistics dataclasses."""
import logging
from dataclasses import dataclass, field
import pandas as pd
from typing import Optional
logger = logging.getLogger(__name__)

class SeriesStats:
    """Summary statistics for one derivatization-series search.

    Attributes
    ----------
    rows : int
        Number of series records found.
    max_groups : int
        Largest series length (max functional-group count) observed.
    missing_total : int
        Total number of missing (gap) steps across all series.
    """

    rows: int = 0
    max_groups: int = 0
    missing_total: int = 0


@dataclass(slots=True)
class PipelineStats:
    """Aggregate counters describing one full pipeline run.

    Attributes
    ----------
    src_loaded, dmet_loaded, dacet_loaded : int
        Peak counts loaded from the source, deuteromethylated and
        deuteroacylated spectra.
    src_denoised, dmet_denoised, dacet_denoised : int
        Peak counts remaining after denoising.
    assigned_count : int
        Number of source peaks assigned a brutto formula.
    assigned_ratio : float
        Fraction of denoised source peaks that were assigned.
    dmet, dacet : SeriesStats
        Series statistics for the -COOH (CD3) and -OH (CD3CO) searches.
    result_rows : int
        Number of rows in the final result table.
    result_n_cooh_gt0, result_n_oh_gt0 : int
        Count of result rows with at least one -COOH / -OH group.
    """

    src_loaded: int = 0
    dmet_loaded: int = 0
    dacet_loaded: int = 0

    src_denoised: int = 0
    dmet_denoised: int = 0
    dacet_denoised: int = 0

    assigned_count: int = 0
    assigned_ratio: float = 0.0

    dmet: SeriesStats = field(default_factory=SeriesStats)
    dacet: SeriesStats = field(default_factory=SeriesStats)

    result_rows: int = 0
    result_n_cooh_gt0: int = 0
    result_n_oh_gt0: int = 0


@dataclass(slots=True)
class PipelineRunResult:
    """Result of a single (non-test) pipeline run.

    Attributes
    ----------
    table : pandas.DataFrame
        Final result table with per-compound -COOH / -OH counts.
    stats : PipelineStats
        Aggregate run statistics.
    messages : list of str
        Human-readable status/diagnostic messages produced during the run.
    """

    table: pd.DataFrame
    stats: PipelineStats
    messages: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Датаклассы тест-режима
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class TestSetResult:
    """Validation metrics for one synthetic test set in test mode.

    Attributes
    ----------
    set_name : str
        Name of the test set (e.g. ``"set_01"``).
    total_signals : int
        Number of ground-truth signals in the set.
    denoised_kept : int
        Peaks retained after denoising.
    assigned_ok : int
        Peaks assigned a correct brutto formula.
    dmet_found, dmet_matched, dmet_wrong : int
        -COOH (CD3) series counts: found, matching ground truth, and wrong.
    dacet_found, dacet_matched, dacet_wrong : int
        -OH (CD3CO) series counts: found, matching ground truth, and wrong.
    errors : list of str
        Error messages accumulated while processing the set.
    result_table : pandas.DataFrame or None
        Final result table for the set, if produced.
    assigned_only : pandas.DataFrame or None
        Subset of assigned peaks, if produced.
    """

    set_name: str
    total_signals: int = 0
    denoised_kept: int = 0
    assigned_ok: int = 0

    # Серии
    dmet_found: int = 0
    dmet_matched: int = 0
    dmet_wrong: int = 0
    dacet_found: int = 0
    dacet_matched: int = 0
    dacet_wrong: int = 0

    # Ошибки
    errors: list[str] = field(default_factory=list)

    # Финальная таблица
    result_table: Optional[pd.DataFrame] = None
    assigned_only: Optional[pd.DataFrame] = None

    @property
    def denoise_recall(self) -> float:
        """float: Fraction of ground-truth signals kept after denoising."""
        return self.denoised_kept / self.total_signals if self.total_signals else 0.0

    @property
    def assign_recall(self) -> float:
        """float: Fraction of ground-truth signals correctly assigned."""
        return self.assigned_ok / self.total_signals if self.total_signals else 0.0


# ---------------------------------------------------------------------------
# Основной пайплайн
# ---------------------------------------------------------------------------

