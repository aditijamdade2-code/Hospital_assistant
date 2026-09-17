import React from 'react';
import { AlertOctagon, FileCheck, ShieldAlert, Cpu } from 'lucide-react';
import { EscalationReason } from '../../types';
import { PriorityBadge } from '../common/PriorityBadge';

interface ExplainableEscalationCardProps {
  escalation: EscalationReason;
}

export const ExplainableEscalationCard: React.FC<ExplainableEscalationCardProps> = ({
  escalation,
}) => {
  return (
    <div className="bg-red-50/90 border-2 border-red-300 rounded-xl p-4 sm:p-5 shadow-xs text-red-950">
      <div className="flex items-center justify-between pb-3 border-b border-red-200">
        <div className="flex items-center space-x-2">
          <AlertOctagon className="w-5 h-5 text-red-600 shrink-0" />
          <h4 className="font-bold text-sm sm:text-base tracking-tight text-red-900">
            Explainable Clinical Escalation Audit Record
          </h4>
        </div>
        <PriorityBadge priority={escalation.priority} size="sm" />
      </div>

      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        {/* Triggered Rule */}
        <div className="bg-white/80 p-2.5 rounded-lg border border-red-200">
          <span className="font-semibold text-slate-500 uppercase tracking-wider block text-[10px]">
            Triggered Rule ID
          </span>
          <span className="font-mono font-bold text-red-700 text-sm">
            {escalation.triggered_rule}
          </span>
          <p className="text-slate-700 mt-0.5">{escalation.rule_description}</p>
        </div>

        {/* Required Clinical Action */}
        <div className="bg-white/80 p-2.5 rounded-lg border border-red-200">
          <span className="font-semibold text-slate-500 uppercase tracking-wider block text-[10px]">
            Designated Clinical Action
          </span>
          <span className="font-semibold text-slate-900 text-sm">
            {escalation.action}
          </span>
          {escalation.clinical_instruction && (
            <p className="text-red-700 font-medium mt-0.5">{escalation.clinical_instruction}</p>
          )}
        </div>

        {/* Detected Information */}
        <div className="bg-white/80 p-2.5 rounded-lg border border-red-200 sm:col-span-2">
          <span className="font-semibold text-slate-500 uppercase tracking-wider block text-[10px]">
            Detected Information (Deterministic Extraction)
          </span>
          <div className="mt-1 flex flex-wrap gap-2 font-mono text-[11px]">
            {Object.entries(escalation.detected_information || {}).map(([k, v]) => (
              <span key={k} className="bg-red-100/70 text-red-800 px-2 py-0.5 rounded border border-red-200">
                <strong>{k}:</strong> {Array.isArray(v) ? v.join(', ') : String(v)}
              </span>
            ))}
          </div>
        </div>

        {/* Protocol Version */}
        <div className="bg-white/80 p-2.5 rounded-lg border border-red-200 sm:col-span-2 flex items-center justify-between text-[11px]">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-slate-400" />
            <span>
              <strong>Evaluated Protocol:</strong> {escalation.protocol_id || 'N/A'} (v{escalation.protocol_version || '1.0'})
            </span>
          </div>
          {escalation.timestamp && (
            <span className="text-slate-500">
              Triggered at: {new Date(escalation.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
