# Human Decisions: AI Workflow Bootstrap

| # | Date | Question | Decision | Rationale |
|---|------|----------|----------|-----------|
| 1 | 2026-08-08 | JSON vs YAML for task.json | JSON | No external dependency; stdlib json module |
| 2 | 2026-08-08 | Single CLI file vs multiple | Single file | Simpler maintenance |
| 3 | 2026-08-08 | Emoji in CLI output? | ASCII only | Windows cp1252 compatibility |
| 4 | 2026-08-08 | Auto-create git branch? | Explicit flag | Don't assume workflow |
| 5 | 2026-08-08 | Validate completed tasks in CI? | Yes, blocking | Tasks must pass validation at all stages |
| 6 | 2026-08-08 | Reuse existing release_exe.yml? | Yes | Existing workflow is working; new ones are additive |
