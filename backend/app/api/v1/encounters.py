from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.database.session import get_db
from backend.app.models.encounter import Encounter, Message
from backend.app.models.audit import AuditLog
from backend.app.schemas.encounter import (
    EncounterCreate, EncounterResponse, EncounterSummary,
    AcknowledgeRequest, ManualEscalateRequest
)
from backend.app.schemas.message import (
    PatientMessageInput, MessageResponse, ConversationHistoryResponse
)
from backend.app.services.encounter_service import EncounterService

router = APIRouter(prefix="/encounters", tags=["Encounters"])

def _to_encounter_response(encounter: Encounter) -> EncounterResponse:
    return EncounterResponse(
        encounter_id=encounter.encounter_id,
        patient={
            "patient_id": encounter.patient.patient_id,
            "age": encounter.patient.age,
            "gender": encounter.patient.gender
        },
        language=encounter.language,
        chief_complaint=encounter.chief_complaint,
        symptoms=encounter.symptoms or [],
        duration=encounter.duration,
        severity=encounter.severity,
        extracted_fields=encounter.extracted_fields or {},
        medical_history=encounter.medical_history or [],
        allergies=encounter.allergies or [],
        medications=encounter.medications or [],
        vitals=encounter.vitals or {},
        red_flags=encounter.red_flags or [],
        protocol_id=encounter.protocol_id,
        protocol_version=encounter.protocol_version,
        protocol_name=encounter.protocol_name,
        priority=encounter.priority,
        escalation_required=encounter.escalation_required,
        escalation_reason=encounter.escalation_reason,
        status=encounter.status,
        acknowledged_by=encounter.acknowledged_by,
        acknowledged_at=encounter.acknowledged_at,
        created_at=encounter.created_at,
        updated_at=encounter.updated_at
    )

@router.post("", response_model=EncounterResponse, status_code=201)
async def create_encounter(
    data: EncounterCreate,
    db: AsyncSession = Depends(get_db)
):
    """Creates a new patient encounter."""
    encounter = await EncounterService.create_encounter(db, data)
    return _to_encounter_response(encounter)

@router.get("", response_model=List[EncounterSummary])
async def list_encounters(
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Lists encounters with optional filters for staff dashboard."""
    query = select(Encounter).options(selectinload(Encounter.patient)).order_by(Encounter.updated_at.desc())
    if priority:
        query = query.where(Encounter.priority == priority)
    if status:
        query = query.where(Encounter.status == status)
    query = query.limit(limit)

    result = await db.execute(query)
    encounters = result.scalars().all()

    return [
        EncounterSummary(
            encounter_id=e.encounter_id,
            patient_id=e.patient.patient_id,
            age=e.patient.age,
            gender=e.patient.gender,
            language=e.language,
            chief_complaint=e.chief_complaint,
            priority=e.priority,
            protocol_id=e.protocol_id,
            protocol_version=e.protocol_version,
            escalation_required=e.escalation_required,
            status=e.status,
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in encounters
    ]

@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(
    encounter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves detailed encounter information."""
    stmt = select(Encounter).options(
        selectinload(Encounter.patient),
        selectinload(Encounter.messages)
    ).where(Encounter.encounter_id == encounter_id)
    result = await db.execute(stmt)
    encounter = result.scalar_one_or_none()

    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    return _to_encounter_response(encounter)

@router.post("/{encounter_id}/message")
async def post_message(
    encounter_id: str,
    msg_input: PatientMessageInput,
    db: AsyncSession = Depends(get_db)
):
    """Processes a patient message: extraction, safety, protocol, and guidance."""
    try:
        res = await EncounterService.process_patient_message(db, encounter_id, msg_input)
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal processing error: {e}")

@router.get("/{encounter_id}/conversation", response_model=ConversationHistoryResponse)
async def get_conversation(
    encounter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Returns the full chronological conversation history for an encounter."""
    stmt = select(Message).where(Message.encounter_id == encounter_id).order_by(Message.created_at.asc())
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return ConversationHistoryResponse(
        encounter_id=encounter_id,
        messages=[MessageResponse.model_validate(m) for m in messages],
        total=len(messages)
    )

@router.post("/{encounter_id}/acknowledge", response_model=EncounterResponse)
async def acknowledge_encounter(
    encounter_id: str,
    req: AcknowledgeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Staff acknowledges an encounter and sends an acknowledgment message to patient chat."""
    try:
        encounter = await EncounterService.acknowledge_encounter(db, encounter_id, req.staff_id, req.notes)
        return _to_encounter_response(encounter)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

class StaffGuidanceRequest(BaseModel):
    staff_id: str = "DOCTOR-ON-DUTY"
    guidance: str

@router.post("/{encounter_id}/staff-guidance")
async def send_staff_guidance(
    encounter_id: str,
    req: StaffGuidanceRequest,
    db: AsyncSession = Depends(get_db)
):
    """Staff sends direct clinical guidance or treatment notes to the patient's chat."""
    try:
        msg = await EncounterService.send_staff_guidance(db, encounter_id, req.staff_id, req.guidance)
        return {
            "status": "sent",
            "message_id": msg.id,
            "content": msg.content,
            "sender": msg.sender
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{encounter_id}/escalate", response_model=EncounterResponse)
async def manual_escalate(
    encounter_id: str,
    req: ManualEscalateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Staff manually escalates an encounter."""
    try:
        encounter = await EncounterService.manual_escalate(db, encounter_id, req.staff_id, req.reason, req.priority)
        return _to_encounter_response(encounter)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{encounter_id}/audit")
async def get_audit_logs(
    encounter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the full audit log history for an encounter."""
    stmt = select(AuditLog).where(AuditLog.encounter_id == encounter_id).order_by(AuditLog.created_at.asc())
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "event_type": log.event_type,
            "details": log.details,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]
