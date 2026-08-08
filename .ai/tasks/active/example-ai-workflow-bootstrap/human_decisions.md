# Human Decisions: AI Workflow Bootstrap

| # | Date | Question | Decision | Rationale |
|---|------|----------|----------|-----------|
| 1 | 2026-08-08 | JSON vs YAML for task.json | JSON | No external dependency; stdlib json module sufficient |
| 2 | 2026-08-08 | Single CLI file vs multiple | Single file | Simpler maintenance; all commands in one place |
| 3 | 2026-08-08 | Emoji in CLI output? | ASCII only | Windows cp1252 console compatibility |
| 4 | 2026-08-08 | Auto-create git branch? | Explicit flag `--create-branch` | Don't assume workflow; some tasks don't need branches |
| 5 | 2026-08-08 | Validate completed tasks in CI? | Yes, with `|| true` | Warnings should not block CI for pre-existing issues |
| 6 | 2026-08-08 | Reuse existing release_exe.yml? | Yes, leave unchanged | Existing workflow is working; new workflows are additive |
