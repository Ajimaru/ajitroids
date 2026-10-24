"""Regression checks for required locale catalogs and key comparisons."""

import json

import pytest

from scripts import check_locales


@pytest.mark.parametrize("missing", [("en",), ("de",), ("en", "de")])
def test_missing_supported_catalog_fails(tmp_path, monkeypatch, capsys, missing):
    for name in ("en", "de"):
        if name not in missing:
            (tmp_path / f"{name}.json").write_text('{"hello": "Hello"}', encoding="utf-8")
    monkeypatch.setattr(check_locales, "LOCALES_DIR", tmp_path)

    assert check_locales.main() == 1
    output = capsys.readouterr()
    for name in missing:
        assert f"{name}.json" in output.err
    assert "All locale catalogs are in sync" not in output.out


@pytest.mark.parametrize("translation,expected", [
    ({"hello": "Hallo"}, 0),
    ({}, 1),
    ({"hello": "Hallo", "extra": "Extra"}, 1),
])
def test_supported_catalog_keys_are_compared(tmp_path, monkeypatch, translation, expected):
    (tmp_path / "en.json").write_text('{"hello": "Hello"}', encoding="utf-8")
    (tmp_path / "de.json").write_text(json.dumps(translation), encoding="utf-8")
    monkeypatch.setattr(check_locales, "LOCALES_DIR", tmp_path)

    assert check_locales.main() == expected
