import logging
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

from .settings import current_settings


class TTSManager:
    def __init__(self):
        self.engine = None
        self.voice = ""
        self.language = getattr(current_settings, "language", "en")
        self.enabled = getattr(current_settings, "voice_announcements_enabled", True)
        self.preferred_voice = getattr(current_settings, "tts_voice", "")
        self.preferred_voice_lang = getattr(current_settings, "tts_voice_language", self.language)

        # Single-threaded executor for TTS operations to avoid concurrent engine.runAndWait calls
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._lock = threading.Lock()

        if pyttsx3 and self.enabled:
            try:
                self.engine = pyttsx3.init()
                voices = self.engine.getProperty("voices") or []
                selected = None
                if self.preferred_voice:
                    for v in voices:
                        if self.preferred_voice in (getattr(v, "id", ""), getattr(v, "name", "")):
                            selected = v
                            break
                if not selected and self.preferred_voice_lang:
                    for v in voices:
                        langs = getattr(v, "languages", []) or []
                        for lang_item in langs:
                            try:
                                # languages can be bytes or strings
                                ls = lang_item.decode() if isinstance(lang_item, (bytes, bytearray)) else str(lang_item)
                                if self.preferred_voice_lang in ls:
                                    selected = v
                                    break
                            except Exception:
                                continue
                        if selected:
                            break
                if selected:
                    try:
                        self.engine.setProperty("voice", selected.id)
                        self.voice = selected.id
                    except Exception:
                        pass
            except Exception:
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
                except Exception:
                    logging.exception("TTS speak failed")
        except Exception:
            # Ensure any unexpected errors in the worker are logged
            logging.exception("TTS worker failed")

    def speak(self, text: str):
        # Enqueue speak work on background thread and return immediately
        if not self.enabled:
            return
        try:
            # Submit to single-thread executor; it will serialize calls
            self._executor.submit(self._do_speak, text)
        except Exception:
            # If executor submission fails, attempt fallback logging
            logging.exception("TTS enqueue failed")
            logging.info("TTS fallback: %s", text)


# Module-level singleton
_tts_manager = None


def get_tts_manager():
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager()
    return _tts_manager
