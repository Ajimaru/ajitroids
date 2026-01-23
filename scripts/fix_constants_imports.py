#!/usr/bin/env python3
"""Remove unused names from `from modul.constants import (...)` imports in tests.

This script finds files under `tests/` that import from `modul.constants` using
an import block, computes which of the imported names are actually used in the
file, and rewrites the import to include only those used names (or removes the
import entirely if none are used).
"""
import re
from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]
PAT_NAME = re.compile(r"\b([A-Z][A-Z0-9_]*)\b")

def main():
    """Process test files and rewrite imports; return list of changed files."""
    files = list((ROOT / 'tests').rglob('*.py'))
    changed = []
    for p in files:
        s = p.read_text(encoding='utf-8')
        # Parse the file AST and find ImportFrom nodes importing from modul.constants
        try:
            tree = ast.parse(s)
        except SyntaxError:
            continue

        lines = s.splitlines(True)
        # collect replacements as (start_idx, end_idx, NEW_IMPORT)
        replacements = []
        for node in [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]:
            if node.module != 'modul.constants':
                continue
            start = node.lineno - 1
            end = getattr(node, 'end_lineno', node.lineno) - 1
            if start < 0 or start >= len(lines) or end < start:
                continue

            import_block = ''.join(lines[start:end + 1])
            # extract imported names from the AST node
            names = [alias.name for alias in node.names if alias.name]
            if not names:
                continue

            # compute used names in file excluding the import block
            s_excl = ''.join(lines[:start] + lines[end + 1:])
            used = set()
            for name in names:
                if re.search(fr"\b{re.escape(name)}\b", s_excl):
                    used.add(name)
            if set(names) == used:
                continue  # no change

            # build replacement
            if used:
                # format as a single-line import if short, else multi-line
                used_list = sorted(used)
                if len(used_list) <= 6:
                    NEW_IMPORT = f"from modul.constants import {', '.join(used_list)}\n"
                else:
                    out_lines = ["from modul.constants import (\n"]
                    for n in used_list:
                        out_lines.append(f"    {n},\n")
                    out_lines.append(")\n")
                    NEW_IMPORT = "".join(out_lines)
            else:
                NEW_IMPORT = ""  # remove import entirely

            replacements.append((start, end, NEW_IMPORT))

        if not replacements:
            continue

        # apply replacements from bottom to top to not shift indices
        for start, end, NEW_IMPORT in sorted(replacements, key=lambda x: x[0], reverse=True):
            lines[start:end + 1] = [NEW_IMPORT]

        new_s = ''.join(lines)
        if new_s != s:
            p.write_text(new_s, encoding='utf-8')
            changed.append(str(p.relative_to(ROOT)))

    return changed


if __name__ == "__main__":
    changed = main()
    if changed:
        print("Updated files:")
        for c in changed:
            print(c)
    else:
        print("No changes needed.")
