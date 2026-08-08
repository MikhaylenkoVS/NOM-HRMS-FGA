# Risks: AI Workflow Bootstrap

## Technical risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CLI encoding issues on Windows | medium | low | Use ASCII-safe output, avoid emojis in CLI |
| CI workflow syntax errors | low | medium | Validate YAML syntax before commit |
| Task packet validation too strict | medium | low | Warnings vs errors distinction in validate-task |
| .gitignore blocks .ai/ files | low | medium | .ai/ uses .md and .json — not blocked |

## Scientific risks

None — this is infrastructure only, no scientific code is changed.

## Risk assessment

Overall risk level: medium
