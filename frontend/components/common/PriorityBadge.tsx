import React from 'react';
import { AlertOctagon, AlertTriangle, Clock, CheckCircle2 } from 'lucide-react';
import { Priority } from '../../types';

interface PriorityBadgeProps {
  priority: Priority;
  size?: 'sm' | 'md' | 'lg';
  showDescription?: boolean;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({
  priority,
  size = 'md',
  showDescription = false,
}) => {
  const configs = {
    IMMEDIATE_ESCALATION: {
      bg: 'bg-red-50 text-red-700 border-red-200',
      badgeBg: 'bg-red-600 text-white',
      icon: AlertOctagon,
      label: 'IMMEDIATE ESCALATION',
      ariaLabel: 'Critical Alert: Immediate clinical staff escalation required',
      desc: 'Immediate triage and clinician alert sent',
    },
    PRIORITY: {
      bg: 'bg-amber-50 text-amber-800 border-amber-200',
      badgeBg: 'bg-amber-500 text-white',
      icon: AlertTriangle,
      label: 'PRIORITY CARE',
      ariaLabel: 'High Priority: Prioritized clinical staff review required',
      desc: 'Urgent assessment queue',
    },
    NEEDS_REVIEW: {
      bg: 'bg-yellow-50 text-yellow-800 border-yellow-200',
      badgeBg: 'bg-yellow-500 text-slate-950',
      icon: Clock,
      label: 'NEEDS REVIEW',
      ariaLabel: 'Medium Priority: Clinical staff review recommended',
      desc: 'Follow-up triage required',
    },
    NORMAL: {
      bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      badgeBg: 'bg-emerald-600 text-white',
      icon: CheckCircle2,
      label: 'NORMAL OPD',
      ariaLabel: 'Low Priority: Standard OPD outpatient queue',
      desc: 'Standard intake queue',
    },
  };

  const config = configs[priority] || configs.NORMAL;
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3 py-1.5 gap-2 font-semibold',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  };

  return (
    <div className="inline-flex flex-col items-start">
      <span
        role="status"
        aria-label={config.ariaLabel}
        className={`inline-flex items-center rounded-full border ${config.bg} ${sizeClasses[size]}`}
      >
        <Icon className={`${iconSizes[size]} shrink-0`} aria-hidden="true" />
        <span>{config.label}</span>
      </span>
      {showDescription && (
        <span className="text-[11px] text-slate-500 mt-0.5 ml-1">
          {config.desc}
        </span>
      )}
    </div>
  );
};
