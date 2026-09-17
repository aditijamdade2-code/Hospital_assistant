from typing import Dict, Any, List, Optional
import logging
from backend.app.schemas.safety import SafetyEvaluationResult, EscalationDetail, RedFlagRule
from backend.app.safety.red_flags import PREDEFINED_RED_FLAGS
from backend.app.safety.escalation import EscalationBuilder

logger = logging.getLogger(__name__)

PRIORITY_RANK = {
    "NORMAL": 0,
    "NEEDS_REVIEW": 1,
    "PRIORITY": 2,
    "IMMEDIATE_ESCALATION": 3
}

class SafetyEngine:
    def __init__(self, rules: Optional[List[RedFlagRule]] = None):
        self.rules = rules or PREDEFINED_RED_FLAGS

    def evaluate(
        self,
        extracted_fields: Dict[str, Any],
        raw_text: Optional[str] = None,
        protocol_id: Optional[str] = None,
        protocol_version: Optional[str] = "1.0",
        language: str = "en"
    ) -> SafetyEvaluationResult:
        """
        Deterministically evaluates patient parameters against predefined clinical safety rules.
        Does NOT rely on LLM for safety decisions.
        """
        escalations: List[EscalationDetail] = []
        highest_priority = "NORMAL"
        
        # Combine text for keyword/safety matching
        full_text = (raw_text or "").lower()
        symptoms = [str(s).lower() for s in extracted_fields.get("symptoms", [])]
        chief_complaint = str(extracted_fields.get("chief_complaint", "")).lower()
        pain_level = extracted_fields.get("pain_level")

        # 1. Rule RF-001: Pulsating or arterial bleeding
        if any(term in full_text or any(term in s for s in symptoms) for term in [
            "pulsat", "spurting", "fountain", "pumping blood", "dhamni", "fuhara"
        ]) or str(extracted_fields.get("bleeding_rate")).lower() in ["spurting", "pulsating"]:
            rule = next(r for r in self.rules if r.rule_id == "RF-001")
            escalations.append(EscalationBuilder.build_escalation(
                rule=rule,
                detected_information={"bleeding_rate": "spurting/pulsating", "symptoms": symptoms},
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                clinical_instruction="Direct continuous heavy pressure; urgent triage alert sent"
            ))

        # 2. Rule RF-002: Uncontrolled bleeding > 10 min
        duration_val = str(extracted_fields.get("duration", "")).lower()
        bleeding_status = str(extracted_fields.get("bleeding_status", "")).lower()
        if (
            ("not stopping" in full_text or "ruk nahi raha" in full_text or "uncontrolled" in bleeding_status or "continuously" in bleeding_status)
            and any(t in duration_val or t in full_text for t in ["15", "20", "30", "hour", "hours", "minute", "min", "der"])
        ) or any(t in full_text for t in ["bleeding not stopping", "ruk nahi raha", "thambath nahi"]):
            rule = next(r for r in self.rules if r.rule_id == "RF-002")
            escalations.append(EscalationBuilder.build_escalation(
                rule=rule,
                detected_information={"duration": duration_val, "bleeding_status": bleeding_status},
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                clinical_instruction="Continuous firm pressure; nursing staff notified"
            ))

        # 3. Rule RF-003: Anaphylaxis / Airway compromise
        breathing_issue = extracted_fields.get("breathing_status")
        swelling = extracted_fields.get("lip_tongue_swelling")
        airway_symptoms = any("lip" in s or "tongue" in s or "throat" in s or "swelling" in s for s in symptoms)
        if (
            any(w in full_text for w in [
                "can't breathe", "cannot breathe", "difficulty breathing", "trouble breathing",
                "breathless", "sans lene me takleef", "shwas ghyayla tras", "choking",
                "throat tight", "throat is closing", "closing up", "throat swelling", "gale me"
            ])
            or any(w in full_text for w in ["lip swelling", "tongue swelling", "swollen lips", "swollen tongue", "hives"])
            or (airway_symptoms and any(w in full_text for w in ["allergy", "peanuts", "sting", "reaction", "rash"]))
            or str(breathing_issue).lower() in ["yes", "difficulty", "tight", "true"]
            or str(swelling).lower() in ["yes", "lips", "tongue", "true"]
        ):
            rule = next(r for r in self.rules if r.rule_id == "RF-003")
            escalations.append(EscalationBuilder.build_escalation(
                rule=rule,
                detected_information={"breathing_status": breathing_issue or "compromised", "swelling": swelling},
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                clinical_instruction="High-flow oxygen standby, alert nursing triage immediately"
            ))

        # 4. Rule RF-004: Chest pain or cardiovascular distress
        if any(w in full_text for w in ["chest pain", "sine me dard", "chhatit dukhne", "heart pain", "pressure on chest", "left arm"]):
            rule = next(r for r in self.rules if r.rule_id == "RF-004")
            escalations.append(EscalationBuilder.build_escalation(
                rule=rule,
                detected_information={"chief_complaint": "chest pain / cardiovascular distress", "symptoms": symptoms},
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                clinical_instruction="Immediate ECG protocol and cardiology OPD priority triage"
            ))

        # 5. Rule RF-005: Loss of consciousness / syncope
        if any(w in full_text for w in ["lost consciousness", "passed out", "behoshi", "behtar", "bheshuddh", "blackout", "head hit"]):
            rule = next(r for r in self.rules if r.rule_id == "RF-005")
            escalations.append(EscalationBuilder.build_escalation(
                rule=rule,
                detected_information={"consciousness": "loss_reported", "symptoms": symptoms},
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                clinical_instruction="Keep patient recumbent; staff vitals inspection"
            ))

        # 6. Rule RF-006: Severe burn or chemical/electrical
        burn_source = str(extracted_fields.get("burn_source", "")).lower()
        if (
            "chemical" in full_text or "chemical" in burn_source
            or "electric" in full_text or "electric" in burn_source
            or any(w in full_text for w in ["face burn", "blackened", "charred"])
        ):
            rule = next(r for r in self.rules if r.rule_id == "RF-006")
            escalations.append(EscalationBuilder.build_escalation(
                rule=rule,
                detected_information={"burn_source": burn_source or "chemical/electrical", "text": full_text},
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                clinical_instruction="Copious gentle water flush; burn dressing priority"
            ))

        # 7. Rule RF-007: Fever with stiff neck or convulsions
        if (
            ("fever" in full_text or "bukhar" in full_text or "taap" in full_text)
            and any(w in full_text for w in ["stiff neck", "gardan", "man aakhadne", "seizure", "convulsion", "jhatke"])
        ):
            rule = next(r for r in self.rules if r.rule_id == "RF-007")
            escalations.append(EscalationBuilder.build_escalation(
                rule=rule,
                detected_information={"fever": "present", "neurological_sign": "stiff neck/convulsions"},
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                clinical_instruction="Urgent clinician review for suspected central infection"
            ))

        # 8. Rule RF-008: Visible deformity or fracture
        if any(w in full_text for w in ["bone sticking", "deformity", "broken bone", "haddi toot", "cannot walk", "tedha"]):
            rule = next(r for r in self.rules if r.rule_id == "RF-008")
            escalations.append(EscalationBuilder.build_escalation(
                rule=rule,
                detected_information={"deformity": "reported", "weight_bearing": "unable"},
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                clinical_instruction="Immobilize limb; prevent weight bearing; orthopedic triage"
            ))

        # 9. Rule RF-009: Severe pain (>= 8 by number OR by keywords)
        # Keyword detection: catches "bahut zyada dard", "bahut pen", "تीवر", "unbearable", etc.
        _severe_pain_keywords = [
            # English
            "severe pain", "unbearable pain", "extreme pain", "excruciating", "worst pain",
            # Hindi transliterated
            "bahut zyada", "bahut dard", "bahut pen", "bahut pain", "bahut jyada dard",
            "bahut jyada pen", "bahut taklif", "bahut takleef", "bahut peeda", "bahut vedana",
            # Hindi Devanagari
            "बहुत दर्द", "बहुत तकलीफ", "बहुत पीड़ा", "तीव्र दर्द", "असह्य दर्द",
            "बहुत ज्यादा", "नहीं सहा जाता",
            # Marathi transliterated
            "khup dukht", "khup vedana", "khup jast", "tivra vedana", "asahya vedana",
            # Marathi Devanagari
            "खूप दुखते", "खूप वेदना", "तीव्र वेदना", "असह्य वेदना",
        ]
        _text_severe_pain = any(kw in full_text for kw in _severe_pain_keywords)
        try:
            _numeric_severe_pain = (pain_level is not None and int(pain_level) >= 8)
        except (ValueError, TypeError):
            _numeric_severe_pain = False
        if _text_severe_pain or _numeric_severe_pain:
            rule = next(r for r in self.rules if r.rule_id == "RF-009")
            escalations.append(EscalationBuilder.build_escalation(
                rule=rule,
                detected_information={
                    "pain_level": pain_level,
                    "text_trigger": next((kw for kw in _severe_pain_keywords if kw in full_text), None)
                },
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                clinical_instruction="Triage pain score review; nursing priority queue"
            ))

        # 10. Distress check: patient reports no nurse/staff available + severe pain
        _no_staff_keywords = [
            "no nurse", "nurse nahi", "nurse nahin", "koi nurse nahi", "कोई नर्स नहीं",
            "no staff", "staff nahi", "doctor nahi", "koi nahi", "कोई नहीं",
            "nurse nahi hai", "koi doctor nahi", "parichaarika nahi", "ithey koni nahi"
        ]
        if any(kw in full_text for kw in _no_staff_keywords) and (
            _text_severe_pain or any(kw in full_text for kw in ["dard", "pen", "pain", "dukhne", "vedana", "दर्द", "वेदना"])
        ):
            # Escalate to PRIORITY if not already higher
            # Synthesise an RF-005 escalation (staff-reachability + pain) if not already triggered
            if not any(e.rule_id == "RF-005" for e in escalations):
                rule = next(r for r in self.rules if r.rule_id == "RF-005")
                escalations.append(EscalationBuilder.build_escalation(
                    rule=rule,
                    detected_information={"trigger": "no_staff_reported", "pain": "reported"},
                    protocol_id=protocol_id,
                    protocol_version=protocol_version,
                    clinical_instruction="Patient reports no staff visible; immediate nursing desk check required"
                ))

        # Determine highest priority
        for esc in escalations:
            if PRIORITY_RANK[esc.priority] > PRIORITY_RANK[highest_priority]:
                highest_priority = esc.priority

        escalation_required = PRIORITY_RANK[highest_priority] >= PRIORITY_RANK["PRIORITY"]
        stop_questioning = (highest_priority == "IMMEDIATE_ESCALATION")

        # Provide hospital approved immediate instruction in patient's language
        immediate_instruction = None
        if highest_priority == "IMMEDIATE_ESCALATION":
            if language == "hi":
                immediate_instruction = "तत्काल सूचना: कृपया शांत बैठें। अस्पताल के स्वास्थ्य कर्मी को आपकी स्थिति की सूचना भेज दी गई है और वे तुरंत आ रहे हैं।"
            elif language == "mr":
                immediate_instruction = "तातडीची सूचना: कृपया शांत बसा. रुग्णालयातील वैद्यकीय कर्मचाऱ्यांना माहिती देण्यात आली असून ते लगेच आपल्याकडे येत आहेत."
            else:
                immediate_instruction = "HIGH-PRIORITY ALERT: Please remain calm and seated. Hospital clinical staff have been alerted to your room/station and are attending to you immediately."
        elif highest_priority == "PRIORITY":
            if language == "hi":
                immediate_instruction = "सूचना: आपकी स्थिति को प्राथमिकता श्रेणी में दर्ज किया गया है। नर्सिंग स्टाफ आपकी जांच करेंगे।"
            elif language == "mr":
                immediate_instruction = "सूचना: आपली स्थिती प्राधान्य श्रेणीत नोंदवली गेली आहे. नर्सिंग कर्मचारी लवकरच तपासणी करतील."
            else:
                immediate_instruction = "PRIORITY ALERT: Your situation has been flagged for prioritized nursing review. Please follow the guidance instructions below."

        return SafetyEvaluationResult(
            triggered=(len(escalations) > 0),
            highest_priority=highest_priority,
            escalation_required=escalation_required,
            escalations=escalations,
            immediate_instruction=immediate_instruction,
            stop_questioning=stop_questioning
        )

safety_engine = SafetyEngine()
