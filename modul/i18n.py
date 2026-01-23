"""Simple i18n helper for loading localized strings from JSON files."""

import json
import os
import logging
# Try to import the runtime settings module once at import time. Keep the
# reference optional to avoid repeated dynamic imports inside `gettext()` and
# to satisfy linters complaining about imports outside top-level (C0415).
logger = logging.getLogger(__name__)

_locales_cache = {}

# Try to import the runtime settings module once at import time. Keep the
# reference optional to avoid repeated dynamic imports inside `gettext()` and
# to satisfy linters complaining about imports outside top-level (C0415).
try:
    from modul import settings as settings_mod  # type: ignore
except (ImportError, ModuleNotFoundError):  # pragma: no cover - optional runtime integration
    settings_mod = None


def load_locale(lang_code: str):
    """Load and return the locale dictionary for the given language code."""
    if lang_code in _locales_cache:
        return _locales_cache[lang_code]

    locales_dir = os.path.join(os.path.dirname(__file__), "locales")
    path = os.path.join(locales_dir, f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            _locales_cache[lang_code] = data
            return data
    except (OSError, json.JSONDecodeError):
        # Fallback to English
        if lang_code != "en":
            return load_locale("en")
        return {}


def t(key: str, lang_code: str = "en"):
    """Return the localized string for the given key and language code."""
    locale = load_locale(lang_code)
    return locale.get(key, key)


def gettext(key: str):
    """Get localized string for current settings language, fallback to English.

    This consults the runtime `current_settings.language` when available.
    """
    try:
        lang = getattr(settings_mod, "current_settings", None) if settings_mod else None
        if lang and getattr(lang, "language", None):
            return t(key, lang.language)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.debug(
            "i18n.gettext: Exception reading settings_mod.current_settings.language for key '%s': %r",
            key, e, exc_info=True
        )
    return t(key, "en")


def reload_locales():
    """Clear the locale cache so subsequent gettext calls reload JSON files.

    Call this after changing the active language to force fresh loading of
    locale files. This is safe to call repeatedly.
    """
    _locales_cache.clear()
