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
    Load and return the locale mapping for the specified language, caching the result and falling back to English on error.
    
    Parameters:
        lang_code (str): BCP 47-like language code used to locate the corresponding JSON file (e.g., "en", "fr").
    
    Returns:
        dict: Mapping of translation keys to localized strings for the requested language; returns an empty dict if the locale cannot be loaded and no English fallback is available.
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
    Retrieve the localized string for a given key in the specified language.
    
    Parameters:
        key (str): The lookup key for the localized text.
        lang_code (str): Language code to use (e.g., "en"); defaults to "en".
    
    Returns:
        str: The localized string if present in the locale for `lang_code`, otherwise returns `key`.
    """
    locale = load_locale(lang_code)
    return locale.get(key, key)


def gettext(key: str):
    """
    Retrieve the localized text for a key using the runtime's configured language, falling back to English.
    
    Attempts to read the runtime language from settings_mod.current_settings.language; if a language is found, returns the localized text for that language. If the language is not set or an exception occurs while reading settings, a debug message is logged and the English localization is used.
    
    Parameters:
        key (str): The localization key to look up.
    
    Returns:
        str: The localized text for the resolved language. If no translation exists for the key, returns the key itself.
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
    Clear the internal locales cache so subsequent locale lookups reload JSON files.
    
    This forces the module to re-read locale JSON files on the next request; safe to call repeatedly.
    """
    _locales_cache.clear()