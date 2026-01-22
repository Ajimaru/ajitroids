"""Version helper for runtime display.

Tries to read the installed package version via importlib.metadata. If the
package is not installed (e.g., running from source), it falls back to the
setuptools-scm generated ``modul._version``. This avoids needing to bump
version strings in multiple places.
"""

from importlib import metadata


# Prefer generated version from setuptools-scm when available. Keep as a
# module-level optional value to avoid repeated dynamic imports inside
# functions and to satisfy linters complaining about imports outside
# the top-level (C0415).
try:
    from modul._version import __version__ as _generated_version  # type: ignore
except Exception:  # pragma: no cover - best-effort fallback, tested at runtime
    _generated_version = None


def _fallback_version() -> str:
    """TODO: add docstring."""
    # Use the module-level cached generated version when present.
    if _generated_version:
        return _generated_version
    return "0.0.0"


try:
    __version__ = metadata.version("ajitroids")
except metadata.PackageNotFoundError:
    __version__ = _fallback_version()


def get_version() -> str:
    """Return the current version string."""

    return __version__
