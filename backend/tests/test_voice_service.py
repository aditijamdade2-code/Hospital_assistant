import pytest
from httpx import AsyncClient
from backend.app.services.voice.factory import get_stt_provider, get_tts_provider

@pytest.mark.asyncio
async def test_voice_stt_and_tts_providers():
    stt = get_stt_provider()
    tts = get_tts_provider()

    dummy_audio = b"dummy-audio-bytes"
    text_en = await stt.transcribe(dummy_audio, language="en")
    assert "finger" in text_en.lower() or "cut" in text_en.lower()

    text_hi = await stt.transcribe(dummy_audio, language="hi")
    assert "उंगली" in text_hi or "खून" in text_hi

    text_mr = await stt.transcribe(dummy_audio, language="mr")
    assert "रक्त" in text_mr or "हात" in text_mr

    audio_bytes = await tts.synthesize("Please apply pressure", language="en")
    assert len(audio_bytes) > 0
    assert audio_bytes.startswith(b"RIFF")

@pytest.mark.asyncio
async def test_voice_api_endpoints(client: AsyncClient):
    # Test Synthesize endpoint
    synth_resp = await client.post("/api/v1/voice/synthesize", json={
        "text": "Hello, how can I help you?",
        "language": "en"
    })
    assert synth_resp.status_code == 200
    assert synth_resp.headers["content-type"] == "audio/wav"

    # Test Transcribe endpoint
    files = {"file": ("test.wav", b"RIFF-dummy-sample", "audio/wav")}
    data = {"language": "hi"}
    trans_resp = await client.post("/api/v1/voice/transcribe", files=files, data=data)
    assert trans_resp.status_code == 200
    payload = trans_resp.json()
    assert "transcription" in payload
    assert payload["language"] == "hi"
