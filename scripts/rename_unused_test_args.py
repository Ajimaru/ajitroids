#!/usr/bin/env python3
"""Rename unused function arguments in tests by prefixing with an underscore.

This script parses test files under `tests/` and for each top-level function
definition it detects arguments that are never used in the function body and
renames them by prefixing an underscore. It writes changes back in-place.
"""
import ast
import re
import logging
from pathlib import Path


def process_file(path: Path) -> bool:
    """Rename unused positional args in top-level functions by prefixing with _.

    Parses the file, finds top-level FunctionDef args that aren't used in the
    function body, updates the function definition line, and returns True if
    the file was modified.
    """
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    edits = []  # (lineno0, old_line, new_line)

    lines = src.splitlines()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue

        arg_names = [a.arg for a in node.args.args]
        # collect all names used in function body
        used = set()
        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                used.add(n.id)

        unused = [arg for arg in arg_names if arg not in used and not arg.startswith("_")]
        if not unused:
            continue

        lineno0 = node.lineno - 1
        if lineno0 < 0 or lineno0 >= len(lines):
            continue

        def_line = lines[lineno0]
        # Build a regex that matches whole-word occurrences of the unused args
        pattern = r"\b(" + "|".join(re.escape(a) for a in unused) + r")\b"

        def _repl(m):
            return "_" + m.group(1)

        new_line = re.sub(pattern, _repl, def_line)
        if new_line != def_line:
            edits.append((lineno0, def_line, new_line))

    if not edits:
        return False

    for lineno, old, new in sorted(edits, key=lambda x: x[0]):
        if lines[lineno] == old:
            lines[lineno] = new

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main():
    """Main entry point.

    Scan tests/ for Python files, run process_file() on each, log exceptions,
    collect modified paths, and print a brief summary (updated files or
    'No changes').
    """
    changed = []
    for p in sorted(Path("tests").glob("**/*.py")):
        try:
            if process_file(p):
                changed.append(str(p))
        except (OSError, SyntaxError, UnicodeDecodeError):
            logging.exception("Failed processing %s", p)

    if changed:
        print("Updated files:")
        for f in changed:
            print(f)
    else:
        print("No changes")


if __name__ == "__main__":
    main()
