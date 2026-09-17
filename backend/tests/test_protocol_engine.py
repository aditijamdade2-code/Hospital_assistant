import pytest
from backend.app.protocols.engine import protocol_engine

def test_protocol_matching_minor_cut():
    protocol = protocol_engine.select_protocol(
        chief_complaint="cut",
        symptoms=["bleeding"],
        raw_text="My finger got cut with a kitchen knife"
    )
    assert protocol is not None
    assert protocol.protocol_id in ["P001", "P002"]

def test_protocol_matching_burn():
    protocol = protocol_engine.select_protocol(
        chief_complaint="burn",
        symptoms=["pain"],
        raw_text="Garm paani se haath jal gaya"
    )
    assert protocol is not None
    assert protocol.protocol_id == "P003"

def test_protocol_missing_fields():
    p001 = protocol_engine.loader.get("P001")
    assert p001 is not None

    extracted = {"body_part": "finger"}
    missing = protocol_engine.get_missing_fields(p001, extracted)
    assert "bleeding_status" in missing
    assert "duration" in missing
    assert "body_part" not in missing

def test_protocol_next_question_multilingual():
    p001 = protocol_engine.loader.get("P001")
    assert p001 is not None

    q_en = protocol_engine.get_next_question(p001, ["body_part"], language="en")
    assert q_en is not None
    assert "cut located" in q_en.text

    q_hi = protocol_engine.get_next_question(p001, ["body_part"], language="hi")
    assert q_hi is not None
    assert q_hi.text_hi is not None

    q_mr = protocol_engine.get_next_question(p001, ["body_part"], language="mr")
    assert q_mr is not None
    assert q_mr.text_mr is not None

def test_protocol_guidance_marked_demo():
    p001 = protocol_engine.loader.get("P001")
    assert p001 is not None
    guidance = protocol_engine.get_guidance(p001, language="en")
    assert len(guidance) > 0
    assert any("DEMO" in g["instruction"] for g in guidance)
