"""Pytest configuration shared by the whole test suite.

Tests import helper modules that live outside the installed package, for
example `from scripts import check_locales`. Those are plain files in the
repository, not part of the `ajitroids` distribution, so they are only
importable when the repository root is on `sys.path`.

`python -m pytest` happens to prepend the current directory, which hides the
problem locally, but the bare `pytest` console script used in CI does not —
collection then fails with `ModuleNotFoundError: No module named 'scripts'`.
Inserting the root here makes both invocations behave the same.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
