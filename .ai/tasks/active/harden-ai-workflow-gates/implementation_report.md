# Implementation Report

**Task:** harden-ai-workflow-gates
**Date:** 2026-08-08
**Implemented by:** DeepCode

## Summary

Hardened AI-workflow CI/CD infrastructure against multiple security weaknesses
found during architecture audit. Removed arbitrary shell execution from
benchmark workflow, categorized CI checks as blocking vs advisory, fixed
task lifecycle, strengthened validation.

## Changes made

| File | Change type | Description |
|------|-------------|-------------|
| tools/run_benchmark.py | add | Safe benchmark runner with ID allowlist |
| .github/workflows/benchmark.yml | modify | Replaced arbitrary shell input with choice; blocking validation |
| .github/workflows/ci.yml | modify | lint-advisory naming with migration plan |
| .github/workflows/ai-artifacts.yml | modify | Removed `\|\| true` from validation (blocking) |
| .github/workflows/security.yml | modify | dependency-check-advisory naming; secret scan blocking |
| tools/ai_workflow.py | modify | Path traversal check, ADR existence check, benchmark non-empty check, active/completed status consistency, workflow safety scan |
| .ai/tasks/completed/example-ai-workflow-bootstrap/ | move | Moved from active/ to completed/ |
| .ai/tasks/completed/.gitkeep | add | Tracked empty directory |
| .ai/tasks/archived/.gitkeep | add | Tracked empty directory |
| .ai/workflow.md | modify | Added benchmark policy section |
| tests/unit/test_ai_workflow.py | modify | +11 new tests (benchmark runner, hardening validations); 3 skipped |

## Tests added

| Test name | What it verifies |
|-----------|------------------|
| test_unknown_benchmark_id_rejected | Unknown benchmark ID produces error |
| test_registered_benchmark_resolves | Registered ID maps to fixed argument list |
| test_benchmark_never_accepts_shell_command | All benchmarks are lists, not shell strings |
| test_invalid_task_id_rejected | Invalid task_id blocked before benchmark |
| test_benchmark_requires_existing_task | Non-existent task blocked |
| test_path_traversal_rejected | `../` rejected in task-id |
| test_completed_task_requires_final_status | FINAL_STATUSES contains 'completed' |
| test_active_task_not_final | 'draft', 'review' not in FINAL_STATUSES |
| test_workflow_safety_detects_shell_input | `${{ inputs.*command }}` detected |
| test_workflow_safety_passes_clean | Clean workflow does not flag |
| test_benchmark_yml_uses_choice | benchmark.yml uses `type: choice`, no `benchmark_command` |

## Tests executed

```bash
pytest tests/unit/test_ai_workflow.py -v  # 30 passed, 3 skipped
```

## Validation

```bash
python tools/ai_workflow.py check-repo                          # PASSED
python tools/ai_workflow.py validate-task harden-ai-workflow-gates  # PASSED
python tools/ai_workflow.py validate-task example-ai-workflow-bootstrap  # PASSED
```

## Assumptions

- Only `ai-workflow-smoke` benchmark exists; others are template placeholders
- lint and pip-audit remain advisory with documented migration plan
- Workflow safety scan uses regex patterns; not a full YAML parser

## Open issues

- None

## Human decisions required

See [human_decisions.md](human_decisions.md)
