import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database.session import init_db

@pytest.mark.asyncio
async def test_marathi_acknowledgment_no_repeat():
    """Verify that saying 'ok' or in Marathi 'ठीक आहे.' / 'thik ahe' does not repeat the previous guidance/question."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Create encounter in Marathi
        res = await client.post("/api/v1/encounters", json={
            "age": 23,
            "gender": "female",
            "language": "mr",
            "initial_complaint": "ताप सर्दी खोकला आहे."
        })
        assert res.status_code == 201
        enc_id = res.json()["encounter_id"]

        # 2. Answer temperature question
        res1 = await client.post(f"/api/v1/encounters/{enc_id}/message", json={
            "message": "नाही मोजला.",
            "language": "mr"
        })
        assert res1.status_code == 200

        # 3. Answer duration question
        res2 = await client.post(f"/api/v1/encounters/{enc_id}/message", json={
            "message": "दोन दिवसांपासून.",
            "language": "mr"
        })
        assert res2.status_code == 200

        # 4. Answer associated symptoms question -> guidance provided
        res3 = await client.post(f"/api/v1/encounters/{enc_id}/message", json={
            "message": "थंडी वाजत आहे.",
            "language": "mr"
        })
        assert res3.status_code == 200
        guidance_reply = res3.json()["assistant_response"]
        assert "प्रथमोपचार" in guidance_reply

        # 5. Patient says "ठीक आहे." (with punctuation / Devanagari)
        res4 = await client.post(f"/api/v1/encounters/{enc_id}/message", json={
            "message": "ठीक आहे.",
            "language": "mr"
        })
        assert res4.status_code == 200
        ack_reply1 = res4.json()["assistant_response"]

        # MUST NOT repeat the full first-aid guidance
        assert "प्रथमोपचार" not in ack_reply1
        # Must give natural closing (new ack says 'ठीक आहे. माहिती...' or 'डॉक्टर')
        assert "ठीक आहे" in ack_reply1 or "डॉक्टर" in ack_reply1 or "माहिती" in ack_reply1

        # 6. Patient says "thik ahe" in Latin
        res5 = await client.post(f"/api/v1/encounters/{enc_id}/message", json={
            "message": "thik ahe",
            "language": "mr"
        })
        assert res5.status_code == 200
        ack_reply2 = res5.json()["assistant_response"]

        # MUST NOT repeat the first-aid guidance
        assert "प्रथमोपचार" not in ack_reply2
        assert "ठीक आहे" in ack_reply2 or "डॉक्टर" in ack_reply2 or "माहिती" in ack_reply2

        # 7. Patient says "ok"
        res6 = await client.post(f"/api/v1/encounters/{enc_id}/message", json={
            "message": "ok",
            "language": "mr"
        })
        assert res6.status_code == 200
        ack_reply3 = res6.json()["assistant_response"]
        assert "प्रथमोपचार" not in ack_reply3
