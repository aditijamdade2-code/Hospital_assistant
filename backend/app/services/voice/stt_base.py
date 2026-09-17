from abc import ABC, abstractmethod
from typing import Optional

class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = "en", filename: str = "audio.wav") -> str:
        """
        Transcribes raw audio bytes into text in the specified language (en, hi, mr).
        """
        pass
