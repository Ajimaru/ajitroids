#!/usr/bin/env python3
"""Rename unused function arguments in tests by prefixing with an underscore.

This script parses test files under `tests/` and for each top-level function
definition it detects arguments that are never used in the function body and
renames them by prefixing an underscore. It writes changes back in-place.
"""
import ast
<<<<<<< HEAD
import re
import logging
=======
>>>>>>> origin/main
from pathlib import Path


def process_file(path: Path) -> bool:
<<<<<<< HEAD
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
        if not isinstance(node, ast.FunctionDef):
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
=======
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
>>>>>>> origin/main

    if not edits:
        return False

<<<<<<< HEAD
    for item in sorted(edits, key=lambda x: x[0]):
        start, end, old_lines, new_lines = item
        if lines[start:end + 1] == old_lines:
            lines[start:end + 1] = new_lines
=======
    lines = src.splitlines()
    for lineno, old, new in sorted(edits, reverse=False):
        if lines[lineno] == old:
            lines[lineno] = new
>>>>>>> origin/main

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main():
<<<<<<< HEAD
    """Main entry point.

    Scan tests/ for Python files, run process_file() on each, log exceptions,
    collect modified paths, and print a brief summary (updated files or
    'No changes').
    """
=======
>>>>>>> origin/main
    changed = []
    for p in sorted(Path("tests").glob("**/*.py")):
        try:
            if process_file(p):
                changed.append(str(p))
<<<<<<< HEAD
        except (OSError, SyntaxError, UnicodeDecodeError):
            logging.exception("Failed processing %s", p)
=======
        except Exception:
            # skip problematic files
            continue
>>>>>>> origin/main

    if changed:
        print("Updated files:")
        for f in changed:
            print(f)
    else:
        print("No changes")


if __name__ == "__main__":
    main()
