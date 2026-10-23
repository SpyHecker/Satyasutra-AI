import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function Login() {
  const navigate = useNavigate();
  const { login, dbStatus } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide both account email and password.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-card-glow"></div>
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-icon-badge">⚖️</div>
          <h1 className="auth-title">Investigator & Admin Sign In</h1>
          <p className="auth-subtitle">
            Sign in to access your secure case files, knowledge graphs, and forensic reports
          </p>
        </div>

        {error && (
          <div className="auth-alert-error" role="alert">
            <span className="alert-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">
              Official Email
            </label>
            <div className="input-with-icon">
              <span className="input-icon">✉️</span>
              <input
                id="login-email"
                type="email"
                className="form-input"
                placeholder="admin@satyasutra.ai or investigator@agency.gov"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <div className="label-row">
              <label className="form-label" htmlFor="login-password">
                Password
              </label>
              <button
                type="button"
                className="toggle-pw-btn"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            <div className="input-with-icon">
              <span className="input-icon">🔐</span>
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                className="form-input"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary auth-submit-btn"
            disabled={loading}
          >
            {loading ? (
              <span className="btn-loading-content">
                <span className="btn-spinner"></span>
                <span>Authenticating...</span>
              </span>
            ) : (
              'Sign In to Case Vault →'
            )}
          </button>
        </form>

        <div className="auth-footer-links">
          <span>Need an investigator account? </span>
          <Link to="/register" className="auth-link">
            Create Clearance Credentials
          </Link>
        </div>

        {dbStatus && (
          <div className="db-status-pill">
            <span className={`db-dot ${dbStatus.mongodb_connected ? 'online' : 'fallback'}`}></span>
            <span>
              Database: {dbStatus.mongodb_connected ? 'MongoDB Active' : 'Local Fallback Active'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
