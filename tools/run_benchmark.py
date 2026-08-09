#!/usr/bin/env python3
"""
Safe benchmark runner for NOM-HRMS-FGA.

Maps registered benchmark IDs to fixed argument lists.
Never accepts arbitrary shell commands.
Produces structured reports with collision-free run IDs.
Writes GITHUB_OUTPUT for safe artifact upload when running in CI.

Usage:
    python tools/run_benchmark.py <benchmark_id> --task-id <task_id>
"""

import json
import os
import platform
import re
import subprocess
import sys
import textwrap
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / ".ai" / "reports" / "benchmarks"

# ── Registered benchmarks ──────────────────────────────────────────────
BENCHMARKS: dict[str, dict] = {
    "ai-workflow-validation-smoke": {
        "cmd": [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/test_ai_workflow.py",
            "-q",
            "--tb=short",
        ],
        "kind": "validation_smoke",
    },
}


def _safe_run_id(benchmark_id: str) -> str:
    """Generate a collision-free safe run-id."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    us = datetime.now(timezone.utc).microsecond
    suffix = uuid.uuid4().hex[:8]
    return f"{ts}-{us:06d}Z-{benchmark_id}-{suffix}"


def _write_github_output(report_dir: Path, status: str) -> None:
    """Write GITHUB_OUTPUT for safe artifact upload in CI."""
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        rel = report_dir.resolve().relative_to(PROJECT_ROOT.resolve())
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"report_dir={rel.as_posix()}\n")
            f.write(f"report_status={status}\n")
            f.write("report_created=true\n")


def run_benchmark(benchmark_id: str, task_id: str) -> int:
    """Run a registered benchmark. Returns exit code."""
    # ----- validate benchmark_id -----
    if benchmark_id not in BENCHMARKS:
        print(f"ERROR: Benchmark '{benchmark_id}' is not registered.")
        return 1

    # ----- validate task_id format -----
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$", task_id):
        print(f"ERROR: Invalid task_id '{task_id}'")
        return 1

    # ----- validate task exists -----
    task_dirs = [
        PROJECT_ROOT / ".ai" / "tasks" / "active" / task_id,
        PROJECT_ROOT / ".ai" / "tasks" / "completed" / task_id,
    ]
    if not any(d.exists() for d in task_dirs):
        print(f"ERROR: Task '{task_id}' not found in active/ or completed/")
        return 1

    # ----- validate-task -----
    validate_result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "tools" / "ai_workflow.py"),
            "validate-task",
            task_id,
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    if validate_result.returncode != 0:
        print(f"ERROR: validate-task failed for '{task_id}'")
        return 1

    # ----- prepare report directory -----
    run_id = _safe_run_id(benchmark_id)
    report_dir = (REPORTS_DIR / task_id / run_id).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)

    bench_info = BENCHMARKS[benchmark_id]
    cmd = bench_info["cmd"]

    print(f"=== Benchmark: {benchmark_id} ===")
    print(f"Task: {task_id}")
    print(f"Run:  {run_id}")
    print(f"Kind: {bench_info['kind']}")
    print()

    # ----- run benchmark -----
    started_at = datetime.now(timezone.utc)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    finished_at = datetime.now(timezone.utc)
    duration = (finished_at - started_at).total_seconds()

    exit_code = result.returncode
    status = "passed" if exit_code == 0 else "failed"

    # ----- write raw output -----
    raw_path = report_dir / "raw_output.txt"
    raw_path.write_text(
        f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}",
        encoding="utf-8",
    )

    # ----- write JSON report -----
    json_report = {
        "schema_version": 1,
        "benchmark_id": benchmark_id,
        "benchmark_kind": bench_info["kind"],
        "task_id": task_id,
        "run_id": run_id,
        "started_at_utc": started_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "finished_at_utc": finished_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_seconds": round(duration, 3),
        "command": cmd,
        "working_directory": ".",
        "exit_code": exit_code,
        "status": status,
        "stdout_file": "raw_output.txt",
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    json_path = report_dir / "benchmark_report.json"
    json_path.write_text(
        json.dumps(json_report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # ----- write Markdown report -----
    md_path = report_dir / "benchmark_report.md"
    md_path.write_text(
        "\n".join(
            [
                f"# Benchmark Report: {benchmark_id}",
                "",
                f"- **Task:** {task_id}",
                f"- **Run:** {run_id}",
                f"- **Kind:** {bench_info['kind']}",
                f"- **Status:** {status.upper()}",
                f"- **Exit code:** {exit_code}",
                f"- **Duration:** {duration:.3f}s",
            ]
        ),
        encoding="utf-8",
    )

    # ----- write GITHUB_OUTPUT -----
    _write_github_output(report_dir, status)

    # ----- print summary -----
    print(f"Benchmark {status.upper()}")
    print(f"Duration: {duration:.3f}s")
    print(f"Report:   {report_dir}")

    return exit_code


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Safe benchmark runner with ID allowlist",
    )
    parser.add_argument(
        "benchmark_id",
        choices=sorted(BENCHMARKS.keys()),
        help="Registered benchmark identifier",
    )
    parser.add_argument(
        "--task-id",
        required=True,
        help="Task ID associated with this benchmark",
    )
    args = parser.parse_args()
    return run_benchmark(args.benchmark_id, args.task_id)


if __name__ == "__main__":
    sys.exit(main())
