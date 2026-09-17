import datetime
from typing import Dict, Any, Optional
from backend.app.schemas.safety import EscalationDetail, RedFlagRule

class EscalationBuilder:
    @staticmethod
    def build_escalation(
        rule: RedFlagRule,
        detected_information: Dict[str, Any],
        protocol_id: Optional[str] = None,
        protocol_version: Optional[str] = None,
        clinical_instruction: Optional[str] = None
    ) -> EscalationDetail:
        """
        Builds a fully explainable escalation structure for clinical auditability.
        Section 11 requirement:
        Priority, Triggered Rule, Detected Information, Protocol, Protocol Version, Action.
        """
        return EscalationDetail(
            priority=rule.priority,
            triggered_rule=rule.rule_id,
            rule_description=rule.description,
            detected_information=detected_information,
            protocol_id=protocol_id,
            protocol_version=protocol_version or "1.0",
            action=rule.action,
            clinical_instruction=clinical_instruction or "Clinical staff review required immediately",
            timestamp=datetime.datetime.utcnow().isoformat()
        )
