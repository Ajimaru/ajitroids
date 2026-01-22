"""Module modul.tts — minimal module docstring."""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import collections.abc

try:
    import pyttsx3
except ImportError:
    PYTTSX3 = None
else:
    PYTTSX3 = pyttsx3

from .settings import current_settings


class TTSManager:
    """Manages text-to-speech functionality using pyttsx3."""

    def __init__(self):
        """Initialize the TTS manager with settings and engine setup."""
        self.logger = logging.getLogger(__name__)
        self.engine = None
        self.voice = ""
        self.language = getattr(current_settings, "language", "en")
        self.enabled = getattr(
            current_settings, "voice_announcements_enabled", True
        )
        self.preferred_voice = getattr(current_settings, "tts_voice", "")
        self.preferred_voice_lang = getattr(
            current_settings, "tts_voice_language", self.language
        )

        # Single-threaded executor for TTS operations.
        # This avoids concurrent `engine.runAndWait()` calls.
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._lock = threading.Lock()

        if PYTTSX3 and self.enabled:
            try:
                self.engine = PYTTSX3.init()
                voices_prop = self.engine.getProperty("voices")
                voices = list(voices_prop) if isinstance(voices_prop, collections.abc.Iterable) else []
                selected = None
                if self.preferred_voice:
                    for v in voices:
                        vid = getattr(v, "id", "")
                        vname = getattr(v, "name", "")
                        if self.preferred_voice in (vid, vname):
                            selected = v
                            break
                if not selected and self.preferred_voice_lang:
                    selected = self._find_voice_by_language(voices, self.preferred_voice_lang)
                if selected:
                    try:
                        self.engine.setProperty("voice", getattr(selected, "id", ""))
                        self.voice = getattr(selected, "id", "")
                    except Exception as exc:  # pylint: disable=broad-exception-caught
                        self.logger.warning(
                            "TTSManager.__init__: Failed to setProperty('voice', %r) on engine %r: %s",
                            getattr(selected, "id", ""), self.engine, exc, exc_info=True
                        )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.logger.error(
                    "TTSManager.__init__: Exception during TTS engine initialization (self.engine assignment): %s",
                    exc, exc_info=True
                )
                self.engine = None

    def _find_voice_by_language(self, voices, lang_code):
        """Return the first voice whose languages include lang_code."""
        for voice in voices:
            langs = getattr(voice, "languages", []) or []
            for lang in langs:
                try:
                    if isinstance(lang, (bytes, bytearray)):
                        lang_str = lang.decode()
                    else:
                        lang_str = str(lang)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logging.debug(
                        "TTS: Failed to decode language %r for voice %r: %s",
                        lang, getattr(voice, 'id', None), e
                    )
                    continue
                if lang_code in lang_str:
                    return voice
        return None

    def _do_speak(self, text: str):
        """Execute text-to-speech in a background thread."""
        try:
            with self._lock:
                if not self.engine:
                    logging.info("TTS fallback: %s", text)
                    return
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception:  # pylint: disable=broad-exception-caught
                    logging.exception("TTS speak failed")
        except Exception:  # pylint: disable=broad-exception-caught
            # Ensure any unexpected errors in the worker are logged
            logging.exception("TTS worker failed")

    def speak(self, text: str):
        """Enqueue text for speech synthesis in background."""
        if not self.enabled:
            return
        try:
            # Submit to single-thread executor; it will serialize calls
            self._executor.submit(self._do_speak, text)
        except Exception:  # pylint: disable=broad-exception-caught
            # If executor submission fails, attempt fallback logging
            logging.exception("TTS enqueue failed")
            logging.info("TTS fallback: %s", text)

    def list_voices(self):
        """Return a list of available voices from the underlying engine.

        Each entry is a dict with at least `id` and `name`, and an optional
        `languages` entry.
        """
        voices = []
        try:
            if not self.engine:
                return []
            raw = self.engine.getProperty("voices") or []
            # Ensure raw is iterable
            if not isinstance(raw, collections.abc.Iterable):
                raw = [raw]
            for v in raw:
                try:
                    vid = getattr(v, "id", None) or getattr(v, "name", str(v))
                    name = getattr(v, "name", vid)
                    langs = getattr(v, "languages", []) or []
                    entry = {"id": vid, "name": name, "languages": langs}
                    voices.append(entry)
                except Exception:  # pylint: disable=broad-exception-caught
                    continue
        except Exception:  # pylint: disable=broad-exception-caught
            logging.exception("Failed to list TTS voices")
        return voices

    def set_preferred_voice(self, voice_id: str, voice_language: Optional[str] = None):
        """Set the preferred voice on the engine and update the manager state.

        Pass an empty string to revert to the engine default.
        """
        try:
            # Update internal preferred values
            self.preferred_voice = voice_id or ""
            if voice_language:
                self.preferred_voice_lang = voice_language

            if not self.engine:
                return False

            if not self.preferred_voice:
                # No preferred voice: do not change engine property. Let the
                # engine default apply instead.
                self.voice = ""
                return True

            # Try to find matching voice by id or name
            voices_prop = self.engine.getProperty("voices")
            if isinstance(voices_prop, collections.abc.Iterable):
                voices = list(voices_prop)
            elif voices_prop:
                voices = [voices_prop]
            else:
                voices = []
            selected = None
            for v in voices:
                vid = getattr(v, "id", "")
                vname = getattr(v, "name", "")
                if self.preferred_voice in (vid, vname):
                    selected = v
                    break

            if selected:
                try:
                    voice_id = getattr(selected, "id", "")
                    self.engine.setProperty("voice", voice_id)
                    self.voice = voice_id
                    return True
                except Exception:  # pylint: disable=broad-exception-caught
                    logging.exception("Failed to set TTS voice")
                    return False

            return False
        except Exception:  # pylint: disable=broad-exception-caught
            logging.exception("Error setting preferred voice")
            return False


# Module-level singleton lock and instance
_tts_manager_lock = threading.Lock()
_TTS_MANAGER_INSTANCE = None


def get_tts_manager():
    """Get the singleton TTS manager instance."""
    global _TTS_MANAGER_INSTANCE
    if _TTS_MANAGER_INSTANCE is None:
        with _tts_manager_lock:
            if _TTS_MANAGER_INSTANCE is None:
                # initialize once while holding the lock
                _TTS_MANAGER_INSTANCE = TTSManager()
    return _TTS_MANAGER_INSTANCE
