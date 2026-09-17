import pytest
from backend.app.services.llm.mock_provider import MockLocalLLMProvider

@pytest.mark.asyncio
async def test_extraction_english():
    provider = MockLocalLLMProvider()
    result = await provider.extract_information(
        text="My finger got cut and it is bleeding a little",
        conversation_history=[],
        current_language="en"
    )
    assert result.chief_complaint == "cut"
    assert result.body_part == "finger"
    assert "bleeding" in result.symptoms
    assert result.severity == "mild"
    # Unknown values must remain None / null!
    assert result.duration is None

@pytest.mark.asyncio
async def test_extraction_hindi():
    provider = MockLocalLLMProvider()
    result = await provider.extract_information(
        text="मेरी उंगली कट गई है और थोड़ा खून आ रहा है",
        conversation_history=[],
        current_language="hi"
    )
    assert result.chief_complaint == "cut"
    assert result.body_part == "finger"
    assert "bleeding" in result.symptoms
    assert result.detected_language == "hi"

@pytest.mark.asyncio
async def test_extraction_marathi():
    provider = MockLocalLLMProvider()
    result = await provider.extract_information(
        text="माझ्या हातातून रक्त येत आहे",
        conversation_history=[],
        current_language="mr"
    )
    assert result.chief_complaint == "bleeding"
    assert result.body_part == "hand"
    assert "bleeding" in result.symptoms
    assert result.detected_language == "mr"

@pytest.mark.asyncio
async def test_extraction_hinglish_mixed():
    provider = MockLocalLLMProvider()
    result = await provider.extract_information(
        text="Doctor, mere hand mein cut hua hai and slight pain hai",
        conversation_history=[],
        current_language="hi"
    )
    assert result.chief_complaint == "cut"
    assert result.body_part == "hand"
    assert "pain" in result.symptoms

@pytest.mark.asyncio
async def test_no_hallucination_on_missing_info():
    provider = MockLocalLLMProvider()
    result = await provider.extract_information(
        text="I am feeling unwell today",
        conversation_history=[],
        current_language="en"
    )
    # Must NOT hallucinate cut, burn, etc.
    assert result.chief_complaint is None
    assert result.body_part is None
    assert result.duration is None
