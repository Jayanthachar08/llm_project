import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to inject JWT Bearer Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('campusflow_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to handle unauthorized 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('campusflow_token');
      localStorage.removeItem('campusflow_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getMe: () => api.get('/auth/me'),
};

export const profileAPI = {
  getFullProfile: () => api.get('/profile'),
  updateProfile: (data) => api.put('/profile', data),
  getSubjects: () => api.get('/profile/subjects'),
  addSubject: (data) => api.post('/profile/subjects', data),
  deleteSubject: (id) => api.delete(`/profile/subjects/${id}`),
  getAvailability: () => api.get('/profile/availability'),
  updateAvailability: (data) => api.put('/profile/availability', data),
  getCollegeSchedule: () => api.get('/profile/college-schedule'),
  updateCollegeSchedule: (data) => api.put('/profile/college-schedule', data),
};

export const announcementAPI = {
  uploadFile: (formData) => api.post('/announcements/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  pasteText: (text) => api.post('/announcements/paste-text', { text }),
  extractTasks: (data) => api.post('/announcements/extract', data),
  extractById: (id, useRag = true) => api.post(`/announcements/${id}/extract`, null, { params: { use_rag: useRag } }),
  getAnnouncements: () => api.get('/announcements'),
  getAnnouncementById: (id) => api.get(`/announcements/${id}`),
};

export const availabilityAPI = {
  getAvailability: () => api.get('/availability'),
  updateAvailability: (data) => api.put('/availability', data),
};

export const progressAPI = {
  getSummary: () => api.get('/progress/summary'),
  getSubjects: () => api.get('/progress/subjects'),
};

export const taskAPI = {
  getTasks: (params) => api.get('/tasks', { params }),
  createTask: (data) => api.post('/tasks', data),
  confirmBatch: (data) => api.post('/tasks/confirm', data),
  getTaskById: (id) => api.get(`/tasks/${id}`),
  updateTask: (id, data) => api.put(`/tasks/${id}`, data),
  deleteTask: (id) => api.delete(`/tasks/${id}`),
  completeTask: (id) => api.patch(`/tasks/${id}/complete`),
  updateProgress: (id, data) => api.patch(`/tasks/${id}/progress`, data),
  getPriorities: () => api.get('/tasks/priorities'),
};

export const plannerAPI = {
  generatePlan: (params) => api.post('/planner/generate', params || {}),
  reschedule: (taskId) => api.post('/planner/reschedule', { task_id: taskId }),
  getConflicts: () => api.get('/planner/conflicts'),
  getCalendar: () => api.get('/planner/calendar'),
  updateSession: (sessionId, data) => api.patch(`/planner/sessions/${sessionId}`, data),
};

export const ragAPI = {
  ingest: (data) => api.post('/rag/ingest', data),
  search: (query, topK = 3) => api.post('/rag/search', { query, top_k: topK }),
  deleteDoc: (id) => api.delete(`/rag/documents/${id}`),
  reindex: () => api.post('/rag/reindex'),
};

export const notificationAPI = {
  getNotifications: () => api.get('/notifications'),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
  markAllRead: () => api.post('/notifications/read-all'),
};

export const dashboardAPI = {
  getSummary: () => api.get('/dashboard/summary'),
};

export default api;
