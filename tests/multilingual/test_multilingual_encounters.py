import pytest
from backend.app.services.llm.mock_provider import MockLocalLLMProvider

@pytest.mark.asyncio
async def test_multilingual_translation_and_normalization():
    provider = MockLocalLLMProvider()
    
    # 1. English
    en_res = await provider.extract_information(
        text="I burned my arm with boiling water 20 minutes ago",
        conversation_history=[],
        current_language="en"
    )
    assert en_res.chief_complaint == "burn"
    assert en_res.body_part == "arm"
    assert "20 minutes" in str(en_res.duration)

    # 2. Hindi
    hi_res = await provider.extract_information(
        text="गरम पानी से हाथ जल गया है",
        conversation_history=[],
        current_language="hi"
    )
    assert hi_res.chief_complaint == "burn"
    assert hi_res.body_part == "hand"
    assert hi_res.detected_language == "hi"

    # 3. Marathi
    mr_res = await provider.extract_information(
        text="माझ्या हातावर गरम पाणी सांडले आणि भाजले",
        conversation_history=[],
        current_language="mr"
    )
    assert mr_res.chief_complaint == "burn"
    assert mr_res.body_part == "hand"
    assert mr_res.detected_language == "mr"
