#!/usr/bin/env python3
"""Mark `except Exception:` occurrences with a pylint disable comment.

This is a conservative automated helper: it finds lines containing
`except Exception:` or `except Exception as` and appends
`  # pylint: disable=broad-exception-caught` if not already present.
Run this only when you accept suppressing those specific warnings.
"""
from pathlib import Path
import logging


def process(path: Path) -> bool:
    """Process a Python file, marking lines with 'except Exception:' by appending a pylint disable comment.

    Args:
        path (Path): The path to the Python file to process.

    Returns:
        bool: True if the file was changed, False otherwise.
    """
    try:
        original_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logging.warning("Skipping unreadable file due to UnicodeDecodeError: %s", path)
        return False
    sep = '\r\n' if '\r\n' in original_text else '\n'
    lines = original_text.splitlines()
    changed = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped.startswith("except Exception:") or stripped.startswith("except Exception as")):
            if "pylint: disable=broad-exception-caught" not in line:
                lines[i] = line + "  # pylint: disable=broad-exception-caught"
                changed = True
    if changed:
        path.write_text(sep.join(lines) + sep, encoding="utf-8")
    return changed


def main():
    """Scan Python files in the 'modul' directory and mark broad exception handlers with a pylint disable comment."""
    changed_files = []
    for p in sorted(Path("modul").glob("**/*.py")):
        try:
            if process(p):
                changed_files.append(str(p))
        except OSError:
            logging.exception("Failed processing %s", p)
    if changed_files:
        print("Updated files:")
        for f in changed_files:
            print(f)
    else:
        print("No changes")


if __name__ == "__main__":
    main()
