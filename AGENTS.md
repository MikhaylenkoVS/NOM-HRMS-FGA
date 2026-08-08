# AGENTS.md — Rules for AI Agents

Project: NOM-HRMS-FGA — functional-group analyzer for NOM mass spectra.
Stack: Python ≥3.10, setuptools, tkinter (GUI), RDKit, matplotlib, pandas.

## Mandatory Rules

1. **Read before write.** Study README, AGENTS.md, relevant docs/, tests,
   and current module implementation before changing code.

2. **Task packet required.** For architecture, scientific, performance,
   formula-db, packaging, or security tasks, a task packet in
   `.ai/tasks/active/<task-id>/` is mandatory.

3. **Do not touch unrelated files.** Stay within the scope specified in the
   task packet.

4. **Never push to main.** Do not push to `main` or `master`. Use feature
   branches.

5. **No destructive git operations.** No `git push --force`, `git reset --hard`
   on shared branches, `git rebase` of pushed commits.

6. **No secrets.** Never add tokens, keys, passwords, local paths, personal
   data, or API credentials to the repository.

7. **No dependency without justification.** Every new dependency must be
   documented with rationale.

8. **Scientific invariants are sacred.** Do not change chemical/scientific
   rules without an ADR and regression tests on reference data.

9. **Tests before completion.** Run applicable tests before marking a task
   complete.

10. **Implementation report required.** Every completed task must have
    `implementation_report.md` in the task packet.

11. **Benchmark for performance tasks.** Performance tasks require
    `benchmark_report.md` with baseline comparison.

12. **Reference equivalence for scientific tasks.** Scientific tasks require
    a reference-equivalence test on known datasets.

13. **Document ambiguity.** If requirements are unclear, do not guess —
    escalate questions to `human_decisions.md`.

14. **No merge, release, or destructive actions.** Do not perform merge,
    release, publish, push to main, file deletion, or GitHub secrets
    changes without explicit human confirmation.

## Quick Reference

```bash
# Validate a task packet
python tools/ai_workflow.py validate-task <task-id>

# Check entire repository
python tools/ai_workflow.py check-repo

# Run tests
pytest tests/ -q
pytest tests/ -q -m unit
```

## See Also

- `.ai/workflow.md` — full workflow description
- `docs/ai_workflow.md` — detailed process flow
- `docs/ai_task_lifecycle.md` — task lifecycle and statuses
- `CONTRIBUTING.md` — contribution guide for humans
