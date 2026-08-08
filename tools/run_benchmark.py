#!/usr/bin/env python3
"""
Safe benchmark runner for NOM-HRMS-FGA.

Maps registered benchmark IDs to fixed argument lists.
Never accepts arbitrary shell commands.
No shell=True, no os.system(), no eval().

Produces structured reports in .ai/reports/benchmarks/<task-id>/<run-id>/
even when the benchmark command fails.

Usage:
    python tools/run_benchmark.py <benchmark_id> --task-id <task_id>

To register a new benchmark, add an entry to BENCHMARKS dict below.
Each entry maps to a list of arguments for subprocess.run().
New benchmark IDs require human-approved PR.
"""

import json
import os
import platform
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / ".ai" / "reports" / "benchmarks"

# ── Registered benchmarks ──────────────────────────────────────────────
# Each key maps to:
#   cmd: list[str] — fixed argument list for subprocess.run()
#   kind: str — "validation_smoke" | "performance" | ...
#
# To add a new benchmark:
# 1. Add a new key here with cmd and kind.
# 2. Open a PR — a human must approve new benchmark IDs.
# 3. Update the workflow input options in .github/workflows/benchmark.yml.

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


def _safe_run_id() -> str:
    """Generate a safe run-id: UTC timestamp + benchmark_id without dangerous chars."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    # No colons, no spaces, no backslashes
    return ts


def run_benchmark(benchmark_id: str, task_id: str) -> int:
    """Run a registered benchmark. Produces structured report. Returns exit code."""
    import re

    # ----- validate benchmark_id -----
    if benchmark_id not in BENCHMARKS:
        print(f"ERROR: Benchmark '{benchmark_id}' is not registered.")
        print(f"Registered IDs: {', '.join(sorted(BENCHMARKS.keys()))}")
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
        print(f"ERROR: validate-task failed for '{task_id}':")
        print(validate_result.stdout)
        print(validate_result.stderr)
        return 1

    # ----- prepare report directory -----
    run_id = _safe_run_id()
    report_dir = REPORTS_DIR / task_id / run_id
    report_dir.mkdir(parents=True, exist_ok=True)

    bench_info = BENCHMARKS[benchmark_id]
    cmd = bench_info["cmd"]

    print(f"=== Benchmark: {benchmark_id} ===")
    print(f"Task: {task_id}")
    print(f"Run:  {run_id}")
    print(f"Kind: {bench_info['kind']}")
    print(f"Command: {' '.join(cmd)}")
    print(f"Report: {report_dir}")
    print()

    # ----- run benchmark -----
    started_at = datetime.now(timezone.utc)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
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
    md_lines = [
        f"# Benchmark Report: {benchmark_id}",
        "",
        f"- **Task:** {task_id}",
        f"- **Run:** {run_id}",
        f"- **Kind:** {bench_info['kind']}",
        f"- **Status:** {status.upper()}",
        f"- **Exit code:** {exit_code}",
        f"- **Duration:** {duration:.3f}s",
        f"- **Python:** {platform.python_version()}",
        f"- **Platform:** {platform.platform()}",
        "",
        "## Command",
        "",
        "```",
        " ".join(cmd),
        "```",
        "",
        "## Output",
        "",
        "<details>",
        "<summary>STDOUT / STDERR</summary>",
        "",
        "```",
        textwrap.shorten(result.stdout + result.stderr, width=10000, placeholder="..."),
        "```",
        "",
        "</details>",
    ]
    md_path = report_dir / "benchmark_report.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    # ----- print summary -----
    print(f"Benchmark {status.upper()}")
    print(f"Duration: {duration:.3f}s")
    print(f"Report:   {report_dir}")
    print(f"  {json_path.name}")
    print(f"  {md_path.name}")
    print(f"  {raw_path.name}")

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
