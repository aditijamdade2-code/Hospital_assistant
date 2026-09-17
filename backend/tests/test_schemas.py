import pytest
from datetime import datetime
from backend.app.schemas.encounter import EncounterCreate, EncounterResponse, PatientBase
from backend.app.schemas.protocol import ProtocolSchema
from backend.app.schemas.safety import RedFlagRule, EscalationDetail

def test_encounter_create_schema():
    create_data = {
        "patient_id": "OPD-1234",
        "age": 42,
        "gender": "Female",
        "language": "hi",
        "initial_complaint": "ungli kat gayi hai"
    }
    obj = EncounterCreate(**create_data)
    assert obj.patient_id == "OPD-1234"
    assert obj.age == 42
    assert obj.gender == "Female"
    assert obj.language == "hi"
    assert obj.initial_complaint == "ungli kat gayi hai"

def test_encounter_response_defaults():
    resp = EncounterResponse(
        encounter_id="ENC-000001",
        patient=PatientBase(patient_id="OPD-001", age=30, gender="Male"),
        language="en",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert resp.encounter_id == "ENC-000001"
    assert resp.priority == "NORMAL"
    assert resp.status == "COLLECTING_INFORMATION"
    assert resp.symptoms == []
    assert resp.red_flags == []
    assert resp.escalation_required is False

def test_escalation_detail_schema():
    detail = EscalationDetail(
        priority="IMMEDIATE_ESCALATION",
        triggered_rule="RF-001",
        rule_description="Arterial spurting bleeding",
        detected_information={"bleeding_rate": "spurting"},
        action="Alert trauma triage"
    )
    assert detail.priority == "IMMEDIATE_ESCALATION"
    assert detail.triggered_rule == "RF-001"
    assert detail.detected_information["bleeding_rate"] == "spurting"
