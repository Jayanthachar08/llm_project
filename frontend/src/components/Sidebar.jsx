import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UploadCloud,
  CheckSquare,
  ListTodo,
  TrendingUp,
  Calendar,
  AlertTriangle,
  Clock,
  BarChart3,
  Database,
  Bell,
  User,
  Settings
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/upload', label: 'Upload Announcement', icon: UploadCloud },
  { path: '/review', label: 'Extraction Review', icon: CheckSquare },
  { path: '/tasks', label: 'Task Management', icon: ListTodo },
  { path: '/priorities', label: 'Priority View', icon: TrendingUp },
  { path: '/calendar', label: 'Deadline Calendar', icon: Calendar },
  { path: '/conflicts', label: 'Conflict Alerts', icon: AlertTriangle },
  { path: '/planner', label: 'Study Planner', icon: Clock },
  { path: '/progress', label: 'Progress Tracking', icon: BarChart3 },
  { path: '/rag', label: 'RAG Knowledge Base', icon: Database },
  { path: '/notifications', label: 'Notifications', icon: Bell },
  { path: '/profile', label: 'Profile & Subjects', icon: User },
  { path: '/settings', label: 'Availability & Timetable', icon: Settings },
];

const Sidebar = () => {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-61px)] p-4 flex flex-col justify-between hidden md:flex">
      <div className="space-y-1">
        <p className="text-[11px] font-semibold text-slate-400 tracking-wider uppercase px-3 mb-2">
          Academic Flow
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-medium transition ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-200'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="pt-4 border-t border-slate-100">
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
          <p className="text-[11px] font-semibold text-slate-700">CampusFlow AI v1.0</p>
          <p className="text-[10px] text-slate-500 mt-0.5">Google GenAI + RAG + Priority Engine</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
