import React, { useState, useEffect } from 'react';
import { plannerAPI } from '../services/api';
import { AlertTriangle, RefreshCw, CheckCircle2, ShieldAlert, ArrowRight } from 'lucide-react';

const ConflictAlerts = () => {
  const [conflicts, setConflicts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchConflicts();
  }, []);

  const fetchConflicts = async () => {
    try {
      setLoading(true);
      const res = await plannerAPI.getConflicts();
      setConflicts(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAutoResolve = async () => {
    try {
      setResolving(true);
      setSuccessMessage('');
      await plannerAPI.generatePlan({ preserve_completed: true });
      await fetchConflicts();
      setSuccessMessage('Dynamic rescheduling engine ran successfully to re-align study sessions.');
    } catch (e) {
      console.error(e);
    } finally {
      setResolving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Scheduling Conflict Detection</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated conflict engine detects session overlaps, competing deadlines, and insufficient study time.
          </p>
        </div>

        {conflicts.length > 0 && (
          <button
            onClick={handleAutoResolve}
            disabled={resolving}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow-sm flex items-center space-x-1.5 transition self-start disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${resolving ? 'animate-spin' : ''}`} />
            <span>{resolving ? 'Re-aligning Sessions...' : 'Auto-Resolve with Rescheduling'}</span>
          </button>
        )}
      </div>

      {successMessage && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center space-x-2 text-emerald-800 text-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400 bg-white rounded-2xl border">Analyzing schedule conflicts...</div>
      ) : conflicts.length === 0 ? (
        <div className="bg-white rounded-2xl border border-emerald-200 p-8 text-center space-y-2 shadow-sm">
          <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-2">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-slate-900 text-sm">All Academic Schedules Are Feasible!</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            No session overlaps, competing deadline bottlenecks, or college hour collisions detected.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {conflicts.map((c, idx) => (
            <div
              key={idx}
              className="bg-white rounded-2xl border border-rose-200 p-5 shadow-sm space-y-3 hover:border-rose-300 transition"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                <div className="flex items-center space-x-2">
                  <ShieldAlert className="w-5 h-5 text-rose-600" />
                  <h3 className="font-bold text-sm text-slate-900">{c.title}</h3>
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-rose-100 text-rose-700 px-2 py-0.5 rounded-full">
                    {c.severity} Severity
                  </span>
                </div>
                <span className="text-xs font-semibold text-slate-500 capitalize">
                  Type: {c.conflict_type.replace('_', ' ')}
                </span>
              </div>

              <p className="text-xs text-slate-700 leading-relaxed">{c.description}</p>

              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 flex items-start space-x-2 text-xs">
                <span className="font-bold text-indigo-700 flex-shrink-0">Recommendation:</span>
                <span className="text-slate-600">{c.suggested_action}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConflictAlerts;
