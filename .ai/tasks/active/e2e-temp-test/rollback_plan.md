# Rollback Plan

**Task:** e2e-temp-test

## How to detect failure

[Monitoring, test failures, user reports]

## How to rollback

### Code rollback

```bash
git revert <commit>
git push origin
```

### Data rollback (if applicable)

[Steps to restore data]

## Recovery time estimate

[Minutes/hours]

## Who can rollback

[Human only / DeepCode with approval]
