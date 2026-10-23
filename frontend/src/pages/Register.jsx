import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

const INVESTIGATOR_ROLES = [
  'Lead Investigator',
  'Forensic Intelligence Analyst',
  'Senior Detective / Inspector',
  'Prosecution & Legal Counsel',
  'Digital Forensics Specialist',
  'Independent Investigative Journalist',
];

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    role: 'Lead Investigator',
    badgeNumber: '',
    password: '',
    confirmPassword: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!formData.fullName.trim()) {
      setError('Please provide your full legal name or agent alias.');
      return;
    }

    if (!formData.email.trim()) {
      setError('Please provide a valid official email address.');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must contain at least 6 characters.');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Password and confirmation do not match.');
      return;
    }

    try {
      setLoading(true);
      await register({
        email: formData.email.trim(),
        password: formData.password,
        full_name: formData.fullName.trim(),
        role: formData.role,
        badge_number: formData.badgeNumber.trim() || undefined,
      });
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed. Please check your information.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-card-glow"></div>
      <div className="auth-card auth-card-wide">
        <div className="auth-header">
          <div className="auth-icon-badge">🛡️</div>
          <h1 className="auth-title">Investigator Registration</h1>
          <p className="auth-subtitle">
            Establish verified clearance credentials to ingest evidence and manage case dossiers
          </p>
        </div>

        {error && (
          <div className="auth-alert-error" role="alert">
            <span className="alert-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form auth-grid-form">
          <div className="form-group">
            <label className="form-label" htmlFor="reg-fullname">
              Full Name / Officer Alias *
            </label>
            <input
              id="reg-fullname"
              name="fullName"
              type="text"
              className="form-input"
              placeholder="e.g. Agent Sunita Rao"
              value={formData.fullName}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">
              Official Email Address *
            </label>
            <input
              id="reg-email"
              name="email"
              type="email"
              className="form-input"
              placeholder="officer@agency.gov or analyst@satyasutra.ai"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-role">
              Forensic Role / Assignment *
            </label>
            <select
              id="reg-role"
              name="role"
              className="form-input form-select"
              value={formData.role}
              onChange={handleChange}
            >
              {INVESTIGATOR_ROLES.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-badge">
              Badge / Department ID (Optional)
            </label>
            <input
              id="reg-badge"
              name="badgeNumber"
              type="text"
              className="form-input"
              placeholder="e.g. SS-8842 or CID-09"
              value={formData.badgeNumber}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-password">
              Secure Password *
            </label>
            <input
              id="reg-password"
              name="password"
              type="password"
              className="form-input"
              placeholder="Minimum 6 characters"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-confirm">
              Confirm Password *
            </label>
            <input
              id="reg-confirm"
              name="confirmPassword"
              type="password"
              className="form-input"
              placeholder="Repeat password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-full-width">
            <button
              type="submit"
              className="btn btn-primary auth-submit-btn"
              disabled={loading}
            >
              {loading ? (
                <span className="btn-loading-content">
                  <span className="btn-spinner"></span>
                  <span>Issuing Clearance Credentials...</span>
                </span>
              ) : (
                'Create Clearance Credentials & Launch Workspace →'
              )}
            </button>
          </div>
        </form>

        <div className="auth-footer-links">
          <span>Already hold investigator clearance? </span>
          <Link to="/login" className="auth-link">
            Sign In to Existing Vault
          </Link>
        </div>
      </div>
    </div>
  );
}
