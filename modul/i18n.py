"""Simple i18n helper for loading localized strings from JSON files."""

import json
import os
import logging
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
    """
    Load locale strings for the given language and cache the result.
    
    Attempts to read JSON from the module-local `locales/{lang_code}.json` file and store the parsed mapping in an internal cache. On file or decode errors, falls back to the English locale; if English is unavailable, returns an empty dict.
    
    Parameters:
        lang_code (str): Language code (e.g., "en", "fr") identifying the locale file to load.
    
    Returns:
        dict: Mapping of localization keys to localized strings for the resolved language, or an empty dict if no valid locale can be loaded.
    """
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
    """
    Retrieve the localized string for a message key in the specified language.
    
    Parameters:
        key (str): Message identifier to look up.
        lang_code (str): Language code (e.g., "en", "fr") used to select the locale.
    
    Returns:
        The localized string for `key` if present in the selected locale, otherwise the original `key`.
    """
    locale = load_locale(lang_code)
    return locale.get(key, key)


def gettext(key: str):
    """
    Return the localized string for the active runtime language, falling back to English.
    
    Parameters:
        key (str): Localization key to look up.
    
    Returns:
        str: The localized string for `key` in the detected language. If no language is set or detection fails, returns the English localization (or `key` itself if the entry is missing).
    
    Notes:
        If an exception occurs while reading runtime settings, a debug message is logged and the function falls back to English.
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
    """
    Clear the in-memory locale cache so subsequent locale lookups reload JSON files.
    
    Safe to call repeatedly; call this after changing the active language or updating locale files to ensure fresh data is loaded on the next t/gettext call.
    """
    _locales_cache.clear()