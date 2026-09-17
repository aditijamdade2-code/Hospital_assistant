from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RedFlagRule(BaseModel):
    rule_id: str
    condition: str
    priority: str  # IMMEDIATE_ESCALATION, PRIORITY, NEEDS_REVIEW
    action: str
    description: str
    applicable_protocols: List[str] = Field(default_factory=lambda: ["*"])

class EscalationDetail(BaseModel):
    priority: str
    triggered_rule: str
    rule_description: str
    detected_information: Dict[str, Any]
    protocol_id: Optional[str] = None
    protocol_version: Optional[str] = None
    action: str
    clinical_instruction: Optional[str] = None
    timestamp: Optional[str] = None

class SafetyEvaluationResult(BaseModel):
    triggered: bool
    highest_priority: str = "NORMAL"
    escalation_required: bool = False
    escalations: List[EscalationDetail] = Field(default_factory=list)
    immediate_instruction: Optional[str] = None
    stop_questioning: bool = False
