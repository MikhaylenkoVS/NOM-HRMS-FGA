#!/usr/bin/env python3
"""
Safe benchmark runner for NOM-HRMS-FGA.

Maps registered benchmark IDs to fixed argument lists.
Never accepts arbitrary shell commands.
No shell=True, no os.system(), no eval().

Usage:
    python tools/run_benchmark.py <benchmark_id> --task-id <task_id>

To register a new benchmark, add an entry to BENCHMARKS dict below.
Each entry maps to a list of arguments for subprocess.run().
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Registered benchmarks ──────────────────────────────────────────────
# Each value is a list of arguments passed to subprocess.run().
# ONLY subprocess.run(cmd, check=True, ...) is used — no shell=True ever.
#
# To add a new benchmark:
# 1. Add a new key here with a descriptive name.
# 2. Map it to a fixed argument list pointing to the benchmark script/command.
# 3. Open a PR — a human must approve new benchmark IDs.
# 4. Update the workflow input options in .github/workflows/benchmark.yml.

BENCHMARKS: dict[str, list[str]] = {
    "ai-workflow-smoke": [
        sys.executable, "-m", "pytest",
        "tests/unit/test_ai_workflow.py", "-q", "--tb=short",
    ],
    # Example template for future benchmarks:
    # "formula-db-search": [
    #     sys.executable, "tools/benchmark_formula_db.py",
    #     "--queries", "1000",
    # ],
    # "package-smoke": [
    #     sys.executable, "-c", "import src; print('import OK')",
    # ],
}


def run_benchmark(benchmark_id: str, task_id: str) -> int:
    """Run a registered benchmark. Returns exit code."""
    if benchmark_id not in BENCHMARKS:
        print(f"ERROR: Benchmark '{benchmark_id}' is not registered.")
        print(f"Registered IDs: {', '.join(sorted(BENCHMARKS.keys()))}")
        print("To register a new benchmark, add it to tools/run_benchmark.py")
        print("and update .github/workflows/benchmark.yml.")
        return 1

    # Validate task_id format (same regex as ai_workflow.py)
    import re
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$", task_id):
        print(f"ERROR: Invalid task_id '{task_id}'")
        return 1

    # Validate task exists and passes validate-task
    task_dir = PROJECT_ROOT / ".ai" / "tasks" / "active" / task_id
    completed_dir = PROJECT_ROOT / ".ai" / "tasks" / "completed" / task_id

    if not task_dir.exists() and not completed_dir.exists():
        print(f"ERROR: Task '{task_id}' not found in active/ or completed/")
        return 1

    # Run validate-task
    validate_result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "tools" / "ai_workflow.py"),
         "validate-task", task_id],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    if validate_result.returncode != 0:
        print(f"ERROR: validate-task failed for '{task_id}':")
        print(validate_result.stdout)
        print(validate_result.stderr)
        return 1

    cmd = BENCHMARKS[benchmark_id]
    print(f"=== Benchmark: {benchmark_id} ===")
    print(f"Task: {task_id}")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


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
