'use client';

import React, { useState, useEffect } from 'react';
import {
  X, CheckCircle, AlertTriangle, ShieldCheck, User,
  Calendar, FileText, HeartPulse, Clock, Activity, MessageSquare,
  Send, Stethoscope, Sparkles
} from 'lucide-react';
import { EncounterResponse, Message } from '../../types';
import { PriorityBadge } from '../common/PriorityBadge';
import { ExplainableEscalationCard } from './ExplainableEscalationCard';
import {
  getConversation, acknowledgeEncounter,
  manualEscalate, sendStaffGuidance
} from '../../lib/api';

interface EncounterDetailDrawerProps {
  encounter: EncounterResponse | null;
  onClose: () => void;
  onRefresh: () => void;
}

export const EncounterDetailDrawer: React.FC<EncounterDetailDrawerProps> = ({
  encounter,
  onClose,
  onRefresh,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeTab, setActiveTab] = useState<'clinical' | 'conversation'>('clinical');
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [staffId, setStaffId] = useState('NURSE-ON-DUTY');
  const [ackNotes, setAckNotes] = useState('');
  const [guidanceText, setGuidanceText] = useState('');
  const [feedbackNotice, setFeedbackNotice] = useState<string | null>(null);
  const [escalateReason, setEscalateReason] = useState('');
  const [isEscalatingModal, setIsEscalatingModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (!encounter) return;
    loadDetails(encounter.encounter_id);
  }, [encounter?.encounter_id]);

  const loadDetails = async (id: string) => {
    setIsLoadingDetails(true);
    try {
      const convData = await getConversation(id);
      setMessages(convData.messages);
    } catch (e) {
      console.error('Failed to load encounter details:', e);
    } finally {
      setIsLoadingDetails(false);
    }
  };

  if (!encounter) return null;

  const handleAcknowledge = async () => {
    setActionLoading(true);
    try {
      const noteToSend = ackNotes.trim() || 'Staff acknowledged case file. Please wait for clinical examination.';
      await acknowledgeEncounter(encounter.encounter_id, staffId, noteToSend);
      setFeedbackNotice('✓ Encounter acknowledged! Patient chat updated in real time.');
      setTimeout(() => setFeedbackNotice(null), 4000);
      onRefresh();
      loadDetails(encounter.encounter_id);
    } catch (e) {
      alert(`Acknowledge failed: ${e}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSendGuidance = async (customText?: string) => {
    const textToSend = (customText || guidanceText).trim();
    if (!textToSend) return;
    setActionLoading(true);
    try {
      await sendStaffGuidance(encounter.encounter_id, staffId, textToSend);
      setGuidanceText('');
      setFeedbackNotice('✓ Treatment guidance sent directly to patient chat!');
      setTimeout(() => setFeedbackNotice(null), 4000);
      onRefresh();
      loadDetails(encounter.encounter_id);
    } catch (e) {
      alert(`Send guidance failed: ${e}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleManualEscalate = async () => {
    if (!escalateReason.trim()) return;
    setActionLoading(true);
    try {
      await manualEscalate(encounter.encounter_id, staffId, escalateReason.trim());
      setIsEscalatingModal(false);
      setEscalateReason('');
      onRefresh();
      loadDetails(encounter.encounter_id);
    } catch (e) {
      alert(`Manual escalation failed: ${e}`);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 max-w-full flex z-40">
      <div className="w-screen max-w-2xl bg-white shadow-2xl border-l border-slate-200 flex flex-col">
        {/* Header */}
        <div className="p-4 sm:p-6 border-b border-slate-200 bg-slate-50/70 flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-slate-900 font-mono">
                {encounter.encounter_id}
              </h2>
              <PriorityBadge priority={encounter.priority} size="sm" />
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Patient: <strong className="text-slate-800">{encounter.patient.patient_id || 'Walk-in'}</strong>
              {encounter.patient.age && ` • ${encounter.patient.age} years`}
              {encounter.patient.gender && ` • ${encounter.patient.gender}`}
              {` • Lang: ${encounter.language.toUpperCase()}`}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 bg-white px-6">
          <button
            onClick={() => setActiveTab('clinical')}
            className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center space-x-1.5 transition ${
              activeTab === 'clinical'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Clinical Information & Protocol</span>
          </button>
          <button
            onClick={() => setActiveTab('conversation')}
            className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center space-x-1.5 transition ${
              activeTab === 'conversation'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Conversation History ({messages.length})</span>
          </button>
        </div>

        {/* Drawer Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeTab === 'clinical' && (
            <div className="space-y-6">
              {/* Explainable Escalation Card if triggered */}
              {encounter.escalation_reason && (
                <ExplainableEscalationCard escalation={encounter.escalation_reason as any} />
              )}

              {/* Feedback Success Notification */}
              {feedbackNotice && (
                <div className="bg-emerald-600 text-white px-4 py-2.5 rounded-xl text-xs font-semibold flex items-center justify-between shadow-xs animate-fade-in">
                  <span>{feedbackNotice}</span>
                  <button onClick={() => setFeedbackNotice(null)} className="text-emerald-100 hover:text-white">✕</button>
                </div>
              )}

              {/* Status & Staff Acknowledgement Bar */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3 text-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <span className="text-slate-500">Current Status:</span>{' '}
                    <span className="font-bold text-slate-900 uppercase">
                      {encounter.status.replace(/_/g, ' ')}
                    </span>
                    {encounter.acknowledged_by && (
                      <p className="text-emerald-700 font-medium mt-0.5">
                        ✓ Acknowledged by {encounter.acknowledged_by} at{' '}
                        {new Date(encounter.acknowledged_at!).toLocaleTimeString()}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setIsEscalatingModal(true)}
                      disabled={actionLoading}
                      className="px-3 py-1.5 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white rounded-lg font-medium shadow-xs flex items-center space-x-1 transition"
                    >
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>Manual Escalate</span>
                    </button>
                  </div>
                </div>

                {/* Staff ID & Acknowledgment Controls */}
                <div className="pt-2 border-t border-slate-200 flex flex-col sm:flex-row gap-2 items-stretch sm:items-center">
                  <input
                    type="text"
                    value={staffId}
                    onChange={(e) => setStaffId(e.target.value)}
                    placeholder="Staff ID / Role"
                    className="w-full sm:w-36 px-2.5 py-1.5 text-xs bg-white border border-slate-300 rounded-lg font-mono"
                    title="Staff Identifier"
                  />
                  <input
                    type="text"
                    value={ackNotes}
                    onChange={(e) => setAckNotes(e.target.value)}
                    placeholder="Optional message to patient (e.g. Please proceed to Room 4)..."
                    className="flex-1 px-3 py-1.5 text-xs bg-white border border-slate-300 rounded-lg"
                  />
                  <button
                    onClick={handleAcknowledge}
                    disabled={actionLoading || encounter.status === 'ACKNOWLEDGED_BY_STAFF'}
                    className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg font-semibold shadow-xs flex items-center justify-center space-x-1.5 transition shrink-0"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Acknowledge & Notify Patient</span>
                  </button>
                </div>
              </div>

              {/* Direct Patient Clinical Guidance & Treatment Instructions */}
              <div className="bg-emerald-50/50 p-5 rounded-xl border border-emerald-200/80 shadow-xs space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-emerald-950 font-bold text-xs uppercase tracking-wider">
                    <Stethoscope className="w-4 h-4 text-emerald-700" />
                    <span>Direct Patient Clinical Guidance & Treatment (Live Chat)</span>
                  </div>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold">
                    Real-time Push
                  </span>
                </div>
                <p className="text-xs text-slate-600">
                  Send treatment instructions, medications, or room directions directly into this patient's active chat window. The patient will see it immediately without refreshing.
                </p>

                {/* Quick Guidance Presets */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {[
                    'Please proceed to OPD Room 3 for vitals triage.',
                    'Please rest in Observation Bay A. Attending doctor is arriving in 5 minutes.',
                    'Take Paracetamol 500mg after food if fever > 100°F. Doctor will see you shortly.',
                    'Prescription is prepared. Please collect from Pharmacy Counter 2.',
                  ].map((tpl, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setGuidanceText(tpl)}
                      className="text-[11px] bg-white text-slate-700 hover:text-emerald-800 hover:bg-emerald-50 px-2.5 py-1 rounded-lg border border-slate-200 transition text-left"
                    >
                      + {tpl}
                    </button>
                  ))}
                </div>

                <div className="flex gap-2">
                  <textarea
                    rows={2}
                    value={guidanceText}
                    onChange={(e) => setGuidanceText(e.target.value)}
                    placeholder="Type clinical guidance, treatment advice, or consultation instructions..."
                    className="flex-1 text-xs p-2.5 rounded-lg border border-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 bg-white"
                  />
                  <button
                    type="button"
                    disabled={actionLoading || !guidanceText.trim()}
                    onClick={() => handleSendGuidance()}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg font-semibold text-xs shadow-xs flex items-center space-x-1.5 transition self-end"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>Send to Chat</span>
                  </button>
                </div>
              </div>

              {/* Structured Clinical Intake Summary */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
                <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500">
                  Structured Clinical Intake Information
                </h3>
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-slate-500 block">Chief Complaint:</span>
                    <span className="font-semibold text-slate-900 text-sm capitalize">
                      {encounter.chief_complaint || 'None extracted'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Identified Symptoms:</span>
                    <div className="flex flex-wrap gap-1 mt-0.5">
                      {encounter.symptoms.length > 0 ? (
                        encounter.symptoms.map((s, i) => (
                          <span key={i} className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-medium">
                            {s}
                          </span>
                        ))
                      ) : (
                        <span className="text-slate-400">None specified</span>
                      )}
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Duration:</span>
                    <span className="font-medium text-slate-800">
                      {encounter.duration || 'Unknown'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Severity:</span>
                    <span className="font-medium text-slate-800 capitalize">
                      {encounter.severity || 'Unknown'}
                    </span>
                  </div>
                </div>

                {/* Additional Extracted Fields */}
                {Object.keys(encounter.extracted_fields || {}).length > 0 && (
                  <div className="pt-3 border-t border-slate-100">
                    <span className="text-slate-500 block text-xs font-semibold mb-1">
                      Additional Deterministic Fields:
                    </span>
                    <div className="flex flex-wrap gap-2 text-xs font-mono">
                      {Object.entries(encounter.extracted_fields).map(([k, v]) => (
                        <span key={k} className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                          {k}: {String(v)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Protocol Evaluated */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2 text-xs">
                <h3 className="font-bold uppercase tracking-wider text-slate-500">
                  Clinical Protocol Engine State
                </h3>
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-slate-900 text-sm">
                      {encounter.protocol_name || 'No Protocol Matched'}
                    </span>
                    <span className="text-slate-500 block mt-0.5">
                      ID: {encounter.protocol_id || 'N/A'} (v{encounter.protocol_version || '1.0'})
                    </span>
                  </div>
                  <span className="bg-amber-50 text-amber-800 border border-amber-200 px-2 py-1 rounded text-[10px] font-semibold">
                    DEMO PROTOCOL
                  </span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'conversation' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Full Chronological Conversation Record
                </h3>
                <span className="text-[11px] text-slate-400">
                  {messages.length} messages
                </span>
              </div>

              <div className="space-y-3">
                {messages.map((m) => {
                  const isStaff = m.sender === 'CLINICAL_STAFF';
                  const isPatient = m.sender === 'PATIENT';

                  return (
                    <div
                      key={m.id}
                      className={`p-4 rounded-xl border text-xs leading-relaxed shadow-xs ${
                        isStaff
                          ? 'bg-emerald-50/80 border-emerald-300 text-emerald-950'
                          : isPatient
                          ? 'bg-blue-50/60 border-blue-200 text-blue-950'
                          : 'bg-white border-slate-200 text-slate-800'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5 font-semibold text-[11px] opacity-80">
                        <span className="flex items-center space-x-1.5">
                          {isStaff ? (
                            <>
                              <Stethoscope className="w-3.5 h-3.5 text-emerald-700" />
                              <span className="text-emerald-900 font-bold">👨‍⚕️ Clinical Staff Note / Guidance</span>
                            </>
                          ) : isPatient ? (
                            <span>Patient Input</span>
                          ) : (
                            <span>Assistant / System Guidance</span>
                          )}
                        </span>
                        <span className="text-[10px] text-slate-500">
                          {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <p className="whitespace-pre-line">{m.content}</p>
                    </div>
                  );
                })}
              </div>

              {/* Direct Reply / Guidance input bar in conversation tab */}
              <div className="pt-3 border-t border-slate-200">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={guidanceText}
                    onChange={(e) => setGuidanceText(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendGuidance();
                      }
                    }}
                    placeholder="Send direct message / treatment guidance to patient..."
                    className="flex-1 text-xs px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 bg-white"
                  />
                  <button
                    type="button"
                    disabled={actionLoading || !guidanceText.trim()}
                    onClick={() => handleSendGuidance()}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg font-semibold text-xs shadow-xs flex items-center space-x-1 transition"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>Send</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Manual Escalation Modal */}
        {isEscalatingModal && (
          <div className="fixed inset-0 bg-slate-950/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
              <div className="flex items-center space-x-2 text-red-600 font-bold">
                <AlertTriangle className="w-5 h-5" />
                <h3>Manual Clinical Escalation</h3>
              </div>
              <p className="text-xs text-slate-600">
                Provide a clinical rationale for manually escalating this encounter. This reason will be recorded in the audit trail.
              </p>
              <textarea
                rows={3}
                required
                value={escalateReason}
                onChange={(e) => setEscalateReason(e.target.value)}
                placeholder="e.g., Patient appears disoriented; vital signs triage priority required..."
                className="w-full text-xs p-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
              />
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsEscalatingModal(false)}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  disabled={!escalateReason.trim() || actionLoading}
                  onClick={handleManualEscalate}
                  className="px-4 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white text-xs font-semibold shadow-xs"
                >
                  Confirm Escalation
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
