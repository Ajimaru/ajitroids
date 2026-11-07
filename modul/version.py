"""Single runtime source for the version string.

The version is derived from the git tag at install/build time and shipped as
package metadata, so no version string lives in the repository. Reading it
through ``importlib.metadata`` keeps the displayed version in sync with the
tag that produced the installed distribution.

If the package is not installed (running from a bare source checkout), the
marker ``0.0.0+unknown`` is returned instead of guessing.
"""

import json
from importlib import metadata
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

_PACKAGE_NAME = "ajitroids"
_UNKNOWN_VERSION = "0.0.0+unknown"


def _read_version() -> str:
    """Return the installed package version, or the unknown marker."""
    try:
        distribution = metadata.distribution(_PACKAGE_NAME)
        source = Path(__file__).resolve()
        # Wheels identify their files in RECORD. Editable installs identify
        # their source root in the standard direct_url.json metadata.
        if any(
            Path(distribution.locate_file(file)).resolve() == source
            for file in distribution.files or ()
        ):
            return distribution.version
        direct_url = json.loads(distribution.read_text("direct_url.json") or "{}")
        if direct_url.get("dir_info", {}).get("editable"):
            url = urlparse(direct_url.get("url", ""))
            if url.scheme == "file":
                root = Path(url2pathname(url.path)).resolve()
                if root / "modul" / "version.py" == source:
                    return distribution.version
        return _UNKNOWN_VERSION
    except (metadata.PackageNotFoundError, ValueError, OSError):
        return _UNKNOWN_VERSION


__version__ = _read_version()


def get_version() -> str:
    """Return the current version string."""

    return __version__
