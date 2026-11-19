import React, { useState, useEffect } from 'react';
import { profileAPI } from '../services/api';
import { Settings as SettingsIcon, Clock, School, CheckCircle2, AlertCircle, Save } from 'lucide-react';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const Settings = () => {
  const [availabilities, setAvailabilities] = useState([]);
  const [collegeHours, setCollegeHours] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await profileAPI.getFullProfile();
      const existingAvail = res.data.availabilities || [];
      const existingCollege = res.data.college_schedules || [];

      // Ensure all 7 days represented
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
      setCollegeHours(existingCollege);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAvailChange = (day, field, value) => {
    setAvailabilities((prev) =>
      prev.map((a) => (a.day_of_week === day ? { ...a, [field]: value } : a))
    );
  };

  const handleSaveAvailability = async () => {
    try {
      setSaving(true);
      setMessage('');
      await profileAPI.updateAvailability({
        availabilities: availabilities.map((a) => ({
          day_of_week: a.day_of_week,
          start_time: a.start_time,
          end_time: a.end_time,
          is_available: a.is_available
        }))
      });
      setMessage('Weekly study availability updated successfully.');
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Availability & College Timetable</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure your daily study hours and college schedule so the study planner prevents conflicts.
          </p>
        </div>

        <button
          onClick={handleSaveAvailability}
          disabled={saving}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow-sm flex items-center space-x-1.5 transition self-start disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          <span>{saving ? 'Saving...' : 'Save Availability'}</span>
        </button>
      </div>

      {message && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center space-x-2 text-emerald-800 text-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Weekly Study Availability */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
          <Clock className="w-4 h-4 text-indigo-600" />
          <span>Daily Available Study Time Slots</span>
        </h3>
        <p className="text-xs text-slate-500">
          The scheduling engine will place generated study sessions exclusively within these active hours.
        </p>

        <div className="space-y-3 pt-2">
          {availabilities.map((slot) => (
            <div
              key={slot.day_of_week}
              className={`p-3.5 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition ${
                slot.is_available ? 'bg-slate-50/70 border-slate-200' : 'bg-slate-100/50 border-slate-100 opacity-60'
              }`}
            >
              <div className="flex items-center space-x-3 w-32">
                <input
                  type="checkbox"
                  id={`check-${slot.day_of_week}`}
                  checked={slot.is_available}
                  onChange={(e) => handleAvailChange(slot.day_of_week, 'is_available', e.target.checked)}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor={`check-${slot.day_of_week}`} className="text-xs font-semibold text-slate-800 cursor-pointer">
                  {slot.day_of_week}
                </label>
              </div>

              {slot.is_available ? (
                <div className="flex items-center space-x-2 text-xs">
                  <span className="text-slate-500">From</span>
                  <input
                    type="time"
                    value={slot.start_time}
                    onChange={(e) => handleAvailChange(slot.day_of_week, 'start_time', e.target.value)}
                    className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:ring-2 focus:ring-indigo-500/20 outline-none"
                  />
                  <span className="text-slate-500">To</span>
                  <input
                    type="time"
                    value={slot.end_time}
                    onChange={(e) => handleAvailChange(slot.day_of_week, 'end_time', e.target.value)}
                    className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:ring-2 focus:ring-indigo-500/20 outline-none"
                  />
                </div>
              ) : (
                <span className="text-xs text-slate-400 italic">Day marked off for study</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* College Working Hours Notice */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
          <School className="w-4 h-4 text-indigo-600" />
          <span>College Working Hours</span>
        </h3>
        <p className="text-xs text-slate-500">
          Standard college working hours (09:00 - 16:00, Monday through Friday). The planner automatically avoids scheduling study blocks during these hours.
        </p>

        <div className="p-4 bg-indigo-50/50 border border-indigo-100 rounded-xl text-xs text-slate-700">
          <span className="font-semibold block text-indigo-900 mb-1">Enforced Constraint:</span>
          <span>9:00 AM – 4:00 PM (Monday – Friday) is reserved for classes and labs. Study sessions will only be scheduled outside this window.</span>
        </div>
      </div>
    </div>
  );
};

export default Settings;
