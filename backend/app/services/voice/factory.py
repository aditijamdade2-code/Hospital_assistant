from backend.app.core.config import settings
from backend.app.services.voice.stt_base import SpeechToTextProvider
from backend.app.services.voice.tts_base import TextToSpeechProvider
from backend.app.services.voice.mock_voice_provider import MockSpeechToTextProvider, MockTextToSpeechProvider
from backend.app.services.voice.openai_voice_provider import OpenAISpeechToTextProvider, OpenAITextToSpeechProvider

def get_stt_provider() -> SpeechToTextProvider:
    if settings.LLM_PROVIDER.lower() == "openai" and settings.OPENAI_API_KEY:
        return OpenAISpeechToTextProvider()
    return MockSpeechToTextProvider()

def get_tts_provider() -> TextToSpeechProvider:
    if settings.LLM_PROVIDER.lower() == "openai" and settings.OPENAI_API_KEY:
        return OpenAITextToSpeechProvider()
    return MockTextToSpeechProvider()
