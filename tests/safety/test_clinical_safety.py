from backend.app.safety.engine import safety_engine

def test_cardiac_red_flag_priority():
    result = safety_engine.evaluate(
        extracted_fields={"chief_complaint": "chest pain"},
        raw_text="Left chest pain spreading to arm and shortness of breath",
        protocol_id="P006"
    )
    assert result.triggered is True
    assert result.highest_priority == "IMMEDIATE_ESCALATION"
    assert result.stop_questioning is True
    assert any(e.triggered_rule == "RF-004" for e in result.escalations)

def test_anaphylactic_airway_closure():
    result = safety_engine.evaluate(
        extracted_fields={"symptoms": ["itching", "lip swelling"]},
        raw_text="My throat is closing up and I cannot breathe after eating peanuts",
        protocol_id="P008"
    )
    assert result.triggered is True
    assert result.highest_priority == "IMMEDIATE_ESCALATION"
    assert any(e.triggered_rule == "RF-003" for e in result.escalations)
