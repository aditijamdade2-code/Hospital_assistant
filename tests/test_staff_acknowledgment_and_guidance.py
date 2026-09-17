import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database.session import init_db

@pytest.mark.asyncio
async def test_staff_acknowledgment_and_patient_chat_visibility():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Patient creates encounter with complaint
        res = await client.post("/api/v1/encounters", json={
            "age": 35,
            "gender": "male",
            "language": "en",
            "initial_complaint": "Severe stomach ache and mild fever since yesterday"
        })
        assert res.status_code == 201
        enc_data = res.json()
        encounter_id = enc_data["encounter_id"]
        assert enc_data["status"] in ["COLLECTING_INFORMATION", "GUIDANCE_PROVIDED"]

        # 2. Staff acknowledges the encounter with custom note
        staff_note = "Please proceed to OPD Room 4 for vitals examination."
        ack_res = await client.post(f"/api/v1/encounters/{encounter_id}/acknowledge", json={
            "staff_id": "NURSE-MEERA",
            "notes": staff_note
        })
        assert ack_res.status_code == 200
        ack_data = ack_res.json()
        assert ack_data["status"] == "ACKNOWLEDGED_BY_STAFF"
        assert ack_data["acknowledged_by"] == "NURSE-MEERA"

        # 3. Staff sends direct clinical treatment guidance
        guidance_text = "Take 1 tablet of Paracetamol 500mg after meals if temperature > 100°F. Attending doctor will see you in 10 minutes."
        guidance_res = await client.post(f"/api/v1/encounters/{encounter_id}/staff-guidance", json={
            "staff_id": "DR-SHARMA",
            "guidance": guidance_text
        })
        assert guidance_res.status_code == 200
        guidance_data = guidance_res.json()
        assert guidance_data["status"] == "sent"
        assert guidance_data["sender"] == "CLINICAL_STAFF"

        # 4. Check conversation history visible to patient
        conv_res = await client.get(f"/api/v1/encounters/{encounter_id}/conversation")
        assert conv_res.status_code == 200
        messages = conv_res.json()["messages"]

        # Verify that CLINICAL_STAFF messages exist in the conversation
        staff_messages = [m for m in messages if m["sender"] == "CLINICAL_STAFF"]
        assert len(staff_messages) >= 2, f"Expected at least 2 staff messages, got {len(staff_messages)}"

        # Verify acknowledgement message content
        assert any(staff_note in m["content"] for m in staff_messages)
        # Verify treatment guidance content
        assert any(guidance_text in m["content"] for m in staff_messages)
