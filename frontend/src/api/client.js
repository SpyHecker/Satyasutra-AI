/**
 * API Client — centralized fetch wrapper for the SatyaSutra backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
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

  evidence: {
    upload: (file) => {
      const form = new FormData();
      form.append('file', file);
      return request('/evidence/upload', { method: 'POST', body: form });
    },
    list: () => request('/evidence/'),
  },
};

export default api;
