# Constraints: AI Workflow Bootstrap

## Functional constraints

- Infrastructure only — no product functionality changes
- Compatible with existing Python 3.10+ codebase
- Works on Windows (primary dev platform) and Linux (CI)

## Technical constraints

- Python stdlib only for `tools/ai_workflow.py`
- No new pip dependencies
- Must pass existing test suite
- Must not change `.gitignore` behavior for existing tracked files

## Non-constraints (explicitly out of scope)

- New formula database
- New codec or installer
- Product features
- Auto-merge or auto-release
- Cloud/SaaS integration

## Forbidden paths

- `src/core/` — scientific code
- `src/app.py` — GUI main
- `src/ui/` — GUI components
- `src/structures/` — molecule visualization
- `src/simulations/` — test set generation
- `src/configs/` — runtime configuration
- `data/` — test data and formula DB
- `tools/build_exe.py` — PyInstaller build
- `tools/NOM_HRMS_FGA.spec` — PyInstaller spec
