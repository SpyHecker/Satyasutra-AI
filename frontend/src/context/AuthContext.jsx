import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import { AuthContext } from './auth-context-def';

const TOKEN_KEY = 'satyasutra_token';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true);
  const [dbStatus, setDbStatus] = useState(null);

  // Check auth status and database connectivity on load
  const initAuth = useCallback(async () => {
    try {
      // Check database status
      api.auth.status()
        .then((res) => setDbStatus(res.database))
        .catch(() => setDbStatus({ type: 'local_fallback', mongodb_connected: false }));

      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (!storedToken) {
        setUser(null);
        setLoading(false);
        return;
      }

      // Verify token with backend
      const userData = await api.auth.me();
      setUser(userData);
      setToken(storedToken);
    } catch (err) {
      console.warn('Session verification failed, logging out:', err);
      localStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  const login = async (email, password) => {
    const res = await api.auth.login({ email, password });
    localStorage.setItem(TOKEN_KEY, res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  };

  const register = async (formData) => {
    const res = await api.auth.register(formData);
    localStorage.setItem(TOKEN_KEY, res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    loading,
    dbStatus,
    isAuthenticated: Boolean(user),
    login,
    register,
    logout,
    refreshUser: initAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;
