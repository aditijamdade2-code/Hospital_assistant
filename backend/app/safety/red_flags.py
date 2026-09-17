from typing import List
from backend.app.schemas.safety import RedFlagRule

# Predefined deterministic red-flag rules
# Priority levels: IMMEDIATE_ESCALATION, PRIORITY, NEEDS_REVIEW, NORMAL
PREDEFINED_RED_FLAGS: List[RedFlagRule] = [
    RedFlagRule(
        rule_id="RF-001",
        condition="pulsating_or_arterial_spurting",
        priority="IMMEDIATE_ESCALATION",
        action="Immediate clinical staff triage and trauma team alert required",
        description="Pulsating or arterial spurting bleeding indicating major vascular compromise",
        applicable_protocols=["P001", "P002", "*"]
    ),
    RedFlagRule(
        rule_id="RF-002",
        condition="uncontrolled_bleeding_exceeding_10_min",
        priority="IMMEDIATE_ESCALATION",
        action="Immediate nursing pressure dressing and doctor assessment required",
        description="Bleeding not slowing or controlled after direct pressure for over 10 minutes",
        applicable_protocols=["P001", "P002", "P007", "*"]
    ),
    RedFlagRule(
        rule_id="RF-003",
        condition="anaphylaxis_airway_compromise",
        priority="IMMEDIATE_ESCALATION",
        action="Immediate resuscitation bay escalation; nurse emergency alert",
        description="Signs of airway involvement, wheezing, throat tightness, or lip/tongue swelling",
        applicable_protocols=["P008", "*"]
    ),
    RedFlagRule(
        rule_id="RF-004",
        condition="chest_pain_or_cardiovascular_symptoms",
        priority="IMMEDIATE_ESCALATION",
        action="Immediate ECG and doctor evaluation required",
        description="Dizziness or fainting associated with chest pain, pressure, or shortness of breath",
        applicable_protocols=["P006", "*"]
    ),
    RedFlagRule(
        rule_id="RF-005",
        condition="loss_of_consciousness_syncope",
        priority="PRIORITY",
        action="Clinical staff review and vitals check required",
        description="Patient experienced full loss of consciousness or head impact",
        applicable_protocols=["P006", "P007", "*"]
    ),
    RedFlagRule(
        rule_id="RF-006",
        condition="severe_burn_or_chemical_source",
        priority="PRIORITY",
        action="Urgent medical dressing and irrigation evaluation",
        description="Burn involves face, hands, joints, large area, or chemical/electrical source",
        applicable_protocols=["P003", "*"]
    ),
    RedFlagRule(
        rule_id="RF-007",
        condition="high_grade_fever_with_neck_stiffness",
        priority="PRIORITY",
        action="Urgent clinician review for possible CNS infection / sepsis screening",
        description="Fever associated with stiff neck, severe headache, confusion, or convulsions",
        applicable_protocols=["P005", "*"]
    ),
    RedFlagRule(
        rule_id="RF-008",
        condition="visible_deformity_or_compound_fracture",
        priority="PRIORITY",
        action="Orthopedic triage and urgent X-ray immobilization",
        description="Visible bone deformity, skin tenting, or inability to bear weight",
        applicable_protocols=["P004", "*"]
    ),
    RedFlagRule(
        rule_id="RF-009",
        condition="severe_unbearable_pain",
        priority="NEEDS_REVIEW",
        action="Nursing pain assessment and priority clinician queue",
        description="Patient reports severe pain (score 8-10 / 10)",
        applicable_protocols=["*"]
    )
]
