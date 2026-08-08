# Design: AI-Assisted Engineering Workflow

## Approach

Create a lightweight, maintainable infrastructure for semi-automated collaboration
between Perplexity (research/design/review), DeepCode (code/tests/commit/PR),
and human (priorities/approval/merge/release).

## Architecture

```
.ai/                     AI workflow artifacts
  tasks/                 Task packets (system of record)
  templates/             Reusable templates
  contracts/             JSON schemas for validation
  decisions/             Architecture Decision Records
  prompts/               Prompt registry for AI agents

tools/
  ai_workflow.py         Single CLI (stdlib only)

AGENTS.md                 Rules for AI agents
CONTRIBUTING.md           Human contributor guide

.github/                  GitHub integration
  workflows/              CI, AI checks, benchmark, release, security
  ISSUE_TEMPLATE/         Structured issue forms
  PULL_REQUEST_TEMPLATE.md
  CODEOWNERS, dependabot.yml
```

## Key decisions

1. **JSON format for task.json** — machine-readable, no YAML dependency.
2. **Single CLI file** — `tools/ai_workflow.py` uses only stdlib.
3. **Existing stack preserved** — PyInstaller, pytest markers, flake8, black.
4. **Human gate** — merge and release are exclusively human operations.

## Alternatives considered

| Alternative | Pros | Cons | Rejected |
|------------|------|------|----------|
| YAML task format | Human-readable | Requires PyYAML | JSON is stdlib |
| Multiple CLI files | Separation of concerns | More complexity | Single file simpler |
| Auto-merge for low-risk | Faster | Risk to scientific code | Human gate required |
