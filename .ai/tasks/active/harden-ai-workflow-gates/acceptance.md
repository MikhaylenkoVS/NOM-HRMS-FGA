# Acceptance Criteria: Harden AI-workflow gates

## Must have

- [ ] benchmark.yml: arbitrary shell input removed, replaced with benchmark_id choice
- [ ] tools/run_benchmark.py: safe runner with allowlist, task validation gate
- [ ] benchmark CLI: `python tools/ai_workflow.py run-benchmark <id> --task-id <id>`
- [ ] ci.yml: lint-advisory naming with migration plan comment
- [ ] ai-artifacts.yml: `|| true` removed from validation (blocking)
- [ ] security.yml: dependency-check-advisory naming with reason
- [ ] example-ai-workflow-bootstrap moved to completed/ with completion_summary.md
- [ ] .gitkeep in completed/ and archived/
- [ ] validate-task: path traversal check, semantic artifact checks
- [ ] check-repo: workflow safety scan (shell injection, registered benchmarks)
- [ ] Tests: 10+ new test cases
- [ ] Documentation updated

## Must not

- [ ] No changes to src/core/, src/app.py, src/ui/, src/structures/
- [ ] No new dependencies
- [ ] No secrets or credentials
- [ ] No push to main

## Test commands

```bash
python tools/ai_workflow.py check-repo
python tools/ai_workflow.py validate-task harden-ai-workflow-gates
pytest tests/unit/test_ai_workflow.py -v
```
