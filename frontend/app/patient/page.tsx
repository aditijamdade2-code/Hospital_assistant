'use client';

import React, { useState, useEffect, useRef } from 'react';
import { RotateCcw, AlertOctagon, UserCheck, Bell } from 'lucide-react';
import { Header } from '../../components/common/Header';
import { PatientIntake } from '../../components/patient/PatientIntake';
import { ChatWindow } from '../../components/patient/ChatWindow';
import { StatusBanner } from '../../components/patient/StatusBanner';
import { EncounterResponse, Message, Language } from '../../types';
import { createEncounter, postPatientMessage, getConversation, getEncounter } from '../../lib/api';
import { translations } from '../../lib/translations';
import { staffWsClient } from '../../lib/websocket';

export default function PatientPage() {
  const [language, setLanguage] = useState<Language>('en');
  const [encounter, setEncounter] = useState<EncounterResponse | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [staffNotification, setStaffNotification] = useState<string | null>(null);
  const t = translations[language] || translations.en;

  // Restore active encounter from localStorage on initial mount (no refresh data loss)
  useEffect(() => {
    const savedId = typeof window !== 'undefined' ? localStorage.getItem('opd_active_encounter_id') : null;
    const savedLang = (typeof window !== 'undefined' ? localStorage.getItem('opd_active_language') : null) as Language | null;

    if (savedLang) {
      setLanguage(savedLang);
    }

    if (savedId) {
      setIsLoading(true);
      Promise.all([
        getEncounter(savedId),
        getConversation(savedId)
      ])
        .then(([enc, conv]) => {
          setEncounter(enc);
          setMessages(conv.messages);
          if (enc.language) {
            setLanguage(enc.language as Language);
          }
        })
        .catch((err) => {
          console.warn('Could not restore previous encounter:', err);
          localStorage.removeItem('opd_active_encounter_id');
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, []);

  // Real-time WebSocket listener: when staff acknowledges or sends guidance, update patient chat live!
  useEffect(() => {
    staffWsClient.connect();

    const unsubscribe = staffWsClient.subscribe((event, data) => {
      if (!encounter || !data) return;

      // Check if this event pertains to this patient's active encounter
      if (data.encounter_id === encounter.encounter_id) {
        if (event === 'STAFF_ACKNOWLEDGED') {
          setStaffNotification(
            data.notes
              ? `👨‍⚕️ Clinical staff acknowledged: "${data.notes}"`
              : '👨‍⚕️ Clinical staff has reviewed and acknowledged your case file.'
          );
          // Instantly refresh conversation and encounter data without patient refreshing!
          Promise.all([
            getConversation(encounter.encounter_id),
            getEncounter(encounter.encounter_id)
          ]).then(([conv, updatedEnc]) => {
            setMessages(conv.messages);
            setEncounter(updatedEnc);
          }).catch(console.error);
        } else if (event === 'STAFF_GUIDANCE') {
          setStaffNotification('👨‍⚕️ New clinical instructions received from hospital staff!');
          Promise.all([
            getConversation(encounter.encounter_id),
            getEncounter(encounter.encounter_id)
          ]).then(([conv, updatedEnc]) => {
            setMessages(conv.messages);
            setEncounter(updatedEnc);
          }).catch(console.error);
        } else if (event === 'ENCOUNTER_UPDATED' || event === 'PRIORITY_CHANGED' || event === 'ESCALATION_TRIGGERED') {
          getEncounter(encounter.encounter_id).then(setEncounter).catch(console.error);
        }
      }
    });

    return () => {
      unsubscribe();
    };
  }, [encounter?.encounter_id]);

  const handleStartEncounter = async (data: {
    patient_id?: string;
    age?: number;
    gender?: string;
    language: string;
    initial_complaint: string;
  }) => {
    setIsLoading(true);
    try {
      const created = await createEncounter(data);
      setEncounter(created);

      // Persist in localStorage so page reload doesn't wipe patient session
      if (typeof window !== 'undefined') {
        localStorage.setItem('opd_active_encounter_id', created.encounter_id);
        localStorage.setItem('opd_active_language', data.language);
      }

      // Fetch the conversation containing initial complaint + assistant reply
      const convData = await getConversation(created.encounter_id);
      setMessages(convData.messages);

      // Refresh encounter state to get latest priority & extracted fields
      const refreshed = await getEncounter(created.encounter_id);
      setEncounter(refreshed);
    } catch (e: any) {
      alert(`Error starting encounter: ${e.message || e}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!encounter) return;
    setIsLoading(true);
    try {
      await postPatientMessage(encounter.encounter_id, text, language);

      // Refresh conversation & encounter details
      const [convData, refreshedEnc] = await Promise.all([
        getConversation(encounter.encounter_id),
        getEncounter(encounter.encounter_id),
      ]);
      setMessages(convData.messages);
      setEncounter(refreshedEnc);
    } catch (e: any) {
      alert(`Error sending message: ${e.message || e}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('opd_active_encounter_id');
    }
    setEncounter(null);
    setMessages([]);
    setStaffNotification(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-100">
      <Header
        language={language}
        onLanguageChange={setLanguage}
        showLanguagePicker={!encounter}
        role="patient"
      />

      <main className="flex-1 max-w-4xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {!encounter ? (
          <PatientIntake
            language={language}
            onLanguageChange={setLanguage}
            onSubmit={handleStartEncounter}
            isLoading={isLoading}
          />
        ) : (
          <div className="space-y-4">
            {/* Top Bar for Active Encounter */}
            <div className="flex items-center justify-between">
              <div className="text-xs text-slate-500 font-medium">
                {t.activeEncounter}: <span className="font-mono font-bold text-slate-800">{encounter.encounter_id}</span>
                {encounter.patient.patient_id && ` (${encounter.patient.patient_id})`}
              </div>
              <button
                onClick={handleReset}
                className="flex items-center space-x-1 text-xs text-slate-600 hover:text-slate-900 bg-white px-2.5 py-1.5 rounded-lg border border-slate-200 shadow-xs transition"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>{t.reset}</span>
              </button>
            </div>

            {/* Live Encounter Status Banner */}
            <StatusBanner
              status={encounter.status}
              priority={encounter.priority}
              encounterId={encounter.encounter_id}
              language={language}
            />

            {/* Live Staff Acknowledgment & Guidance Banner */}
            {staffNotification && (
              <div className="bg-emerald-600 text-white px-4 py-3 rounded-xl shadow-md flex items-center justify-between border border-emerald-500 animate-fade-in">
                <div className="flex items-center space-x-2.5">
                  <UserCheck className="w-5 h-5 text-emerald-100 shrink-0" />
                  <span className="text-xs sm:text-sm font-medium">{staffNotification}</span>
                </div>
                <button
                  onClick={() => setStaffNotification(null)}
                  className="text-emerald-100 hover:text-white text-xs font-bold px-2 py-1 rounded hover:bg-emerald-700 transition ml-2"
                >
                  Dismiss
                </button>
              </div>
            )}

            {/* Conversation Window */}
            <ChatWindow
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              priority={encounter.priority}
              isEscalated={encounter.escalation_required}
              language={language}
            />
          </div>
        )}
      </main>
    </div>
  );
}
