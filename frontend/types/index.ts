export type Language = 'en' | 'hi' | 'mr';

export type Priority = 'NORMAL' | 'NEEDS_REVIEW' | 'PRIORITY' | 'IMMEDIATE_ESCALATION';

export type EncounterStatus = 
  | 'COLLECTING_INFORMATION'
  | 'GUIDANCE_PROVIDED'
  | 'ESCALATED'
  | 'ACKNOWLEDGED_BY_STAFF'
  | 'CLOSED';

export interface Patient {
  patient_id: string | null;
  age: number | null;
  gender: string | null;
}

export interface EscalationReason {
  priority: Priority;
  triggered_rule: string;
  rule_description: string;
  detected_information: Record<string, any>;
  protocol_id?: string | null;
  protocol_version?: string | null;
  action: string;
  clinical_instruction?: string | null;
  timestamp?: string;
}

export interface EncounterSummary {
  encounter_id: string;
  patient_id: string | null;
  age: number | null;
  gender: string | null;
  language: string;
  chief_complaint: string | null;
  priority: Priority;
  protocol_id: string | null;
  protocol_version: string | null;
  escalation_required: boolean;
  status: EncounterStatus;
  created_at: string;
  updated_at: string;
}

export interface EncounterResponse {
  encounter_id: string;
  patient: Patient;
  language: string;
  chief_complaint: string | null;
  symptoms: string[];
  duration: string | null;
  severity: string | null;
  extracted_fields: Record<string, any>;
  medical_history: string[];
  allergies: string[];
  medications: string[];
  vitals: Record<string, any>;
  red_flags: EscalationReason[];
  protocol_id: string | null;
  protocol_version: string | null;
  protocol_name: string | null;
  priority: Priority;
  escalation_required: boolean;
  escalation_reason: EscalationReason | null;
  status: EncounterStatus;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  encounter_id: string;
  sender: 'PATIENT' | 'ASSISTANT' | 'SYSTEM' | 'CLINICAL_STAFF';
  content: string;
  language: string;
  extracted_info?: Record<string, any> | null;
  created_at: string;
}

export interface AuditLog {
  id: number;
  event_type: string;
  details: Record<string, any>;
  created_at: string;
}
