'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Stethoscope, RefreshCw, Radio, AlertOctagon,
  Filter, CheckCircle, Clock, ShieldAlert, AlertTriangle, LogOut
} from 'lucide-react';
import { Header } from '../../components/common/Header';
import { EncountersTable } from '../../components/staff/EncountersTable';
import { EncounterDetailDrawer } from '../../components/staff/EncounterDetailDrawer';
import { EncounterSummary, EncounterResponse, Priority } from '../../types';
import { listEncounters, getEncounter } from '../../lib/api';
import { staffWsClient } from '../../lib/websocket';

export default function StaffPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [staffId, setStaffId] = useState<string | null>(null);

  const [encounters, setEncounters] = useState<EncounterSummary[]>([]);
  const [selectedEncounter, setSelectedEncounter] = useState<EncounterResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [lastLiveEvent, setLastLiveEvent] = useState<string | null>(null);

  // Authentication Guard
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const auth = sessionStorage.getItem('staff_authenticated');
      const id = sessionStorage.getItem('staff_id');
      if (auth !== 'true') {
        router.replace('/staff/login');
      } else {
        setIsAuthenticated(true);
        setStaffId(id);
      }
    }
  }, [router]);

  const handleLogout = () => {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('staff_authenticated');
      sessionStorage.removeItem('staff_id');
    }
    router.replace('/staff/login');
  };

  const fetchEncounters = useCallback(async () => {
    try {
      const data = await listEncounters(priorityFilter || undefined);
      setEncounters(data);
    } catch (e) {
      console.error('Failed to list encounters:', e);
    } finally {
      setIsLoading(false);
    }
  }, [priorityFilter]);

  // Load encounters on mount & when filter changes (only if authenticated)
  useEffect(() => {
    if (!isAuthenticated) return;
    setIsLoading(true);
    fetchEncounters();
  }, [fetchEncounters, isAuthenticated]);

  // WebSocket Live Subscription (only if authenticated)
  useEffect(() => {
    if (!isAuthenticated) return;
    staffWsClient.connect();

    const unsubscribe = staffWsClient.subscribe((event, data) => {
      if (event === 'STATUS') {
        setWsConnected(data.connected);
      } else {
        setLastLiveEvent(`${event} at ${new Date().toLocaleTimeString()}`);
        // Automatically refresh table on any encounter change event
        fetchEncounters();

        // If the open drawer is for this encounter, refresh drawer too
        if (selectedId && data.encounter_id === selectedId) {
          getEncounter(selectedId).then(setSelectedEncounter).catch(console.error);
        }
      }
    });

    return () => {
      unsubscribe();
    };
  }, [fetchEncounters, selectedId, isAuthenticated]);

  const handleSelectEncounter = async (id: string) => {
    setSelectedId(id);
    try {
      const enc = await getEncounter(id);
      setSelectedEncounter(enc);
    } catch (e) {
      console.error('Failed to load encounter details:', e);
    }
  };

  const handleCloseDrawer = () => {
    setSelectedId(null);
    setSelectedEncounter(null);
  };

  // Metrics summary
  const immediateCount = encounters.filter(e => e.priority === 'IMMEDIATE_ESCALATION').length;
  const priorityCount = encounters.filter(e => e.priority === 'PRIORITY').length;
  const normalCount = encounters.filter(e => e.priority === 'NORMAL').length;

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-3 border-indigo-400/30 border-t-indigo-400 rounded-full animate-spin" />
          <p className="text-xs text-indigo-300 font-medium tracking-wide">Checking clinical authorization...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-100">
      <Header
        language="en"
        showLanguagePicker={false}
        role="staff"
        staffId={staffId}
        onLogout={handleLogout}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {/* Dashboard Title & Top Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                OPD Clinical Staff Triage Dashboard
              </h1>
              {/* WebSocket Status Indicator */}
              <div
                className={`inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                  wsConnected
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-amber-50 text-amber-700 border border-amber-200'
                }`}
              >
                <Radio className={`w-3 h-3 ${wsConnected ? 'animate-pulse text-emerald-600' : 'text-amber-600'}`} />
                <span>{wsConnected ? 'LIVE FEED' : 'RECONNECTING'}</span>
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Real-time monitoring of patient complaints, deterministic red-flag escalations, and first-aid triage.
              {lastLiveEvent && (
                <span className="ml-2 text-blue-600 font-mono">Last event: {lastLiveEvent}</span>
              )}
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => fetchEncounters()}
              className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-medium flex items-center space-x-1.5 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh Queue</span>
            </button>
            <button
              onClick={handleLogout}
              className="px-3 py-2 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded-xl text-xs font-medium flex items-center space-x-1.5 transition"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Logout</span>
            </button>
          </div>
        </div>

        {/* Priority KPI Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div
            onClick={() => setPriorityFilter('IMMEDIATE_ESCALATION')}
            className={`cursor-pointer p-4 rounded-xl border transition-all ${
              priorityFilter === 'IMMEDIATE_ESCALATION'
                ? 'bg-red-50 border-red-400 ring-2 ring-red-500/20 shadow-sm'
                : 'bg-white border-slate-200 hover:border-red-300'
            }`}
          >
            <div className="flex items-center justify-between text-red-600">
              <span className="text-xs font-bold uppercase tracking-wider">Immediate Escalation</span>
              <AlertOctagon className="w-5 h-5" />
            </div>
            <div className="text-2xl font-black text-slate-900 mt-2">{immediateCount}</div>
            <p className="text-[11px] text-slate-500 mt-0.5">Arterial / Anaphylaxis / Cardiac</p>
          </div>

          <div
            onClick={() => setPriorityFilter('PRIORITY')}
            className={`cursor-pointer p-4 rounded-xl border transition-all ${
              priorityFilter === 'PRIORITY'
                ? 'bg-amber-50 border-amber-400 ring-2 ring-amber-500/20 shadow-sm'
                : 'bg-white border-slate-200 hover:border-amber-300'
            }`}
          >
            <div className="flex items-center justify-between text-amber-600">
              <span className="text-xs font-bold uppercase tracking-wider">Priority Care</span>
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="text-2xl font-black text-slate-900 mt-2">{priorityCount}</div>
            <p className="text-[11px] text-slate-500 mt-0.5">Urgent assessment queue</p>
          </div>

          <div
            onClick={() => setPriorityFilter('NORMAL')}
            className={`cursor-pointer p-4 rounded-xl border transition-all ${
              priorityFilter === 'NORMAL'
                ? 'bg-emerald-50 border-emerald-400 ring-2 ring-emerald-500/20 shadow-sm'
                : 'bg-white border-slate-200 hover:border-emerald-300'
            }`}
          >
            <div className="flex items-center justify-between text-emerald-600">
              <span className="text-xs font-bold uppercase tracking-wider">Normal OPD</span>
              <CheckCircle className="w-5 h-5" />
            </div>
            <div className="text-2xl font-black text-slate-900 mt-2">{normalCount}</div>
            <p className="text-[11px] text-slate-500 mt-0.5">Standard first-aid & waitlist</p>
          </div>

          <div
            onClick={() => setPriorityFilter('')}
            className={`cursor-pointer p-4 rounded-xl border transition-all ${
              priorityFilter === ''
                ? 'bg-blue-50 border-blue-400 ring-2 ring-blue-500/20 shadow-sm'
                : 'bg-white border-slate-200 hover:border-blue-300'
            }`}
          >
            <div className="flex items-center justify-between text-blue-600">
              <span className="text-xs font-bold uppercase tracking-wider">Total Active</span>
              <Filter className="w-5 h-5" />
            </div>
            <div className="text-2xl font-black text-slate-900 mt-2">{encounters.length}</div>
            <p className="text-[11px] text-slate-500 mt-0.5">Click to show all cases</p>
          </div>
        </div>

        {/* Encounters Table */}
        <EncountersTable
          encounters={encounters}
          selectedEncounterId={selectedId}
          onSelectEncounter={handleSelectEncounter}
          isLoading={isLoading}
        />

        {/* Detailed Inspection Drawer */}
        {selectedEncounter && (
          <EncounterDetailDrawer
            encounter={selectedEncounter}
            onClose={handleCloseDrawer}
            onRefresh={fetchEncounters}
          />
        )}
      </main>
    </div>
  );
}
