"""Single runtime source for the version string.

The version is derived from the git tag at install/build time and shipped as
package metadata, so no version string lives in the repository. Reading it
through ``importlib.metadata`` keeps the displayed version in sync with the
tag that produced the installed distribution.

If the package is not installed (running from a bare source checkout), the
marker ``0.0.0+unknown`` is returned instead of guessing.
"""

from importlib import metadata

_PACKAGE_NAME = "ajitroids"
_UNKNOWN_VERSION = "0.0.0+unknown"


def _read_version() -> str:
    """Return the installed package version, or the unknown marker."""
    try:
        return metadata.version(_PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return _UNKNOWN_VERSION


__version__ = _read_version()


def get_version() -> str:
    """Return the current version string."""

    return __version__
