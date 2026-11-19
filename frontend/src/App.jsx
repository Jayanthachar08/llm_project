import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import UploadAnnouncement from './pages/UploadAnnouncement';
import ExtractionReview from './pages/ExtractionReview';
import TaskManagement from './pages/TaskManagement';
import PriorityView from './pages/PriorityView';
import CalendarView from './pages/CalendarView';
import ConflictAlerts from './pages/ConflictAlerts';
import StudyPlanner from './pages/StudyPlanner';
import ProgressTracking from './pages/ProgressTracking';
import RAGKnowledge from './pages/RAGKnowledge';
import Notifications from './pages/Notifications';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  if (isAuthenticated) return <Navigate to="/" replace />;
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

          {/* Protected Application Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="upload" element={<UploadAnnouncement />} />
            <Route path="review" element={<ExtractionReview />} />
            <Route path="tasks" element={<TaskManagement />} />
            <Route path="priorities" element={<PriorityView />} />
            <Route path="calendar" element={<CalendarView />} />
            <Route path="conflicts" element={<ConflictAlerts />} />
            <Route path="planner" element={<StudyPlanner />} />
            <Route path="progress" element={<ProgressTracking />} />
            <Route path="rag" element={<RAGKnowledge />} />
            <Route path="notifications" element={<Notifications />} />
            <Route path="profile" element={<Profile />} />
            <Route path="settings" element={<Settings />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
