from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PatientMessageInput(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    language: Optional[str] = None

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    encounter_id: str
    sender: str
    content: str
    language: str
    extracted_info: Optional[Dict[str, Any]] = None
    created_at: datetime

class ConversationHistoryResponse(BaseModel):
    encounter_id: str
    messages: List[MessageResponse]
    total: int
