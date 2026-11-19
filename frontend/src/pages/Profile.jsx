import React, { useState, useEffect } from 'react';
import { profileAPI } from '../services/api';
import { User, BookOpen, Plus, Trash2, CheckCircle2, AlertCircle, Clock, School, Save } from 'lucide-react';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [semester, setSemester] = useState('7th Semester');
  const [department, setDepartment] = useState('Computer Science & Engineering');
  const [newSubjName, setNewSubjName] = useState('');
  const [newSubjCode, setNewSubjCode] = useState('');
  const [availabilities, setAvailabilities] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const res = await profileAPI.getFullProfile();
      setProfile(res.data);
      setName(res.data.user?.name || '');

      const existingAvail = res.data.availabilities || [];
      const fullAvail = DAYS.map((d) => {
        const found = existingAvail.find((a) => a.day_of_week === d);
        return found || {
          day_of_week: d,
          start_time: '18:00',
          end_time: '22:00',
          is_available: d !== 'Sunday'
        };
      });
      setAvailabilities(fullAvail);
    } catch (e) {
      console.error(e);
      setError('Failed to load student profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateName = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSavingProfile(true);
    setMessage('');
    setError('');
    try {
      await profileAPI.updateProfile({ name: name.trim() });
      setMessage('Profile details updated successfully.');
      fetchProfile();
    } catch (err) {
      console.error(err);
      setError('Failed to update profile.');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleAddSubject = async (e) => {
    e.preventDefault();
    if (!newSubjName.trim()) return;
    setError('');
    setMessage('');
    try {
      await profileAPI.addSubject({
        subject_name: newSubjName.trim(),
        subject_code: newSubjCode.trim() || null
      });
      setNewSubjName('');
      setNewSubjCode('');
      setMessage('Academic subject added successfully.');
      fetchProfile();
    } catch (err) {
      console.error(err);
      setError('Failed to add subject.');
    }
  };

  const handleDeleteSubject = async (id) => {
    if (window.confirm('Delete this subject?')) {
      try {
        await profileAPI.deleteSubject(id);
        fetchProfile();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleAvailChange = (day, field, value) => {
    setAvailabilities((prev) =>
      prev.map((a) => (a.day_of_week === day ? { ...a, [field]: value } : a))
    );
  };

  const handleSaveAvailability = async () => {
    try {
      setMessage('');
      await profileAPI.updateAvailability({
        availabilities: availabilities.map((a) => ({
          day_of_week: a.day_of_week,
          start_time: a.start_time,
          end_time: a.end_time,
          is_available: a.is_available
        }))
      });
      setMessage('Weekly study availability slots saved successfully.');
    } catch (e) {
      console.error(e);
      setError('Failed to save study availability.');
    }
  };

  if (loading && !profile) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Student Profile & Academic Settings</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Manage student identity, enrolled courses, and weekly study availability.
        </p>
      </div>

      {message && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center space-x-2 text-emerald-800 text-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-center space-x-2 text-rose-700 text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Basic Student Info Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
          <User className="w-4 h-4 text-indigo-600" />
          <span>Student Account Details</span>
        </h3>
        
        <form onSubmit={handleUpdateName} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Student Full Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Email Address (Read-only)</label>
              <input
                type="email"
                disabled
                value={profile?.user?.email || ''}
                className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs bg-slate-50 text-slate-500 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Semester</label>
              <input
                type="text"
                value={semester}
                onChange={(e) => setSemester(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Department</label>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={savingProfile}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition disabled:opacity-50"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{savingProfile ? 'Saving...' : 'Save Profile Details'}</span>
          </button>
        </form>
      </div>

      {/* Enrolled Subjects Management */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-indigo-600" />
          <span>Enrolled Subjects ({profile?.subjects?.length || 0})</span>
        </h3>

        {/* Add Subject Form */}
        <form onSubmit={handleAddSubject} className="flex flex-col sm:flex-row gap-3 pt-2">
          <input
            type="text"
            required
            value={newSubjName}
            onChange={(e) => setNewSubjName(e.target.value)}
            placeholder="Subject Name (e.g. Database Management Systems)"
            className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
          />
          <input
            type="text"
            value={newSubjCode}
            onChange={(e) => setNewSubjCode(e.target.value)}
            placeholder="Code (e.g. 18CS71)"
            className="w-full sm:w-36 px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center justify-center space-x-1 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Add Course</span>
          </button>
        </form>

        {/* Subjects List */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-3">
          {(profile?.subjects || []).map((s) => (
            <div key={s.id} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-xs text-slate-900">{s.subject_name}</h4>
                {s.subject_code && (
                  <span className="text-[10px] text-slate-500">{s.subject_code}</span>
                )}
              </div>
              <button
                onClick={() => handleDeleteSubject(s.id)}
                className="text-slate-400 hover:text-rose-600 p-1"
                title="Delete subject"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Weekly Study Availability Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
            <Clock className="w-4 h-4 text-indigo-600" />
            <span>Weekly Study Availability Timetable</span>
          </h3>
          <button
            onClick={handleSaveAvailability}
            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Hours</span>
          </button>
        </div>

        <div className="divide-y divide-slate-100">
          {availabilities.map((a) => (
            <div key={a.day_of_week} className="py-2.5 flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-800 w-28">{a.day_of_week}</span>
              <div className="flex items-center space-x-2">
                <input
                  type="time"
                  disabled={!a.is_available}
                  value={a.start_time}
                  onChange={(e) => handleAvailChange(a.day_of_week, 'start_time', e.target.value)}
                  className="px-2 py-1 rounded-lg border border-slate-200 text-xs disabled:opacity-40"
                />
                <span className="text-slate-400">to</span>
                <input
                  type="time"
                  disabled={!a.is_available}
                  value={a.end_time}
                  onChange={(e) => handleAvailChange(a.day_of_week, 'end_time', e.target.value)}
                  className="px-2 py-1 rounded-lg border border-slate-200 text-xs disabled:opacity-40"
                />
              </div>
              <label className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={a.is_available}
                  onChange={(e) => handleAvailChange(a.day_of_week, 'is_available', e.target.checked)}
                  className="rounded text-indigo-600 focus:ring-0"
                />
                <span className="text-slate-500 text-[11px]">Available</span>
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Profile;
