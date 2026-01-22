"""Version helper for runtime display.

Tries to read the installed package version via importlib.metadata. If the
package is not installed (e.g., running from source), it falls back to the
setuptools-scm generated ``modul._version``. This avoids needing to bump
version strings in multiple places.
"""

from importlib import metadata


def _fallback_version() -> str:
    try:
        from modul._version import \
            __version__ as generated_version  # type: ignore

        return generated_version
    except Exception:
        return "0.0.0"


try:
    __version__ = metadata.version("ajitroids")
except metadata.PackageNotFoundError:
    __version__ = _fallback_version()


def get_version() -> str:
    """Return the current version string."""

    return __version__
