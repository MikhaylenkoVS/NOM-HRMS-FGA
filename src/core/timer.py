"""Lightweight wall-clock timer for pipeline stage profiling.

Usage (context manager)::

    from src.core.timer import stage_timer

    with stage_timer() as t:
        ...  # expensive work
    print(f"Stage took {t.elapsed:.3f}s")
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class StageTimer:
    """Context manager that records wall-clock elapsed time."""

    _start: float = 0.0
    elapsed: float = 0.0

    def __enter__(self) -> StageTimer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args) -> None:
        self.elapsed = time.perf_counter() - self._start


@dataclass
class PipelineTimings:
    """Wall-clock timings (seconds) for each major pipeline stage."""

    load: float = 0.0
    denoise: float = 0.0
    assign: float = 0.0
    series: float = 0.0
    build_table: float = 0.0
    total: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "load": self.load,
            "denoise": self.denoise,
            "assign": self.assign,
            "series": self.series,
            "build_table": self.build_table,
            "total": self.total,
        }

    def summary(self) -> str:
        return (
            f"load={self.load:.2f}s denoise={self.denoise:.2f}s "
            f"assign={self.assign:.2f}s series={self.series:.2f}s "
            f"build_table={self.build_table:.3f}s total={self.total:.2f}s"
        )
