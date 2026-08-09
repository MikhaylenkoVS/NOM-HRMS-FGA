# DeepCode Handoff: 96-user-guide
**Generated:** 2026-08-09T10:22:17Z

## Goal
User guide — черновик и интеграция в документацию

## Scope
- docs/user-guide/
- docs/
- README.md

## Forbidden Paths
- **src/** -- DO NOT MODIFY
- **tools/** -- DO NOT MODIFY
- **tests/** -- DO NOT MODIFY

## Design
# Design

## Approach

[Chosen approach]

## Architecture

[Key modules, interfaces, data flow]

## Alternatives considered

| Alternative | Pros | Cons | Reason rejected |
|------------|------|------|-----------------|
| | | | |

## API / Interface changes

[New or changed functions, classes, CLI args, file formats]

## Data model

[Schema, relationships, constraints]

## Error handling

[Expected failure modes and responses]


## Constraints
# Constraints

## Functional constraints

- [Constraint 1]
- [Constraint 2]

## Technical constraints

- Python ≥ 3.10
- Only standard library for tools/*
- No new dependencies without justification
- Must pass existing test suite

## Non-constraints (explicitly out of scope)

- [Out-of-scope 1]
- [Out-of-scope 2]

## Forbidden paths

Paths that MUST NOT be modified:

- `[path/to/protected/dir]`
- `[path/to/protected/file.py]`

## Max files to change

[N or null for unlimited]


## Acceptance Criteria
# Acceptance Criteria

## Must have

- [ ] Criterion 1
- [ ] Criterion 2

## Must not

- [ ] Regression 1
- [ ] Regression 2

## Test commands

```bash
# Unit tests
pytest tests/ -q -m unit

# Integration tests
pytest tests/ -q -m integration

# Specific test file
pytest tests/unit/test_xxx.py -v
```

## Success metrics

| Metric | Target | Measurement method |
|--------|--------|--------------------|
| | | |


## Validation Commands
```bash
pytest tests/ -q          # All tests
pytest tests/ -q -m unit  # Unit tests only
```

## Risk Level: **LOW**

## Required Artifacts
- [design](design.md)
- [acceptance](acceptance.md)
- [implementation_report](implementation_report.md)
- [rollback_plan](rollback_plan.md)

## Open Questions / Human Decisions
# Human Decisions

**Task:** 96-user-guide

| # | Date | Question | Decision | Rationale |
|---|------|----------|----------|-----------|
| 1 | | | | |


## Mandatory Instructions for DeepCode

1. Read `AGENTS.md` at repo root before starting.
2. Study existing code -- do not guess about non-existent APIs.
3. Stay within scope. Do not modify forbidden paths.
4. Implement only what is asked. No scope creep.
5. Add tests for new functionality.
6. Run validation commands before reporting completion.
7. Update `implementation_report.md` in the task packet.
8. Mark assumptions clearly in the report.
9. **DO NOT merge, release, or push to main.**
10. Return `implementation_report.md` when done.
