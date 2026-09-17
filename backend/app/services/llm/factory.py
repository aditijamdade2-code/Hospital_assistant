from backend.app.core.config import settings
from backend.app.services.llm.base import LLMProvider
from backend.app.services.llm.mock_provider import MockLocalLLMProvider
from backend.app.services.llm.openai_provider import OpenAIProvider

def get_llm_provider() -> LLMProvider:
    provider_type = settings.LLM_PROVIDER.lower().strip()
    if provider_type == "ollama":
        return OpenAIProvider(
            api_key="ollama",
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL
        )
    if provider_type == "openai" and settings.OPENAI_API_KEY:
        return OpenAIProvider()
    return MockLocalLLMProvider()
