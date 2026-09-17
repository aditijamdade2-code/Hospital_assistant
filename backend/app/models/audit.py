import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    encounter_id = Column(String(64), ForeignKey("encounters.encounter_id"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)  # ENCOUNTER_CREATED, MESSAGE_RECEIVED, RED_FLAG_TRIGGERED, etc.
    details = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    encounter = relationship("Encounter", back_populates="audit_logs")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    encounter_id = Column(String(64), nullable=False, index=True)
    priority = Column(String(32), nullable=False)
    triggered_rule = Column(String(64), nullable=False)
    action = Column(String(128), nullable=False)
    details = Column(JSON, default=dict, nullable=False)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(String(128), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
