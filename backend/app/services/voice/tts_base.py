from abc import ABC, abstractmethod
from typing import Optional

class TextToSpeechProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, language: Optional[str] = "en", voice: Optional[str] = None) -> bytes:
        """
        Synthesizes text into audio bytes (e.g. mp3 or wav).
        """
        pass
