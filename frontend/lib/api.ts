import { EncounterResponse, EncounterSummary, Message, AuditLog } from '../types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function createEncounter(data: {
  patient_id?: string;
  age?: number;
  gender?: string;
  language: string;
  initial_complaint?: string;
}): Promise<EncounterResponse> {
  const res = await fetch(`${API_BASE}/api/v1/encounters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create encounter: ${res.statusText}`);
  return res.json();
}

export async function getEncounter(encounterId: string): Promise<EncounterResponse> {
  const res = await fetch(`${API_BASE}/api/v1/encounters/${encounterId}`);
  if (!res.ok) throw new Error(`Failed to get encounter: ${res.statusText}`);
  return res.json();
}

export async function listEncounters(priority?: string, status?: string): Promise<EncounterSummary[]> {
  const params = new URLSearchParams();
  if (priority) params.append('priority', priority);
  if (status) params.append('status', status);

  const res = await fetch(`${API_BASE}/api/v1/encounters?${params.toString()}`);
  if (!res.ok) throw new Error(`Failed to list encounters: ${res.statusText}`);
  return res.json();
}

export async function postPatientMessage(encounterId: string, message: string, language?: string): Promise<{
  assistant_response: string;
  encounter_status: string;
  priority: string;
  escalation_required: boolean;
  extracted_fields: Record<string, any>;
}> {
  const res = await fetch(`${API_BASE}/api/v1/encounters/${encounterId}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language }),
  });
  if (!res.ok) throw new Error(`Failed to post message: ${res.statusText}`);
  return res.json();
}

export async function getConversation(encounterId: string): Promise<{ encounter_id: string; messages: Message[]; total: number }> {
  const res = await fetch(`${API_BASE}/api/v1/encounters/${encounterId}/conversation`);
  if (!res.ok) throw new Error(`Failed to get conversation: ${res.statusText}`);
  return res.json();
}

export async function acknowledgeEncounter(encounterId: string, staffId: string, notes?: string): Promise<EncounterResponse> {
  const res = await fetch(`${API_BASE}/api/v1/encounters/${encounterId}/acknowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ staff_id: staffId, notes }),
  });
  if (!res.ok) throw new Error(`Failed to acknowledge: ${res.statusText}`);
  return res.json();
}

export async function manualEscalate(encounterId: string, staffId: string, reason: string, priority: string = "IMMEDIATE_ESCALATION"): Promise<EncounterResponse> {
  const res = await fetch(`${API_BASE}/api/v1/encounters/${encounterId}/escalate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ staff_id: staffId, reason, priority }),
  });
  if (!res.ok) throw new Error(`Failed to escalate: ${res.statusText}`);
  return res.json();
}

export async function getAuditLogs(encounterId: string): Promise<AuditLog[]> {
  const res = await fetch(`${API_BASE}/api/v1/encounters/${encounterId}/audit`);
  if (!res.ok) throw new Error(`Failed to get audit logs: ${res.statusText}`);
  return res.json();
}

export async function sendStaffGuidance(
  encounterId: string,
  staffId: string,
  guidance: string
): Promise<{ status: string; message_id: number; content: string; sender: string }> {
  const res = await fetch(`${API_BASE}/api/v1/encounters/${encounterId}/staff-guidance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ staff_id: staffId, guidance }),
  });
  if (!res.ok) throw new Error(`Failed to send staff guidance: ${res.statusText}`);
  return res.json();
}

export async function listProtocols(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/v1/protocols`);
  if (!res.ok) throw new Error(`Failed to list protocols: ${res.statusText}`);
  return res.json();
}
