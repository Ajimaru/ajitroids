#!/usr/bin/env python3
"""Add minimal docstrings to modules, classes and functions in `modul/`.

This script inserts a placeholder docstring ("TODO: add docstring.") for any
module, class or function that is missing one. It edits files in-place but
creates a backup with the suffix `.bak` before modifying each file.

Usage: python3 scripts/add_missing_docstrings.py
"""
import ast
import io
import os
from pathlib import Path


PLACEHOLDER = 'TODO: add docstring.'


def add_module_docstring(lines, module_node):
    if ast.get_docstring(module_node) is not None:
        return lines
    # Find insertion index after any shebang/encoding comments and module-level
    # comments/imports. We'll insert at top (line 0) unless a shebang present.
    insert_idx = 0
    if lines and lines[0].startswith('#!'):
        insert_idx = 1
    doc = f'"""{PLACEHOLDER}"""\n\n'
    lines.insert(insert_idx, doc)
    return lines


def collect_inserts(tree):
    inserts = []  # list of (lineno0, indent, docstring)
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node) is None and node.body:
                # insert before first body statement
                first = node.body[0]
                lineno0 = first.lineno - 1
                # get indentation by counting leading spaces of that line later
                inserts.append((lineno0, node))
    return inserts


def process_file(path: Path):
    src = path.read_text(encoding='utf-8')
    try:
        tree = ast.parse(src)
    except SyntaxError:
        print(f"Skipping (syntax error): {path}")
        return False

    lines = src.splitlines(keepends=True)

    changed = False

    # module docstring
    if ast.get_docstring(tree) is None:
        lines = add_module_docstring(lines, tree)
        changed = True

    inserts = collect_inserts(tree)
    if not inserts:
        if changed:
            backup_and_write(path, lines)
        return changed

    # prepare to insert in reverse order
    inserts_sorted = sorted(inserts, key=lambda x: x[0], reverse=True)
    for lineno0, node in inserts_sorted:
        # compute indentation based on current content at lineno0
        if lineno0 < 0 or lineno0 >= len(lines):
            indent = '    '
        else:
            line = lines[lineno0]
            # leading whitespace of that line
            indent = line[: len(line) - len(line.lstrip())]

        doc = indent + '"""' + PLACEHOLDER + '"""\n'
        lines.insert(lineno0, doc)
        changed = True

    if changed:
        backup_and_write(path, lines)
    return changed


def backup_and_write(path: Path, lines):
    bak = path.with_suffix(path.suffix + '.bak')
    if not bak.exists():
        path.rename(bak)
        bak.write_text(''.join(lines), encoding='utf-8')
        # restore to original filename
        bak.rename(path)
    else:
        # fallback: write directly but keep original as .orig
        orig = path.with_suffix(path.suffix + '.orig')
        if not orig.exists():
            path.rename(orig)
        path.write_text(''.join(lines), encoding='utf-8')


def main():
    root = Path('modul')
    if not root.exists():
        print('Directory modul/ not found; aborting.')
        return
    changed_files = []
    for p in sorted(root.rglob('*.py')):
        # skip __pycache__ or hidden
        if any(part.startswith('.') for part in p.parts):
            continue
        if process_file(p):
            changed_files.append(str(p))

    if changed_files:
        print('Updated files:')
        for f in changed_files:
            print(' -', f)
    else:
        print('No changes needed.')


if __name__ == '__main__':
    main()
