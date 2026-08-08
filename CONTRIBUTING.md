# Contributing to NOM-HRMS-FGA

## Branch naming

- `feature/<slug>` — new features and tasks
- `fix/<slug>` — bug fixes
- `refactor/<slug>` — refactoring
- `docs/<slug>` — documentation changes

Base all branches on `main`.

## Commit conventions

Follow existing commit style: prefix with component area.

```
core: fix denoise round-trip precision
ui: add tooltip to parameter tab
test: add regression test for assign_formulas
docs: update architecture diagram
```

## AI-assisted workflow

This project uses AI agents (Perplexity + DeepCode) for implementation,
with human oversight. See:

- [AGENTS.md](AGENTS.md) — rules for AI agents
- [docs/ai_workflow.md](docs/ai_workflow.md) — full workflow
- [docs/ai_task_lifecycle.md](docs/ai_task_lifecycle.md) — task lifecycle
- [.ai/decisions/index.md](.ai/decisions/index.md) — architecture decisions

### When a task packet is required

Task packets in `.ai/tasks/active/<task-id>/` are mandatory for:

- `architecture` — architectural changes
- `scientific` — changes affecting scientific results
- `performance` — performance optimization
- `formula-db` — formula database changes
- `packaging` — build system changes
- `security` — security-related changes

Task packets are recommended but optional for:

- `feature` — new functionality
- `refactor` — code restructuring
- `bugfix` — high/critical risk fixes

Task packets are not required for:

- `documentation` — trivial doc fixes
- `maintenance` — minor cleanups without behavioral changes
- `test` — test additions without logic changes

### When an ADR is needed

ADR (`.ai/decisions/NNNN-title.md`) is required when:

- A decision affects architecture (multiple modules)
- A change affects scientific results or methodology
- A new data format or storage format is introduced
- A new dependency with system-level impact is added

### When a benchmark is needed

Benchmark (`.ai/baselines/` + `benchmark_report.md`) is required for:

- Performance optimization tasks
- Algorithm changes that may affect speed
- Formula database query performance changes

### When scientific validation is needed

Scientific validation is required when:

- Chemical rules or invariants change
- Formula assignment logic changes
- Thresholds affecting scientific results change
- New elements or isotope patterns are added

## Running tests

```bash
# All tests
pytest tests/ -q

# By marker
pytest tests/ -q -m unit
pytest tests/ -q -m integration
pytest tests/ -q -m smoke
```

## Preparing a PR

1. Create a feature branch from `main`
2. If the task type requires it, create a task packet:
   ```bash
   python tools/ai_workflow.py new-task <task-id> --title "..." --type <type> --risk <level>
   ```
3. Implement, add tests, update documentation
4. Fill in `implementation_report.md`
5. Run validation:
   ```bash
   python tools/ai_workflow.py validate-task <task-id>
   ```
6. Open a PR using the PR template
7. Ensure CI passes
8. Request human review and approval

## Using DeepCode

1. Perplexity creates task packet (research, design, acceptance criteria)
2. Run `render-handoff` to create instructions for DeepCode:
   ```bash
   python tools/ai_workflow.py render-handoff <task-id>
   ```
3. DeepCode implements according to handoff instructions
4. DeepCode fills `implementation_report.md`
5. Task goes through validation, review, approval

## Human approval required

The following actions require explicit human approval:

- Merge to `main`
- Push to `main`
- Release creation
- File deletion (beyond own task scope)
- GitHub secrets management
- Baseline updates in `.ai/baselines/`
- ADR finalization

## Completing and archiving tasks

```bash
# After merge
python tools/ai_workflow.py complete-task <task-id>
python tools/ai_workflow.py archive-task <task-id>
```
