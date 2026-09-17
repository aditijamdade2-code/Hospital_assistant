'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { User, Stethoscope, ArrowRight, ShieldAlert, Cpu, HeartPulse, Activity, Lock, ShieldCheck } from 'lucide-react';
import { Header } from '../components/common/Header';
import { Language } from '../types';

export default function Home() {
  const [lang, setLang] = useState<Language>('en');

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header language={lang} onLanguageChange={setLang} role="landing" />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-10 sm:py-16 space-y-12">
        {/* Hero */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-semibold">
            <Activity className="w-3.5 h-3.5" />
            <span>Phase 1 — Core Text MVP Operational</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Oscar Multispeciality Hospital
          </h1>
          <p className="text-sm sm:text-base font-semibold text-blue-700 tracking-tight uppercase">
            OPD Multilingual Assistant & Triage System
          </p>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
            An assistive clinical communication tool enabling patients to describe complaints in English, Hindi, or Marathi, extracting structured information without hallucination, and routing through deterministic hospital safety protocols.
          </p>
        </div>

        {/* Portals Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {/* Patient Portal Card */}
          <Link
            href="/patient"
            className="group relative bg-white rounded-2xl p-8 border border-slate-200/90 shadow-md hover:shadow-xl hover:border-blue-300 transition-all flex flex-col justify-between"
          >
            <div className="space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-lg shadow-blue-500/30 group-hover:scale-105 transition-transform">
                <User className="w-7 h-7" />
              </div>
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                  Open Patient Access
                </span>
                <h2 className="text-2xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors mt-2">
                  Patient Intake Portal
                </h2>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed">
                Simple, hospital-grade multilingual interface for patients. Enter complaints in English, Hindi, or Marathi, receive protocol follow-up questions, and view approved first-aid advice.
              </p>
              <ul className="text-xs text-slate-500 space-y-1.5 pt-2">
                <li>✓ Multi-language intake (EN, HI, MR)</li>
                <li>✓ Structured extraction without hallucination</li>
                <li>✓ Hospital-approved first-aid guidance</li>
              </ul>
            </div>

            <div className="mt-8 flex items-center text-sm font-semibold text-blue-600 group-hover:text-blue-700">
              <span>Enter as Patient</span>
              <ArrowRight className="w-4 h-4 ml-1.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          {/* Staff OPD Dashboard Card (Protected by Login) */}
          <Link
            href="/staff/login"
            className="group relative bg-white rounded-2xl p-8 border border-slate-200/90 shadow-md hover:shadow-xl hover:border-indigo-300 transition-all flex flex-col justify-between"
          >
            <div className="space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-indigo-600 text-white flex items-center justify-center shadow-lg shadow-indigo-500/30 group-hover:scale-105 transition-transform">
                <Lock className="w-7 h-7" />
              </div>
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded flex items-center w-fit space-x-1">
                  <ShieldCheck className="w-3 h-3" />
                  <span>Authorized Personnel Only</span>
                </span>
                <h2 className="text-2xl font-bold text-slate-900 group-hover:text-indigo-600 transition-colors mt-2">
                  Staff OPD Dashboard
                </h2>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed">
                Protected clinical workspace for doctors and triage nurses. Real-time queue, immediate red-flag escalations, clinical audit history, and direct patient communication.
              </p>
              <ul className="text-xs text-slate-500 space-y-1.5 pt-2">
                <li>🔒 Protected by Staff ID & Secure PIN</li>
                <li>✓ Real-time live queue monitoring</li>
                <li>✓ Protocol escalation acknowledgment</li>
              </ul>
            </div>

            <div className="mt-8 flex items-center text-sm font-semibold text-indigo-600 group-hover:text-indigo-700">
              <span>Staff Login</span>
              <ArrowRight className="w-4 h-4 ml-1.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        </div>

        {/* Safety & Architecture Pillars */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 max-w-4xl mx-auto shadow-xs">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
            System Architecture Principles
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs">
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold text-sm">
                <Cpu className="w-4 h-4 text-blue-600" />
                <span>Deterministic Rules</span>
              </div>
              <p className="text-slate-600 leading-relaxed">
                LLM does not diagnose or prescribe. Clinical protocols (P001–P008) and red-flag safety rules run deterministically.
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold text-sm">
                <ShieldAlert className="w-4 h-4 text-amber-600" />
                <span>Explainable Escalation</span>
              </div>
              <p className="text-slate-600 leading-relaxed">
                Every red flag logs the specific Rule ID, detected parameters, protocol version, and designated action for auditability.
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold text-sm">
                <HeartPulse className="w-4 h-4 text-emerald-600" />
                <span>Human-in-the-Loop</span>
              </div>
              <p className="text-slate-600 leading-relaxed">
                Assistive tool only. Final clinical assessment, medication orders, and triage triage remain with authorized hospital staff.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
