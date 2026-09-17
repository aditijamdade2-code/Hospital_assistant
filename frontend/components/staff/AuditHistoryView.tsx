import React from 'react';
import { History, Shield, CheckCircle2, MessageSquare, AlertTriangle } from 'lucide-react';
import { AuditLog } from '../../types';

interface AuditHistoryViewProps {
  logs: AuditLog[];
  isLoading: boolean;
}

export const AuditHistoryView: React.FC<AuditHistoryViewProps> = ({ logs, isLoading }) => {
  if (isLoading) {
    return (
      <div className="py-6 text-center text-xs text-slate-500">
        Loading audit events...
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="py-6 text-center text-xs text-slate-400">
        No audit logs recorded for this encounter yet.
      </div>
    );
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'ENCOUNTER_CREATED':
        return <Shield className="w-3.5 h-3.5 text-blue-600" />;
      case 'MESSAGE_PROCESSED':
        return <MessageSquare className="w-3.5 h-3.5 text-indigo-600" />;
      case 'RED_FLAG_TRIGGERED':
      case 'MANUAL_ESCALATION':
        return <AlertTriangle className="w-3.5 h-3.5 text-red-600" />;
      case 'STAFF_ACKNOWLEDGED':
        return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />;
      default:
        return <History className="w-3.5 h-3.5 text-slate-500" />;
    }
  };

  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {logs.map((log, idx) => (
          <li key={log.id}>
            <div className="relative pb-6">
              {idx !== logs.length - 1 && (
                <span
                  className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-slate-200"
                  aria-hidden="true"
                />
              )}
              <div className="relative flex space-x-3 items-start">
                <div className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center ring-4 ring-white shrink-0 border border-slate-200">
                  {getEventIcon(log.event_type)}
                </div>
                <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                  <div>
                    <p className="text-xs font-semibold text-slate-800">
                      {log.event_type.replace(/_/g, ' ')}
                    </p>
                    <div className="mt-1 text-[11px] text-slate-600 font-mono bg-slate-50 p-2 rounded border border-slate-200">
                      {JSON.stringify(log.details, null, 2)}
                    </div>
                  </div>
                  <div className="text-right text-[10px] whitespace-nowrap text-slate-400">
                    {new Date(log.created_at).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit',
                    })}
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};
