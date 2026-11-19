import React, { useState, useEffect } from 'react';
import { plannerAPI } from '../services/api';
import { Calendar as CalendarIcon, Clock, BookOpen, AlertCircle, Sparkles } from 'lucide-react';

const CalendarView = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all'); // all, study_session, deadline, exam

  useEffect(() => {
    fetchCalendar();
  }, []);

  const fetchCalendar = async () => {
    try {
      setLoading(true);
      const res = await plannerAPI.getCalendar();
      setEvents(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const filteredEvents = events.filter((e) => {
    if (filterType === 'all') return true;
    return e.event_type === filterType;
  });

  // Group events by date
  const groupedEvents = filteredEvents.reduce((acc, curr) => {
    const dateKey = curr.start.split('T')[0];
    if (!acc[dateKey]) acc[dateKey] = [];
    acc[dateKey].push(curr);
    return acc;
  }, {});

  const sortedDates = Object.keys(groupedEvents).sort();

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Academic Deadline & Study Calendar</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Unified view of submission deadlines, examination schedules, and personalized study sessions.
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex flex-wrap items-center gap-1.5 bg-white p-1 rounded-xl border border-slate-200">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              filterType === 'all' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            All Events
          </button>
          <button
            onClick={() => setFilterType('deadline')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              filterType === 'deadline' ? 'bg-rose-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Deadlines
          </button>
          <button
            onClick={() => setFilterType('exam')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              filterType === 'exam' ? 'bg-amber-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Exams & Tests
          </button>
          <button
            onClick={() => setFilterType('study_session')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              filterType === 'study_session' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Study Sessions
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400 bg-white rounded-2xl border">Loading calendar events...</div>
      ) : sortedDates.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-2xl border text-xs text-slate-500">
          No calendar events found for the selected filter.
        </div>
      ) : (
        <div className="space-y-6">
          {sortedDates.map((dateStr) => {
            const dayEvents = groupedEvents[dateStr];
            const dateObj = new Date(dateStr + 'T00:00:00');
            const formattedDate = dateObj.toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            });

            return (
              <div key={dateStr} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
                <div className="flex items-center space-x-2 border-b border-slate-100 pb-2">
                  <CalendarIcon className="w-4 h-4 text-indigo-600" />
                  <span className="font-bold text-sm text-slate-900">{formattedDate}</span>
                  <span className="text-xs text-slate-400">({dayEvents.length} items)</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {dayEvents.map((e) => (
                    <div
                      key={e.id}
                      className={`p-3.5 rounded-xl border flex flex-col justify-between space-y-2 ${
                        e.event_type === 'deadline'
                          ? 'bg-rose-50/50 border-rose-200'
                          : e.event_type === 'exam'
                          ? 'bg-amber-50/50 border-amber-200'
                          : 'bg-indigo-50/40 border-indigo-200'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span
                            className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                              e.event_type === 'deadline'
                                ? 'bg-rose-100 text-rose-700'
                                : e.event_type === 'exam'
                                ? 'bg-amber-100 text-amber-700'
                                : 'bg-indigo-100 text-indigo-700'
                            }`}
                          >
                            {e.event_type === 'study_session' ? 'Study Session' : e.event_type}
                          </span>
                          {e.status && (
                            <span className="text-[10px] font-medium text-slate-500 capitalize">{e.status}</span>
                          )}
                        </div>
                        <h4 className="font-semibold text-xs text-slate-900">{e.title}</h4>
                      </div>

                      <div className="text-[11px] text-slate-500 flex items-center space-x-1 pt-1 border-t border-slate-100/50">
                        <Clock className="w-3.5 h-3.5" />
                        <span>
                          {e.start.includes('T') ? e.start.split('T')[1].substring(0, 5) : 'All Day'}
                          {e.end && e.end !== e.start ? ` - ${e.end.split('T')[1].substring(0, 5)}` : ''}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default CalendarView;
