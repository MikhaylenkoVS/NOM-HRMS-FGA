# Rollback Plan: AI Workflow Bootstrap

## How to detect failure

- `python tools/ai_workflow.py check-repo` returns non-zero
- CI workflows fail with syntax errors
- Existing tests break

## How to rollback

### Code rollback

```bash
git revert COMMIT_SHA
git push origin
```

### File removal (if infrastructure abandoned)

```bash
rm -rf .ai/
rm -f AGENTS.md CONTRIBUTING.md
rm -f tools/ai_workflow.py
rm -f .github/CODEOWNERS .github/dependabot.yml
rm -f .github/workflows/ai-artifacts.yml
rm -f .github/workflows/benchmark.yml
rm -f .github/workflows/release-readiness.yml
rm -f .github/workflows/security.yml
rm -rf .github/ISSUE_TEMPLATE/
rm -f .github/PULL_REQUEST_TEMPLATE.md
# Restore ci.yml from git history
git checkout HEAD~1 -- .github/workflows/ci.yml
rm -f docs/ai_*.md docs/scientific_change_protocol.md docs/release_checklist.md docs/github_manual_setup.md
```

## Recovery time estimate

< 5 minutes (git revert) or < 15 minutes (manual file removal)

## Who can rollback

Human only
