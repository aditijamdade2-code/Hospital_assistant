from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class StructuredExtraction(BaseModel):
    chief_complaint: Optional[str] = None
    body_part: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    duration: Optional[str] = None
    severity: Optional[str] = None
    additional_fields: Dict[str, Any] = Field(default_factory=dict)
    detected_language: str = "en"

    @field_validator("body_part", "chief_complaint", "duration", "severity", mode="before")
    @classmethod
    def coerce_to_string(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return ", ".join(str(item) for item in v) if v else None
        return str(v)

class LLMProvider(ABC):
    @abstractmethod
    async def extract_information(
        self,
        text: str,
        conversation_history: List[Dict[str, str]],
        current_language: str = "en"
    ) -> StructuredExtraction:
        """
        Understands patient natural language and extracts structured fields without hallucination.
        Unknown values must remain null/empty.
        """
        pass

    @abstractmethod
    async def generate_response(
        self,
        patient_message: str,
        conversation_history: List[Dict[str, str]],
        next_question: Optional[str],
        guidance_steps: Optional[List[Dict[str, Any]]],
        alert_instruction: Optional[str],
        language: str = "en"
    ) -> str:
        """
        Generates natural-language response based strictly on instructions from protocol/safety engine.
        Does NOT independently prescribe or diagnose.
        """
        pass
