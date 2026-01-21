import logging

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
                        for l in langs:
                            try:
                                # languages can be bytes or strings
                                ls = l.decode() if isinstance(l, (bytes, bytearray)) else str(l)
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

    def speak(self, text: str):
        if not self.enabled:
            return
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                logging.exception("TTS speak failed")
        else:
            # Fallback for environments without TTS: log/print the announcement
            logging.info("TTS fallback: %s", text)


# Module-level singleton
_tts_manager = None


def get_tts_manager():
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager()
    return _tts_manager
