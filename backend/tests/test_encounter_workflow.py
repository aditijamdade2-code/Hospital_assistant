import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_encounter_workflow_normal_case(client: AsyncClient):
    # 1. Create Encounter
    create_resp = await client.post("/api/v1/encounters", json={
        "patient_id": "OPD-9901",
        "age": 28,
        "gender": "Female",
        "language": "en"
    })
    assert create_resp.status_code == 201
    enc = create_resp.json()
    encounter_id = enc["encounter_id"]
    assert enc["priority"] == "NORMAL"
    assert enc["status"] == "COLLECTING_INFORMATION"

    # 2. Patient sends first message
    msg1_resp = await client.post(f"/api/v1/encounters/{encounter_id}/message", json={
        "message": "My finger got cut with paper and it is bleeding a little"
    })
    assert msg1_resp.status_code == 200
    m1_data = msg1_resp.json()
    assert m1_data["priority"] == "NORMAL"
    assert m1_data["encounter_status"] == "COLLECTING_INFORMATION"
    assert "assistant_response" in m1_data

    # 3. Check conversation history
    conv_resp = await client.get(f"/api/v1/encounters/{encounter_id}/conversation")
    assert conv_resp.status_code == 200
    conv_data = conv_resp.json()
    assert conv_data["total"] == 2
    assert conv_data["messages"][0]["sender"] == "PATIENT"
    assert conv_data["messages"][1]["sender"] == "ASSISTANT"

    # 4. Patient answers duration & bleeding status
    msg2_resp = await client.post(f"/api/v1/encounters/{encounter_id}/message", json={
        "message": "It happened 10 minutes ago, bleeding is controlled and pain is 2"
    })
    assert msg2_resp.status_code == 200
    m2_data = msg2_resp.json()

    # 5. Check encounter state after answer
    enc_detail = await client.get(f"/api/v1/encounters/{encounter_id}")
    assert enc_detail.status_code == 200
    enc_data = enc_detail.json()
    assert enc_data["protocol_id"] in ["P001", "P002"]

    # 6. Staff acknowledges encounter
    ack_resp = await client.post(f"/api/v1/encounters/{encounter_id}/acknowledge", json={
        "staff_id": "NURSE-SARAH",
        "notes": "Patient seated in cubicle 3"
    })
    assert ack_resp.status_code == 200
    assert ack_resp.json()["acknowledged_by"] == "NURSE-SARAH"

    # 7. Check Audit Logs
    audit_resp = await client.get(f"/api/v1/encounters/{encounter_id}/audit")
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    event_types = [l["event_type"] for l in logs]
    assert "ENCOUNTER_CREATED" in event_types
    assert "MESSAGE_PROCESSED" in event_types
    assert "STAFF_ACKNOWLEDGED" in event_types

@pytest.mark.asyncio
async def test_escalation_workflow_red_flag(client: AsyncClient):
    # 1. Create Encounter
    create_resp = await client.post("/api/v1/encounters", json={
        "patient_id": "OPD-EMERGENCY",
        "age": 55,
        "gender": "Male",
        "language": "en"
    })
    enc = create_resp.json()
    encounter_id = enc["encounter_id"]

    # 2. Patient reports arterial spurting blood
    msg_resp = await client.post(f"/api/v1/encounters/{encounter_id}/message", json={
        "message": "Arterial blood is spurting from deep laceration and not stopping"
    })
    assert msg_resp.status_code == 200
    res = msg_resp.json()
    assert res["priority"] == "IMMEDIATE_ESCALATION"
    assert res["escalation_required"] is True
    assert res["encounter_status"] == "ESCALATED"

    # 3. Check details for explainable escalation
    enc_detail = await client.get(f"/api/v1/encounters/{encounter_id}")
    d = enc_detail.json()
    assert d["priority"] == "IMMEDIATE_ESCALATION"
    assert d["escalation_reason"] is not None
    assert d["escalation_reason"]["triggered_rule"] in ["RF-001", "RF-002"]
    assert "action" in d["escalation_reason"]
