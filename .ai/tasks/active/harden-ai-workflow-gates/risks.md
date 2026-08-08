# Risks: Harden AI-workflow gates

## Technical risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CI breaks after removing `\|\| true` | medium | high | Test locally first, verify CI on PR |
| Benchmark runner too restrictive | low | low | Allowlist can be extended via documented PR process |
| Workflow safety scan false positives | low | low | Human review of scan results |

## Security risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shell injection via workflow_dispatch | high (before fix) | critical | Removed entirely |
| Adversarial benchmark_id | low | low | Hardcoded allowlist in Python |
| Path traversal in artifact paths | low | medium | Validation in validate-task |

## Risk assessment

Overall risk level: high (security task, touches CI/CD infrastructure)
