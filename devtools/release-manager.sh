#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

success_msg() { echo -e "${GREEN}[OK] $1${NC}"; }
error_msg()   { echo -e "${RED}[FAIL] $1${NC}"; }
warn_msg()    { echo -e "${YELLOW}[WARN] $1${NC}"; }
info_msg()    { echo -e "${BLUE}[INFO] $1${NC}"; }

log_action() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGFILE"
}

show_help() {
    echo "Usage: $0 [--dry-run] [--logfile <path>] [--pagesize <n>] [--help]"
    echo
    echo "Options:"
    echo "  --dry-run         Preview deletions without executing"
    echo "  --logfile PATH    Set custom log file location"
    echo "  --pagesize N      Set number of items per page (default: 10)"
    echo "  --help            Show this help message"
    exit 0
}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGFILE="$SCRIPT_DIR/release-manager.log"
QUEUE_FILE="$SCRIPT_DIR/delete.queue"
PAGE_SIZE=10
DRY_RUN=0
REPO_ARG=""

resolve_repository() {
    if [[ -n "$REPO_ARG" ]]; then
        OWNER=$(echo "$REPO_ARG" | cut -d'/' -f1)
        REPO=$(echo "$REPO_ARG" | cut -d'/' -f2)
        REMOTE_URL="https://github.com/${OWNER}/${REPO}.git"
    else
        REMOTE_URL=$(git config --get remote.origin.url)

        if [[ -z "$REMOTE_URL" ]]; then
            warn_msg "No remote repository found – please set it manually with --repo owner/name"
            show_help
        fi

        REPO=$(basename -s .git "$REMOTE_URL")
        OWNER=$(basename "$(dirname "$REMOTE_URL")")
    fi

    info_msg "Repository: $OWNER/$REPO"
}

resolve_repository

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        --logfile) LOGFILE="$2"; QUEUE_FILE="$(dirname "$LOGFILE")/delete.queue"; shift 2 ;;
        --pagesize) PAGE_SIZE="$2"; shift 2 ;;
        --help) show_help ;;
        *) warn_msg "Unknown option: $1"; show_help ;;
    esac
done

fetch_tags_with_details() {
    curl -s "https://api.github.com/repos/$OWNER/$REPO/tags" | jq -r '.[].name'
}

fetch_tags() {
    curl -s "https://api.github.com/repos/$OWNER/$REPO/tags" | grep '"name":' | cut -d '"' -f4
}

fetch_releases() {
    curl -s "https://api.github.com/repos/$OWNER/$REPO/releases" | \
    jq -r '.[] | "\(.tag_name) | \(.name) | \(.author.login) | \(.created_at)"'
}

delete_tag() {
    if [[ $DRY_RUN -eq 1 ]]; then
        warn_msg "DRY RUN: Would delete tag '$1'"
    else
        git push --delete origin "$1" && success_msg "Deleted tag '$1'"
        log_action "Deleted TAG: $1"
    fi
}

delete_release() {
    local tag="$1"
    local api_url="https://api.github.com/repos/$OWNER/$REPO/releases/tags/$tag"
    local status
    status=$(curl -s -w "%{http_code}" -o /tmp/release.json "$api_url")

    if [[ "$status" != "200" ]]; then
        if grep -qi "rate limit" /tmp/release.json; then
            error_msg "GitHub API rate limit reached – please try again later"
        else
            error_msg "API error ($status) for release '$tag'"
        fi
        log_action "API ERROR ($status) for RELEASE: $tag"
        return
    fi

    local release_id
    release_id=$(jq -r '.id' /tmp/release.json)

    if [[ "$DRY_RUN" -eq 1 ]]; then
        warn_msg "DRY RUN: Would delete release '$tag' with ID $release_id"
        log_action "DRY RUN – RELEASE: $tag"
    else
        curl -s -X DELETE -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/repos/$OWNER/$REPO/releases/$release_id"
        success_msg "Deleted release '$tag'"
        log_action "Deleted RELEASE: $tag (ID: $release_id)"
    fi
}

paginate_list() {
    local -a items=("$@")
    local total=${#items[@]}
    local start=0
    if [[ $start -eq 0 ]]; then
        true > "$QUEUE_FILE"
    fi

    while [[ $start -lt $total ]]; do
        echo
        echo "[INFO]  $start to $((start+PAGE_SIZE-1)):"
        for (( i=start; i<start+PAGE_SIZE && i<total; i++ )); do
            echo "$((i+1))) ${items[i]}"
        done
        echo -n "Enter numbers to delete (e.g. 1 3), or press Enter to skip: "
        read -r input

        if [[ -n "$input" ]]; then
            for num in $input; do
                idx=$((num-1))
                entry="${items[$idx]}"
                [[ $idx -ge 0 && $idx -lt $total ]] && \
                    grep -qxF "$entry" "$QUEUE_FILE" || echo "$entry" >> "$QUEUE_FILE"
            done
            break
        fi

        start=$((start+PAGE_SIZE))

        if [[ $start -ge $total ]]; then
            echo -n "Restart list? [y/N]: "
            read -r again
            if [[ $again == "y" || $again == "Y" ]]; then
                start=0
            else
                break
            fi
        fi
    done
}

confirm_deletion() {
    local count
    count=$(wc -l < "$QUEUE_FILE")
    [[ "$count" -eq 0 ]] && return
    echo
    echo "[INFO] You selected $count item(s) to delete:"
    cat "$QUEUE_FILE"
    echo -n "Confirm deletion? [y/N]: "
    read -r confirm
    [[ "$confirm" == "y" || "$confirm" == "Y" ]] || { warn_msg "Deletion canceled."; rm "$QUEUE_FILE"; return 1; }
    return 0
}

manage_tags() {
    info_msg "Fetching tags with metadata..."
    tags=()

    while IFS= read -r tag; do
        release=$(curl -s "https://api.github.com/repos/$OWNER/$REPO/releases/tags/$tag")
        name=$(echo "$release" | jq -r '.name // "-"')
        author=$(echo "$release" | jq -r '.author.login // "-"')
        date=$(echo "$release" | jq -r '.created_at // "-"')
        date_formatted=$( [[ "$date" != "-" ]] && echo "$date" | cut -d'T' -f1 || echo "-" )

        info="$tag | Name: $name | Author: $author | Date: $date_formatted"
        tags+=("$info")
    done < <(fetch_tags_with_details)

    [[ ${#tags[@]} -eq 0 ]] && warn_msg "No tags found." && return

    paginate_list "${tags[@]}"
    confirm_deletion || return

    while IFS= read -r line; do
        tag=$(echo "$line" | cut -d'|' -f1 | xargs)
        delete_tag "$tag"
    done < "$QUEUE_FILE"

    rm "$QUEUE_FILE"
}

manage_releases() {
    info_msg "Fetching release data with additional info..."

    releases=()

    while IFS= read -r line; do
        releases+=("$line")
    done < <(
        curl -s "https://api.github.com/repos/$OWNER/$REPO/releases" | \
        jq -r '.[] | "\(.tag_name) | \(.name // "-") | \(.author.login // "-") | \(.published_at // "-") | Draft: \(.draft) | Prerelease: \(.prerelease) | Assets: \(.assets | length)"'
    )

    [[ ${#releases[@]} -eq 0 ]] && warn_msg "No releases found." && return

    paginate_list "${releases[@]}"
    confirm_deletion || return

    while IFS= read -r line; do
        tag=$(echo "$line" | cut -d'|' -f1 | xargs)
        delete_release "$tag"
    done < "$QUEUE_FILE"

    rm "$QUEUE_FILE"
}

while true; do
    echo
    echo "[INFO] GitHub Release & Tag Manager"
    echo "[INFO] Repository: $OWNER/$REPO"
    echo "Choose mode:"
    echo "1) Manage Releases"
    echo "2) Manage Tags"
    echo "3) Exit"
    read -rp "Enter 1, 2 or 3: " choice
    case "$choice" in
        1) manage_releases ;;
        2) manage_tags ;;
        3) echo "Goodbye!" && exit 0 ;;
        *) warn_msg "Invalid choice." ;;
    esac
done
