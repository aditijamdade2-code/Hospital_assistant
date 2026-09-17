'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Stethoscope, Lock, UserCircle2, AlertCircle, ShieldCheck, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

// Demo credentials — flexible matching for ease of use
const VALID_CREDENTIALS: Record<string, string> = {
  admin: '1234',
  nurse: '1234',
  nurse1: '1234',
  nurse01: '1234',
  nurse2: '1234',
  nurse02: '1234',
  doctor: '1234',
  doctor1: '1234',
  doctor01: '1234',
  doc: '1234',
  staff: '1234',
  staff01: '1234',
};

export default function StaffLoginPage() {
  const router = useRouter();
  const [staffId, setStaffId] = useState('');
  const [pin, setPin] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [shake, setShake] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const performLogin = async (id: string, enteredPin: string) => {
    setError(null);
    const cleanId = id.trim().toLowerCase();
    const cleanPin = enteredPin.trim();

    if (!cleanId || !cleanPin) {
      setError('Please enter both Staff ID and PIN.');
      triggerShake();
      return;
    }

    setIsLoading(true);
    await new Promise((r) => setTimeout(r, 300));

    // Valid if matched in credentials, or default PIN 1234 for any staff ID
    const isValid = VALID_CREDENTIALS[cleanId] === cleanPin || cleanPin === '1234';

    if (isValid) {
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('staff_authenticated', 'true');
        sessionStorage.setItem('staff_id', cleanId || 'nurse01');
      }
      router.push('/staff');
    } else {
      setError('Invalid Staff ID or PIN. Use PIN 1234.');
      triggerShake();
      setIsLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    await performLogin(staffId, pin);
  };

  const handleQuickLogin = async (roleId: string, rolePin: string = '1234') => {
    setStaffId(roleId);
    setPin(rolePin);
    await performLogin(roleId, rolePin);
  };

  const triggerShake = () => {
    setShake(true);
    setTimeout(() => setShake(false), 500);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900">
      {/* Subtle top bar */}
      <div className="bg-indigo-600/30 backdrop-blur-sm border-b border-indigo-500/20 px-4 py-2">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2 text-indigo-200 hover:text-white transition group">
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
            <span className="text-xs font-medium">Back to Home</span>
          </Link>
          <div className="flex items-center space-x-2 text-indigo-300 text-xs font-medium">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Authorized Personnel Only</span>
          </div>
        </div>
      </div>

      {/* Login Card */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className={`w-full max-w-md transition-transform ${shake ? 'animate-shake' : ''}`}>
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-indigo-600 shadow-2xl shadow-indigo-500/40 mb-5">
              <Stethoscope className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Staff Portal Login
            </h1>
            <p className="text-sm text-indigo-300 mt-1.5">
              OPD Clinical Triage Dashboard Access
            </p>
          </div>

          {/* Card */}
          <div className="bg-white/[0.07] backdrop-blur-xl rounded-2xl border border-white/10 p-8 shadow-2xl">
            <form onSubmit={handleLogin} className="space-y-5">
              {/* Staff ID */}
              <div>
                <label htmlFor="staffId" className="block text-xs font-semibold text-indigo-200 mb-2 uppercase tracking-wider">
                  Staff ID
                </label>
                <div className="relative">
                  <UserCircle2 className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-indigo-400" />
                  <input
                    id="staffId"
                    type="text"
                    value={staffId}
                    onChange={(e) => { setStaffId(e.target.value); setError(null); }}
                    placeholder="e.g. nurse1, doctor01, admin"
                    autoComplete="username"
                    className="w-full pl-12 pr-4 py-3 bg-white/[0.08] border border-white/10 rounded-xl text-white placeholder-indigo-400/60 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-400 transition"
                  />
                </div>
              </div>

              {/* PIN */}
              <div>
                <label htmlFor="pin" className="block text-xs font-semibold text-indigo-200 mb-2 uppercase tracking-wider">
                  PIN / Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-indigo-400" />
                  <input
                    id="pin"
                    type="password"
                    value={pin}
                    onChange={(e) => { setPin(e.target.value); setError(null); }}
                    placeholder="Enter PIN (e.g. 1234)"
                    autoComplete="current-password"
                    className="w-full pl-12 pr-4 py-3 bg-white/[0.08] border border-white/10 rounded-xl text-white placeholder-indigo-400/60 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-400 transition"
                  />
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="flex items-center space-x-2 bg-red-500/15 border border-red-500/30 text-red-300 text-xs font-medium px-4 py-2.5 rounded-xl">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 disabled:hover:bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-500/30 transition-all flex items-center justify-center space-x-2 cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Verifying...</span>
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    <span>Sign In & Access Dashboard</span>
                  </>
                )}
              </button>
            </form>

            {/* Quick 1-click Sign In Options */}
            <div className="mt-6 pt-5 border-t border-white/10 text-center space-y-3">
              <p className="text-[11px] text-indigo-400 font-medium uppercase tracking-wider">
                ⚡ 1-Click Quick Sign In
              </p>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => handleQuickLogin('nurse1', '1234')}
                  className="px-2 py-2 bg-white/[0.08] hover:bg-indigo-600/50 text-indigo-200 hover:text-white border border-white/10 rounded-xl text-xs font-semibold transition"
                >
                  👩‍⚕️ Nurse
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickLogin('doctor01', '1234')}
                  className="px-2 py-2 bg-white/[0.08] hover:bg-indigo-600/50 text-indigo-200 hover:text-white border border-white/10 rounded-xl text-xs font-semibold transition"
                >
                  👨‍⚕️ Doctor
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickLogin('admin', '1234')}
                  className="px-2 py-2 bg-white/[0.08] hover:bg-indigo-600/50 text-indigo-200 hover:text-white border border-white/10 rounded-xl text-xs font-semibold transition"
                >
                  🛡️ Admin
                </button>
              </div>
              <p className="text-[11px] text-slate-400">
                Any Staff ID with PIN <code className="text-indigo-300 font-mono">1234</code> will sign in.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Shake animation */}
      <style jsx>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-6px); }
          20%, 40%, 60%, 80% { transform: translateX(6px); }
        }
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
      `}</style>
    </div>
  );
}
