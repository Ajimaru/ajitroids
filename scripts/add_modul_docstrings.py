#!/usr/bin/env python3
"""Add simple module docstrings to files under `modul/` that lack them.

This script prepends a one-line module docstring to each Python file in
`modul/` that does not already start with a string literal. It is intended
to fix Pylint C0114/C0115 quickly and safely.
"""
from pathlib import Path


def needs_docstring(src: str) -> bool:
    """Return True if the given source string lacks a module docstring."""
    s = src.lstrip()
    # Recognize single- or triple-quoted module docstrings with either
    # single or double quote styles.
    return not (
        s.startswith("'''")
        or s.startswith('"""')
        or s.startswith("'")
        or s.startswith('"')
    )


def process(path: Path) -> bool:
    """Add a minimal module docstring to the given file if it lacks one.

    Returns True if a docstring was added, otherwise False.
    """
    src = path.read_text(encoding='utf-8')
    if not needs_docstring(src):
        return False
    name = path.stem
    doc = f'"""Module modul.{name} — minimal module docstring."""\n\n'
    path.write_text(doc + src, encoding='utf-8')
    return True


def main():
    """Scan Python files in 'modul/' and add minimal module docstrings if missing."""
    changed = []
    for p in sorted(Path('modul').glob('*.py')):
        try:
            if process(p):
                changed.append(str(p))
        except OSError:
            continue

    if changed:
        print('Added docstrings to:')
        for f in changed:
            print(f)
    else:
        print('No changes')


if __name__ == '__main__':
    main()
