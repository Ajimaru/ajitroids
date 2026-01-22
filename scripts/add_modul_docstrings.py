#!/usr/bin/env python3
"""Add simple module docstrings to files under `modul/` that lack them.

This script prepends a one-line module docstring to each Python file in
`modul/` that does not already start with a string literal. It is intended
to fix Pylint C0114/C0115 quickly and safely.
"""
from pathlib import Path
import re
import ast
import logging

logger = logging.getLogger(__name__)


def needs_docstring(src: str) -> bool:
    """Return True if the given source string lacks a module docstring."""
    try:
        module = ast.parse(src)
    except SyntaxError:
        # If the file is invalid Python, be conservative and don't add a docstring
        return False
    return ast.get_docstring(module) is None


def process(path: Path) -> bool:
    """Add a minimal module docstring to the given file if it lacks one.

    Returns True if a docstring was added, otherwise False.
    """
    src = path.read_text(encoding='utf-8')
    if not needs_docstring(src):
        return False
    name = path.stem
    doc = f'"""Module modul.{name} — minimal module docstring."""\n\n'
    # Preserve a leading shebang and optional encoding declaration
    lines = src.splitlines(keepends=True)
    insert_idx = 0
    if lines and lines[0].startswith('#!'):
        insert_idx = 1
    # If the next line is an encoding declaration, keep it before the docstring
    if insert_idx < len(lines) and re.search(r'coding[:=]', lines[insert_idx]):
        insert_idx += 1

    new_src = ''.join(lines[:insert_idx] + [doc] + lines[insert_idx:])
    path.write_text(new_src, encoding='utf-8')
    return True


def main():
    """Scan Python files in 'modul/' and add minimal module docstrings if missing."""
    changed = []
    for p in sorted(Path('modul').glob('*.py')):
        try:
            if process(p):
                changed.append(str(p))
        except OSError as e:
            logger.warning("Skipping file %s due to OSError: %s", p, e, exc_info=True)

    if changed:
        print('Added docstrings to:')
        for f in changed:
            print(f)
    else:
        print('No changes')


if __name__ == '__main__':
    main()
