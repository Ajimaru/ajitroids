#!/usr/bin/env python3
"""Auto-resolve simple merge hunks: prefer the side without the TODO placeholder.

This script finds files with merge conflict markers and, for hunks where one
side contains the exact placeholder "TODO: add docstring.", it replaces the
hunk with the other side. Files with undecidable hunks are left untouched.
"""
import subprocess
from pathlib import Path

PLACEHOLDER = 'TODO: add docstring.'


def get_conflicted_files():
    p = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True)
    return [s for s in p.stdout.splitlines() if s]


def try_resolve(path: Path):
    txt = path.read_text(encoding='utf-8')
    if '<<<<<<<' not in txt:
        return False
    lines = txt.splitlines(keepends=True)
    out = []
    i = 0
    changed = False
    undecidable = False
    while i < len(lines):
        line = lines[i]
        if line.startswith('<<<<<<<'):
            # collect ours
            i += 1
            ours = []
            while i < len(lines) and not lines[i].startswith('======='):
                ours.append(lines[i])
                i += 1
            if i >= len(lines):
                undecidable = True
                break
            i += 1  # skip =======
            theirs = []
            while i < len(lines) and not lines[i].startswith('>>>>>>>'):
                theirs.append(lines[i])
                i += 1
            if i >= len(lines):
                undecidable = True
                break
            i += 1  # skip >>>>>>>
            ours_text = ''.join(ours)
            theirs_text = ''.join(theirs)
            # Decision rule: prefer side that does NOT contain PLACEHOLDER
            ours_has = PLACEHOLDER in ours_text
            theirs_has = PLACEHOLDER in theirs_text
            if ours_has and not theirs_has:
                out.append(theirs_text)
                changed = True
            elif theirs_has and not ours_has:
                out.append(ours_text)
                changed = True
            else:
                # undecidable for this hunk -> abort resolution for this file
                undecidable = True
                break
        else:
            out.append(line)
            i += 1
    if changed and not undecidable:
        path.write_text(''.join(out), encoding='utf-8')
        return True
    return False


def main():
    files = get_conflicted_files()
    if not files:
        print('No conflicted files found.')
        return
    resolved = []
    skipped = []
    for f in files:
        p = Path(f)
        if not p.exists():
            skipped.append((f, 'missing'))
            continue
        ok = try_resolve(p)
        if ok:
            resolved.append(f)
        else:
            skipped.append((f, 'undecided'))
    if resolved:
        print('Resolved files:')
        for f in resolved:
            print(' -', f)
        # stage resolved files
        subprocess.run(['git', 'add'] + resolved)
    if skipped:
        print('Skipped files:')
        for f, reason in skipped:
            print(' -', f, reason)

if __name__ == '__main__':
    main()
