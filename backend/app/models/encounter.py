import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(String(64), unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    encounters = relationship("Encounter", back_populates="patient", cascade="all, delete-orphan")


class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    encounter_id = Column(String(64), unique=True, index=True, nullable=False)
    patient_db_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    language = Column(String(16), default="en", nullable=False)
    chief_complaint = Column(String(255), nullable=True)
    symptoms = Column(JSON, default=list, nullable=False)
    duration = Column(String(64), nullable=True)
    severity = Column(String(64), nullable=True)
    extracted_fields = Column(JSON, default=dict, nullable=False)
    
    medical_history = Column(JSON, default=list, nullable=False)
    allergies = Column(JSON, default=list, nullable=False)
    medications = Column(JSON, default=list, nullable=False)
    vitals = Column(JSON, default=dict, nullable=False)
    red_flags = Column(JSON, default=list, nullable=False)
    
    protocol_id = Column(String(64), nullable=True)
    protocol_version = Column(String(32), nullable=True)
    protocol_name = Column(String(255), nullable=True)
    
    # Priority: NORMAL, NEEDS_REVIEW, PRIORITY, IMMEDIATE_ESCALATION
    priority = Column(String(32), default="NORMAL", nullable=False)
    escalation_required = Column(Boolean, default=False, nullable=False)
    escalation_reason = Column(JSON, nullable=True)
    
    # Status: COLLECTING_INFORMATION, GUIDANCE_PROVIDED, ESCALATED, ACKNOWLEDGED_BY_STAFF, CLOSED
    status = Column(String(64), default="COLLECTING_INFORMATION", nullable=False)
    
    acknowledged_by = Column(String(128), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    patient = relationship("Patient", back_populates="encounters")
    messages = relationship("Message", back_populates="encounter", cascade="all, delete-orphan", order_by="Message.created_at")
    audit_logs = relationship("AuditLog", back_populates="encounter", cascade="all, delete-orphan", order_by="AuditLog.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    encounter_id = Column(String(64), ForeignKey("encounters.encounter_id"), nullable=False, index=True)
    sender = Column(String(32), nullable=False)  # PATIENT, ASSISTANT, CLINICAL_STAFF, SYSTEM
    content = Column(Text, nullable=False)
    language = Column(String(16), default="en", nullable=False)
    extracted_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    encounter = relationship("Encounter", back_populates="messages")
