#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION_FILE="$SCRIPT_DIR/version.txt"
CHANGELOG_FILE="$SCRIPT_DIR/changelog.md"
LOG_FILE="$SCRIPT_DIR/release.log"
VERSION_COMMENT="$(head -n 1 "$VERSION_FILE")"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

color_msg() {
  local color="$1"
  shift
  printf "%b\n" "${color}$*${NC}"
}

log() {
  printf "%s\n" "$(date +"%Y-%m-%d %H:%M:%S") — $1" >> "$LOG_FILE"
}

color_msg "$CYAN" "[VERSION] Loaded from version.txt: $VERSION_COMMENT"
log "Version loaded: $VERSION_COMMENT"

check_clean_state() {
  CHANGED=$(git status --porcelain || true)
  if [[ -n "$CHANGED" ]]; then
    color_msg "$RED" "[ERROR] Working directory is not clean:"
    printf "%s\n" "$CHANGED"
    printf "%s\n" "Please commit or stash all changes before bumping version."
    exit 1
  fi
}

color_msg "$CYAN" "[INFO] Commit creation"
if ! command -v pytest >/dev/null 2>&1; then
  color_msg "$YELLOW" "[WARNING] pytest not found in PATH."
  read -r -p "Continue without tests? (y/n): " DO_CONTINUE
  if [[ ! "$DO_CONTINUE" =~ ^[Yy]$ ]]; then
    color_msg "$RED" "[CANCELLED] Release aborted."
    exit 1
  fi
else
  color_msg "$CYAN" "[TEST] Starting pytest..."
  if ! pytest --cov --cov-report=html --import-mode=importlib; then
    color_msg "$RED" "[ERROR] Pytest failed. Release aborted."
    exit 1
  fi
  color_msg "$GREEN" "[OK] All tests passed."
fi

PS3="Choose commit type: "
select TYPE in feat fix docs style refactor perf test chore ci build Cancel; do
  case $TYPE in
    Cancel) color_msg "$RED" "[CANCELLED] Operation aborted."; exit 0 ;;
    *) break ;;
  esac
done

PS3="Choose commit scope (or Cancel): "
select SCOPE in api ui docs parser script config test build Cancel; do
  case $SCOPE in
    Cancel) SCOPE=""; break ;;
    *) break ;;
  esac
done

read -r -p "Commit description: " DESCRIPTION

if [ -n "$SCOPE" ]; then
  COMMIT_MSG="$TYPE($SCOPE): $DESCRIPTION"
else
  COMMIT_MSG="$TYPE: $DESCRIPTION"
fi

color_msg "$YELLOW" "[PREVIEW] $COMMIT_MSG"
read -r -p "Proceed with commit? (y/n): " DO_COMMIT
if [[ "$DO_COMMIT" =~ ^[Yy]$ ]]; then
  git add .
  if git diff --cached --quiet; then
    color_msg "$YELLOW" "[WARNING] No changes to commit – skipping."
    log "Commit skipped: no changes"
  else
    git commit -m "$COMMIT_MSG"
    color_msg "$GREEN" "[OK] Commit successful."
    log "Commit: $COMMIT_MSG"
  fi
else
  color_msg "$RED" "[CANCELLED] Commit aborted."
  exit 0
fi

printf "\n"
read -r -p "Create new version? (y/n): " DO_VERSION
if ! [[ "$DO_VERSION" =~ ^[Yy]$ ]]; then
  color_msg "$CYAN" "[INFO] Version bump skipped."
  exit 0
fi

check_clean_state

SENSITIVE=$(git diff --cached --name-only | grep -E '(\.env|\.key|\.pem|\.DS_Store)$' || true)
if [ -n "$SENSITIVE" ]; then
  color_msg "$RED" "[WARNING] Sensitive files staged:"
  printf "%s\n" "$SENSITIVE"
  read -r -p "Abort release? (y/n): " CANCEL
  [[ "$CANCEL" =~ ^[Yy]$ ]] && exit 1
fi

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
RANGE="${LAST_TAG}..HEAD"
[ -z "$LAST_TAG" ] && RANGE="HEAD"
COMMITS=$(git log "$RANGE" --pretty=format:"%s" | wc -l)

if [ "$COMMITS" -eq 0 ]; then
  color_msg "$YELLOW" "[INFO] No new commits since last tag ($LAST_TAG)."
  read -r -p "Proceed anyway? (y/n): " DO_BUMP
  [[ ! "$DO_BUMP" =~ ^[Yy]$ ]] && { color_msg "$CYAN" "[CANCELLED] Release aborted."; exit 0; }
fi

VERSION=$(sed 's/^v//' "$VERSION_FILE")
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"
color_msg "$CYAN" "[VERSION] Current version: $MAJOR.$MINOR.$PATCH"

PS3="Choose release type: "
while true; do
  select RELEASE in Patch Minor Major Cancel; do
    case $RELEASE in
      Patch) PATCH=$((PATCH + 1)); break 2 ;;
      Minor) MINOR=$((MINOR + 1)); PATCH=0; break 2 ;;
      Major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0; break 2 ;;
      Cancel) color_msg "$RED" "[CANCELLED] Operation aborted."; exit 0 ;;
      *) color_msg "$RED" "[ERROR] Invalid selection." ;;
    esac
  done
done

NEW_VERSION="v$MAJOR.$MINOR.$PATCH"
while true; do
  read -r -p "Use version ($NEW_VERSION)? Enter custom or press Enter: " MANUAL_VERSION
  if [ -z "$MANUAL_VERSION" ]; then
    break
  fi
  if [[ "$MANUAL_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    NEW_VERSION="$MANUAL_VERSION"
    break
  else
    color_msg "$RED" "[ERROR] Invalid version format. Use vX.Y.Z (e.g. v1.2.3)"
  fi
done
echo "$NEW_VERSION" > "$VERSION_FILE"

TYPES=(feat fix docs style refactor perf test chore ci build)
{
  echo "## $NEW_VERSION ($(date +%Y-%m-%d))"
  echo ""
  for TYPE in "${TYPES[@]}"; do
    COMMITS=$(git log "$RANGE" --pretty=format:"%s" | grep -E "^$TYPE(\([^)]+\))?: " || true)
    if [ -n "$COMMITS" ]; then
      echo "### $TYPE"
      while IFS= read -r line; do
        echo "- $line"
      done <<< "$COMMITS"
      echo ""
    fi
  done
} >> "$CHANGELOG_FILE"

git add -f "$VERSION_FILE" "$CHANGELOG_FILE"
git commit -m "chore(release): bump to $NEW_VERSION"
git tag "$NEW_VERSION"

color_msg "$CYAN" "[BUILD] Starting build to update modul/_version.py ..."
if ! command -v python3 >/dev/null 2>&1; then
  color_msg "$RED" "[ERROR] python3 not found. Build skipped."
else
  if python3 -m pip show setuptools-scm >/dev/null 2>&1; then
    if python3 -m build; then
      color_msg "$GREEN" "[OK] Build completed. modul/_version.py should be updated."
    else
      color_msg "$YELLOW" "[WARNING] build failed. Trying pip install . ..."
      if python3 -m pip install .; then
        color_msg "$GREEN" "[OK] pip install . completed. modul/_version.py should be updated."
      else
        color_msg "$RED" "[ERROR] Build and pip install . failed. Version not updated."
      fi
    fi
  else
    color_msg "$YELLOW" "[WARNING] setuptools-scm not installed. Version cannot be written."
  fi
fi

color_msg "$GREEN" "[OK] Release completed: $NEW_VERSION"
color_msg "$GREEN" "[RELEASE] Tag and release commit created: $NEW_VERSION"
log "Release: $NEW_VERSION"

read -r -p "Push changes? (y/n): " DO_PUSH
if [[ "$DO_PUSH" =~ ^[Yy]$ ]]; then
  git push origin HEAD
  git push origin "$NEW_VERSION"
  color_msg "$GREEN" "[PUSHED] Changes pushed successfully."
  log "Pushed: $NEW_VERSION"
else
  color_msg "$CYAN" "[INFO] Changes remain local."
fi
log "Release completed"
color_msg "$CYAN" "[FILE] Release log: $LOG_FILE"
color_msg "$CYAN" "[FILE] Changelog: $CHANGELOG_FILE"
color_msg "$CYAN" "[VERSION] Stored in: $VERSION_FILE"

exit 0
