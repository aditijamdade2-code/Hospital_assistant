import React from 'react';
import { ChevronRight, Clock, AlertOctagon, User, Shield } from 'lucide-react';
import { EncounterSummary, Priority } from '../../types';
import { PriorityBadge } from '../common/PriorityBadge';

interface EncountersTableProps {
  encounters: EncounterSummary[];
  selectedEncounterId: string | null;
  onSelectEncounter: (id: string) => void;
  isLoading: boolean;
}

export const EncountersTable: React.FC<EncountersTableProps> = ({
  encounters,
  selectedEncounterId,
  onSelectEncounter,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-500 text-sm">
        <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
        Loading OPD encounters...
      </div>
    );
  }

  if (encounters.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-500 text-sm">
        <Shield className="w-8 h-8 text-slate-400 mx-auto mb-2" />
        No active encounters in this triage filter.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-700">
          <thead className="bg-slate-50/80 text-slate-600 uppercase text-[10px] font-semibold tracking-wider border-b border-slate-200">
            <tr>
              <th className="py-3 px-4">Priority</th>
              <th className="py-3 px-4">Encounter / Patient</th>
              <th className="py-3 px-4">Chief Complaint</th>
              <th className="py-3 px-4">Protocol</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Language</th>
              <th className="py-3 px-4">Time</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {encounters.map((enc) => {
              const isSelected = selectedEncounterId === enc.encounter_id;
              const isCritical = enc.priority === 'IMMEDIATE_ESCALATION';

              return (
                <tr
                  key={enc.encounter_id}
                  onClick={() => onSelectEncounter(enc.encounter_id)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-blue-50/70 font-medium'
                      : isCritical
                      ? 'bg-red-50/40 hover:bg-red-50/70'
                      : 'hover:bg-slate-50/80'
                  }`}
                >
                  <td className="py-3 px-4 whitespace-nowrap">
                    <PriorityBadge priority={enc.priority} size="sm" />
                  </td>

                  <td className="py-3 px-4 whitespace-nowrap">
                    <div className="font-mono font-bold text-slate-900">
                      {enc.encounter_id}
                    </div>
                    <div className="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                      <User className="w-3 h-3 text-slate-400" />
                      <span>{enc.patient_id || 'Unknown'}</span>
                      {enc.age && <span>• {enc.age}y</span>}
                      {enc.gender && <span>• {enc.gender[0]}</span>}
                    </div>
                  </td>

                  <td className="py-3 px-4">
                    <span className="font-medium text-slate-800 capitalize">
                      {enc.chief_complaint || 'Pending clarification'}
                    </span>
                  </td>

                  <td className="py-3 px-4 whitespace-nowrap">
                    {enc.protocol_id ? (
                      <span className="font-mono font-medium text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                        {enc.protocol_id} (v{enc.protocol_version || '1.0'})
                      </span>
                    ) : (
                      <span className="text-slate-400 italic">Evaluating</span>
                    )}
                  </td>

                  <td className="py-3 px-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wide ${
                        enc.status === 'ESCALATED'
                          ? 'bg-red-100 text-red-800'
                          : enc.status === 'ACKNOWLEDGED_BY_STAFF'
                          ? 'bg-emerald-100 text-emerald-800'
                          : enc.status === 'GUIDANCE_PROVIDED'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {enc.status.replace(/_/g, ' ')}
                    </span>
                  </td>

                  <td className="py-3 px-4 uppercase font-semibold text-slate-500">
                    {enc.language}
                  </td>

                  <td className="py-3 px-4 whitespace-nowrap text-slate-500">
                    {new Date(enc.updated_at).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>

                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    <button
                      type="button"
                      className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800 font-medium"
                    >
                      <span>Review</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
