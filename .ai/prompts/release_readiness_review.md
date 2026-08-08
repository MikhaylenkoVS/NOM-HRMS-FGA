# Release Readiness Review Prompt

**Release version:** {{VERSION}}
**Base branch:** main
**Date:** {{DATE}}

## Instructions

You are Perplexity, performing a release readiness review.

### Review checklist

1. **Version consistency** — Does `pyproject.toml` version match release notes?
2. **Test suite** — All tests passing? Any skipped tests with justification?
3. **Dependency review** — No unexpected dependency changes?
4. **Changelog** — Is CHANGELOG/RELEASE_NOTES complete and accurate?
5. **Formula database compatibility** — Does the release work with the existing formula DB?
6. **Configuration changes** — Any new config keys? Are they documented?
7. **Breaking changes** — Any API breakage?
8. **Security** — Any tracked secrets? Unsafe operations?
9. **Scientific integrity** — Do regression tests pass on reference data?
10. **Packaging** — Does `.exe` build succeed?

### Output

1. Populate release checklist in `docs/release_checklist.md`.
2. Report readiness: READY / NOT READY / CONDITIONAL.

### Test commands

{{TEST_COMMANDS}}

### Open questions

{{OPEN_QUESTIONS}}
