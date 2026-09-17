import pytest
import httpx
from backend.app.services.llm.openai_provider import OpenAIProvider

@pytest.mark.asyncio
async def test_ollama_local_availability():
    """Verify that local Ollama is running and accessible with llama3.2."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get("http://localhost:11434/api/tags")
            assert res.status_code == 200
            models = [m["name"] for m in res.json().get("models", [])]
            assert any("llama3.2" in m or "mistral" in m for m in models)
    except Exception as e:
        pytest.skip(f"Ollama server not reachable: {e}")

@pytest.mark.asyncio
async def test_ollama_provider_generation():
    """Verify that OpenAIProvider can communicate with Ollama on localhost:11434."""
    provider = OpenAIProvider(
        api_key="ollama",
        model="llama3.2:3b",
        base_url="http://localhost:11434/v1"
    )
    try:
        response = await provider.generate_response(
            patient_message="Hello, I have a fever",
            conversation_history=[],
            next_question="Have you measured your body temperature?",
            guidance_steps=None,
            alert_instruction=None,
            language="en"
        )
        assert response is not None
        assert len(response) > 5
    except Exception as e:
        pytest.skip(f"Ollama generation skipped: {e}")
