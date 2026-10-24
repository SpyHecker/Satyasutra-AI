/**
 * API Client — centralized fetch wrapper for the SatyaSutra backend.
 * Automatically injects JWT Bearer tokens and handles auth & evidence endpoints.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  // Build headers with optional auth token
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const token = localStorage.getItem('satyasutra_token');
  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  // Remove Content-Type for FormData (file uploads)
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  const res = await fetch(url, config);

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export const api = {
  health: () => request('/health'),

  auth: {
    login: (credentials) => request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
    register: (userData) => request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),
    me: () => request('/auth/me'),
    status: () => request('/auth/status'),
  },

  evidence: {
    upload: (file) => {
      const form = new FormData();
      form.append('file', file);
      return request('/evidence/upload', { method: 'POST', body: form });
    },
    list: () => request('/evidence/'),
    get: (id) => request(`/evidence/${id}`),
    delete: (id) => request(`/evidence/${id}`, { method: 'DELETE' }),
  },

  analysis: {
    graph: () => request('/evidence/analysis/graph'),
    timeline: () => request('/evidence/analysis/timeline'),
    contradictions: () => request('/evidence/analysis/contradictions'),
    report: () => request('/evidence/analysis/report'),
    stats: () => request('/evidence/analysis/stats'),
  },

  chatbot: {
    ask: (message, history = []) => request('/chatbot/ask', {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    }),
    suggestions: () => request('/chatbot/suggestions'),
  },
};

export default api;
