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
PEP440_VERSION = re.compile(r"^\d+\.\d+\.\d+((a|b|rc)\d+)?(\.dev\d+)?$")


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


@pytest.mark.parametrize("value", ["1.2.3", "1.2.3.dev4", "1.2.3a1", "1.2.3b2", "1.2.3rc1",
                                  "1.2.3a1.dev2", "1.2.3b1.dev2", "1.2.3rc1.dev2"])
def test_version_pattern_accepts_release_stages(value):
    assert PEP440_VERSION.fullmatch(value)


def test_compatibility_version():
    from modul._version import version
    assert version == get_version()


@pytest.mark.parametrize("editable", [False, True])
def test_version_rejects_unrelated_install(monkeypatch, tmp_path, editable):
    import json
    from unittest.mock import Mock
    from modul import version
    dist = Mock(files=["modul/version.py"])
    dist.locate_file.side_effect = lambda file: tmp_path / file
    dist.read_text.return_value = json.dumps({
        "url": tmp_path.as_uri(), "dir_info": {"editable": editable}})
    monkeypatch.setattr(metadata, "distribution", lambda name: dist)
    assert version._read_version() == UNKNOWN_VERSION


def test_version_without_distribution(monkeypatch):
    from modul import version
    def missing(name):
        raise metadata.PackageNotFoundError(name)
    monkeypatch.setattr(metadata, "distribution", missing)
    assert version._read_version() == UNKNOWN_VERSION


@pytest.mark.parametrize("editable", [False, True])
def test_version_accepts_own_distribution(monkeypatch, editable):
    import json
    from pathlib import Path
    from unittest.mock import Mock
    from modul import version
    source = Path(version.__file__).resolve()
    dist = Mock(version="1.2.3rc1", files=[] if editable else ["modul/version.py"])
    dist.locate_file.return_value = source
    dist.read_text.return_value = json.dumps({
        "url": source.parent.parent.as_uri(), "dir_info": {"editable": editable}})
    monkeypatch.setattr(metadata, "distribution", lambda name: dist)
    assert version._read_version() == "1.2.3rc1"
