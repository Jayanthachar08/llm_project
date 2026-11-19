import React, { useState, useEffect } from 'react';
import { progressAPI, dashboardAPI } from '../services/api';
import { BarChart3, CheckCircle2, Clock, BookOpen, AlertTriangle, Flame } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';

const ProgressTracking = () => {
  const [summary, setSummary] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sumRes, subjRes] = await Promise.all([
        progressAPI.getSummary().catch(() => dashboardAPI.getSummary()),
        progressAPI.getSubjects().catch(() => ({ data: [] }))
      ]);
      setSummary(sumRes.data);
      setSubjects(subjRes.data || sumRes.data?.subject_progress || []);
    } catch (e) {
      console.error("Progress data fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  const subjectChartData = subjects.map((s) => ({
    name: s.subject_name,
    Completed: s.completed_tasks,
    Pending: s.total_tasks - s.completed_tasks,
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Academic Progress Analytics</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Real-time tracking of task completions, study hours, and course workload distribution.
        </p>
      </div>

      {/* Progress Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Completion Rate</span>
            <CheckCircle2 className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-3xl font-bold text-indigo-600">{summary?.completion_percentage || 0}%</div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${summary?.completion_percentage || 0}%` }}
            ></div>
          </div>
          <p className="text-xs text-slate-400">
            {summary?.completed_tasks || 0} of {summary?.total_tasks || 0} tasks finished
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Pending Workload</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-bold text-slate-800">{summary?.pending_tasks || 0}</div>
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 font-medium">
              {summary?.in_progress_tasks || 0} In Progress
            </span>
            {summary?.overdue_tasks > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 font-medium flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> {summary?.overdue_tasks} Overdue
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400">Active assignments & exams</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Study Hours</span>
            <Flame className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-3xl font-bold text-slate-800">
            {summary?.study_hours_completed || 0} <span className="text-sm font-normal text-slate-400">/ {summary?.study_hours_planned || 0} hrs</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
              style={{
                width: `${
                  summary?.study_hours_planned
                    ? Math.min(100, (summary.study_hours_completed / summary.study_hours_planned) * 100)
                    : 0
                }%`
              }}
            ></div>
          </div>
          <p className="text-xs text-slate-400">Hours invested in personalized study slots</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Enrolled Courses</span>
            <BookOpen className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-bold text-emerald-600">{subjects.length}</div>
          <p className="text-xs text-slate-400 mt-4">Active subjects with planned syllabus activities</p>
        </div>
      </div>

      {/* Course Workload Bar Chart */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Course Workload Distribution</h3>
            <p className="text-xs text-slate-500">Completed vs Pending Tasks per Academic Course</p>
          </div>
        </div>

        {subjectChartData.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            No course workload recorded yet. Upload an announcement or add tasks to view distribution.
          </div>
        ) : (
          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={subjectChartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="Completed" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Pending" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Subject Detailed Breakdown */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900">Subject Breakdown Table</h3>
        {subjects.length === 0 ? (
          <p className="text-xs text-slate-400 py-4">No subject records available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 uppercase font-semibold">
                  <th className="pb-3">Subject Name</th>
                  <th className="pb-3">Total Tasks</th>
                  <th className="pb-3">Completed</th>
                  <th className="pb-3">Pending</th>
                  <th className="pb-3">Completion Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 text-slate-700">
                {subjects.map((s) => (
                  <tr key={s.subject_id || s.subject_name}>
                    <td className="py-3 font-semibold text-slate-900">{s.subject_name}</td>
                    <td className="py-3">{s.total_tasks}</td>
                    <td className="py-3 text-emerald-600 font-medium">{s.completed_tasks}</td>
                    <td className="py-3 text-slate-500">{s.total_tasks - s.completed_tasks}</td>
                    <td className="py-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold">{s.completion_percentage}%</span>
                        <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-indigo-600 h-1.5 rounded-full"
                            style={{ width: `${s.completion_percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressTracking;
