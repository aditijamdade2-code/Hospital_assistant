from typing import Optional
from backend.app.services.voice.stt_base import SpeechToTextProvider
from backend.app.services.voice.tts_base import TextToSpeechProvider

class MockSpeechToTextProvider(SpeechToTextProvider):
    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = "en", filename: str = "audio.wav") -> str:
        # Returns simulated transcription based on language if dummy audio passed
        if language == "hi":
            return "मेरी उंगली कट गई है और थोड़ा खून आ रहा है"
        elif language == "mr":
            return "माझ्या हातातून रक्त येत आहे"
        return "My finger got cut and it is bleeding a little"

class MockTextToSpeechProvider(TextToSpeechProvider):
    async def synthesize(self, text: str, language: Optional[str] = "en", voice: Optional[str] = None) -> bytes:
        # Returns minimal valid RIFF/WAV header (44 bytes) for audio playback test
        riff_header = (
            b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        )
        return riff_header
