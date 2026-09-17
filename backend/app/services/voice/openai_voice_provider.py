import httpx
import logging
from typing import Optional
from backend.app.services.voice.stt_base import SpeechToTextProvider
from backend.app.services.voice.tts_base import TextToSpeechProvider
from backend.app.services.voice.mock_voice_provider import MockSpeechToTextProvider, MockTextToSpeechProvider
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAISpeechToTextProvider(SpeechToTextProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = (base_url or settings.OPENAI_BASE_URL).rstrip("/")
        self.fallback = MockSpeechToTextProvider()

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = "en", filename: str = "audio.wav") -> str:
        if not self.api_key:
            logger.warning("OpenAI API key not set, using mock STT fallback.")
            return await self.fallback.transcribe(audio_bytes, language, filename)

        try:
            files = {"file": (filename, audio_bytes, "audio/wav")}
            data = {"model": "whisper-1"}
            if language:
                data["language"] = language

            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    data=data,
                    files=files
                )
                if res.status_code == 200:
                    return res.json().get("text", "")
                else:
                    logger.error(f"Whisper STT failed with status {res.status_code}: {res.text}")
                    return await self.fallback.transcribe(audio_bytes, language, filename)
        except Exception as e:
            logger.error(f"Whisper STT request exception: {e}")
            return await self.fallback.transcribe(audio_bytes, language, filename)


class OpenAITextToSpeechProvider(TextToSpeechProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = (base_url or settings.OPENAI_BASE_URL).rstrip("/")
        self.fallback = MockTextToSpeechProvider()

    async def synthesize(self, text: str, language: Optional[str] = "en", voice: Optional[str] = None) -> bytes:
        if not self.api_key:
            logger.warning("OpenAI API key not set, using mock TTS fallback.")
            return await self.fallback.synthesize(text, language, voice)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{self.base_url}/audio/speech",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "tts-1",
                        "input": text,
                        "voice": voice or "alloy"
                    }
                )
                if res.status_code == 200:
                    return res.content
                else:
                    logger.error(f"OpenAI TTS failed with status {res.status_code}: {res.text}")
                    return await self.fallback.synthesize(text, language, voice)
        except Exception as e:
            logger.error(f"OpenAI TTS request exception: {e}")
            return await self.fallback.synthesize(text, language, voice)
