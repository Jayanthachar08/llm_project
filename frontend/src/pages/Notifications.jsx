import React, { useState, useEffect } from 'react';
import { notificationAPI } from '../services/api';
import { Bell, CheckCircle2, Clock, AlertTriangle, CheckCheck } from 'lucide-react';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const res = await notificationAPI.getNotifications();
      setNotifications(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (id) => {
    try {
      await notificationAPI.markRead(id);
      fetchNotifications();
    } catch (e) {
      console.error(e);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationAPI.markAllRead();
      fetchNotifications();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Reminders & Notifications</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated alerts scheduled for upcoming deadlines, examinations, and study sessions with deduplication.
          </p>
        </div>

        {notifications.some((n) => n.status !== 'read') && (
          <button
            onClick={handleMarkAllRead}
            className="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold text-xs rounded-xl flex items-center space-x-1.5 transition self-start"
          >
            <CheckCheck className="w-4 h-4" />
            <span>Mark All as Read</span>
          </button>
        )}
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading notifications...</div>
        ) : notifications.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">
            <Bell className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p>No reminders or alerts generated yet.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {notifications.map((n) => (
              <div
                key={n.id}
                className={`p-4 md:p-5 flex items-start justify-between gap-4 transition ${
                  n.status !== 'read' ? 'bg-indigo-50/30' : 'hover:bg-slate-50/50'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div
                    className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 ${
                      n.notification_type === 'overdue'
                        ? 'bg-rose-100 text-rose-700'
                        : n.notification_type === 'deadline'
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-indigo-100 text-indigo-700'
                    }`}
                  >
                    {n.notification_type === 'overdue' ? (
                      <AlertTriangle className="w-4 h-4" />
                    ) : (
                      <Clock className="w-4 h-4" />
                    )}
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">
                        {n.notification_type}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {new Date(n.scheduled_at).toLocaleString()}
                      </span>
                    </div>
                    <p className={`text-xs ${n.status !== 'read' ? 'font-semibold text-slate-900' : 'text-slate-700'}`}>
                      {n.message}
                    </p>
                  </div>
                </div>

                {n.status !== 'read' && (
                  <button
                    onClick={() => handleMarkRead(n.id)}
                    className="text-xs text-indigo-600 hover:underline font-semibold flex-shrink-0"
                  >
                    Mark read
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

export default Notifications;
