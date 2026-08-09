# Design: Harden AI-workflow CI gates and benchmark execution

## Problem

Architecture audit found multiple security weaknesses:

1. **Arbitrary shell execution** in `benchmark.yml`: `${{ inputs.benchmark_command }}` is injected directly into shell — an attacker with workflow_dispatch access can execute arbitrary commands.

2. **Undisciplined continue-on-error**: linting failures hidden, task validation failures swallowed with `|| true`, pip-audit failures invisible.

3. **Task lifecycle inconsistency**: `example-ai-workflow-bootstrap` has filled implementation report and checked acceptance criteria but sits in `active/`.

4. **Weak validation**: `validate-task` checks file existence but not semantic correctness. `check-repo` doesn't scan workflows for unsafe patterns.

## Solution

### 1. Safe benchmark runner

Replace arbitrary `benchmark_command` input with `benchmark_id` choice. Runner uses hardcoded allowlist:

```python
BENCHMARKS = {
    "ai-workflow-smoke": ["python", "-m", "pytest", "tests/unit/test_ai_workflow.py", "-q"],
}
```

- No `shell=True`, no `os.system()`, no `eval()`
- Validates task_id before execution
- Validates `validate-task` passes before benchmark
- Unknown IDs produce blocking failure

### 2. CI policy: blocking vs advisory

| Check | Category | Reason |
|-------|----------|--------|
| Unit tests | blocking | Core safety net |
| AI task validation | blocking | Scientific gate |
| check-repo | blocking | Infrastructure health |
| Lint (flake8, black) | advisory | Pre-existing 62+ violations |
| pip-audit | advisory | Existing vulnerability baseline |
| Secret scan | blocking | Security gate |

Advisory checks: named with `-advisory` suffix, commented with migration plan, visible in logs (no `|| true` swallowing).

### 3. Task lifecycle: complete example

Move `example-ai-workflow-bootstrap` to `completed/`, create `completion_summary.md`.

### 4. Strengthened validation

- Path traversal detection (`../`)
- Workflow safety scan in check-repo
- Completed tasks must have final status
- Active tasks must not have final status
