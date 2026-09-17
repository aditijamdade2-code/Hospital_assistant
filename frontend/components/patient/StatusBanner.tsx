'use client';

import React from 'react';
import { ShieldCheck, AlertCircle, AlertOctagon, UserCheck } from 'lucide-react';
import { Priority, EncounterStatus, Language } from '../../types';
import { PriorityBadge } from '../common/PriorityBadge';
import { translations } from '../../lib/translations';

interface StatusBannerProps {
  status: EncounterStatus;
  priority: Priority;
  encounterId?: string;
  language: Language;
}

export const StatusBanner: React.FC<StatusBannerProps> = ({
  status,
  priority,
  encounterId,
  language,
}) => {
  const t = translations[language] || translations.en;

  const statusLabels: Record<EncounterStatus, { label: string; desc: string; icon: any }> = {
    COLLECTING_INFORMATION: {
      label: 'Collecting Initial Information',
      desc: 'Please answer follow-up questions so clinical staff have complete details.',
      icon: AlertCircle,
    },
    GUIDANCE_PROVIDED: {
      label: 'Approved First-Aid Guidance Displayed',
      desc: 'Follow the approved steps while waiting for clinical staff to call you.',
      icon: ShieldCheck,
    },
    ESCALATED: {
      label: 'High Priority Escalation Active',
      desc: 'Red-flag identified. Clinical staff have been alerted to your intake.',
      icon: AlertOctagon,
    },
    ACKNOWLEDGED_BY_STAFF: {
      label: 'Acknowledged by Healthcare Staff',
      desc: 'A nurse or triage doctor has accepted your case file.',
      icon: UserCheck,
    },
    CLOSED: {
      label: 'Consultation Completed',
      desc: 'Encounter has been closed by clinical staff.',
      icon: ShieldCheck,
    },
  };

  const current = statusLabels[status] || statusLabels.COLLECTING_INFORMATION;
  const Icon = current.icon;

  return (
    <div className={`rounded-xl border p-4 shadow-xs transition-all ${
      priority === 'IMMEDIATE_ESCALATION'
        ? 'bg-red-50/80 border-red-200 text-red-900'
        : priority === 'PRIORITY'
        ? 'bg-amber-50/80 border-amber-200 text-amber-900'
        : 'bg-white border-slate-200 text-slate-900'
    }`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-start space-x-3">
          <div className={`p-2 rounded-lg shrink-0 ${
            priority === 'IMMEDIATE_ESCALATION'
              ? 'bg-red-100 text-red-700'
              : priority === 'PRIORITY'
              ? 'bg-amber-100 text-amber-700'
              : 'bg-blue-100 text-blue-700'
          }`}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold text-sm sm:text-base">{current.label}</h3>
              {encounterId && (
                <span className="text-xs font-mono font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                  {encounterId}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-600 mt-0.5">{current.desc}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 self-start sm:self-center">
          <PriorityBadge priority={priority} size="md" />
        </div>
      </div>
    </div>
  );
};
