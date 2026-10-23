import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function Navbar() {
  const { isAuthenticated, user, logout, dbStatus } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar" id="main-nav">
      <div className="navbar-left">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">⚖️</span>
          <span><span className="brand-accent">Satya</span>Sutra</span>
        </Link>

        {dbStatus && (
          <span
            className={`navbar-db-badge ${dbStatus.mongodb_connected ? 'mongo-live' : 'local-live'}`}
            title={dbStatus.mongodb_connected ? `MongoDB connected: ${dbStatus.database_name}` : 'Running on local file storage'}
          >
            <span className="db-indicator-dot"></span>
            <span>{dbStatus.mongodb_connected ? 'MongoDB' : 'Local DB'}</span>
          </span>
        )}
      </div>

      <ul className="navbar-links">
        {isAuthenticated ? (
          <>
            <li>
              <NavLink to="/dashboard" end className="nav-link">
                📊 Dashboard
              </NavLink>
            </li>
            <li>
              <NavLink to="/evidence" className="nav-link">
                📁 Evidence Ingestion
              </NavLink>
            </li>
            <li>
              <NavLink to="/graph" className="nav-link">
                🕸️ Knowledge Graph
              </NavLink>
            </li>
            <li>
              <NavLink to="/timeline" className="nav-link">
                📅 Timeline
              </NavLink>
            </li>
            <li>
              <NavLink to="/report" className="nav-link">
                📄 Case Report
              </NavLink>
            </li>
          </>
        ) : (
          <>
            <li>
              <NavLink to="/" end className="nav-link">
                🏠 Overview
              </NavLink>
            </li>
            <li>
              <a href="/#capabilities" className="nav-link">
                ⚡ Capabilities
              </a>
            </li>
            <li>
              <a href="/#workflow" className="nav-link">
                🔄 Pipeline
              </a>
            </li>
            <li>
              <a href="/#use-cases" className="nav-link">
                🎯 Use Cases
              </a>
            </li>
          </>
        )}
      </ul>

      <div className="navbar-auth-actions">
        {isAuthenticated ? (
          <div className="user-profile-menu">
            <div className="user-info-pill">
              <span className="user-avatar-circle">
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'I'}
              </span>
              <div className="user-details">
                <span className="user-name">{user?.full_name || 'Investigator'}</span>
                <span className="user-role-badge">{user?.badge_number || user?.role || 'Verified'}</span>
              </div>
            </div>
            <button
              onClick={handleSignOut}
              className="btn btn-outline-danger btn-signout"
              title="Sign Out of Case Vault"
            >
              Sign Out
            </button>
          </div>
        ) : (
          <div className="auth-button-group">
            <Link to="/login" className="btn btn-ghost btn-nav-login">
              Sign In
            </Link>
            <Link to="/register" className="btn btn-primary btn-nav-register">
              Create Clearance →
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
