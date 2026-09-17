from typing import Optional, List, Dict, Any, Tuple
import logging
from backend.app.schemas.protocol import ProtocolSchema, QuestionSchema, GuidanceStepSchema
from backend.app.protocols.loader import ProtocolLoader, protocol_loader

logger = logging.getLogger(__name__)

class ProtocolEngine:
    def __init__(self, loader: Optional[ProtocolLoader] = None):
        self.loader = loader or protocol_loader

    def select_protocol(
        self,
        chief_complaint: Optional[str] = None,
        symptoms: Optional[List[str]] = None,
        raw_text: Optional[str] = None
    ) -> Optional[ProtocolSchema]:
        """
        Deterministically selects the most applicable clinical protocol based on keywords.
        Clinical decisions must come from deterministic logic, not LLM invention.
        """
        all_protocols = self.loader.list_all()
        if not all_protocols:
            return None

        tokens = set()
        if chief_complaint:
            tokens.update([w.lower().strip() for w in chief_complaint.split()])
        if symptoms:
            for s in symptoms:
                tokens.update([w.lower().strip() for w in s.split()])
        if raw_text:
            tokens.update([w.lower().strip() for w in raw_text.split()])

        best_protocol: Optional[ProtocolSchema] = None
        best_score = 0

        full_text_combined = f"{chief_complaint or ''} {' '.join(symptoms or [])} {raw_text or ''}".lower()
        cc_lower = (chief_complaint or "").lower().strip()

        for proto in all_protocols:
            score = 0
            for kw in proto.keywords:
                kw_lower = kw.lower().strip()
                # 1. Direct match with chief complaint
                if cc_lower and (kw_lower == cc_lower or kw_lower in cc_lower):
                    score += 15
                # 2. Multi-word or exact phrase match in text
                elif " " in kw_lower and kw_lower in full_text_combined:
                    score += 8
                # 3. Individual token match
                elif kw_lower in tokens:
                    score += 4
                elif any(kw_lower in t for t in tokens if len(kw_lower) > 3):
                    score += 2

            # Give specific protocols slight preference over generic P009/P010 if they match
            if proto.protocol_id not in ["P009", "P010"] and score > 0:
                score += 1

            if score > best_score:
                best_score = score
                best_protocol = proto

        if best_score > 0 and best_protocol:
            return best_protocol

        # Fallback to P009 (Pain) if pain or body part is involved
        if any("pain" in t or "dard" in t or "ache" in t or "dukh" in t for t in tokens):
            return self.loader.get("P009") or self.loader.get("P010")

        # General OPD Clinical Triage fallback (P010)
        return self.loader.get("P010") or self.loader.get("P001")

    def get_missing_fields(
        self,
        protocol: ProtocolSchema,
        extracted_fields: Dict[str, Any]
    ) -> List[str]:
        """Returns list of required fields that are not yet known or null."""
        missing = []
        for req in protocol.required_fields:
            val = extracted_fields.get(req)
            if val is None or val == "" or str(val).lower() in ["unknown", "null", "none"]:
                missing.append(req)
        return missing

    def get_next_question(
        self,
        protocol: ProtocolSchema,
        missing_fields: List[str],
        language: str = "en"
    ) -> Optional[QuestionSchema]:
        """Finds the question corresponding to the first missing field."""
        if not missing_fields:
            return None

        target_field = missing_fields[0]
        for q in protocol.questions:
            if q.field == target_field:
                return q
        return None

    def get_guidance(
        self,
        protocol: ProtocolSchema,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Returns the approved first aid guidance steps in the requested language."""
        result = []
        for step in protocol.guidance:
            text = step.instruction
            if language == "hi" and step.instruction_hi:
                text = step.instruction_hi
            elif language == "mr" and step.instruction_mr:
                text = step.instruction_mr
            result.append({
                "step": step.step,
                "instruction": text
            })
        return result

protocol_engine = ProtocolEngine()
