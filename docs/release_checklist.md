# Release Checklist

## Before release

### Application version
- [ ] `pyproject.toml` version updated
- [ ] `CITATION.cff` version/date updated (if used)
- [ ] Version string consistent across all files

### Tests
- [ ] `pytest tests/ -q` — all tests pass
- [ ] `pytest tests/ -q -m unit` — unit tests pass
- [ ] `pytest tests/ -q -m integration` — integration tests pass
- [ ] No skipped tests without documented justification

### Packaging smoke test
- [ ] `python -m build` succeeds (if using build)
- [ ] `pip install -e ".[dev]"` clean install
- [ ] CLI entry point works: `nom-hrms-fga`

### .exe smoke test (Windows only)
- [ ] `python tools/build_exe.py --test` succeeds
- [ ] `dist/NOM_HRMS_FGA.exe` launches without errors
- [ ] `.exe` size is reasonable (~120 MB)
- [ ] Smoked for ≥ 15 seconds without crash

### Dependency review
- [ ] `pip-audit` shows no critical vulnerabilities
- [ ] No unexpected dependency additions
- [ ] Dependencies pinned in `requirements.txt`

### Changelog
- [ ] Release notes in `docs/RELEASE_NOTES_vX.Y.Z.md`
- [ ] Breaking changes documented
- [ ] New features documented
- [ ] Bug fixes documented

### Formula database compatibility
- [ ] Existing formula DB loads without errors
- [ ] Formula queries return expected results
- [ ] DB version/format documented

### SHA-256 and artifact integrity
- [ ] `.exe` SHA-256 recorded
- [ ] Source tarball integrity verified (if published)

### Release notes
- [ ] Release notes complete
- [ ] Links to ADRs, issues, PRs updated
- [ ] Installation instructions current

### Signing (if used)
- [ ] `.exe` signed (if code signing cert available)
- [ ] GPG signature for source tarball (if published)

### Rollback procedure
- [ ] Previous release `.exe` available
- [ ] Rollback instructions documented
- [ ] Database downgrade path (if applicable)

## During release

- [ ] Create GitHub Release from tag
- [ ] Attach `.exe` to release
- [ ] Attach SHA-256 checksums
- [ ] Publish release notes

## After release

- [ ] Verify download works
- [ ] Verify `.exe` launches (clean machine)
- [ ] Monitor for crash reports (first 48 hours)
- [ ] Update Zenodo (if used)
