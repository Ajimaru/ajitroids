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


    def __init__(self):
        """
        Create and configure a Text-to-Speech manager based on current settings.
        
        Initializes logger, internal state (language, enabled flag, preferred voice and language),
        a single-worker ThreadPoolExecutor for serialized TTS operations, and an internal lock.
        If a TTS backend is available and enabled, attempts to initialize the engine and
        apply a preferred voice (by id/name or by language). On failure to initialize or
        apply a voice, the manager falls back to a disabled engine state while preserving
        configured preferences.
        """
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
        """
        Find the first voice whose declared languages contain the given language code.
        
        Iterates the provided voice objects and checks each voice's `languages` entries for a match containing `lang_code`. Byte or bytearray language entries are decoded to strings; entries that fail to decode are skipped.
        
        Parameters:
            voices (iterable): Iterable of voice-like objects (expected to have a `languages` attribute).
            lang_code (str): Language code substring to match (for example, "en" or "en_US").
        
        Returns:
            voice or None: The first matching voice object, or `None` if no match is found.
        """
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
        """
        Perform speech synthesis for the provided text in the TTS worker.
        
        If no TTS engine is available, logs a fallback message and returns. Any exceptions raised while issuing speech commands or from the worker are caught and logged; exceptions are not propagated.
        
        Parameters:
            text (str): The text to synthesize and speak.
        """
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
        """
        Enqueue the provided text to be spoken asynchronously by the manager.
        
        If TTS is disabled, this is a no-op. If enqueuing fails, the failure is logged and the text is written to the log as a fallback.
        
        Parameters:
            text (str): The text to speak.
        """
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
        """
        Retrieve available TTS voices from the underlying engine.
        
        Each voice is represented as a dict with keys:
        - `id` (str): voice identifier (falls back to `name` or str(voice) if missing)
        - `name` (str): human-readable voice name
        - `languages` (list): list of language tags (may be empty)
        
        Returns:
            list: A list of voice dictionaries as described above. Returns an empty list if no engine is available or on error.
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
        """
        Update the manager's preferred TTS voice and apply it to the underlying engine if available.
        
        Parameters:
            voice_id (str): Voice identifier or display name to select. Pass an empty string to clear the preference and revert to the engine default.
            voice_language (Optional[str]): Optional language code to store as the preferred voice language for future selection.
        
        Returns:
            bool: `True` if the preferred voice was applied to the engine or the preference was cleared successfully, `False` otherwise (including when no engine is available or the specified voice could not be found/applied).
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
    """
    Get the singleton TTSManager, creating it lazily with thread-safe initialization.
    
    Returns:
        TTSManager: The singleton TTSManager instance.
    """
    global _TTS_MANAGER_INSTANCE
    if _TTS_MANAGER_INSTANCE is None:
        with _tts_manager_lock:
            if _TTS_MANAGER_INSTANCE is None:
                # initialize once while holding the lock
                _TTS_MANAGER_INSTANCE = TTSManager()
    return _TTS_MANAGER_INSTANCE