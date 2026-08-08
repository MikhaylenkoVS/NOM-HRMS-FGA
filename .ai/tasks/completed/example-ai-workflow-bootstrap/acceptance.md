# Acceptance Criteria: AI Workflow Bootstrap

## Must have

- [x] `AGENTS.md` with 14 mandatory rules
- [x] Task packet protocol: `.ai/tasks/active/`, `task.json`, artifacts
- [x] CLI `tools/ai_workflow.py` with all 8 commands
- [x] ADR-0001: AI-assisted development workflow
- [x] 5 GitHub Actions workflows (ci, ai-artifacts, benchmark, release-readiness, security)
- [x] 5 issue template forms
- [x] PR template with checklist
- [x] `CONTRIBUTING.md` with complete guide
- [x] 6 docs files (ai_workflow, ai_task_lifecycle, ai_review_protocol, scientific_change_protocol, release_checklist, github_manual_setup)
- [x] CODEOWNERS, dependabot.yml
- [x] Example task packet
- [x] Unit tests for CLI

## Must not

- [x] No changes to `src/core/`, `src/app.py`, `src/ui/`, `src/structures/`
- [x] No new dependencies
- [x] No changes to existing tests
- [x] No push to main

## Test commands

```bash
python tools/ai_workflow.py check-repo
python tools/ai_workflow.py validate-task example-ai-workflow-bootstrap
pytest tests/unit/test_ai_workflow.py -v
```
