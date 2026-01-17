# Release Process

This document describes the release process for Ajitroids.

## Release Workflow

Ajitroids uses an automated release workflow with GitHub Actions and
`setuptools-scm` for version management.

## Version Management

### Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Version Source

Versions are managed through Git tags using `setuptools-scm`:

```toml
[tool.setuptools_scm]
version_scheme = "guess-next-dev"
local_scheme = "no-local-version"
write_to = "modul/_version.py"
```

The version is automatically generated based on Git tags and commits.

## Release Types

### Development Releases

Commits on `main` without a tag get a dev version:

```
1.2.3.dev5+g1234567
```

This includes:

- Last tag version: `1.2.3`
- Commits since tag: `.dev5`
- Git hash: `+g1234567`

### Stable Releases

Tagged commits create stable releases:

```bash
git tag v1.2.3
git push origin v1.2.3
```

This creates version `1.2.3`.

## Release Steps

### 1. Prepare Release

#### Update CHANGELOG

Update `CHANGELOG.md` with all changes since last release:

```markdown
## [1.2.3] - 2024-01-15

### Added

- New power-up: Shield
- Achievement system
- Boss fight in level 5

### Changed

- Improved asteroid collision detection
- Updated UI styling

### Fixed

- Fixed player respawn bug
- Corrected sound volume issue
```

#### Update Documentation

- Review and update docs for new features
- Update screenshots if UI changed
- Verify all links work

#### Run Full Test Suite

```bash
# Run all tests
pytest

# Check code style
black --check modul/ tests/ main.py
flake8 modul/ tests/ main.py

# Build package
python -m build
```

### 2. Create Release Branch (Optional)

For major releases, create a release branch:

```bash
git checkout -b release/1.2.3
```

### 3. Tag the Release

Create an annotated tag:

```bash
git tag -a v1.2.3 -m "Release version 1.2.3"
```

Tag message format:

```
Release version 1.2.3

- Brief description of major changes
- Link to changelog
```

### 4. Push Tag

```bash
git push origin v1.2.3
```

This triggers the GitHub Actions release workflow.

## GitHub Actions Release Workflow

The release workflow (`.github/workflows/release.yml`) automatically:

1. **Detects** new version tags (matching `v*.*.*`)
2. **Builds** the package
3. **Runs tests** to verify release
4. **Creates GitHub Release** with changelog
5. **Publishes** to PyPI (if configured)

### Workflow Configuration

```yaml
name: Release

on:
  push:
    tags:
      - "v*.*.*"

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
      - name: Build package
        run: python -m build
      - name: Create Release
        uses: actions/create-release@v1
```

## Manual Release (Fallback)

If automated release fails, you can release manually:

### 1. Build Package

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build
```

This creates:

- `dist/ajitroids-1.2.3.tar.gz` (source)
- `dist/ajitroids-1.2.3-py3-none-any.whl` (wheel)

### 2. Test Package

```bash
# Install in test environment
pip install dist/ajitroids-1.2.3-py3-none-any.whl

# Test game runs
python -m ajitroids
```

### 3. Upload to PyPI

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ ajitroids

# Upload to production PyPI
twine upload dist/*
```

### 4. Create GitHub Release

1. Go to GitHub releases page
2. Click "Draft a new release"
3. Select the tag
4. Fill in release notes
5. Attach built packages
6. Publish release

## Release Checklist

### Pre-Release

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number decided
- [ ] No critical bugs open
- [ ] Code formatted and linted

### Release

- [ ] Release branch created (for major releases)
- [ ] Git tag created
- [ ] Tag pushed to GitHub
- [ ] GitHub Actions workflow succeeded
- [ ] GitHub Release created
- [ ] Package published (if applicable)

### Post-Release

- [ ] Release announcement posted
- [ ] Documentation site updated
- [ ] Social media announcement (if applicable)
- [ ] Close released milestone
- [ ] Create next milestone

## Release Notes Format

### Title

```
Release v1.2.3 - Feature Name
```

### Body

```markdown
## What's New in 1.2.3

### 🎮 New Features

- Feature 1 description
- Feature 2 description

### 🐛 Bug Fixes

- Bug fix 1
- Bug fix 2

### 🔧 Improvements

- Improvement 1
- Improvement 2

### 📚 Documentation

- Doc update 1

### 🙏 Contributors

Thanks to @username1, @username2 for contributions!

## Installation

\`\`\`bash pip install ajitroids==1.2.3 \`\`\`

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for details.
```

## Versioning Examples

### Patch Release (Bug Fixes)

```
1.2.3 → 1.2.4
```

Changes:

- Bug fixes only
- No new features
- No breaking changes

### Minor Release (New Features)

```
1.2.3 → 1.3.0
```

Changes:

- New features
- Bug fixes
- Backward compatible

### Major Release (Breaking Changes)

```
1.2.3 → 2.0.0
```

Changes:

- Breaking API changes
- Major refactoring
- New features and fixes

## Hotfix Process

For critical bugs in production:

1. **Create hotfix branch** from release tag

   ```bash
   git checkout -b hotfix/1.2.4 v1.2.3
   ```

2. **Fix the bug**

   ```bash
   # Make fix
   git commit -m "fix: critical bug description"
   ```

3. **Tag hotfix release**

   ```bash
   git tag v1.2.4
   git push origin v1.2.4
   ```

4. **Merge back to main**
   ```bash
   git checkout main
   git merge hotfix/1.2.4
   ```

## Version Checking

Users can check their version:

```python
from modul._version import version
print(f"Ajitroids version: {version}")
```

Or via command line:

```bash
python -c "from modul._version import version; print(version)"
```

## Release Cadence

- **Patch releases**: As needed for bugs
- **Minor releases**: Monthly or when features ready
- **Major releases**: Yearly or for significant changes

## Deprecation Policy

When deprecating features:

1. **Announce** deprecation in release notes
2. **Add warnings** in code for at least one minor version
3. **Document** alternatives
4. **Remove** in next major version

Example:

```python
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning
    )
    return new_function()
```

## Rollback Procedure

If a release has critical issues:

1. **Identify** the issue
2. **Create** hotfix or revert
3. **Tag** new version
4. **Communicate** with users
5. **Document** what happened

## Communication

Announce releases through:

- GitHub Release notes
- README.md update
- Documentation site
- Social media (if applicable)
- Community channels

## Next Steps

- [Contributing Guide](contributing.md): How to contribute
- [Testing](testing.md): Testing guidelines
- [CHANGELOG](https://github.com/Ajimaru/ajitroids/blob/main/CHANGELOG.md): View
  all releases
