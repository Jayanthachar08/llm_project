import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI, plannerAPI } from '../services/api';
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  Flame,
  Calendar,
  BookOpen,
  ArrowRight,
  Sparkles,
  RefreshCw,
  PlusCircle,
  TrendingUp
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const res = await dashboardAPI.getSummary();
      setSummary(res.data);
    } catch (e) {
      console.error('Error fetching dashboard summary:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePlan = async () => {
    try {
      setGenerating(true);
      await plannerAPI.generatePlan();
      await fetchSummary();
    } catch (e) {
      console.error('Error generating plan:', e);
    } finally {
      setGenerating(false);
    }
  };

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const pieData = [
    { name: 'Completed', value: summary?.completed_tasks || 0, color: '#10b981' },
    { name: 'In Progress', value: summary?.in_progress_tasks || 0, color: '#6366f1' },
    { name: 'Not Started', value: Math.max(0, (summary?.pending_tasks || 0) - (summary?.in_progress_tasks || 0)), color: '#cbd5e1' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Actions */}
      <div className="bg-gradient-to-r from-indigo-700 via-indigo-600 to-indigo-800 rounded-2xl p-6 text-white shadow-xl shadow-indigo-100 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-200 text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Academic Command Center</span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight">
            Academic Schedule & Study Intelligence
          </h1>
          <p className="text-xs text-indigo-100 mt-1 max-w-xl">
            Automating deadline extraction, deterministic task prioritization, conflict alerts, and dynamic study timetable generation.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Link
            to="/upload"
            className="px-4 py-2 bg-white text-indigo-700 hover:bg-indigo-50 font-semibold text-xs rounded-xl shadow-sm transition flex items-center space-x-1.5"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Upload Notice</span>
          </Link>
          <button
            onClick={handleGeneratePlan}
            disabled={generating}
            className="px-4 py-2 bg-indigo-500 hover:bg-indigo-400 text-white font-semibold text-xs rounded-xl transition flex items-center space-x-1.5 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
            <span>{generating ? 'Calculating...' : 'Generate Plan'}</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium text-slate-500">Total Tasks</span>
            <BookOpen className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{summary?.total_tasks || 0}</div>
          <p className="text-[11px] text-slate-400 mt-1">
            {summary?.completed_tasks || 0} completed ({summary?.completion_percentage || 0}%)
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium text-slate-500">High Priority</span>
            <Flame className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{summary?.high_priority_count || 0}</div>
          <p className="text-[11px] text-rose-500 font-medium mt-1">Requires immediate study</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium text-slate-500">Upcoming (7d)</span>
            <Calendar className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{summary?.upcoming_deadlines_count || 0}</div>
          <p className="text-[11px] text-slate-400 mt-1">Deadlines in next 7 days</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium text-slate-500">Active Conflicts</span>
            <AlertTriangle className={`w-4 h-4 ${(summary?.active_conflicts_count || 0) > 0 ? 'text-rose-500' : 'text-emerald-500'}`} />
          </div>
          <div className="text-2xl font-bold text-slate-900">{summary?.active_conflicts_count || 0}</div>
          <p className={`text-[11px] font-medium mt-1 ${(summary?.active_conflicts_count || 0) > 0 ? 'text-rose-500' : 'text-emerald-600'}`}>
            {(summary?.active_conflicts_count || 0) > 0 ? 'Action required' : 'No schedule clashes'}
          </p>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 spans): High Priority Tasks & Today's Study Sessions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Conflict Warning Banner if any */}
          {(summary?.conflicts?.length || 0) > 0 && (
            <div className="bg-rose-50 border border-rose-200 rounded-2xl p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2 text-rose-800 font-bold text-sm">
                  <AlertTriangle className="w-4 h-4 text-rose-600" />
                  <span>{summary.conflicts.length} Academic Schedule Conflicts Detected</span>
                </div>
                <Link to="/conflicts" className="text-xs text-rose-700 hover:underline font-semibold flex items-center space-x-1">
                  <span>View All</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
              <p className="text-xs text-rose-700 mb-2">
                {summary.conflicts[0].title}: {summary.conflicts[0].description}
              </p>
              <div className="text-[11px] text-rose-600 font-medium">
                Recommendation: {summary.conflicts[0].suggested_action}
              </div>
            </div>
          )}

          {/* High Priority Tasks */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-slate-900 text-sm">High Priority Responsibilities</h3>
                <p className="text-xs text-slate-500">Evaluated using P = 0.40U + 0.25I + 0.20D + 0.15W</p>
              </div>
              <Link to="/priorities" className="text-xs text-indigo-600 hover:underline font-semibold flex items-center space-x-1">
                <span>Priority breakdown</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {(!summary?.high_priority_tasks || summary.high_priority_tasks.length === 0) ? (
              <p className="text-xs text-slate-500 py-6 text-center">No high priority tasks pending. You're on track!</p>
            ) : (
              <div className="space-y-3">
                {summary.high_priority_tasks.map((task) => (
                  <div key={task.id} className="p-3.5 rounded-xl border border-slate-100 hover:border-slate-200 bg-slate-50/50 flex items-center justify-between transition">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-xs text-slate-900">{task.title}</span>
                        <span className="bg-rose-100 text-rose-700 text-[10px] font-bold px-2 py-0.5 rounded-full">
                          Score {task.priority_score?.toFixed(1)}
                        </span>
                        {task.subject_name && (
                          <span className="bg-slate-200 text-slate-700 text-[10px] px-2 py-0.5 rounded-full">
                            {task.subject_name}
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-500">
                        {task.deadline ? `Deadline: ${new Date(task.deadline).toLocaleDateString()}` : (task.event_date ? `Event: ${new Date(task.event_date).toLocaleDateString()}` : 'No date set')} • Duration: {task.estimated_duration}h
                      </p>
                    </div>
                    <Link to="/tasks" className="text-xs text-indigo-600 hover:underline font-semibold">
                      Manage
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Today's Study Sessions */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Today's Study Plan</h3>
                <p className="text-xs text-slate-500">Generated around your available study hours and college timetable</p>
              </div>
              <Link to="/planner" className="text-xs text-indigo-600 hover:underline font-semibold flex items-center space-x-1">
                <span>Full Timetable</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {(!summary?.today_sessions || summary.today_sessions.length === 0) ? (
              <div className="text-center py-6">
                <Clock className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="text-xs text-slate-500">No study sessions scheduled for today.</p>
                <button
                  onClick={handleGeneratePlan}
                  className="mt-3 text-xs bg-indigo-50 text-indigo-700 font-semibold px-3 py-1.5 rounded-lg hover:bg-indigo-100 transition"
                >
                  Generate Study Plan
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {summary.today_sessions.map((s) => (
                  <div key={s.id} className="p-3.5 rounded-xl border border-indigo-100 bg-indigo-50/30 flex items-start space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                      {s.start_time}
                    </div>
                    <div>
                      <h4 className="text-xs font-semibold text-slate-900">{s.task_title || 'Study Block'}</h4>
                      <p className="text-[11px] text-slate-500">
                        {s.start_time} - {s.end_time} ({s.duration} min) • {s.subject_name || 'General'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Workload Progress & Subject Breakdown */}
        <div className="space-y-6">
          {/* Workload Progress Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <h3 className="font-bold text-slate-900 text-sm mb-1">Completion Progress</h3>
            <p className="text-xs text-slate-500 mb-4">Academic tasks completion overview</p>

            <div className="flex items-center justify-center h-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-slate-100">
              <div>
                <span className="block text-emerald-600 font-bold text-sm">{summary?.completed_tasks || 0}</span>
                <span className="text-[10px] text-slate-400">Completed</span>
              </div>
              <div>
                <span className="block text-indigo-600 font-bold text-sm">{summary?.in_progress_tasks || 0}</span>
                <span className="text-[10px] text-slate-400">In Progress</span>
              </div>
              <div>
                <span className="block text-slate-600 font-bold text-sm">
                  {Math.max(0, (summary?.pending_tasks || 0) - (summary?.in_progress_tasks || 0))}
                </span>
                <span className="text-[10px] text-slate-400">Not Started</span>
              </div>
            </div>
          </div>

          {/* Subject Breakdown */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <h3 className="font-bold text-slate-900 text-sm mb-1">Subject-wise Workload</h3>
            <p className="text-xs text-slate-500 mb-4">Progress per enrolled course</p>

            {(!summary?.subject_progress || summary.subject_progress.length === 0) ? (
              <p className="text-xs text-slate-400 text-center py-4">No subjects registered yet.</p>
            ) : (
              <div className="space-y-3">
                {summary.subject_progress.map((subj) => (
                  <div key={subj.subject_id || subj.subject_name} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium text-slate-800">
                      <span>{subj.subject_name}</span>
                      <span className="text-slate-500">{subj.completed_tasks} / {subj.total_tasks} ({subj.completion_percentage}%)</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-indigo-600 h-1.5 rounded-full transition-all"
                        style={{ width: `${subj.completion_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
