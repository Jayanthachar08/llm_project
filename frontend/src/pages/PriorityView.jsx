import React, { useState, useEffect } from 'react';
import { taskAPI } from '../services/api';
import { TrendingUp, Flame, HelpCircle, CheckCircle2, Clock, Sparkles } from 'lucide-react';

const PriorityView = () => {
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPriorities();
  }, []);

  const fetchPriorities = async () => {
    try {
      setLoading(true);
      const res = await taskAPI.getPriorities();
      setPriorities(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Task Prioritization Engine</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Dynamic prioritization using deterministic weighted scoring: P = (0.40 × U) + (0.25 × I) + (0.20 × D) + (0.15 × W)
        </p>
      </div>

      {/* Formula Explanation Card */}
      <div className="bg-indigo-50 border border-indigo-100 rounded-2xl p-5 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-indigo-900 font-bold text-xs uppercase tracking-wider">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Transparent Mathematical Formulation</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="bg-white p-3 rounded-xl border border-indigo-100">
            <span className="font-bold text-indigo-600 block">40% Deadline Urgency (U)</span>
            <span className="text-[11px] text-slate-500">Dynamically evaluated based on hours/days remaining</span>
          </div>
          <div className="bg-white p-3 rounded-xl border border-indigo-100">
            <span className="font-bold text-indigo-600 block">25% Importance (I)</span>
            <span className="text-[11px] text-slate-500">Critical (95), Important (75), Normal (50)</span>
          </div>
          <div className="bg-white p-3 rounded-xl border border-indigo-100">
            <span className="font-bold text-indigo-600 block">20% Difficulty (D)</span>
            <span className="text-[11px] text-slate-500">Difficult (85), Medium (60), Easy (35)</span>
          </div>
          <div className="bg-white p-3 rounded-xl border border-indigo-100">
            <span className="font-bold text-indigo-600 block">15% Workload (W)</span>
            <span className="text-[11px] text-slate-500">Estimated duration in hours required to complete</span>
          </div>
        </div>
      </div>

      {/* Priorities List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400 bg-white rounded-2xl border">Loading priority scores...</div>
        ) : priorities.length === 0 ? (
          <div className="p-12 text-center bg-white rounded-2xl border text-xs text-slate-500">
            No active tasks pending prioritization.
          </div>
        ) : (
          priorities.map((item, idx) => {
            const t = item.task;
            return (
              <div
                key={t.id}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3 hover:border-slate-300 transition"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                  <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-slate-100 text-slate-700 text-xs font-bold flex items-center justify-center">
                      #{idx + 1}
                    </span>
                    <h3 className="font-bold text-sm text-slate-900">{t.title}</h3>
                    {t.subject_name && (
                      <span className="bg-slate-100 text-slate-700 text-[10px] font-medium px-2 py-0.5 rounded-full">
                        {t.subject_name}
                      </span>
                    )}
                    <span className="text-[10px] bg-slate-100 text-slate-600 font-medium px-2 py-0.5 rounded-full capitalize">
                      {t.category}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2 self-start md:self-auto">
                    <span
                      className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                        item.priority_level === 'Critical'
                          ? 'bg-purple-100 text-purple-800 border border-purple-200'
                          : item.priority_level === 'High'
                          ? 'bg-rose-100 text-rose-700 border border-rose-200'
                          : item.priority_level === 'Medium'
                          ? 'bg-amber-100 text-amber-700 border border-amber-200'
                          : 'bg-slate-100 text-slate-600 border border-slate-200'
                      }`}
                    >
                      {item.priority_level} Priority ({item.priority_score.toFixed(1)}/100)
                    </span>
                  </div>
                </div>

                {/* Score Breakdown Bar */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 pt-1 text-xs">
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-400 block font-semibold uppercase">Urgency (0.40)</span>
                    <span className="font-bold text-slate-800">{item.urgency_score.toFixed(0)} / 100</span>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-400 block font-semibold uppercase">Importance (0.25)</span>
                    <span className="font-bold text-slate-800">{item.importance_score.toFixed(0)} ({t.importance})</span>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-400 block font-semibold uppercase">Difficulty (0.20)</span>
                    <span className="font-bold text-slate-800">{item.difficulty_score.toFixed(0)} ({t.difficulty})</span>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-400 block font-semibold uppercase">Workload (0.15)</span>
                    <span className="font-bold text-slate-800">{item.workload_score.toFixed(0)} ({t.estimated_duration}h)</span>
                  </div>
                </div>

                {/* Explanation text */}
                <p className="text-xs text-slate-600 bg-slate-50/70 p-3 rounded-xl border border-slate-100 italic">
                  {item.explanation}
                </p>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default PriorityView;
