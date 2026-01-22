#!/usr/bin/env python3
"""Auto-resolve safe merge hunks: prefer non-placeholder and non-comment sides.

Rules per hunk:
- If one side contains PLACEHOLDER and the other doesn't -> choose the other.
- If one side is only comments/blank lines and the other has code -> choose the code side.
- Otherwise skip the file (leave undecided hunks).
"""
import subprocess
from pathlib import Path
import re

PLACEHOLDER = 'TODO: add docstring.'


def conflicted_files():
    p = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True)
    return [s for s in p.stdout.splitlines() if s]


def is_comment_or_blank_block(text):
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith('#'):
            continue
        # allow docstring delimiters only
        if re.match(r"^('{3}|\"{3}).*\1$", s):
            continue
        return False
    return True


def resolve_file(path: Path):
    txt = path.read_text(encoding='utf-8')
    if '<<<<<<<' not in txt:
        return False
    lines = txt.splitlines(keepends=True)
    out = []
    i = 0
    changed = False
    undecidable = False
    while i < len(lines):
        if lines[i].startswith('<<<<<<<'):
            i += 1
            ours = []
            while i < len(lines) and not lines[i].startswith('======='):
                ours.append(lines[i])
                i += 1
            if i >= len(lines):
                undecidable = True
                break
            i += 1
            theirs = []
            while i < len(lines) and not lines[i].startswith('>>>>>>>'):
                theirs.append(lines[i])
                i += 1
            if i >= len(lines):
                undecidable = True
                break
            i += 1
            ours_text = ''.join(ours)
            theirs_text = ''.join(theirs)
            # Rule 1: placeholder presence
            ours_has = PLACEHOLDER in ours_text
            theirs_has = PLACEHOLDER in theirs_text
            if ours_has and not theirs_has:
                out.append(theirs_text)
                changed = True
                continue
            if theirs_has and not ours_has:
                out.append(ours_text)
                changed = True
                continue
            # Rule 2: comment-only vs code
            ours_comments = is_comment_or_blank_block(ours_text)
            theirs_comments = is_comment_or_blank_block(theirs_text)
            if ours_comments and not theirs_comments:
                out.append(theirs_text)
                changed = True
                continue
            if theirs_comments and not ours_comments:
                out.append(ours_text)
                changed = True
                continue
            undecidable = True
            break
        else:
            out.append(lines[i])
            i += 1
    if changed and not undecidable:
        path.write_text(''.join(out), encoding='utf-8')
        return True
    return False


def main():
    files = conflicted_files()
    if not files:
        print('No conflicted files.')
        return
    resolved = []
    skipped = []
    for f in files:
        p = Path(f)
        if not p.exists():
            skipped.append((f, 'missing'))
            continue
        try:
            ok = resolve_file(p)
        except Exception as e:
            skipped.append((f, f'error:{e}'))
            continue
        if ok:
            resolved.append(f)
        else:
            skipped.append((f, 'undecided'))
    if resolved:
        print('Resolved:')
        for r in resolved:
            print(' -', r)
        subprocess.run(['git', 'add'] + resolved)
    if skipped:
        print('Skipped:')
        for s, reason in skipped:
            print(' -', s, reason)

if __name__ == '__main__':
    main()
