"""Tests for CHROM-01 segmented chromatogram averaging."""

from pathlib import Path

import numpy as np
import pandas as pd

from src.configs import PATHS
from src.core.io.segmented import aggregate_scans, build_rt_segments

THIS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = THIS_DIR.parent
SET01 = PROJECT_ROOT / PATHS.test_sets_dir / "set_01"


class TestBuildRtSegments:
    def test_default_ten_by_two(self):
        segments = build_rt_segments(0.0, 20.0, 2.0)
        assert segments == [
            (0.0, 2.0),
            (2.0, 4.0),
            (4.0, 6.0),
            (6.0, 8.0),
            (8.0, 10.0),
            (10.0, 12.0),
            (12.0, 14.0),
            (14.0, 16.0),
            (16.0, 18.0),
            (18.0, 20.0),
        ]

    def test_last_segment_truncated(self):
        assert build_rt_segments(0.0, 5.0, 2.0) == [(0.0, 2.0), (2.0, 4.0), (4.0, 5.0)]

    def test_invalid_width(self):
        try:
            build_rt_segments(0.0, 10.0, 0.0)
        except ValueError:
            return
        raise AssertionError("expected ValueError for segment_width=0")

    def test_invalid_range(self):
        try:
            build_rt_segments(10.0, 10.0, 2.0)
        except ValueError:
            return
        raise AssertionError("expected ValueError for rt_min == rt_max")


class TestAggregateScans:
    def _scan(self, mz, inten, rt):
        return (np.array(mz, dtype=float), np.array(inten, dtype=float), rt)

    def test_scans_go_to_own_segment(self):
        segments = [(0.0, 2.0), (2.0, 4.0)]
        scans = [
            self._scan([100.0, 200.0], [10.0, 20.0], 1.0),
            self._scan([100.0, 300.0], [5.0, 30.0], 3.0),
        ]
        dfs = aggregate_scans(scans, segments)
        assert len(dfs) == 2
        # сегмент 0: только первый скан
        assert list(dfs[0]["mass"]) == [100.0, 200.0]
        assert list(dfs[0]["intensity"]) == [10.0, 20.0]
        # сегмент 1: только второй скан
        assert list(dfs[1]["mass"]) == [100.0, 300.0]
        assert list(dfs[1]["intensity"]) == [5.0, 30.0]

    def test_same_mz_summed_within_segment(self):
        segments = [(0.0, 2.0)]
        scans = [
            self._scan([100.000001], [10.0], 0.5),
            self._scan([100.000002], [7.0], 1.5),
        ]
        dfs = aggregate_scans(scans, segments)
        assert len(dfs) == 1
        assert len(dfs[0]) == 1
        assert dfs[0].iloc[0]["mass"] == 100.0
        assert dfs[0].iloc[0]["intensity"] == 17.0

    def test_scan_outside_segments_ignored(self):
        segments = [(0.0, 2.0)]
        scans = [
            self._scan([100.0], [10.0], 0.5),
            self._scan([200.0], [20.0], 5.0),
        ]
        dfs = aggregate_scans(scans, segments)
        assert list(dfs[0]["mass"]) == [100.0]


class TestSegmentedPipelineCsvEquivalence:
    def test_csv_single_segment_matches_regular_pipeline(self):
        from src.core import run_pipeline, run_pipeline_segmented

        src = str(SET01 / "original.csv")
        dmet = str(SET01 / "deutermethylated.csv")
        dacet = str(SET01 / "deuteroacylated.csv")

        kw = dict(
            load_mass_min=100.0,
            load_mass_max=1000.0,
            rel_error=0.5,
            noise_force=2.0,
            noise_intensity=None,
            ppm_tol=0.5,
            max_groups=20,
            allow_gaps=True,
            sign="-",
        )

        regular = run_pipeline(
            src_path=src,
            dmet_path=dmet,
            dacet_path=dacet,
            visualize=False,
            use_cache=False,
            **kw,
        )
        segmented = run_pipeline_segmented(
            src_path=src,
            dmet_path=dmet,
            dacet_path=dacet,
            segment_width=2.0,
            rt_min=0.0,
            rt_max=20.0,
            **kw,
        )

        cols = ["mass", "brutto", "N_COOH", "N_OH"]
        assert len(regular.table) > 0
        assert len(segmented.table) == len(regular.table)
        assert segmented.table[cols].equals(regular.table[cols])
        # CSV без RT → один сегмент с rt_start/rt_end = None
        assert segmented.table["rt_start"].isna().all()
        assert segmented.table["rt_end"].isna().all()
