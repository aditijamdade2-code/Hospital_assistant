import re
import uuid
import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.models.encounter import Patient, Encounter, Message
from backend.app.models.audit import AuditLog, Alert
from backend.app.schemas.encounter import EncounterCreate, EncounterResponse
from backend.app.schemas.message import PatientMessageInput
from backend.app.services.llm.factory import get_llm_provider
from backend.app.protocols.engine import protocol_engine
from backend.app.safety.engine import safety_engine
from backend.app.services.websocket_manager import ws_manager

ACK_TERMS = {
    # English
    "ok", "okay", "alright", "sure", "got it", "thank you", "thanks", "fine", "understood", "yes", "k", "okk",
    # Hindi (Latin & Devanagari)
    "theek hai", "theek", "thik hai", "thik", "accha", "achha", "dhanyawad", "shukriya", "dhanyavaad", "sahi hai",
    "theek h", "thik h", "theek he", "thik he", "thek hai", "thek",
    "ठीक है", "ठीक", "अच्छा", "धन्यवाद", "शुक्रिया", "सही है",
    # Marathi (Latin & Devanagari) — "हो" / "ho" only matched as standalone Marathi YES
    "thik ahe", "thik aahe", "theek ahe", "theek aahe", "thik ahay", "bar ahe", "bara ahe",
    "hoy", "bar", "bara", "samajle", "samajla",
    "ठीक आहे", "ठीक", "होय", "बरं आहे", "बरं", "बरे आहे", "धन्यवाद", "समजले", "कळले"
}

def is_acknowledgment_message(text: str) -> bool:
    if not text:
        return False
    cleaned = re.sub(r'[^\w\s\u0900-\u097F]', ' ', text).strip().lower()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    if not cleaned:
        return False
    # A message with more than 4 words is never a simple acknowledgment;
    # it is describing symptoms or asking a question — never treat as ack.
    words = cleaned.split()
    if len(words) > 4:
        return False
    for term in ACK_TERMS:
        if cleaned == term:
            return True
        # Only match multi-word ACK terms (e.g. "theek hai") as sub-phrases
        if " " in term and (cleaned.startswith(term) or cleaned.endswith(term) or f" {term} " in cleaned):
            return True
        # Single-word terms: match only as whole words, not substrings
        if " " not in term and re.search(rf'(?<![\w\u0900-\u097F]){re.escape(term)}(?![\w\u0900-\u097F])', cleaned):
            return True
    return False

class EncounterService:
    @staticmethod
    async def create_encounter(session: AsyncSession, data: EncounterCreate) -> Encounter:
        # 1. Create or link Patient
        patient_id = data.patient_id or f"OPD-{uuid.uuid4().hex[:6].upper()}"
        result = await session.execute(select(Patient).where(Patient.patient_id == patient_id))
        patient = result.scalar_one_or_none()

        if not patient:
            patient = Patient(
                patient_id=patient_id,
                age=data.age,
                gender=data.gender
            )
            session.add(patient)
            await session.flush()
        else:
            if data.age is not None:
                patient.age = data.age
            if data.gender is not None:
                patient.gender = data.gender

        # 2. Create Encounter
        encounter_id = f"ENC-{uuid.uuid4().hex[:6].upper()}"
        encounter = Encounter(
            encounter_id=encounter_id,
            patient_db_id=patient.id,
            language=data.language or "en",
            priority="NORMAL",
            status="COLLECTING_INFORMATION",
            extracted_fields={},
            symptoms=[],
            medical_history=[],
            allergies=[],
            medications=[],
            vitals={},
            red_flags=[]
        )
        session.add(encounter)
        await session.flush()

        # 3. Create Audit Log
        audit = AuditLog(
            encounter_id=encounter_id,
            event_type="ENCOUNTER_CREATED",
            details={
                "patient_id": patient_id,
                "language": encounter.language,
                "created_at": encounter.created_at.isoformat()
            }
        )
        session.add(audit)
        await session.commit()
        await session.refresh(encounter, ["patient", "messages"])

        # Broadcast WebSocket event
        await ws_manager.broadcast("NEW_ENCOUNTER", {
            "encounter_id": encounter.encounter_id,
            "patient_id": patient.patient_id,
            "priority": encounter.priority,
            "status": encounter.status,
            "language": encounter.language,
            "created_at": encounter.created_at.isoformat()
        })

        # Process initial complaint if provided
        if data.initial_complaint:
            await EncounterService.process_patient_message(
                session=session,
                encounter_id=encounter.encounter_id,
                msg_input=PatientMessageInput(message=data.initial_complaint, language=data.language)
            )
            await session.refresh(encounter, ["patient", "messages"])

        return encounter

    @staticmethod
    async def process_patient_message(
        session: AsyncSession,
        encounter_id: str,
        msg_input: PatientMessageInput
    ) -> Dict[str, Any]:
        # Fetch encounter with relations
        stmt = select(Encounter).options(
            selectinload(Encounter.patient),
            selectinload(Encounter.messages)
        ).where(Encounter.encounter_id == encounter_id)
        result = await session.execute(stmt)
        encounter = result.scalar_one_or_none()

        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")

        current_lang = msg_input.language or encounter.language

        # 1. Save Patient Message
        patient_msg = Message(
            encounter_id=encounter_id,
            sender="PATIENT",
            content=msg_input.message,
            language=current_lang
        )
        session.add(patient_msg)
        await session.flush()

        # Build conversation history for LLM
        history = [
            {"sender": m.sender, "content": m.content}
            for m in encounter.messages
        ]

        # 2. Extract Structured Information via Provider
        llm = get_llm_provider()
        extraction = await llm.extract_information(
            text=msg_input.message,
            conversation_history=history,
            current_language=current_lang
        )
        patient_msg.extracted_info = extraction.model_dump()

        # 3. Update Encounter structured state
        fields: Dict[str, Any] = dict(encounter.extracted_fields or {})
        pending_field = fields.get("_pending_question_field")

        # If there was a pending question, resolve it using patient's answer
        if pending_field:
            p_text = msg_input.message.strip().lower()
            if any(w in p_text for w in ["no", "nope", "not yet", "haven't", "dont know", "nahi", "nahin", "nahi pata", "naahi", "nako"]):
                fields[pending_field] = "not checked"
            elif any(w in p_text for w in ["yes", "haan", "ha", "ho", "ahe"]):
                fields[pending_field] = "yes"
            else:
                fields[pending_field] = msg_input.message.strip()

        if extraction.chief_complaint and not encounter.chief_complaint:
            encounter.chief_complaint = extraction.chief_complaint
        if extraction.duration:
            encounter.duration = extraction.duration
            fields["duration"] = extraction.duration
        if extraction.severity:
            encounter.severity = extraction.severity
            fields["severity"] = extraction.severity
        if extraction.body_part:
            fields["body_part"] = extraction.body_part

        for k, v in extraction.additional_fields.items():
            if v is not None:
                fields[k] = v

        current_symptoms = list(encounter.symptoms or [])
        for s in extraction.symptoms:
            if s not in current_symptoms:
                current_symptoms.append(s)
        encounter.symptoms = current_symptoms
        fields["symptoms"] = current_symptoms
        encounter.extracted_fields = fields

        # 4. Protocol Selection / Reassessment
        new_proto = protocol_engine.select_protocol(
            chief_complaint=encounter.chief_complaint,
            symptoms=encounter.symptoms,
            raw_text=msg_input.message
        )

        selected_protocol = None
        if new_proto:
            if not encounter.protocol_id or (encounter.protocol_id in ["P009", "P010"] and new_proto.protocol_id not in ["P009", "P010"]):
                encounter.protocol_id = new_proto.protocol_id
                encounter.protocol_version = new_proto.version
                encounter.protocol_name = new_proto.name
                selected_protocol = new_proto
            else:
                selected_protocol = protocol_engine.loader.get(encounter.protocol_id) or new_proto
        elif encounter.protocol_id:
            selected_protocol = protocol_engine.loader.get(encounter.protocol_id)

        # 5. Deterministic Safety & Red-Flag Evaluation
        safety_result = safety_engine.evaluate(
            extracted_fields=encounter.extracted_fields,
            raw_text=msg_input.message,
            protocol_id=encounter.protocol_id,
            protocol_version=encounter.protocol_version,
            language=current_lang
        )

        previous_priority = encounter.priority
        if safety_result.triggered:
            encounter.priority = safety_result.highest_priority
            encounter.escalation_required = safety_result.escalation_required
            
            # Record red flags
            existing_flags = list(encounter.red_flags or [])
            for esc in safety_result.escalations:
                esc_dict = esc.model_dump()
                if not any(f.get("triggered_rule") == esc.triggered_rule for f in existing_flags):
                    existing_flags.append(esc_dict)
                    encounter.escalation_reason = esc_dict
                    
                    # Create Alert entity
                    alert = Alert(
                        encounter_id=encounter_id,
                        priority=esc.priority,
                        triggered_rule=esc.triggered_rule,
                        action=esc.action,
                        details=esc_dict
                    )
                    session.add(alert)

            encounter.red_flags = existing_flags

            if safety_result.stop_questioning:
                encounter.status = "ESCALATED"

            # Broadcast real-time safety alert
            await ws_manager.broadcast("RED_FLAG_DETECTED", {
                "encounter_id": encounter_id,
                "priority": encounter.priority,
                "escalations": [e.model_dump() for e in safety_result.escalations]
            })

            if previous_priority != encounter.priority:
                await ws_manager.broadcast("PRIORITY_CHANGED", {
                    "encounter_id": encounter_id,
                    "previous_priority": previous_priority,
                    "new_priority": encounter.priority
                })

        # 6. Determine Next Question or Guidance
        next_question_text = None
        guidance_steps = None

        is_ack = is_acknowledgment_message(msg_input.message)

        if is_ack:
            # Patient acknowledged previous instruction; do not repeat questions or guidance
            next_question_text = None
            guidance_steps = None
            if "_pending_question_field" in encounter.extracted_fields:
                del encounter.extracted_fields["_pending_question_field"]
        elif not safety_result.stop_questioning and selected_protocol:
            missing_fields = protocol_engine.get_missing_fields(
                selected_protocol,
                encounter.extracted_fields
            )
            if missing_fields:
                q_obj = protocol_engine.get_next_question(
                    selected_protocol,
                    missing_fields,
                    language=current_lang
                )
                if q_obj:
                    if current_lang == "hi" and q_obj.text_hi:
                        next_question_text = q_obj.text_hi
                    elif current_lang == "mr" and q_obj.text_mr:
                        next_question_text = q_obj.text_mr
                    else:
                        next_question_text = q_obj.text
                    encounter.status = "COLLECTING_INFORMATION"
                    encounter.extracted_fields["_pending_question_field"] = q_obj.field
            else:
                # All required information gathered!
                # Only provide protocol guidance if not already provided in previous turns
                if encounter.status in ["GUIDANCE_PROVIDED", "ACKNOWLEDGED_BY_STAFF"]:
                    guidance_steps = None
                else:
                    guidance_steps = protocol_engine.get_guidance(selected_protocol, language=current_lang)
                    if encounter.status != "ESCALATED":
                        encounter.status = "GUIDANCE_PROVIDED"
                if "_pending_question_field" in encounter.extracted_fields:
                    del encounter.extracted_fields["_pending_question_field"]

        # 7. Generate Assistant Message via LLM
        assistant_content = await llm.generate_response(
            patient_message=msg_input.message,
            conversation_history=history,
            next_question=next_question_text,
            guidance_steps=guidance_steps,
            alert_instruction=safety_result.immediate_instruction,
            language=current_lang
        )

        assistant_msg = Message(
            encounter_id=encounter_id,
            sender="ASSISTANT",
            content=assistant_content,
            language=current_lang
        )
        session.add(assistant_msg)

        # 8. Record Audit Log
        audit = AuditLog(
            encounter_id=encounter_id,
            event_type="MESSAGE_PROCESSED",
            details={
                "extracted_fields": encounter.extracted_fields,
                "protocol_id": encounter.protocol_id,
                "priority": encounter.priority,
                "status": encounter.status,
                "safety_triggered": safety_result.triggered
            }
        )
        session.add(audit)
        await session.commit()

        # Broadcast update to staff dashboard
        await ws_manager.broadcast("ENCOUNTER_UPDATED", {
            "encounter_id": encounter.encounter_id,
            "patient_id": encounter.patient.patient_id,
            "chief_complaint": encounter.chief_complaint,
            "priority": encounter.priority,
            "status": encounter.status,
            "escalation_required": encounter.escalation_required,
            "updated_at": encounter.updated_at.isoformat()
        })

        return {
            "assistant_response": assistant_content,
            "encounter_status": encounter.status,
            "priority": encounter.priority,
            "escalation_required": encounter.escalation_required,
            "extracted_fields": encounter.extracted_fields
        }

    @staticmethod
    async def acknowledge_encounter(
        session: AsyncSession,
        encounter_id: str,
        staff_id: str,
        notes: Optional[str] = None
    ) -> Encounter:
        stmt = select(Encounter).options(
            selectinload(Encounter.patient)
        ).where(Encounter.encounter_id == encounter_id)
        result = await session.execute(stmt)
        encounter = result.scalar_one_or_none()

        if not encounter:
            raise ValueError("Encounter not found")

        encounter.acknowledged_by = staff_id
        encounter.acknowledged_at = datetime.datetime.utcnow()
        if encounter.status in ["COLLECTING_INFORMATION", "ESCALATED", "GUIDANCE_PROVIDED"]:
            encounter.status = "ACKNOWLEDGED_BY_STAFF"

        # Add message into the patient's conversation so it is visible in their chat
        if encounter.language == "hi":
            msg_content = f"🏥 अस्पताल कर्मचारी सूचना ({staff_id}):\nआपकी केस फ़ाइल की समीक्षा कर ली गई है और इसे स्वीकार कर लिया गया है।"
            if notes:
                msg_content += f"\n\nकर्मचारी निर्देश: {notes}"
            msg_content += "\nकृपया आराम से बैठें। स्वास्थ्य कर्मी जल्द ही आपको व्यक्तिगत जांच के लिए बुलाएंगे।"
        elif encounter.language == "mr":
            msg_content = f"🏥 रुग्णालय कर्मचारी नोंद ({staff_id}):\nआपल्या केस फाईलचे पुनरावलोकन करून ती स्वीकारण्यात आली आहे."
            if notes:
                msg_content += f"\n\nकर्मचारी सूचना: {notes}"
            msg_content += "\nकृपया विश्रांती घ्या. आरोग्य कर्मचारी लवकरच आपल्याला तपासणीसाठी बोलावतील."
        else:
            msg_content = f"🏥 Clinical Staff Acknowledgment ({staff_id}):\nYour case file has been reviewed and acknowledged by the on-duty healthcare team."
            if notes:
                msg_content += f"\n\nStaff Instructions / Guidance: {notes}"
            msg_content += "\nPlease remain seated. Healthcare staff will call you for clinical examination shortly."

        staff_msg = Message(
            encounter_id=encounter_id,
            sender="CLINICAL_STAFF",
            content=msg_content,
            language=encounter.language
        )
        session.add(staff_msg)

        # Record audit
        audit = AuditLog(
            encounter_id=encounter_id,
            event_type="STAFF_ACKNOWLEDGED",
            details={"staff_id": staff_id, "notes": notes}
        )
        session.add(audit)
        await session.commit()

        await ws_manager.broadcast("STAFF_ACKNOWLEDGED", {
            "encounter_id": encounter.encounter_id,
            "staff_id": staff_id,
            "status": encounter.status,
            "notes": notes,
            "message": msg_content
        })

        return encounter

    @staticmethod
    async def send_staff_guidance(
        session: AsyncSession,
        encounter_id: str,
        staff_id: str,
        guidance: str
    ) -> Message:
        stmt = select(Encounter).where(Encounter.encounter_id == encounter_id)
        result = await session.execute(stmt)
        encounter = result.scalar_one_or_none()

        if not encounter:
            raise ValueError("Encounter not found")

        formatted_content = f"👨‍⚕️ Clinical Staff Guidance ({staff_id}):\n{guidance.strip()}"
        staff_msg = Message(
            encounter_id=encounter_id,
            sender="CLINICAL_STAFF",
            content=formatted_content,
            language=encounter.language
        )
        session.add(staff_msg)

        audit = AuditLog(
            encounter_id=encounter_id,
            event_type="STAFF_GUIDANCE_SENT",
            details={"staff_id": staff_id, "guidance": guidance}
        )
        session.add(audit)
        await session.commit()
        await session.refresh(staff_msg)

        await ws_manager.broadcast("STAFF_GUIDANCE", {
            "encounter_id": encounter_id,
            "staff_id": staff_id,
            "content": formatted_content
        })

        return staff_msg

    @staticmethod
    async def manual_escalate(
        session: AsyncSession,
        encounter_id: str,
        staff_id: str,
        reason: str,
        priority: str = "IMMEDIATE_ESCALATION"
    ) -> Encounter:
        stmt = select(Encounter).options(
            selectinload(Encounter.patient)
        ).where(Encounter.encounter_id == encounter_id)
        result = await session.execute(stmt)
        encounter = result.scalar_one_or_none()

        if not encounter:
            raise ValueError("Encounter not found")

        encounter.priority = priority
        encounter.escalation_required = True
        encounter.status = "ESCALATED"
        encounter.escalation_reason = {
            "triggered_rule": "MANUAL_STAFF_ESCALATION",
            "rule_description": f"Manually escalated by {staff_id}: {reason}",
            "priority": priority,
            "action": "Immediate clinical review",
            "detected_information": {"reason": reason, "staff_id": staff_id}
        }

        audit = AuditLog(
            encounter_id=encounter_id,
            event_type="MANUAL_ESCALATION",
            details={"staff_id": staff_id, "reason": reason, "priority": priority}
        )
        session.add(audit)
        await session.commit()

        await ws_manager.broadcast("ESCALATION_TRIGGERED", {
            "encounter_id": encounter.encounter_id,
            "staff_id": staff_id,
            "priority": priority,
            "reason": reason
        })

        return encounter
