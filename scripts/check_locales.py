#!/usr/bin/env python3
"""Verify the JSON locale catalogs are in sync with each other.

This project does not use gettext/Babel — `modul/i18n.py` loads plain JSON
files from `modul/locales/`. A key that exists in the reference locale but is
missing from a translation falls back to English silently at runtime, so
nothing fails visibly and the gap goes unnoticed. This check makes that gap a
build error instead.

Run it directly (`python scripts/check_locales.py`) or via CI.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "modul" / "locales"
REFERENCE = "en"


def flatten(obj, prefix: str = "") -> set[str]:
    """Return the set of dotted key paths in a nested locale mapping."""
    keys: set[str] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            keys.add(path)
            keys |= flatten(value, path)
    return keys


def main() -> int:
    reference_path = LOCALES_DIR / f"{REFERENCE}.json"
    if not reference_path.exists():
        print(f"Missing reference locale: {reference_path}", file=sys.stderr)
        return 1

    catalogs: dict[str, set[str]] = {}
    for path in sorted(LOCALES_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"{path}: invalid JSON — {exc}", file=sys.stderr)
            return 1
        catalogs[path.stem] = flatten(data)

    reference_keys = catalogs[REFERENCE]
    print(f"{REFERENCE}.json: {len(reference_keys)} keys (reference)")

    failed = False
    for name, keys in catalogs.items():
        if name == REFERENCE:
            continue
        missing = sorted(reference_keys - keys)
        extra = sorted(keys - reference_keys)
        if missing or extra:
            failed = True
            print(f"\n{name}.json is out of sync with {REFERENCE}.json:",
                  file=sys.stderr)
            for key in missing:
                print(f"  + missing translation: {key}", file=sys.stderr)
            for key in extra:
                print(f"  - key not in {REFERENCE}.json: {key}",
                      file=sys.stderr)
        else:
            print(f"{name}.json: {len(keys)} keys, in sync")

    if failed:
        print("\nAdd the missing keys to the affected catalog(s), or remove "
              "the stale ones, and commit the result.", file=sys.stderr)
        return 1

    print("\nAll locale catalogs are in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
