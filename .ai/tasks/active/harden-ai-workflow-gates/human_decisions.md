# Human Decisions: Harden AI-workflow gates

| # | Date | Question | Decision | Rationale |
|---|------|----------|----------|-----------|
| 1 | 2026-08-08 | Only `ai-workflow-smoke` as registered benchmark? | Yes — only existing benchmark | Other benchmarks not yet implemented |
| 2 | 2026-08-08 | Move example task to completed? | Yes — preferred option | Demonstrates real lifecycle |
| 3 | 2026-08-08 | Make lint blocking now? | No — advisory with migration plan | 62+ pre-existing violations need separate task |
| 4 | 2026-08-08 | Make pip-audit blocking? | No — advisory with migration plan | Existing vulnerability baseline unresolved |
