#!/usr/bin/env python3
"""Remove unused names from `from modul.constants import (...)` imports in tests.

This script finds files under `tests/` that import from `modul.constants` using
an import block, computes which of the imported names are actually used in the
file, and rewrites the import to include only those used names (or removes the
import entirely if none are used).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAT_IMPORT = re.compile(r"^from\s+modul\.constants\s+import\s*\(", re.M)
PAT_NAME = re.compile(r"\b([A-Z][A-Z0-9_]{2,})\b")

files = list((ROOT / 'tests').rglob('*.py'))
changed = []
for p in files:
    s = p.read_text()
    m = PAT_IMPORT.search(s)
    if not m:
        continue
    # find the import block start index
    start = m.start()
    # find the closing parenthesis for that import (naive but sufficient)
    idx = m.end()
    depth = 1
    end = None
    while idx < len(s):
        c = s[idx]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                end = idx
                break
        idx += 1
    if end is None:
        # can't parse, skip
        continue
    import_block = s[m.start(): end+1]
    # extract names from import block
    names = re.findall(r"([A-Z][A-Z0-9_]{2,})", import_block)
    if not names:
        continue
    # compute used names in file excluding the import block
    s_excl = s[:m.start()] + s[end+1:]
    used = set()
    for name in names:
        if re.search(r"\b{}\b".format(re.escape(name)), s_excl):
            used.add(name)
    if set(names) == used:
        continue  # no change
    # build replacement
    if used:
        # format as a single-line import if short, else multi-line
        used_list = sorted(used)
        if len(used_list) <= 6:
            new_import = f"from modul.constants import {', '.join(used_list)}"
        else:
            lines = ["from modul.constants import ("]
            for n in used_list:
                lines.append(f"    {n},")
            lines.append(")")
            new_import = "\n".join(lines)
    else:
        new_import = ""  # remove import entirely
    # replace in source
    new_s = s[:m.start()] + new_import + s[end+1:]
    if new_s != s:
        p.write_text(new_s)
        changed.append(str(p.relative_to(ROOT)))

if changed:
    print("Updated files:")
    for c in changed:
        print(c)
else:
    print("No changes needed.")
