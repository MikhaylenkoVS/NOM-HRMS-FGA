# NOM-HRMS-FGA v0.6.1 — Patch release

**2026-08-15** | [Full changelog](https://github.com/MikhaylenkoVS/NOM-HRMS-FGA/compare/v0.6.0...v0.6.1)

Patch on top of v0.6.0: new packed formula database, AI-assisted engineering
workflow, CI hardening, and artifact/benchmark fixes. No changes to the core
scientific pipeline (formula assignment, denoise, series detection).

---

## ✨ New features

| # | Description |
|---|-------------|
| — | **Packed formula database** (`src/core/formula_db/`) — CNOSP uint32 encoding + byte shuffle + Zstd compression. `FormulaDatabaseReader` (runtime search with LRU block cache), `DatabaseManager` (download/verify/update), CLI `python -m src.core.formula_db build`. Adds dependencies `zstandard>=0.22` and `requests`. |

---

## 🏗️ Infrastructure / workflow

| # | Description |
|---|-------------|
| — | **AI-assisted engineering workflow** (`.ai/`) — task contracts (JSON schemas), ADRs, prompts, task lifecycle, `tools/ai_workflow.py` (`validate-task`, `check-repo`). |

---

## 🔧 CI / build

| # | Description |
|---|-------------|
| — | **Blocking lint** — black formatting + flake8 enabled in CI. |
| — | **Dependency bumps** — `actions/checkout` v7, `setup-python` v7, `upload-artifact` v7, `actions/cache` v6, `softprops/action-gh-release` v3, `pymzml>=2.6.1`. |
| — | **CI fixes** — removed `--timeout` (pytest-timeout absent), `continue-on-error` on lint, skip tests requiring local state or Windows-only deps. |

---

## 🐛 Bug fixes

| # | Description |
|---|-------------|
| — | **Artifacts** — collision-free run IDs; structured benchmark reports with semantic validation and path safety. |
| — | **Benchmark hardening** — removed shell injection vector, categorized CI checks, fixed task lifecycle. |
| — | **Lint** — `black` applied to `run_benchmark.py`. |

---

## 📝 Documentation

| # | Description |
|---|-------------|
| #96 | **User guide** — 6 sections (install, data, analysis, results, presets, FAQ). |
| — | Archived completed tasks and plans; fixed angle-bracket placeholder in `rollback_plan.md`. |

---

## 📦 Assets

- `Source code` (zip) — full repository snapshot at v0.6.1
- `Source code` (tar.gz) — full repository snapshot at v0.6.1

> **Note:** `NOM_HRMS_FGA.exe` is not rebuilt for this patch — the `.exe` build
> workflow (`release_exe.yml`) triggers on release publish; no core pipeline changes.
