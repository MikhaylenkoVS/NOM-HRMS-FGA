#!/usr/bin/env python3
"""
AI Workflow CLI for NOM-HRMS-FGA.

Manages task packets, validates artifacts, collects context,
and performs repository health checks.

Usage:
    python tools/ai_workflow.py <command> [<args>...]

Commands:
    new-task        Create a new task packet
    validate-task   Validate a task packet
    collect-context Collect read-only context snapshot
    render-handoff  Generate handoff document for DeepCode
    task-status     Show task status and artifacts
    complete-task   Move task from active/ to completed/
    archive-task    Move task from completed/ to archived/
    check-repo      Run repository health checks

Dependencies: Python stdlib only (json, argparse, datetime, pathlib, etc.)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_DIR = PROJECT_ROOT / ".ai"
TASKS_ACTIVE = AI_DIR / "tasks" / "active"
TASKS_COMPLETED = AI_DIR / "tasks" / "completed"
TASKS_ARCHIVED = AI_DIR / "tasks" / "archived"
TEMPLATES_DIR = AI_DIR / "templates"
CONTRACTS_DIR = AI_DIR / "contracts"
DECISIONS_DIR = AI_DIR / "decisions"
TASK_SCHEMA_PATH = CONTRACTS_DIR / "task.schema.json"

VALID_STATUSES = [
    "draft",
    "designed",
    "implementation",
    "validation",
    "review",
    "approved",
    "merged",
    "completed",
    "archived",
]

VALID_TYPES = [
    "bugfix",
    "feature",
    "refactor",
    "documentation",
    "test",
    "performance",
    "scientific",
    "architecture",
    "formula-db",
    "packaging",
    "security",
    "release",
    "maintenance",
]

VALID_RISK_LEVELS = ["low", "medium", "high", "critical"]

FINAL_STATUSES = {"approved", "merged", "completed"}

REQUIRED_TASK_PACKET_ARTIFACTS = [
    "task.json",
    "design.md",
    "acceptance.md",
    "implementation_report.md",
]

TEMPLATE_PLACEHOLDER_FILES = [
    "task.json",
    "design.md",
    "acceptance.md",
    "constraints.md",
    "risks.md",
    "implementation_report.md",
    "benchmark_report.md",
    "rollback_plan.md",
    "human_decisions.md",
    "review_request.md",
]

SECRET_PATTERNS = [
    r".*\.env$",
    r".*\.pem$",
    r".*\.key$",
    r"secrets\..*",
    r".*credentials.*",
    r".*private.*key.*",
]

FORBIDDEN_BINARY_EXTENSIONS = [
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
    ".dat",
]

ALLOWED_BINARY_DIRS = {"dist/", "build/", "data/formula_db/"}

DEFAULT_MAX_DEPTH = 3
DEFAULT_CONTEXT_COMMITS = 5

# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------


def load_json(path: Path) -> dict:
    """Load a JSON file, returning {} if not found."""
    if not path.is_file():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    """Save data as JSON with indentation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def utc_now() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_git(*args: str, cwd=None) -> str:
    """Run a git command, return stdout or empty string on failure."""
    if cwd is None:
        cwd = PROJECT_ROOT
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def status_icon(status: str) -> str:
    """Return a visual indicator for a task status."""
    icons = {
        "draft": "[draft]",
        "designed": "[designed]",
        "implementation": "[impl]",
        "validation": "[valid]",
        "review": "[review]",
        "approved": "[approved]",
        "merged": "[merged]",
        "completed": "[completed]",
        "archived": "[archived]",
    }
    return icons.get(status, "[unknown]")


# ----------------------------------------------------------------------
# Schema validation (minimal, no external dependencies)
# ----------------------------------------------------------------------


def validate_json_schema(instance: dict, schema: dict, path: str = "$") -> list[str]:
    """Minimal JSON Schema validator. Returns list of error messages."""
    errors = []
    stype = schema.get("type")

    # type check
    if stype == "object" and not isinstance(instance, dict):
        errors.append(f"{path}: expected object, got {type(instance).__name__}")
        return errors
    if stype == "array" and not isinstance(instance, list):
        errors.append(f"{path}: expected array, got {type(instance).__name__}")
        return errors
    if stype == "string" and not isinstance(instance, str):
        errors.append(f"{path}: expected string, got {type(instance).__name__}")
        return errors
    if stype == "integer" and not isinstance(instance, int):
        errors.append(f"{path}: expected integer, got {type(instance).__name__}")
        return errors
    if stype == "boolean" and not isinstance(instance, bool):
        errors.append(f"{path}: expected boolean, got {type(instance).__name__}")
        return errors

    # required properties
    if stype == "object":
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required property '{req}'")

    # properties
    for prop_name, prop_schema in schema.get("properties", {}).items():
        if prop_name in instance:
            child_path = f"{path}.{prop_name}"
            errors.extend(
                validate_json_schema(instance[prop_name], prop_schema, child_path)
            )

    # enum
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: '{instance}' not in {schema['enum']}")

    # pattern
    if "pattern" in schema and isinstance(instance, str):
        if not re.match(schema["pattern"], instance):
            errors.append(
                f"{path}: '{instance}' does not match pattern '{schema['pattern']}'"
            )

    # minLength / maxLength
    if (
        "minLength" in schema
        and isinstance(instance, str)
        and len(instance) < schema["minLength"]
    ):
        errors.append(
            f"{path}: length {len(instance)} < minLength {schema['minLength']}"
        )

    if (
        "maxLength" in schema
        and isinstance(instance, str)
        and len(instance) > schema["maxLength"]
    ):
        errors.append(
            f"{path}: length {len(instance)} > maxLength {schema['maxLength']}"
        )

    # minimum
    if "minimum" in schema and isinstance(instance, (int, float)):
        if instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")

    # items (array)
    if stype == "array" and "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(validate_json_schema(item, schema["items"], f"{path}[{i}]"))

    # type union: ["string", "null"]
    if isinstance(stype, list):
        valid = False
        type_errors = []
        for t in stype:
            sub_schema = {"type": t}
            sub_errors = validate_json_schema(instance, sub_schema, path)
            if not sub_errors:
                valid = True
                break
            type_errors.extend(sub_errors)
        if not valid:
            errors.extend(type_errors)

    # additionalProperties false check (basic)
    if stype == "object" and schema.get("additionalProperties") is False:
        known = set(schema.get("properties", {}).keys())
        unknown = set(instance.keys()) - known
        for uk in sorted(unknown):
            errors.append(f"{path}: unknown property '{uk}'")

    return errors


# ----------------------------------------------------------------------
# Task-id validation
# ----------------------------------------------------------------------


def validate_task_id(task_id: str) -> list[str]:
    """Validate task-id format. Returns list of errors."""
    errors = []
    if not task_id:
        errors.append("task-id cannot be empty")
        return errors
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$", task_id):
        errors.append(
            f"Invalid task-id '{task_id}': must match [a-zA-Z0-9][a-zA-Z0-9._-]*"
        )
    if len(task_id) > 128:
        errors.append(f"task-id too long: {len(task_id)} > 128 characters")
    return errors


# ----------------------------------------------------------------------
# Command: new-task
# ----------------------------------------------------------------------


def cmd_new_task(args) -> int:
    """Create a new task packet."""
    task_id = args.task_id

    # Validate task-id
    id_errors = validate_task_id(task_id)
    if id_errors:
        for e in id_errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    task_dir = TASKS_ACTIVE / task_id

    if task_dir.exists() and not args.force:
        print(
            f"ERROR: Task '{task_id}' already exists. Use --force to overwrite.",
            file=sys.stderr,
        )
        return 1

    if task_dir.exists() and args.force:
        shutil.rmtree(str(task_dir))
        print(f"Overwriting existing task: {task_dir}")

    # Validate type and risk
    if args.type not in VALID_TYPES:
        print(
            f"ERROR: Invalid task type '{args.type}'. Valid: {', '.join(VALID_TYPES)}",
            file=sys.stderr,
        )
        return 1

    if args.risk not in VALID_RISK_LEVELS:
        print(
            f"ERROR: Invalid risk level '{args.risk}'. Valid: {', '.join(VALID_RISK_LEVELS)}",
            file=sys.stderr,
        )
        return 1

    # Create task directory
    task_dir.mkdir(parents=True, exist_ok=True)

    # Create task.json
    task_json = {
        "schema_version": 1,
        "id": task_id,
        "title": args.title or "",
        "status": "draft",
        "type": args.type,
        "risk_level": args.risk,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "owners": {
            "planner": "perplexity",
            "implementer": "deepcode",
            "approver": "human",
        },
        "git": {
            "base_branch": "main",
            "working_branch": args.branch or "",
            "pull_request": None,
        },
        "scope": {
            "allowed_paths": [],
            "forbidden_paths": [],
            "max_changed_files": None,
        },
        "requirements": {
            "must_have": [],
            "must_not": [],
        },
        "validation": {
            "required_checks": [],
            "required_test_commands": [],
            "requires_benchmark": args.type in ("performance",),
            "requires_reference_equivalence": args.type in ("scientific",),
            "requires_adr": args.type in ("architecture", "scientific", "formula-db"),
            "requires_human_approval": True,
        },
        "artifacts": {
            "design": "design.md",
            "acceptance": "acceptance.md",
            "implementation_report": "implementation_report.md",
            "benchmark_report": (
                "benchmark_report.md" if args.type == "performance" else None
            ),
            "rollback_plan": "rollback_plan.md",
        },
        "links": {
            "issue": None,
            "pull_request": None,
            "adr": [],
        },
    }
    save_json(task_dir / "task.json", task_json)

    # Copy template artifacts
    template_files = [
        "design.md",
        "acceptance.md",
        "constraints.md",
        "risks.md",
        "implementation_report.md",
        "human_decisions.md",
        "rollback_plan.md",
    ]
    if args.type == "performance":
        template_files.append("benchmark_report.md")

    for tf in template_files:
        src = TEMPLATES_DIR / tf
        if src.is_file():
            content = src.read_text(encoding="utf-8")
            content = content.replace("{{TASK_ID}}", task_id)
            (task_dir / tf).write_text(content, encoding="utf-8")
        else:
            (task_dir / tf).write_text(
                f"# {tf.replace('.md', '').replace('_', ' ').title()}\n",
                encoding="utf-8",
            )

    # Create context.md with placeholder
    context_md = TEMPLATES_DIR / "context.md"
    if context_md.is_file():
        shutil.copy(str(context_md), str(task_dir / "context.md"))

    # Create review_request.md
    review_tpl = TEMPLATES_DIR / "review_request.md"
    if review_tpl.is_file():
        content = review_tpl.read_text(encoding="utf-8")
        content = content.replace("{{TASK_ID}}", task_id)
        (task_dir / "review_request.md").write_text(content, encoding="utf-8")

    # Create benchmark_report.md if needed
    if args.type == "performance" and (TEMPLATES_DIR / "benchmark_report.md").is_file():
        content = (TEMPLATES_DIR / "benchmark_report.md").read_text(encoding="utf-8")
        content = content.replace("{{TASK_ID}}", task_id)
        (task_dir / "benchmark_report.md").write_text(content, encoding="utf-8")

    # Conditional branch creation
    branch_created = False
    if args.create_branch:
        branch_name = args.branch or f"feature/{task_id}"
        result = run_git("checkout", "-b", branch_name)
        if result:
            print(f"Created branch: {branch_name}")
            branch_created = True
            # Update task.json with branch info
            task_json["git"]["working_branch"] = branch_name
            save_json(task_dir / "task.json", task_json)
        else:
            print(
                f"WARNING: Could not create git branch '{branch_name}'", file=sys.stderr
            )

    # Print summary
    print(f"\n{'='*60}")
    print(f"Task packet created: {status_icon('draft')} {task_id}")
    print(f"{'='*60}")
    print(f"  Type:     {args.type}")
    print(f"  Risk:     {args.risk}")
    print("  Status:   draft")
    print(f"  Location: {task_dir}")
    if branch_created:
        print(f"  Branch:   {args.branch or f'feature/{task_id}'}")
    print("\nNext steps:")
    print("  1. Perplexity: fill in design.md, acceptance.md, constraints.md, risks.md")
    print("  2. Update task.json -> status: designed")
    print(f"  3. Run: python tools/ai_workflow.py render-handoff {task_id}")
    print("  4. DeepCode: implement, run tests, fill implementation_report.md")
    print(f"  5. Run: python tools/ai_workflow.py validate-task {task_id}")
    print("  6. Send for review -> approved by human -> merge")
    print(f"  7. Run: python tools/ai_workflow.py complete-task {task_id}")
    print()

    return 0


# ----------------------------------------------------------------------
# Command: validate-task
# ----------------------------------------------------------------------


def _check_unfinished_markers(file_path: Path) -> list[str]:
    """Check for template placeholders (TODO, TBD, <...>, {{...}})."""
    errors = []
    if not file_path.is_file():
        return errors
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return errors
    # Check for TODO/TBD
    if re.search(r"\bTODO\b", content, re.IGNORECASE):
        errors.append(f"{file_path.name}: contains 'TODO' marker")
    if re.search(r"\bTBD\b", content, re.IGNORECASE):
        errors.append(f"{file_path.name}: contains 'TBD' marker")
    # Check for angle-bracket placeholders like <task-id>, <title>
    if re.search(r"<\w[\w\s-]*>", content):
        errors.append(f"{file_path.name}: contains angle-bracket placeholder '<...>'")
    # Check for {{PLACEHOLDER}} markers
    if re.search(r"\{\{[A-Z_]+\}\}", content):
        errors.append(f"{file_path.name}: contains template placeholder '{{{{...}}}}'")
    return errors


def cmd_validate_task(args) -> int:
    """Validate a task packet."""
    task_id = args.task_id

    # Try active, then completed, then archived
    task_dir = TASKS_ACTIVE / task_id
    location = "active"

    if not task_dir.exists():
        task_dir = TASKS_COMPLETED / task_id
        location = "completed"
    if not task_dir.exists():
        task_dir = TASKS_ARCHIVED / task_id
        location = "archived"
    if not task_dir.exists():
        print(
            f"ERROR: Task '{task_id}' not found in active/, completed/, or archived/",
            file=sys.stderr,
        )
        return 1

    errors = []
    warnings = []

    # 1. Load and validate task.json
    task_json_path = task_dir / "task.json"
    if not task_json_path.is_file():
        errors.append("task.json not found")
        _print_validation_table(errors, warnings)
        return 1 if errors else 0

    task_data = load_json(task_json_path)
    if not task_data:
        errors.append("task.json is empty or invalid JSON")
        _print_validation_table(errors, warnings)
        return 1

    # Schema validation
    schema = load_json(TASK_SCHEMA_PATH)
    if schema:
        schema_errors = validate_json_schema(task_data, schema)
        errors.extend(schema_errors)

    # Cross-field validations
    status = task_data.get("status", "")
    task_type = task_data.get("type", "")
    risk_level = task_data.get("risk_level", "")

    # Valid status
    if status not in VALID_STATUSES:
        errors.append(f"Invalid status: '{status}'")

    # Valid type
    if task_type not in VALID_TYPES:
        errors.append(f"Invalid type: '{task_type}'")

    # Valid risk
    if risk_level not in VALID_RISK_LEVELS:
        errors.append(f"Invalid risk_level: '{risk_level}'")

    # Consistency: requires_benchmark -> benchmark_report artifact
    if task_data.get("validation", {}).get("requires_benchmark"):
        bench_val = task_data.get("artifacts", {}).get("benchmark_report")
        if not bench_val:
            errors.append(
                "requires_benchmark=true but benchmark_report artifact is null or missing"
            )
        elif not isinstance(bench_val, str) or not bench_val.strip():
            errors.append("requires_benchmark=true but benchmark_report path is empty")
        else:
            if not _check_path_safe(task_dir, bench_val):
                errors.append(
                    f"benchmark_report path escapes task directory: {bench_val}"
                )
            else:
                bench_path = task_dir / bench_val
                if not bench_path.is_file():
                    errors.append(f"benchmark_report '{bench_val}' not found")
                elif bench_path.stat().st_size < 50:
                    errors.append(
                        f"benchmark_report '{bench_val}' is empty or too short"
                    )

    # Consistency: requires_adr -> adr links
    if task_data.get("validation", {}).get("requires_adr"):
        adr_list = task_data.get("links", {}).get("adr", [])
        if not adr_list:
            errors.append("requires_adr=true but links.adr is empty")
        else:
            for adr_ref in adr_list:
                if not isinstance(adr_ref, str):
                    errors.append(f"ADR reference is not a string: {adr_ref}")
                    continue
                if ".." in adr_ref or adr_ref.startswith("/"):
                    errors.append(f"ADR path unsafe: {adr_ref}")
                    continue
                adr_path = DECISIONS_DIR / adr_ref
                if not adr_path.is_file():
                    errors.append(f"ADR '{adr_ref}' not found in decisions/")

    # Consistency: requires_reference_equivalence -> reference_validation artifact
    if task_data.get("validation", {}).get("requires_reference_equivalence"):
        ref_val = task_data.get("artifacts", {}).get("reference_validation")
        if not ref_val:
            errors.append(
                "requires_reference_equivalence=true but reference_validation artifact is null or missing"
            )
        elif not isinstance(ref_val, str) or not ref_val.strip():
            errors.append(
                "requires_reference_equivalence=true but reference_validation path is empty"
            )
        else:
            if not _check_path_safe(task_dir, ref_val):
                errors.append(
                    f"reference_validation path escapes task directory: {ref_val}"
                )
            else:
                ref_path = task_dir / ref_val
                if not ref_path.is_file():
                    errors.append(f"reference_validation '{ref_val}' not found")
                elif ref_path.stat().st_size < 20:
                    errors.append(f"reference_validation '{ref_val}' is empty")

    # Check artifact files exist and paths are safe
    for artifact_key in ["design", "acceptance", "implementation_report"]:
        artifact_val = task_data.get("artifacts", {}).get(artifact_key)
        if artifact_val:
            if not _check_path_safe(task_dir, artifact_val):
                errors.append(
                    f"Artifact '{artifact_key}' path escapes task directory: {artifact_val}"
                )
                continue
            art_path = task_dir / artifact_val
            if not art_path.is_file():
                errors.append(f"Required artifact '{artifact_val}' not found")

    # Check rollback_plan if risk is high/critical
    if risk_level in ("high", "critical"):
        rp = task_data.get("artifacts", {}).get("rollback_plan")
        if rp:
            rp_path = task_dir / rp
            if not rp_path.is_file():
                errors.append(
                    f"rollback_plan required for {risk_level} risk but '{rp}' not found"
                )

    # Unfinished markers check for non-draft statuses
    if status not in ("draft", "designed", "implementation"):
        for tf in TEMPLATE_PLACEHOLDER_FILES:
            fpath = task_dir / tf
            marker_errors = _check_unfinished_markers(fpath)
            errors.extend(marker_errors)

    # Location consistency: completed tasks in completed/ , archived in archived/
    if status in ("completed", "merged") and location != "completed":
        if location != "active":
            warnings.append(f"Task status is '{status}' but located in {location}/")
    if status == "archived" and location != "archived":
        warnings.append(f"Task status is 'archived' but located in {location}/")

    # Path traversal check in artifact paths
    for key, val in task_data.get("artifacts", {}).items():
        if val and isinstance(val, str) and ".." in val:
            errors.append(f"Artifact path '{key}' contains path traversal: {val}")

    # requires_adr: check linked ADRs exist
    if task_data.get("validation", {}).get("requires_adr"):
        adr_list = task_data.get("links", {}).get("adr", [])
        for adr_ref in adr_list:
            adr_path = DECISIONS_DIR / adr_ref
            if not adr_path.is_file():
                errors.append(f"ADR '{adr_ref}' referenced but not found in decisions/")

    # requires_benchmark: check report exists and is non-empty
    if task_data.get("validation", {}).get("requires_benchmark"):
        bench_val = task_data.get("artifacts", {}).get("benchmark_report")
        if bench_val:
            bp = task_dir / bench_val
            if bp.is_file() and bp.stat().st_size < 50:
                errors.append(f"benchmark_report '{bench_val}' is empty or too short")

    # requires_reference_equivalence: check reference validation artifact
    if task_data.get("validation", {}).get("requires_reference_equivalence"):
        ref_artifact = task_data.get("artifacts", {}).get("reference_validation")
        if ref_artifact:
            rp = task_dir / ref_artifact
            if not rp.is_file():
                errors.append(f"reference_validation '{ref_artifact}' not found")

    # Active tasks must not have post-merge status (approved is pre-merge)
    FINAL_ACTIVE_BLOCKED = {"completed", "merged", "archived"}
    if location == "active" and status in FINAL_ACTIVE_BLOCKED:
        errors.append(
            f"Task in active/ has final status '{status}'. Move to completed/."
        )

    # Completed tasks must have final status
    if location == "completed" and status not in FINAL_STATUSES:
        errors.append(f"Task in completed/ has non-final status '{status}'.")

    # Print results
    _print_validation_table(errors, warnings)

    if errors:
        print(
            f"\n{len(errors)} error(s), {len(warnings)} warning(s) -- VALIDATION FAILED"
        )
        return 1
    else:
        print(f"\n{len(warnings)} warning(s) -- VALIDATION PASSED")
        return 0


def _print_validation_table(errors: list[str], warnings: list[str]) -> None:
    """Pretty-print validation results."""
    if not errors and not warnings:
        print("No issues found.")
        return

    print(f"\n{'Level':<7} {'Message':<80}")
    print("-" * 87)
    for e in errors:
        print(f"{'ERROR':<7} {e}")
    for w in warnings:
        print(f"{'WARN':<7} {w}")


# ----------------------------------------------------------------------
# Command: collect-context
# ----------------------------------------------------------------------


def cmd_collect_context(args) -> int:
    """Collect read-only context snapshot."""
    task_id = args.task_id
    task_dir = TASKS_ACTIVE / task_id

    if not task_dir.exists():
        task_dir = TASKS_COMPLETED / task_id
    if not task_dir.exists():
        print(
            f"ERROR: Task '{task_id}' not found in active/ or completed/",
            file=sys.stderr,
        )
        return 1

    # Collect context
    lines = []
    lines.append(f"# Context Snapshot: {task_id}")
    lines.append(f"**Generated:** {utc_now()}")
    lines.append("")

    # Git info
    lines.append("## Git")
    branch = run_git("branch", "--show-current")
    lines.append(f"- **Branch:** {branch or 'unknown'}")
    commit = run_git("rev-parse", "HEAD")
    lines.append(f"- **Commit:** {commit or 'unknown'}")
    lines.append("")

    status = run_git("status", "--short")
    lines.append("### Git Status")
    lines.append("```")
    lines.append(status or "(clean)")
    lines.append("```")
    lines.append("")

    changed_files = run_git("diff", "--name-only", "HEAD")
    lines.append("### Changed Files")
    if changed_files:
        for cf in changed_files.split("\n"):
            lines.append(f"- {cf.strip()}")
    else:
        lines.append("(no uncommitted changes)")
    lines.append("")

    # Last N commits
    num_commits = args.commits or DEFAULT_CONTEXT_COMMITS
    log = run_git("log", f"-{num_commits}", "--oneline", "--no-decorate")
    lines.append(f"### Recent Commits (last {num_commits})")
    lines.append("```")
    lines.append(log or "(no commits)")
    lines.append("```")
    lines.append("")

    # Python version
    py_ver = sys.version
    lines.append("## Environment")
    lines.append(f"- **Python:** {py_ver.split()[0]}")
    lines.append(f"- **Executable:** {sys.executable}")

    # Venv path (sanitized -- only if relative or generic)
    venv = os.environ.get("VIRTUAL_ENV", "")
    if venv and not any(
        p in venv.lower() for p in ["users/", "home/", "mvs", "documents"]
    ):
        lines.append(f"- **Virtual env:** {venv}")
    lines.append("")

    # Available test/lint commands
    lines.append("## Available Commands")
    lines.append("- **Run all tests:** `pytest tests/ -q`")
    lines.append("- **Unit tests:** `pytest tests/ -q -m unit`")
    lines.append("- **Integration tests:** `pytest tests/ -q -m integration`")
    lines.append("- **Smoke tests:** `pytest tests/ -q -m smoke`")
    lines.append("- **Lint (flake8):** `flake8 src/ tests/`")
    lines.append("- **Format (black):** `black --check src/ tests/`")
    lines.append("- **Check repo:** `python tools/ai_workflow.py check-repo`")
    lines.append("")

    # GitHub workflows
    wf_dir = PROJECT_ROOT / ".github" / "workflows"
    lines.append("## GitHub Workflows")
    if wf_dir.is_dir():
        for wf in sorted(wf_dir.glob("*.yml")):
            lines.append(f"- {wf.name}")
    lines.append("")

    # Directory tree (limited)
    lines.append("## Directory Tree (limited depth)")
    tree_lines = _dir_tree(PROJECT_ROOT, max_depth=args.depth or DEFAULT_MAX_DEPTH)
    lines.append("```")
    lines.extend(tree_lines)
    lines.append("```")
    lines.append("")

    # AGENTS.md content
    agents_path = PROJECT_ROOT / "AGENTS.md"
    if agents_path.is_file():
        lines.append("## AGENTS.md")
        lines.append("```markdown")
        agents_content = agents_path.read_text(encoding="utf-8")
        # Truncate if too long
        if len(agents_content) > 3000:
            agents_content = agents_content[:3000] + "\n... (truncated)"
        lines.append(agents_content)
        lines.append("```")
        lines.append("")

    # Task files
    lines.append("## Task Packet Files")
    if task_dir.is_dir():
        for f in sorted(task_dir.rglob("*")):
            if f.is_file():
                rel = f.relative_to(task_dir)
                lines.append(f"- {rel}")

    # Write output
    output_path = task_dir / "context_snapshot.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Context snapshot written to: {output_path}")
    return 0


def _dir_tree(
    path: Path, prefix: str = "", max_depth: int = 3, _depth: int = 0
) -> list[str]:
    """Generate a simple directory tree."""
    if _depth > max_depth:
        return [f"{prefix}..."]
    lines = []
    try:
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return [f"{prefix}(permission denied)"]
    # Filter out some noisy dirs
    skip_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist",
        ".idea",
        "nom_hrms_fga.egg-info",
    }
    entries = [e for e in entries if e.name not in skip_dirs]

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "+-- " if is_last else "|-- "
        lines.append(f"{prefix}{connector}{entry.name}")
        if entry.is_dir() and _depth < max_depth:
            ext_prefix = "    " if is_last else "|   "
            lines.extend(_dir_tree(entry, prefix + ext_prefix, max_depth, _depth + 1))
    return lines


# ----------------------------------------------------------------------
# Command: render-handoff
# ----------------------------------------------------------------------


def cmd_render_handoff(args) -> int:
    """Generate deepcode_handoff.md from task packet."""
    task_id = args.task_id
    task_dir = TASKS_ACTIVE / task_id

    if not task_dir.exists():
        print(f"ERROR: Task '{task_id}' not found in active/", file=sys.stderr)
        return 1

    task_data = load_json(task_dir / "task.json")
    if not task_data:
        print("ERROR: task.json not found or empty", file=sys.stderr)
        return 1

    lines = []
    lines.append(f"# DeepCode Handoff: {task_id}")
    lines.append(f"**Generated:** {utc_now()}")
    lines.append("")

    # Goal
    lines.append("## Goal")
    lines.append(task_data.get("title", "No title"))
    lines.append("")

    # Scope
    lines.append("## Scope")
    scope = task_data.get("scope", {})
    allowed = scope.get("allowed_paths", [])
    if allowed:
        for p in allowed:
            lines.append(f"- {p}")
    else:
        lines.append("(not specified)")
    lines.append("")

    # Forbidden paths
    lines.append("## Forbidden Paths")
    forbidden = scope.get("forbidden_paths", [])
    if forbidden:
        for p in forbidden:
            lines.append(f"- **{p}** -- DO NOT MODIFY")
    else:
        lines.append("(none specified)")
    lines.append("")

    # Design summary (first 50 lines from design.md)
    design_file = task_dir / "design.md"
    if design_file.is_file():
        lines.append("## Design")
        design_content = design_file.read_text(encoding="utf-8")
        lines.append(design_content[:2000])
        if len(design_content) > 2000:
            lines.append("\n... (truncated, see design.md for full)")
    lines.append("")

    # Constraints
    constraints_file = task_dir / "constraints.md"
    if constraints_file.is_file():
        lines.append("## Constraints")
        constr_content = constraints_file.read_text(encoding="utf-8")
        lines.append(constr_content[:1500])
    lines.append("")

    # Acceptance criteria
    acceptance_file = task_dir / "acceptance.md"
    if acceptance_file.is_file():
        lines.append("## Acceptance Criteria")
        acc_content = acceptance_file.read_text(encoding="utf-8")
        lines.append(acc_content[:1500])
    lines.append("")

    # Validation commands
    lines.append("## Validation Commands")
    test_cmds = task_data.get("validation", {}).get("required_test_commands", [])
    if test_cmds:
        for cmd in test_cmds:
            lines.append(f"```bash\n{cmd}\n```")
    lines.append("```bash")
    lines.append("pytest tests/ -q          # All tests")
    lines.append("pytest tests/ -q -m unit  # Unit tests only")
    lines.append("```")
    lines.append("")

    # Risk
    lines.append(f"## Risk Level: **{task_data.get('risk_level', 'unknown').upper()}**")
    lines.append("")

    # Required artifacts
    lines.append("## Required Artifacts")
    artifacts = task_data.get("artifacts", {})
    for k, v in artifacts.items():
        if v:
            lines.append(f"- [{k}]({v})")
    lines.append("")

    # Open questions (from human_decisions.md)
    hd_file = task_dir / "human_decisions.md"
    if hd_file.is_file():
        hd_content = hd_file.read_text(encoding="utf-8")
        lines.append("## Open Questions / Human Decisions")
        lines.append(hd_content[:1000])
    lines.append("")

    # Mandatory instructions
    lines.append("## Mandatory Instructions for DeepCode")
    lines.append("")
    lines.append("1. Read `AGENTS.md` at repo root before starting.")
    lines.append("2. Study existing code -- do not guess about non-existent APIs.")
    lines.append("3. Stay within scope. Do not modify forbidden paths.")
    lines.append("4. Implement only what is asked. No scope creep.")
    lines.append("5. Add tests for new functionality.")
    lines.append("6. Run validation commands before reporting completion.")
    lines.append("7. Update `implementation_report.md` in the task packet.")
    lines.append("8. Mark assumptions clearly in the report.")
    lines.append("9. **DO NOT merge, release, or push to main.**")
    lines.append("10. Return `implementation_report.md` when done.")
    lines.append("")

    output_path = task_dir / "deepcode_handoff.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Handoff document written to: {output_path}")

    # Also try to print to stdout for easy copying (may fail on Windows cp1252)
    print(f"\n{'='*60}")
    print("Handoff ready. File saved. To view:")
    print(f"  type {output_path}")
    print(f"{'='*60}")

    return 0


# ----------------------------------------------------------------------
# Command: task-status
# ----------------------------------------------------------------------


def cmd_task_status(args) -> int:
    """Show task status."""
    task_id = args.task_id
    task_dir = None
    location = "unknown"

    for loc, base in [
        ("active", TASKS_ACTIVE),
        ("completed", TASKS_COMPLETED),
        ("archived", TASKS_ARCHIVED),
    ]:
        candidate = base / task_id
        if candidate.exists():
            task_dir = candidate
            location = loc
            break

    if task_dir is None:
        print(f"ERROR: Task '{task_id}' not found", file=sys.stderr)
        return 1

    task_data = load_json(task_dir / "task.json")
    if not task_data:
        print(f"No task.json in {task_dir}")
        return 1

    status = task_data.get("status", "unknown")
    print(f"\n{'='*60}")
    print(f"Task: {task_id}")
    print(f"{'='*60}")
    print(f"  Status:   {status_icon(status)} {status}")
    print(f"  Type:     {task_data.get('type', '?')}")
    print(f"  Risk:     {task_data.get('risk_level', '?')}")
    print(f"  Title:    {task_data.get('title', '?')}")
    print(f"  Location: {location}/")
    print(f"  Branch:   {task_data.get('git', {}).get('working_branch', '?')}")
    print(f"  PR:       {task_data.get('links', {}).get('pull_request', 'none')}")
    print()

    # Artifacts
    print("Artifacts:")
    for f in sorted(task_dir.rglob("*")):
        if f.is_file():
            rel = f.relative_to(task_dir)
            size = f.stat().st_size
            icon = "[OK]" if size > 0 else "[ ]"
            print(f"  {icon} {rel} ({_format_size(size)})")

    print()
    return 0


def _format_size(size: int) -> str:
    """Format file size human-readably."""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    else:
        return f"{size / (1024 * 1024):.1f}MB"


# ----------------------------------------------------------------------
# Command: complete-task
# ----------------------------------------------------------------------


def cmd_complete_task(args) -> int:
    """Move task from active/ to completed/."""
    task_id = args.task_id
    src_dir = TASKS_ACTIVE / task_id

    if not src_dir.exists():
        print(f"ERROR: Task '{task_id}' not found in active/", file=sys.stderr)
        return 1

    task_data = load_json(src_dir / "task.json")
    if not task_data:
        print("ERROR: No task.json found", file=sys.stderr)
        return 1

    status = task_data.get("status", "")

    # Check status is a final pre-merge status
    if status not in FINAL_STATUSES:
        print(
            f"ERROR: Task status '{status}' is not a final pre-merge status. "
            f"Required: {', '.join(sorted(FINAL_STATUSES))}",
            file=sys.stderr,
        )
        return 1

    # Validate first
    print("Running validation...")
    from argparse import Namespace

    val_args = Namespace(task_id=task_id)
    val_result = cmd_validate_task(val_args)
    if val_result != 0:
        print(
            "ERROR: Validation failed. Fix issues before completing.", file=sys.stderr
        )
        return 1

    # Check implementation report
    impl_report = src_dir / "implementation_report.md"
    if not impl_report.is_file() or impl_report.stat().st_size < 50:
        print(
            "ERROR: implementation_report.md is missing or too short", file=sys.stderr
        )
        return 1

    # Check benchmark if required
    if task_data.get("validation", {}).get("requires_benchmark"):
        bench_val = task_data.get("artifacts", {}).get("benchmark_report")
        if bench_val:
            bench_path = src_dir / bench_val
            if not bench_path.is_file() or bench_path.stat().st_size < 50:
                print(
                    "ERROR: benchmark_report required but missing or empty",
                    file=sys.stderr,
                )
                return 1
    else:
        pass

    # Check ADR if required
    if task_data.get("validation", {}).get("requires_adr"):
        adrs = task_data.get("links", {}).get("adr", [])
        if not adrs:
            print("ERROR: requires_adr=true but no ADR references", file=sys.stderr)
            return 1

    # Move to completed
    dst_dir = TASKS_COMPLETED / task_id
    if dst_dir.exists():
        if args.force:
            shutil.rmtree(str(dst_dir))
        else:
            print(
                "ERROR: Task already exists in completed/. Use --force to overwrite.",
                file=sys.stderr,
            )
            return 1

    shutil.move(str(src_dir), str(dst_dir))

    # Update task.json
    task_data["status"] = "completed"
    task_data["updated_at"] = utc_now()
    save_json(dst_dir / "task.json", task_data)

    # Create completion summary
    summary = []
    summary.append(f"# Completion Summary: {task_id}")
    summary.append(f"**Completed:** {utc_now()}")
    summary.append(f"**Type:** {task_data.get('type')}")
    summary.append(f"**Risk:** {task_data.get('risk_level')}")
    summary.append(
        f"**Working branch:** {task_data.get('git', {}).get('working_branch', 'N/A')}"
    )
    summary.append(f"**PR:** {task_data.get('links', {}).get('pull_request', 'none')}")
    summary.append("")
    summary.append("## Artifacts")
    for f in sorted(dst_dir.rglob("*")):
        if f.is_file():
            summary.append(f"- {f.relative_to(dst_dir)}")
    (dst_dir / "completion_summary.md").write_text("\n".join(summary), encoding="utf-8")

    print(f"Task '{task_id}' moved to completed/")
    print(f"  {dst_dir}")
    print(f"\nNext: archive with `python tools/ai_workflow.py archive-task {task_id}`")
    return 0


# ----------------------------------------------------------------------
# Command: archive-task
# ----------------------------------------------------------------------


def cmd_archive_task(args) -> int:
    """Move task from completed/ to archived/."""
    task_id = args.task_id
    src_dir = TASKS_COMPLETED / task_id

    if not src_dir.exists():
        src_dir = TASKS_ACTIVE / task_id
        if src_dir.exists():
            print(
                f"ERROR: Task '{task_id}' is still in active/. Complete it first.",
                file=sys.stderr,
            )
            return 1
        print(f"ERROR: Task '{task_id}' not found in completed/", file=sys.stderr)
        return 1

    task_data = load_json(src_dir / "task.json")
    status = task_data.get("status", "")

    if status not in ("completed", "merged", "archived"):
        print(
            f"ERROR: Cannot archive task with status '{status}'. Must be completed or merged.",
            file=sys.stderr,
        )
        return 1

    dst_dir = TASKS_ARCHIVED / task_id
    if dst_dir.exists():
        if args.force:
            shutil.rmtree(str(dst_dir))
        else:
            print("ERROR: Task already in archived/. Use --force.", file=sys.stderr)
            return 1

    shutil.move(str(src_dir), str(dst_dir))

    # Update status
    task_data["status"] = "archived"
    task_data["updated_at"] = utc_now()
    save_json(dst_dir / "task.json", task_data)

    print(f"Task '{task_id}' archived -> {dst_dir}")
    return 0


# ----------------------------------------------------------------------
# Command: check-repo
# ----------------------------------------------------------------------


def cmd_check_repo(args) -> int:
    """Run repository health checks."""
    errors = []
    warnings = []

    # 1. AGENTS.md exists
    if not (PROJECT_ROOT / "AGENTS.md").is_file():
        errors.append("AGENTS.md not found at repo root")

    # 2. .ai/README.md exists
    if not (AI_DIR / "README.md").is_file():
        errors.append(".ai/README.md not found")

    # 3. Templates exist
    expected_templates = [
        "task.json",
        "context.md",
        "design.md",
        "acceptance.md",
        "constraints.md",
        "risks.md",
        "implementation_report.md",
        "benchmark_report.md",
        "review_request.md",
        "human_decisions.md",
        "rollback_plan.md",
    ]
    for t in expected_templates:
        if not (TEMPLATES_DIR / t).is_file():
            errors.append(f"Template missing: {t}")

    # 4. JSON schemas exist
    expected_schemas = [
        "task.schema.json",
        "implementation_report.schema.json",
        "benchmark_report.schema.json",
    ]
    for s in expected_schemas:
        if not (CONTRACTS_DIR / s).is_file():
            errors.append(f"Contract missing: {s}")

    # 5. ADR index exists
    if not (DECISIONS_DIR / "index.md").is_file():
        warnings.append("ADR index.md not found")

    # 6. GitHub workflows -- at minimum ci.yml should exist
    wf_dir = PROJECT_ROOT / ".github" / "workflows"
    if not wf_dir.is_dir():
        warnings.append(".github/workflows/ directory not found")
    elif not (wf_dir / "ci.yml").is_file():
        warnings.append("ci.yml workflow not found (standard CI)")

    # 7. Check for accidentally tracked secrets
    SKIP_DIRS = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        ".pytest_cache",
        ".mypy_cache",
        ".idea",
        "build",
        "dist",
        "node_modules",
    }
    for root, dirs, files in os.walk(str(PROJECT_ROOT)):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            for pattern in SECRET_PATTERNS:
                if re.match(pattern, fname):
                    errors.append(
                        f"Secret-like file detected: {os.path.relpath(os.path.join(root, fname), PROJECT_ROOT)}"
                    )

    # 8. Large binary files outside allowed dirs (heuristic: > 5MB)
    for root, dirs, files in os.walk(str(PROJECT_ROOT)):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel_root = os.path.relpath(root, PROJECT_ROOT).replace("\\", "/")
        # Skip if inside an allowed binary directory
        if any(
            rel_root == ad.rstrip("/") or rel_root.startswith(ad)
            for ad in ALLOWED_BINARY_DIRS
        ):
            continue
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                size = os.path.getsize(fpath)
            except OSError:
                continue
            if size > 5 * 1024 * 1024:
                warnings.append(
                    f"Large binary file ({_format_size(size)}): {rel_root}/{fname}"
                )

    # 9. Unfinished tasks in completed/
    if TASKS_COMPLETED.is_dir():
        for task_dir in TASKS_COMPLETED.iterdir():
            if task_dir.is_dir():
                task_data = load_json(task_dir / "task.json")
                status = task_data.get("status", "")
                if status not in ("completed", "merged", "archived"):
                    errors.append(
                        f"Task in completed/ has non-final status: {task_dir.name} -> {status}"
                    )

    # 10. ADR index consistency
    index_path = DECISIONS_DIR / "index.md"
    if index_path.is_file():
        index_content = index_path.read_text(encoding="utf-8")
        # Find ADR references like [NNNN](NNNN-title.md)
        adr_refs = re.findall(r"\[(\d{4})\]\((\d{4}[^)]+\.md)\)", index_content)
        for num, filename in adr_refs:
            adr_path = DECISIONS_DIR / filename
            if not adr_path.is_file():
                errors.append(f"ADR referenced in index but not found: {filename}")

            # Check for duplicate ADR numbers
            nums = [n for n, _ in adr_refs]
            if nums.count(num) > 1:
                errors.append(f"Duplicate ADR number in index: {num}")

    # 11. Task packets in active/ must not have final status
    if TASKS_ACTIVE.is_dir():
        for task_dir in TASKS_ACTIVE.iterdir():
            if task_dir.is_dir():
                task_data = load_json(task_dir / "task.json")
                status = task_data.get("status", "")
                if status in ("completed", "merged", "archived"):
                    errors.append(
                        f"Task in active/ has final status: {task_dir.name} -> {status}"
                    )

    # 12. Workflow safety scan
    wf_dir = PROJECT_ROOT / ".github" / "workflows"
    if wf_dir.is_dir():
        for wf_file in sorted(wf_dir.glob("*.yml")):
            _check_workflow_safety(wf_file, errors, warnings)

    # Print results
    _print_validation_table(errors, warnings)

    if errors:
        print(
            f"\n{len(errors)} error(s), {len(warnings)} warning(s) -- REPO CHECK FAILED"
        )
        return 1
    else:
        print(f"\n{len(warnings)} warning(s) -- REPO CHECK PASSED")
        return 0


def _check_path_safe(task_dir: Path, artifact_path: str) -> bool:
    """Check that artifact_path does not escape task_dir via path traversal."""
    if os.path.isabs(artifact_path):
        return False
    if re.match(r"^[A-Za-z]:", artifact_path) or artifact_path.startswith("\\\\"):
        return False
    if ".." in Path(artifact_path).parts:
        return False
    try:
        resolved = (task_dir / artifact_path).resolve()
        task_root = task_dir.resolve()
        if hasattr(resolved, "is_relative_to"):
            return resolved.is_relative_to(task_root)
        return str(resolved).startswith(str(task_root) + os.sep)
    except (ValueError, OSError):
        return False


def _check_workflow_safety(wf_file: Path, errors: list, warnings: list) -> None:
    """Scan a workflow YAML for unsafe patterns."""
    try:
        content = wf_file.read_text(encoding="utf-8")
    except Exception:
        return

    wf_name = wf_file.name

    # Detect shell injection: unsafe input names used in ${{ inputs.X }}
    unsafe_input_patterns = [
        r"\$\{\{\s*inputs\.\w*(?:command|script|shell|args|module|expression)\w*\s*\}\}",
    ]
    for pattern in unsafe_input_patterns:
        if re.search(pattern, content):
            errors.append(
                f"Workflow safety: {wf_name} contains unsafe shell-injectable input "
                f"(matches '{pattern}'). Replace with choice input and allowlisted runner."
            )

    # Detect shell=True in run steps
    if re.search(r"shell\s*:\s*True", content):
        warnings.append(
            f"Workflow safety: {wf_name} uses shell:true in a subprocess call."
        )

    # Detect failure swallowing
    if wf_name == "benchmark.yml":
        if re.search(r"\|\|\s*true", content) or re.search(r"\|\|\s*echo", content):
            errors.append(
                "Workflow safety: benchmark.yml must not swallow failures with || true or || echo."
            )
        if re.search(r"set\s+\+e", content):
            errors.append("Workflow safety: benchmark.yml must not use set +e.")
        if re.search(r"if-no-files-found:\s*ignore", content):
            errors.append(
                "Workflow safety: benchmark.yml must not ignore missing artifacts."
            )

    # Strict benchmark.yml policy
    if wf_name == "benchmark.yml":
        # Must NOT contain unsafe input names as workflow_dispatch inputs
        forbidden_inputs = [
            "benchmark_command",
            "shell_command",
            "script",
            "command",
            "args",
            "module",
            "expression",
        ]
        # Find input keys in workflow_dispatch section
        input_keys = re.findall(r"^\s{6}(\w+):\s*$", content, re.MULTILINE)
        for ik in input_keys:
            if ik in forbidden_inputs:
                errors.append(
                    f"Workflow safety: benchmark.yml input '{ik}' is forbidden. "
                    f"Allowed: task_id, benchmark_id, upload_artifact."
                )
        # Must use type: choice for benchmark_id
        if "benchmark_id" in content and "type: choice" not in content:
            errors.append(
                "Workflow safety: benchmark.yml must use 'type: choice' for benchmark_id."
            )
        # Must have non-empty options
        if "type: choice" in content:
            if "options:" not in content:
                errors.append(
                    "Workflow safety: benchmark.yml choice input has no options."
                )
        # Must launch via run_benchmark.py
        if "run:" in content and "run_benchmark.py" not in content:
            if wf_name == "benchmark.yml":
                warnings.append(
                    "Workflow safety: benchmark.yml run step should use tools/run_benchmark.py."
                )


# ----------------------------------------------------------------------
# CLI entry point
# ----------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI Workflow CLI for NOM-HRMS-FGA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # new-task
    p_new = sub.add_parser("new-task", help="Create a new task packet")
    p_new.add_argument("task_id", help="Task identifier (e.g., 2026-08-08-fix-denoise)")
    p_new.add_argument("--title", default="", help="Task title")
    p_new.add_argument(
        "--type", default="feature", choices=VALID_TYPES, help="Task type"
    )
    p_new.add_argument(
        "--risk", default="medium", choices=VALID_RISK_LEVELS, help="Risk level"
    )
    p_new.add_argument("--branch", default="", help="Working branch name")
    p_new.add_argument("--create-branch", action="store_true", help="Create git branch")
    p_new.add_argument("--force", action="store_true", help="Overwrite existing task")
    p_new.set_defaults(func=cmd_new_task)

    # validate-task
    p_val = sub.add_parser("validate-task", help="Validate a task packet")
    p_val.add_argument("task_id", help="Task identifier")
    p_val.set_defaults(func=cmd_validate_task)

    # collect-context
    p_ctx = sub.add_parser("collect-context", help="Collect read-only context snapshot")
    p_ctx.add_argument("task_id", help="Task identifier")
    p_ctx.add_argument(
        "--depth", type=int, default=DEFAULT_MAX_DEPTH, help="Directory tree depth"
    )
    p_ctx.add_argument(
        "--commits",
        type=int,
        default=DEFAULT_CONTEXT_COMMITS,
        help="Number of recent commits",
    )
    p_ctx.set_defaults(func=cmd_collect_context)

    # render-handoff
    p_ho = sub.add_parser("render-handoff", help="Generate handoff for DeepCode")
    p_ho.add_argument("task_id", help="Task identifier")
    p_ho.set_defaults(func=cmd_render_handoff)

    # task-status
    p_ts = sub.add_parser("task-status", help="Show task status")
    p_ts.add_argument("task_id", help="Task identifier")
    p_ts.set_defaults(func=cmd_task_status)

    # complete-task
    p_comp = sub.add_parser("complete-task", help="Move task to completed/")
    p_comp.add_argument("task_id", help="Task identifier")
    p_comp.add_argument(
        "--force", action="store_true", help="Overwrite if exists in completed/"
    )
    p_comp.set_defaults(func=cmd_complete_task)

    # archive-task
    p_arch = sub.add_parser("archive-task", help="Move task to archived/")
    p_arch.add_argument("task_id", help="Task identifier")
    p_arch.add_argument(
        "--force", action="store_true", help="Overwrite if exists in archived/"
    )
    p_arch.set_defaults(func=cmd_archive_task)

    # check-repo
    p_chk = sub.add_parser("check-repo", help="Run repository health checks")
    p_chk.set_defaults(func=cmd_check_repo)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
