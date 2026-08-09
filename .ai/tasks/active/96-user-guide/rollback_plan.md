# Rollback Plan

**Task:** 96-user-guide

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
