from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PatientBase(BaseModel):
    patient_id: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

class EncounterCreate(BaseModel):
    patient_id: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    language: str = "en"
    initial_complaint: Optional[str] = None

class AcknowledgeRequest(BaseModel):
    staff_id: str = "STAFF-ON-DUTY"
    notes: Optional[str] = None

class ManualEscalateRequest(BaseModel):
    staff_id: str = "STAFF-ON-DUTY"
    reason: str
    priority: str = "IMMEDIATE_ESCALATION"

class EncounterSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    encounter_id: str
    patient_id: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    language: str
    chief_complaint: Optional[str] = None
    priority: str
    protocol_id: Optional[str] = None
    protocol_version: Optional[str] = None
    escalation_required: bool
    status: str
    created_at: datetime
    updated_at: datetime

class EncounterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    encounter_id: str
    patient: PatientBase
    language: str
    chief_complaint: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    duration: Optional[str] = None
    severity: Optional[str] = None
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    medical_history: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    vitals: Dict[str, Any] = Field(default_factory=dict)
    red_flags: List[Dict[str, Any]] = Field(default_factory=list)
    protocol_id: Optional[str] = None
    protocol_version: Optional[str] = None
    protocol_name: Optional[str] = None
    priority: str = "NORMAL"
    escalation_required: bool = False
    escalation_reason: Optional[Dict[str, Any]] = None
    status: str = "COLLECTING_INFORMATION"
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
