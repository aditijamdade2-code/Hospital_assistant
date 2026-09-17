'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Activity, ShieldAlert, User, Stethoscope, Globe2, LogOut, ArrowLeft } from 'lucide-react';
import { Language } from '../../types';
import { translations } from '../../lib/translations';

interface HeaderProps {
  language: Language;
  onLanguageChange?: (lang: Language) => void;
  showLanguagePicker?: boolean;
  role?: 'patient' | 'staff' | 'landing';
  staffId?: string | null;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  language,
  onLanguageChange,
  showLanguagePicker = true,
  role = 'landing',
  staffId,
  onLogout,
}) => {
  const pathname = usePathname();
  const router = useRouter();
  const t = translations[language] || translations.en;

  const handleDefaultLogout = () => {
    if (onLogout) {
      onLogout();
    } else {
      if (typeof window !== 'undefined') {
        sessionStorage.removeItem('staff_authenticated');
        sessionStorage.removeItem('staff_id');
      }
      router.push('/staff/login');
    }
  };

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Hospital Logo & Brand */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <Activity className="w-6 h-6 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-900 leading-tight tracking-tight">
                  {t.hospitalName}
                </span>
                <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-1.5 py-0.5 rounded tracking-wide">
                  OPD
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                {t.opdAssistant}
              </p>
            </div>
          </Link>

          {/* Navigation Links & Controls */}
          <div className="flex items-center space-x-3 sm:space-x-4">
            <nav className="flex items-center space-x-1 sm:space-x-2 mr-2">
              {/* If patient: Show Back to Home button + Patient Portal label */}
              {role === 'patient' && (
                <div className="flex items-center space-x-2">
                  <Link
                    href="/"
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-blue-700 bg-slate-100 hover:bg-blue-50 border border-slate-200 hover:border-blue-300 transition-colors shadow-2xs group"
                  >
                    <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
                    <span>{t.backToHome || "Back to Home"}</span>
                  </Link>
                  <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold bg-blue-50 text-blue-700">
                    <User className="w-4 h-4" />
                    <span>Patient Intake Portal</span>
                  </div>
                </div>
              )}

              {/* If staff: Show Back to Home button + Staff OPD badge + Logout button */}
              {role === 'staff' && (
                <div className="flex items-center space-x-2">
                  <Link
                    href="/"
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-indigo-700 bg-slate-100 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-300 transition-colors shadow-2xs group"
                  >
                    <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
                    <span>Back to Home</span>
                  </Link>
                  <div className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold bg-indigo-50 text-indigo-700">
                    <Stethoscope className="w-4 h-4" />
                    <span>Staff OPD Dashboard</span>
                  </div>
                  {staffId && (
                    <span className="hidden sm:inline-block text-xs font-mono font-semibold text-slate-500 bg-slate-100 px-2 py-1 rounded-md">
                      ID: {staffId}
                    </span>
                  )}
                  <button
                    onClick={handleDefaultLogout}
                    title="Sign Out"
                    className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 transition border border-red-200"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">Logout</span>
                  </button>
                </div>
              )}

              {/* If landing page, provide quick navigation or role links */}
              {role === 'landing' && (
                <div className="flex items-center space-x-2">
                  <Link
                    href="/patient"
                    className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                      pathname === '/patient'
                        ? 'bg-blue-50 text-blue-700 font-semibold'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    <User className="w-4 h-4" />
                    <span>Patient Intake</span>
                  </Link>
                  <Link
                    href="/staff/login"
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 transition-colors border border-indigo-200"
                  >
                    <Stethoscope className="w-4 h-4" />
                    <span>Staff Login</span>
                  </Link>
                </div>
              )}
            </nav>

            {/* Language Switcher */}
            {showLanguagePicker && onLanguageChange && (
              <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
                <Globe2 className="w-3.5 h-3.5 text-slate-500 ml-1 mr-0.5 hidden sm:inline" />
                {(['en', 'hi', 'mr'] as Language[]).map((lang) => (
                  <button
                    key={lang}
                    onClick={() => onLanguageChange(lang)}
                    className={`px-2 py-1 text-xs rounded font-medium transition-all ${
                      language === lang
                        ? 'bg-white text-blue-700 shadow-xs font-semibold'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    {lang === 'en' ? 'EN' : lang === 'hi' ? 'हिंदी' : 'मराठी'}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

