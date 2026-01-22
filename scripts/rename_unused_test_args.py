#!/usr/bin/env python3
"""Rename unused function arguments in tests by prefixing with an underscore.

This script parses test files under `tests/` and for each top-level function
definition it detects arguments that are never used in the function body and
renames them by prefixing an underscore. It writes changes back in-place.
"""
import ast
from pathlib import Path


def process_file(path: Path) -> bool:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    edits = []  # (offset, old, new)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            arg_names = [a.arg for a in node.args.args]
            # collect all names used in function body
            used = set()

            for n in ast.walk(node):
                if isinstance(n, ast.Name):
                    used.add(n.id)

            for arg in arg_names:
                if arg not in used and not arg.startswith("_"):
                    # rename in the source by replacing the parameter name
                    # in the function signature only (safe because unused)
                    # naive string replace scoped to the def line
                    def_line = src.splitlines()[node.lineno - 1]
                    if f"{arg}" in def_line:
                        new_line = def_line.replace(arg, f"_{arg}")
                        edits.append((node.lineno - 1, def_line, new_line))

    if not edits:
        return False

    lines = src.splitlines()
    for lineno, old, new in sorted(edits, reverse=False):
        if lines[lineno] == old:
            lines[lineno] = new

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main():
    changed = []
    for p in sorted(Path("tests").glob("**/*.py")):
        try:
            if process_file(p):
                changed.append(str(p))
        except Exception:
            # skip problematic files
            continue

    if changed:
        print("Updated files:")
        for f in changed:
            print(f)
    else:
        print("No changes")


if __name__ == "__main__":
    main()
