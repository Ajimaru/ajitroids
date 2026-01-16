# v0.21.0 Release - Final Steps

## Current Status

✅ **Completed:**
- CHANGELOG.md has been updated with v0.21.0 changes
- Release branch `release/v0.21.0` exists at commit `5585761`
- Git tag `v0.21.0` has been created locally pointing to commit `5585761` on the release branch

❌ **Remaining:**
- The tag needs to be pushed to GitHub to trigger the automated release workflow

## To Complete the Release

### Option 1: Command Line (Preferred)

Run the following command to push the tag:

```bash
git push origin v0.21.0
```

This will:
1. Push the v0.21.0 tag to GitHub
2. Automatically trigger the release workflow at `.github/workflows/release.yml`
3. Create a GitHub Release at https://github.com/Ajimaru/ajitroids/releases
4. Populate the release with the changelog content from CHANGELOG.md

### Option 2: GitHub Actions UI (Alternative)

Use the manual release workflow via GitHub Actions:

1. Go to https://github.com/Ajimaru/ajitroids/actions/workflows/manual-release.yml
2. Click "Run workflow"
3. Enter the tag: `v0.21.0`
4. Leave "ref" empty (it will default to `release/v0.21.0`) or specify a specific branch/commit
5. Click "Run workflow" button

This workflow will:
- Create and push the tag if it doesn't exist on GitHub
- Extract the changelog content
- Create the GitHub release automatically

## Release Content Preview

The v0.21.0 release will include:

### Added
- **Quick Restart Feature**: Press 'R' during gameplay or on game over screen
- **Stats Dashboard**: New menu option with detailed game statistics and visual progress bars
- **Replay System**: Complete replay recording and playback functionality
- **Updated Help Screen**: Added Quick Restart shortcut
- **Enhanced Menu**: Added "Replays" and "Statistics" options

### Changed
- Session statistics now automatically track replay-worthy data
- Game over screen displays quick restart instruction

### Tests
- Added 44 new comprehensive tests
- Maintained >89% code coverage

Full Changelog: [v0.20.0...v0.21.0](https://github.com/Ajimaru/ajitroids/compare/v0.20.0...v0.21.0)

## Verification

After pushing the tag, verify:
1. Workflow runs successfully: https://github.com/Ajimaru/ajitroids/actions
2. Release appears: https://github.com/Ajimaru/ajitroids/releases/tag/v0.21.0
3. Release description matches the CHANGELOG.md content

## Alternative: Manual Release

If the automated workflow fails, create the release manually via GitHub CLI:

```bash
gh release create v0.21.0 \
  --title "Release v0.21.0" \
  --notes "$(awk '/^## v0.21.0 / {flag=1; next} /^## v/ {flag=0} flag' CHANGELOG.md)"
```

Or via the GitHub web interface at: https://github.com/Ajimaru/ajitroids/releases/new
