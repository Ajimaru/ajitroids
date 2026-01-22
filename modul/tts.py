"""Module modul.tts — minimal module docstring."""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

try:
    import pyttsx3
except Exception:  # pylint: disable=broad-exception-caught
    pyttsx3 = None

from .settings import current_settings


class TTSManager:
    def __init__(self):
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

        if pyttsx3 and self.enabled:
            try:
                self.engine = pyttsx3.init()
                voices = self.engine.getProperty("voices") or []
                selected = None
                if self.preferred_voice:
                    for v in voices:
                        vid = getattr(v, "id", "")
                        vname = getattr(v, "name", "")
                        if self.preferred_voice in (vid, vname):
                            selected = v
                            break
                if not selected and self.preferred_voice_lang:
                    for v in voices:
                        langs = getattr(v, "languages", []) or []
                        for lang_item in langs:
                            try:
                                # languages can be bytes or strings
                                if isinstance(lang_item, (bytes, bytearray)):
                                    ls = lang_item.decode()
                                else:
                                    ls = str(lang_item)
                                if self.preferred_voice_lang in ls:
                                    selected = v
                                    break
                            except Exception:  # pylint: disable=broad-exception-caught
                                continue
                        if selected:
                            break
                if selected:
                    try:
                        self.engine.setProperty("voice", selected.id)
                        self.voice = selected.id
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass
            except Exception:  # pylint: disable=broad-exception-caught
                self.engine = None

    def _do_speak(self, text: str):
        # Worker method: runs in background thread
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
        # Enqueue speak work on background thread and return immediately
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
            voices = self.engine.getProperty("voices") or []
            selected = None
            for v in voices:
                vid = getattr(v, "id", "")
                vname = getattr(v, "name", "")
                if self.preferred_voice in (vid, vname):
                    selected = v
                    break

            if selected:
                try:
                    self.engine.setProperty("voice", selected.id)
                    self.voice = selected.id
                    return True
                except Exception:  # pylint: disable=broad-exception-caught
                    logging.exception("Failed to set TTS voice")
                    return False

            return False
        except Exception:  # pylint: disable=broad-exception-caught
            logging.exception("Error setting preferred voice")
            return False


# Module-level singleton
_tts_manager = None


def get_tts_manager():
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager()
    return _tts_manager
