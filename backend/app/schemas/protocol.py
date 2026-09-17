from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class QuestionSchema(BaseModel):
    field: str
    text: str
    text_hi: Optional[str] = None
    text_mr: Optional[str] = None

class GuidanceStepSchema(BaseModel):
    step: int
    instruction: str
    instruction_hi: Optional[str] = None
    instruction_mr: Optional[str] = None

class ProtocolEscalationSchema(BaseModel):
    default_priority: str = "NORMAL"
    trigger_conditions: List[str] = Field(default_factory=list)

class ProtocolSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    protocol_id: str
    name: str
    version: str
    category: str
    clinical_validation_status: str
    keywords: List[str] = Field(default_factory=list)
    required_fields: List[str] = Field(default_factory=list)
    questions: List[QuestionSchema] = Field(default_factory=list)
    guidance: List[GuidanceStepSchema] = Field(default_factory=list)
    escalation: ProtocolEscalationSchema
