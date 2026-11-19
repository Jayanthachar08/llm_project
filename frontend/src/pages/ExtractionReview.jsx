import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { taskAPI } from '../services/api';
import {
  CheckCircle2,
  Trash2,
  AlertCircle,
  HelpCircle,
  Clock,
  Sparkles,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';

const ExtractionReview = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const stateTasks = location.state?.tasks || [];
  const rawSummary = location.state?.raw_summary || '';
  const ambiguityDetected = location.state?.ambiguity_detected || false;
  const announcementId = location.state?.announcement_id || null;

  const [tasks, setTasks] = useState(stateTasks);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleFieldChange = (index, field, value) => {
    const updated = [...tasks];
    updated[index][field] = value;
    setTasks(updated);
  };

  const handleRemoveTask = (index) => {
    const updated = tasks.filter((_, i) => i !== index);
    setTasks(updated);
  };

  const handleConfirmAll = async () => {
    if (tasks.length === 0) {
      setError('No tasks to confirm.');
      return;
    }

    setSaving(true);
    setError('');

    try {
      const payload = {
        announcement_id: announcementId,
        tasks: tasks.map((t) => ({
          title: t.title,
          description: t.description || '',
          category: t.category,
          deadline: t.deadline ? `${t.deadline}T23:59:00` : null,
          event_date: t.event_date ? `${t.event_date}T09:00:00` : null,
          importance: t.importance || 'Normal',
          difficulty: t.difficulty || 'Medium',
          estimated_duration: parseFloat(t.estimated_duration) || 2.0,
          subject_name: t.subject || 'General',
          announcement_id: announcementId
        }))
      };

      await taskAPI.confirmBatch(payload);
      navigate('/tasks');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to save confirmed tasks.');
    } finally {
      setSaving(false);
    }
  };

  if (tasks.length === 0) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12 bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
        <Sparkles className="w-10 h-10 text-indigo-400 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-slate-800">No Extracted Tasks to Review</h2>
        <p className="text-xs text-slate-500 mt-1 mb-6">
          Upload an academic notice or paste text to extract structured assignments and examinations.
        </p>
        <Link
          to="/upload"
          className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700 transition"
        >
          Go to Upload Notice
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-600 text-xs font-semibold uppercase tracking-wider mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Human-in-the-Loop Guardrail (Layer 3)</span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">
            Review & Confirm Extracted Tasks
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Verify Google GenAI's extracted deadlines and categories before persisting to PostgreSQL.
          </p>
        </div>
        <button
          onClick={handleConfirmAll}
          disabled={saving}
          className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-emerald-100 flex items-center space-x-2 disabled:opacity-50 transition"
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>{saving ? 'Saving to Database...' : `Confirm & Save ${tasks.length} Tasks`}</span>
        </button>
      </div>

      {ambiguityDetected && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl flex items-start space-x-3 text-xs text-amber-800">
          <HelpCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold block mb-0.5">Ambiguous or Relative Dates Flagged</span>
            <span>
              Some tasks contain relative phrasing (e.g., 'next Monday' or unspecified dates).
              Please review and select explicit calendar dates below before saving.
            </span>
          </div>
        </div>
      )}

      {error && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-center space-x-2 text-rose-700 text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Extracted Tasks Cards */}
      <div className="space-y-4">
        {tasks.map((task, idx) => (
          <div
            key={idx}
            className={`bg-white rounded-2xl border p-5 shadow-sm space-y-4 transition ${
              task.needs_verification ? 'border-amber-300 ring-1 ring-amber-100' : 'border-slate-200'
            }`}
          >
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <span className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-700 text-xs font-bold flex items-center justify-center">
                  {idx + 1}
                </span>
                <span className="text-xs font-bold text-slate-800">Activity #{idx + 1}</span>
                {task.needs_verification && (
                  <span className="bg-amber-100 text-amber-800 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                    Verification Needed
                  </span>
                )}
              </div>
              <button
                onClick={() => handleRemoveTask(idx)}
                className="text-slate-400 hover:text-rose-600 p-1 rounded-lg hover:bg-rose-50 transition"
                title="Reject task"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            {task.needs_verification && task.verification_reason && (
              <div className="text-[11px] bg-amber-50 text-amber-700 p-2 rounded-lg font-medium">
                Reason: {task.verification_reason}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">Task Title</label>
                <input
                  type="text"
                  value={task.title}
                  onChange={(e) => handleFieldChange(idx, 'title', e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">Subject / Course</label>
                <input
                  type="text"
                  value={task.subject || ''}
                  onChange={(e) => handleFieldChange(idx, 'subject', e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">Academic Category</label>
                <select
                  value={task.category}
                  onChange={(e) => handleFieldChange(idx, 'category', e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none bg-white"
                >
                  <option value="assignment">Assignment</option>
                  <option value="examination">Examination</option>
                  <option value="lab">Lab Work</option>
                  <option value="project">Project</option>
                  <option value="event">Academic Event</option>
                </select>
              </div>

              <div>
                {task.category === 'examination' || task.category === 'event' ? (
                  <>
                    <label className="block text-[11px] font-semibold text-slate-600 mb-1">Event / Exam Date</label>
                    <input
                      type="date"
                      value={task.event_date || ''}
                      onChange={(e) => handleFieldChange(idx, 'event_date', e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
                    />
                  </>
                ) : (
                  <>
                    <label className="block text-[11px] font-semibold text-slate-600 mb-1">Submission Deadline</label>
                    <input
                      type="date"
                      value={task.deadline || ''}
                      onChange={(e) => handleFieldChange(idx, 'deadline', e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
                    />
                  </>
                )}
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">Estimated Hours</label>
                <input
                  type="number"
                  step="0.5"
                  min="0.5"
                  max="50"
                  value={task.estimated_duration || 2.0}
                  onChange={(e) => handleFieldChange(idx, 'estimated_duration', e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Importance</label>
                  <select
                    value={task.importance || 'Normal'}
                    onChange={(e) => handleFieldChange(idx, 'importance', e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none bg-white"
                  >
                    <option value="Normal">Normal</option>
                    <option value="Important">Important</option>
                    <option value="Critical">Critical</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Difficulty</label>
                  <select
                    value={task.difficulty || 'Medium'}
                    onChange={(e) => handleFieldChange(idx, 'difficulty', e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none bg-white"
                  >
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Difficult">Difficult</option>
                  </select>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Context / Description</label>
              <textarea
                rows={2}
                value={task.description || ''}
                onChange={(e) => handleFieldChange(idx, 'description', e.target.value)}
                className="w-full p-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
              ></textarea>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExtractionReview;
