"""Tests for the version accessor.

The version is derived from the git tag at install time, so these tests only
make sense when the project is installed (editable installs included).
"""

import re
import sys
from importlib import metadata

import pytest

import main
from modul.version import __version__, get_version

UNKNOWN_VERSION = "0.0.0+unknown"
PEP440_VERSION = re.compile(r"^\d+\.\d+\.\d+(\.dev\d+)?$")


def _installed_version():
    """Return the installed distribution version, or None if not installed."""
    try:
        return metadata.version("ajitroids")
    except metadata.PackageNotFoundError:
        return None


pytestmark = pytest.mark.skipif(
    _installed_version() is None,
    reason="ajitroids is not installed; run uv sync or pip install -e .",
)


def test_version_is_pep440():
    """The reported version must be a PEP 440 version without local metadata."""
    assert PEP440_VERSION.fullmatch(get_version()), get_version()


def test_version_matches_installed_metadata():
    """The accessor must not invent a version of its own."""
    assert get_version() == _installed_version()


def test_get_version_matches_module_attribute():
    """Both public entry points must agree."""
    assert get_version() == __version__


def test_cli_version_flag_prints_version(monkeypatch, capsys):
    """`--version` prints the same string the menu shows."""
    monkeypatch.setattr(sys, "argv", ["main.py", "--version"])

    with pytest.raises(SystemExit) as exit_info:
        main.parse_arguments()

    assert exit_info.value.code == 0
    assert f"Ajitroids v{get_version()}" in capsys.readouterr().out
