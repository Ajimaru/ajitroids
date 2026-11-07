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

The git tag is the only version source. No version string is stored in the
repository: there is no `VERSION` file, no bump commit and no generated module.
`setuptools-scm` resolves the version from the tag history at install/build
time, and the game reads it back from the installed package metadata
(`modul/version.py`).

```toml
[tool.setuptools_scm]
version_scheme = "guess-next-dev"
local_scheme = "no-local-version"
```

Consequences:

- A release is a tag; nothing else has to be edited.
- `local_scheme = "no-local-version"` strips the `+g<hash>` suffix, so the
  version stays PEP 440 clean.
- Building outside a git checkout (source archive without `.git`) is not
  supported. The release workflow always builds from a full clone.

## Release Types

### Development Releases

Commits after the last tag get a dev version. Twelve commits after `v0.25.0`
resolve to:

```
0.25.1.dev12
```

- Base: next patch after the last tag (`0.25.1`)
- Commits since the tag: `.dev12`
- No git hash, because of `local_scheme = "no-local-version"`

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

### 2. Tag the Release

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

### 3. Push Tag

```bash
git push origin v1.2.3
```

This triggers the GitHub Actions release workflow.

## GitHub Actions Release Workflow

A pushed `v*` tag starts `.github/workflows/release.yml`, which:

1. **Checks out** the tagged commit with full history
2. **Exports** the tag as `SETUPTOOLS_SCM_PRETEND_VERSION`, so the built version
   always equals the tag
3. **Builds** sdist and wheel
4. **Stages** the artifacts plus a versioned and a `-latest` source zip
5. **Creates a draft GitHub Release** with generated notes and the artifacts

The release stays a draft on purpose: notes and artifacts are reviewed by hand
before publishing. Tests are not part of this workflow; the `CI` workflow also
runs on tag pushes.

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:83806380482e1b71b0cbcb57b03aa15aeef7056b4f9e2e9239b57cd1dda81a85 -->

Prerelease tags (`v0.25.0rc1`, `v0.25.0.dev6`) are detected and flagged as
prereleases automatically.

## Manual Release (Fallback)

<!-- /coderabbit-ai-generated:v1 -->

If the workflow cannot run, build and publish from a local full clone. A shallow
clone has no tag history and cannot resolve the version.

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:d84c98bb82e9268e4dcdb31f7b9bc2c11f8dfe30f30ccbac897c0d01357d67b2 -->

### 1. Build Package

Use a full clone with tag history. Before installing tools or building, verify
that the working tree is clean (the status command must produce no output),
fetch the tags, and check out the intended release tag:

```bash
git status --porcelain
git fetch origin --tags
git switch --detach v1.2.3
pip install build
python -m build
```

<!-- /coderabbit-ai-generated:v1 -->

This creates:

- `dist/ajitroids-1.2.3.tar.gz` (source)
- `dist/ajitroids-1.2.3-py3-none-any.whl` (wheel)

### 2. Test Package

```bash
pip install dist/ajitroids-1.2.3-py3-none-any.whl
ajitroids --version
```

### 3. Create GitHub Release

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

- [ ] Git tag created (`vX.Y.Z`)
- [ ] Tag pushed to GitHub
- [ ] GitHub Actions workflow succeeded
- [ ] Draft release reviewed and published

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

Download `ajitroids-1.2.3.zip` or the wheel from the release assets.

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

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:aac7785c8d23a0cad86523c991d633cc4c207c1ff8f2780ad5113443825196ae -->

For critical bugs in a published release, isolate the fix from unfinished work:

1. Start from a clean working tree in a full clone. Fetch tags and branch from
   the published release that needs the fix (for example, `v0.25.0`):

   ```bash
   git status --porcelain
   git fetch origin --tags
   git switch -c hotfix/0.25.1 v0.25.0
   ```

   Stop if status reports local changes; commit or stash them first.

2. Apply only the critical fix and its regression tests. If the fix already
   exists elsewhere, cherry-pick its focused commit and resolve conflicts
   without importing unrelated development changes. Run the test suite and
   applicable checks from CI, then commit the validated fix:

   ```bash
   git add <changed-files>
   git commit -m "fix: critical bug description"
   ```

3. Review the diff against the published tag, validate the built package, and
   tag the hotfix commit with the next unused patch version:

   ```bash
   git diff v0.25.0...HEAD
   git tag -a v0.25.1 -m "Release version 0.25.1"
   git push origin hotfix/0.25.1
   git push origin v0.25.1
   ```

   Wait for tag CI and the release workflow, inspect the draft's notes and
   artifacts, and publish the patch release as described above.

4. Reconcile the hotfix with both `main` and `dev` through separate pull
   requests. Merge the hotfix branch into each branch, resolving conflicts while
   preserving that branch's existing changes and the bug fix. If a branch
   already contains the equivalent fix, verify it before resolving any duplicate
   changes. Run CI on both resulting branches. Do not reset either branch to the
   release tag or merge unfinished `dev` work into `main`.

<!-- /coderabbit-ai-generated:v1 -->## Version Checking

The version is shown in the main menu and by the CLI:

```bash
python main.py --version
```

Programmatic access goes through the single accessor module:

```python
from modul.version import get_version
print(f"Ajitroids version: {get_version()}")
```

Without an installed package the accessor returns `0.0.0+unknown`, so install
the project (`uv sync` or `pip install -e .`) before reporting a version.

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
