import React, { useState, useEffect } from 'react';
import { plannerAPI, taskAPI } from '../services/api';
import {
  Clock,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Calendar,
  Layers,
  Settings2
} from 'lucide-react';

const StudyPlanner = () => {
  const [sessions, setSessions] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [sessionDuration, setSessionDuration] = useState(60);
  const [breakDuration, setBreakDuration] = useState(15);
  const [horizonDays, setHorizonDays] = useState(14);
  const [reschedulingTaskId, setReschedulingTaskId] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchPlannerData();
  }, []);

  const fetchPlannerData = async () => {
    try {
      setLoading(true);
      const calendarRes = await plannerAPI.getCalendar();
      const studySessions = (calendarRes.data || [])
        .filter((e) => e.event_type === 'study_session')
        .map((e) => ({
          id: e.id.replace('session-', ''),
          task_title: e.title.replace('Study: ', ''),
          start: e.start,
          end: e.end,
          status: e.status,
          subject: e.subject
        }));
      setSessions(studySessions);

      const taskRes = await taskAPI.getTasks({ status: 'Not Started' });
      setTasks(taskRes.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePlan = async () => {
    try {
      setGenerating(true);
      setMessage('');
      const res = await plannerAPI.generatePlan({
        session_duration: parseInt(sessionDuration),
        break_duration: parseInt(breakDuration),
        horizon_days: parseInt(horizonDays),
        preserve_completed: true
      });
      setWarnings(res.data.warnings || []);
      setMessage(res.data.message || 'Personalized study timetable generated successfully.');
      await fetchPlannerData();
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const handleDynamicReschedule = async () => {
    if (!reschedulingTaskId) return;
    try {
      setGenerating(true);
      setMessage('');
      const res = await plannerAPI.reschedule(parseInt(reschedulingTaskId));
      setMessage('Dynamic Rescheduling complete: Completed sessions preserved, affected timetable updated.');
      await fetchPlannerData();
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const handleMarkSessionComplete = async (sessionId) => {
    try {
      await plannerAPI.updateSession(sessionId, { status: 'completed' });
      fetchPlannerData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Personalized Study Planner</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Deterministic priority-first study timetable tailored to your college hours, deadlines, and break preferences.
          </p>
        </div>

        <button
          onClick={handleGeneratePlan}
          disabled={generating}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-indigo-100 flex items-center space-x-2 transition self-start disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
          <span>{generating ? 'Calculating Timetable...' : 'Generate New Plan'}</span>
        </button>
      </div>

      {message && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center space-x-2 text-emerald-800 text-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {warnings.length > 0 && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl space-y-2 text-xs text-amber-800">
          <div className="flex items-center space-x-2 font-bold">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>Infeasibility Warnings Detected</span>
          </div>
          <ul className="list-disc pl-5 space-y-1 text-slate-700">
            {warnings.map((w, idx) => (
              <li key={idx}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Scheduler Controls */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">Session Duration</label>
          <select
            value={sessionDuration}
            onChange={(e) => setSessionDuration(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none bg-white"
          >
            <option value={45}>45 Minutes</option>
            <option value={60}>60 Minutes (Standard)</option>
            <option value={90}>90 Minutes (Deep Work)</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">Break Duration</label>
          <select
            value={breakDuration}
            onChange={(e) => setBreakDuration(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none bg-white"
          >
            <option value={10}>10 Minutes Gap</option>
            <option value={15}>15 Minutes Gap (Recommended)</option>
            <option value={20}>20 Minutes Gap</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">Horizon Window</label>
          <select
            value={horizonDays}
            onChange={(e) => setHorizonDays(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none bg-white"
          >
            <option value={7}>Next 7 Days (1 Week)</option>
            <option value={14}>Next 14 Days (2 Weeks)</option>
            <option value={30}>Next 30 Days (Month)</option>
          </select>
        </div>

        {/* Dynamic Reschedule dropdown */}
        <div className="flex space-x-2">
          <select
            value={reschedulingTaskId}
            onChange={(e) => setReschedulingTaskId(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none bg-white"
          >
            <option value="">Reschedule Task...</option>
            {tasks.map((t) => (
              <option key={t.id} value={t.id}>{t.title}</option>
            ))}
          </select>
          <button
            onClick={handleDynamicReschedule}
            disabled={!reschedulingTaskId || generating}
            className="px-3 py-2 bg-slate-800 text-white rounded-xl text-xs font-semibold hover:bg-slate-700 transition disabled:opacity-40"
          >
            Update
          </button>
        </div>
      </div>

      {/* Sessions Grid */}
      <div className="space-y-4">
        <h3 className="font-bold text-sm text-slate-900">Scheduled Study Blocks ({sessions.length})</h3>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400 bg-white rounded-2xl border">Loading study sessions...</div>
        ) : sessions.length === 0 ? (
          <div className="p-12 text-center bg-white rounded-2xl border text-xs text-slate-500">
            No study sessions generated. Click 'Generate New Plan' above to allocate study slots!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {sessions.map((s) => (
              <div
                key={s.id}
                className={`p-4 rounded-2xl border shadow-sm space-y-3 transition ${
                  s.status === 'completed'
                    ? 'bg-emerald-50/40 border-emerald-200'
                    : 'bg-white border-slate-200 hover:border-indigo-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full">
                    {s.subject || 'General Course'}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full capitalize ${
                      s.status === 'completed' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {s.status}
                  </span>
                </div>

                <h4 className="font-semibold text-xs text-slate-900 leading-snug">{s.task_title}</h4>

                <div className="text-[11px] text-slate-500 space-y-1 pt-1 border-t border-slate-100">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>{new Date(s.start.split('T')[0] + 'T00:00:00').toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>{s.start.split('T')[1].substring(0, 5)} - {s.end.split('T')[1].substring(0, 5)}</span>
                  </div>
                </div>

                {s.status !== 'completed' && (
                  <button
                    onClick={() => handleMarkSessionComplete(s.id)}
                    className="w-full py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-xl flex items-center justify-center space-x-1 transition"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Mark Completed</span>
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudyPlanner;
