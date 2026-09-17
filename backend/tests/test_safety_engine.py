import pytest
from backend.app.safety.engine import safety_engine

def test_safety_normal_case():
    result = safety_engine.evaluate(
        extracted_fields={"chief_complaint": "cut", "symptoms": ["bleeding"], "bleeding_rate": "slow"},
        raw_text="My finger has a minor scratch that bled a little",
        protocol_id="P001"
    )
    assert result.triggered is False
    assert result.highest_priority == "NORMAL"
    assert result.escalation_required is False
    assert result.stop_questioning is False

def test_safety_spurting_arterial_bleeding():
    result = safety_engine.evaluate(
        extracted_fields={"symptoms": ["bleeding"], "bleeding_rate": "spurting"},
        raw_text="Blood is spurting out like a fountain from my arm",
        protocol_id="P001"
    )
    assert result.triggered is True
    assert result.highest_priority == "IMMEDIATE_ESCALATION"
    assert result.escalation_required is True
    assert result.stop_questioning is True
    assert any(e.triggered_rule == "RF-001" for e in result.escalations)

def test_safety_chest_pain():
    result = safety_engine.evaluate(
        extracted_fields={"chief_complaint": "dizziness"},
        raw_text="I feel dizzy and have severe chest pain",
        protocol_id="P006"
    )
    assert result.triggered is True
    assert result.highest_priority == "IMMEDIATE_ESCALATION"
    assert any(e.triggered_rule == "RF-004" for e in result.escalations)

def test_safety_anaphylaxis_multilingual():
    # Hindi test
    result_hi = safety_engine.evaluate(
        extracted_fields={},
        raw_text="Mujhe rash hua hai aur sans lene me takleef ho rahi hai",
        protocol_id="P008",
        language="hi"
    )
    assert result_hi.triggered is True
    assert result_hi.highest_priority == "IMMEDIATE_ESCALATION"
    assert any(e.triggered_rule == "RF-003" for e in result_hi.escalations)
    assert "तत्काल सूचना" in result_hi.immediate_instruction

def test_explainable_escalation_structure():
    result = safety_engine.evaluate(
        extracted_fields={"burn_source": "chemical acid"},
        raw_text="Chemical acid fell on my hand",
        protocol_id="P003"
    )
    assert result.triggered is True
    assert len(result.escalations) > 0
    esc = result.escalations[0]
    assert esc.triggered_rule == "RF-006"
    assert esc.priority == "PRIORITY"
    assert esc.action is not None
    assert esc.protocol_id == "P003"
    assert "chemical" in str(esc.detected_information).lower()
