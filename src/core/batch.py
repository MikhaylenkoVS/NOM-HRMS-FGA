"""Batch processing: detect sample triples and build a comparison summary."""

from __future__ import annotations

import glob
import os

import pandas as pd

#: Filename markers used to classify a file as source / deuteromethylated /
#: deuteroacylated. Longer markers win on ambiguous names (e.g. ``cd3co``
#: beats ``cd3``).
SPECTRUM_PATTERNS: dict[str, list[str]] = {
    "src": ["original", "src", "source", "исходный", "orig"],
    "dmet": ["deutermethyl", "dmet", "cd3", "дейтерометил"],
    "dacet": ["deuteroacyl", "dacet", "cd3co", "дейтероацил"],
}

SPECTRUM_EXTENSIONS = ("*.csv", "*.xlsx", "*.raw", "*.mzML", "*.mzml")


def _list_files(folder: str) -> list[str]:
    files: list[str] = []
    for ext in SPECTRUM_EXTENSIONS:
        files.extend(glob.glob(os.path.join(folder, ext)))
    return files


def _classify(filename: str, patterns) -> tuple[str | None, str]:
    """Return ``(role, sample_name)`` for a file, or ``(None, name)`` if
    it does not match any role marker."""
    name = os.path.splitext(os.path.basename(filename))[0].lower()
    best: tuple[int, str, str] | None = None
    for role, pats in patterns.items():
        for p in pats:
            if p in name:
                if best is None or len(p) > best[0]:
                    best = (len(p), role, p)
    if best is None:
        return None, name
    _, role, marker = best
    sample = name.replace(marker, "").strip("_.- ")
    return role, (sample or name)


def detect_sample_triples(folder: str, patterns=None) -> list[dict[str, str]]:
    """Group files in *folder* into ``(src, dmet, dacet)`` triples by sample name.

    Returns
    -------
    list of dict
        Each dict has keys ``sample``, ``src``, ``dmet``, ``dacet`` (paths may
        be empty strings when a role was not found for that sample).
    """
    patterns = patterns or SPECTRUM_PATTERNS
    samples: dict[str, dict[str, str]] = {}
    for f in sorted(_list_files(folder)):
        role, sample = _classify(f, patterns)
        if role is None:
            continue
        samples.setdefault(sample, {})[role] = f

    return [
        {
            "sample": sample,
            "src": roles.get("src", ""),
            "dmet": roles.get("dmet", ""),
            "dacet": roles.get("dacet", ""),
        }
        for sample, roles in sorted(samples.items())
    ]


def compute_sample_summary(table, sample_name: str, stats=None) -> dict:
    """Return one summary row for a single sample's result table.

    Parameters
    ----------
    table : pandas.DataFrame or None
        Result table for the sample.
    sample_name : str
        Sample label.
    stats : PipelineStats or None
        Optional aggregate run statistics.
    """
    row: dict = {"sample": sample_name}
    if table is None or table.empty:
        row.update(
            {"n_compounds": 0, "N_COOH_total": 0, "N_OH_total": 0, "avg_mass": None}
        )
    else:
        row["n_compounds"] = len(table)
        row["N_COOH_total"] = int(table["N_COOH"].sum()) if "N_COOH" in table else 0
        row["N_OH_total"] = int(table["N_OH"].sum()) if "N_OH" in table else 0
        row["avg_mass"] = (
            round(float(table["mass"].mean()), 4) if "mass" in table else None
        )
    if stats is not None:
        row["assigned_count"] = stats.assigned_count
        row["assigned_ratio"] = round(stats.assigned_ratio, 4)
        row["n_cooh_gt0"] = stats.result_n_cooh_gt0
        row["n_oh_gt0"] = stats.result_n_oh_gt0
    return row


def build_batch_summary(rows: list[dict]) -> pd.DataFrame:
    """Build a summary DataFrame from a list of per-sample summary dicts."""
    return pd.DataFrame(rows)
