import json
import os

_locales_cache = {}


def load_locale(lang_code: str):
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
    locale = load_locale(lang_code)
    return locale.get(key, key)


def gettext(key: str):
    """Get localized string for current settings language, fallback to English.

    This consults the runtime `current_settings.language` when available.
    """
    try:
        from modul import settings as settings_mod

        lang = getattr(settings_mod, "current_settings", None)
        if lang and getattr(lang, "language", None):
            return t(key, lang.language)
    except Exception:
        # If settings cannot be inspected, fall back to English
        pass
    return t(key, "en")
