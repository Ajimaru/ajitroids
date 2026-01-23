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
    edits = []  # (start_lineno0, end_lineno0, old_lines, new_lines)

    lines = src.splitlines()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        arg_names = [a.arg for a in node.args.args]
        # collect all names used in function body (exclude decorators)
        used = set()
        for stmt in node.body:
            for n in ast.walk(stmt):
                if isinstance(n, ast.Name):
                    used.add(n.id)

        unused = [arg for arg in arg_names if arg not in used and not arg.startswith("_")]
        if not unused:
            continue

        # Determine the range of lines that make up the function signature
        start = node.lineno - 1
        if start < 0 or start >= len(lines):
            continue
        end = getattr(node, "end_lineno", None)
        if end is None:
            # Fallback: use the line before the first statement in the body
            if node.body:
                end = node.body[0].lineno - 1
            else:
                end = start
        else:
            end = end - 1
        if end < start:
            continue

        sig_lines = lines[start:end + 1]
        sig_text = "\n".join(sig_lines)

        # Build a regex that matches whole-word occurrences of the unused args
        pattern = r"\b(" + "|".join(re.escape(a) for a in unused) + r")\b"

        def _repl(m):
            return "_" + m.group(1)

        new_sig_text = re.sub(pattern, _repl, sig_text)
        if new_sig_text != sig_text:
            new_sig_lines = new_sig_text.split("\n")
            edits.append((start, end, sig_lines, new_sig_lines))

    if not edits:
        return False

    for item in sorted(edits, key=lambda x: x[0]):
        start, end, old_lines, new_lines = item
        if lines[start:end + 1] == old_lines:
            lines[start:end + 1] = new_lines

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
