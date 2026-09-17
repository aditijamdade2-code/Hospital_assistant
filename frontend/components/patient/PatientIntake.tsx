'use client';

import React, { useState, useEffect } from 'react';
import { User, Calendar, Users, ArrowRight, Activity, Mic, MicOff, Volume2 } from 'lucide-react';
import { Language } from '../../types';
import { translations } from '../../lib/translations';
import { startSpeechRecognition, stopSpeechRecognition, isSpeechRecognitionSupported } from '../../lib/voice';

interface PatientIntakeProps {
  language: Language;
  onLanguageChange: (lang: Language) => void;
  onSubmit: (data: {
    patient_id?: string;
    age?: number;
    gender?: string;
    language: string;
    initial_complaint: string;
  }) => void;
  isLoading: boolean;
}

export const PatientIntake: React.FC<PatientIntakeProps> = ({
  language,
  onLanguageChange,
  onSubmit,
  isLoading,
}) => {
  const [patientId, setPatientId] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('Male');
  const [complaint, setComplaint] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [hasVoiceSupport, setHasVoiceSupport] = useState(true);

  const t = translations[language] || translations.en;

  useEffect(() => {
    setHasVoiceSupport(isSpeechRecognitionSupported());
  }, []);

  const handleToggleVoice = () => {
    if (isListening) {
      stopSpeechRecognition();
      setIsListening(false);
    } else {
      setVoiceError(null);
      setIsListening(true);
      startSpeechRecognition(
        language,
        (transcript, isFinal) => {
          setComplaint((prev) => {
            if (isFinal) {
              return prev ? `${prev} ${transcript}` : transcript;
            }
            return prev;
          });
        },
        (err) => {
          setVoiceError(err);
          setIsListening(false);
        },
        () => {
          setIsListening(false);
        }
      );
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaint.trim()) return;

    if (isListening) {
      stopSpeechRecognition();
      setIsListening(false);
    }

    onSubmit({
      patient_id: patientId.trim() || undefined,
      age: age ? parseInt(age, 10) : undefined,
      gender: gender || undefined,
      language,
      initial_complaint: complaint.trim(),
    });
  };

  return (
    <div className="max-w-xl mx-auto bg-white rounded-2xl shadow-xl shadow-slate-200/60 border border-slate-200/80 overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 px-6 py-8 text-white text-center relative overflow-hidden">
        <div className="w-14 h-14 mx-auto mb-3 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/20">
          <Activity className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight">{t.hospitalName}</h2>
        <p className="text-blue-100 text-sm mt-1">{t.opdAssistant}</p>
        <div className="mt-3 inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white/20 text-xs font-medium tracking-wide">
          <Volume2 className="w-3.5 h-3.5" />
          <span>Multilingual Voice Enabled (EN / HI / MR)</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-6">
        {/* Language Selection */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
            {t.selectLanguage}
          </label>
          <div className="grid grid-cols-3 gap-2">
            {(['en', 'hi', 'mr'] as Language[]).map((lang) => (
              <button
                type="button"
                key={lang}
                onClick={() => onLanguageChange(lang)}
                className={`py-2 px-3 rounded-lg text-sm font-medium border text-center transition-all ${
                  language === lang
                    ? 'border-blue-600 bg-blue-50/70 text-blue-700 font-semibold shadow-xs'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700'
                }`}
              >
                {lang === 'en' ? 'English' : lang === 'hi' ? 'हिंदी (Hindi)' : 'मराठी (Marathi)'}
              </button>
            ))}
          </div>
        </div>

        {/* Demographics */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-1">
            <label className="block text-xs font-medium text-slate-700 mb-1.5 flex items-center gap-1">
              <User className="w-3.5 h-3.5 text-slate-400" />
              <span>{t.patientId}</span>
            </label>
            <input
              type="text"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              placeholder="e.g. OPD-104"
              className="w-full text-sm px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
            <span className="text-[10px] text-slate-400 mt-1 block">({t.optional})</span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>{t.age}</span>
            </label>
            <input
              type="number"
              min="0"
              max="120"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Years"
              className="w-full text-sm px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5 flex items-center gap-1">
              <Users className="w-3.5 h-3.5 text-slate-400" />
              <span>{t.gender}</span>
            </label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="w-full text-sm px-3 py-2 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            >
              <option value="Male">{t.male}</option>
              <option value="Female">{t.female}</option>
              <option value="Other">{t.other}</option>
            </select>
          </div>
        </div>

        {/* Chief Complaint / Voice Input */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-sm font-semibold text-slate-800">
              {t.tellUsWhatHappened} <span className="text-red-500">*</span>
            </label>

            {/* Microphone Button on Intake Screen */}
            <button
              type="button"
              onClick={handleToggleVoice}
              className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all ${
                isListening
                  ? 'bg-red-500 text-white animate-pulse shadow-md shadow-red-500/30'
                  : 'bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100'
              }`}
            >
              {isListening ? (
                <>
                  <MicOff className="w-3.5 h-3.5" />
                  <span>Listening... Click to Stop</span>
                </>
              ) : (
                <>
                  <Mic className="w-3.5 h-3.5" />
                  <span>Speak Complaint</span>
                </>
              )}
            </button>
          </div>

          {voiceError && (
            <div className="text-xs text-red-600 bg-red-50 p-2 rounded-lg mb-2 border border-red-200">
              {voiceError}
            </div>
          )}

          <div className="relative">
            <textarea
              required
              rows={4}
              value={complaint}
              onChange={(e) => setComplaint(e.target.value)}
              placeholder={isListening ? "Listening to your voice... Speak now in your selected language..." : t.placeholderInput}
              className={`w-full text-sm p-3 rounded-xl border focus:outline-none focus:ring-2 resize-none transition-all ${
                isListening
                  ? 'border-red-400 ring-2 ring-red-500/20 bg-red-50/20'
                  : 'border-slate-300 focus:ring-blue-500/20 focus:border-blue-500'
              }`}
            />
          </div>

          <div className="flex flex-wrap gap-1.5 mt-2">
            <span className="text-[11px] text-slate-500">Quick examples:</span>
            <button
              type="button"
              onClick={() => setComplaint("My finger got cut with a knife and it's bleeding slightly.")}
              className="text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-0.5 rounded transition"
            >
              Minor Cut (EN)
            </button>
            <button
              type="button"
              onClick={() => {
                onLanguageChange('hi');
                setComplaint("मेरी उंगली कट गई है और थोड़ा खून आ रहा है।");
              }}
              className="text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-0.5 rounded transition"
            >
              उंगली कटी (HI)
            </button>
            <button
              type="button"
              onClick={() => {
                onLanguageChange('mr');
                setComplaint("माझ्या हातातून रक्त येत आहे.");
              }}
              className="text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-0.5 rounded transition"
            >
              रक्तस्त्राव (MR)
            </button>
            <button
              type="button"
              onClick={() => setComplaint("Severe chest pain and dizziness, cannot breathe!")}
              className="text-[11px] bg-red-50 hover:bg-red-100 text-red-700 px-2 py-0.5 rounded transition font-medium"
            >
              🚨 Red Flag Demo
            </button>
          </div>
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={isLoading || !complaint.trim()}
          className="w-full py-3.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-xl shadow-md shadow-blue-500/25 flex items-center justify-center space-x-2 transition-all"
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <span>{t.startEncounter}</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
