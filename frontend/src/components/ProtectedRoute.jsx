import { Link } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="auth-gate-loading">
        <div className="vault-spinner"></div>
        <p className="vault-loading-text">Verifying Security Clearance & Forensic Credentials...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="auth-gate-container">
        <div className="auth-gate-card">
          <div className="auth-gate-badge">
            <span className="gate-lock-icon">🔒</span>
            <span>RESTRICTED FORENSIC ACCESS</span>
          </div>

          <h2 className="auth-gate-title">Investigator Authentication Required</h2>
          <p className="auth-gate-desc">
            To maintain chain-of-custody and evidence auditability, accessing case materials,
            entity graphs, and contradiction reports requires verified investigator credentials.
          </p>

          <div className="auth-gate-actions">
            <Link to="/login" className="btn btn-primary gate-btn">
              🔑 Sign In to Case Vault →
            </Link>
          </div>

          <div className="auth-gate-footer">
            <span>Powered by SatyaSutra Forensic Intelligence • 256-bit Evidence Integrity</span>
          </div>
        </div>
      </div>
    );
  }

  return children;
}
