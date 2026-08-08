# Rollback Plan: Harden AI-workflow gates

## How to detect failure

- CI workflows fail after changes
- `check-repo` reports new errors
- Benchmark workflow can't execute

## How to rollback

```bash
git revert COMMIT
git push origin
```

Individual file restores:
```bash
git checkout HEAD~1 -- .github/workflows/benchmark.yml
git checkout HEAD~1 -- .github/workflows/ci.yml
git checkout HEAD~1 -- .github/workflows/ai-artifacts.yml
git checkout HEAD~1 -- .github/workflows/security.yml
```

## Recovery time estimate

< 5 minutes (git revert)

## Who can rollback

Human only
