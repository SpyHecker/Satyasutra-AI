import { NavLink, Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="navbar" id="main-nav">
      <Link to="/" className="navbar-brand">
        <span className="brand-icon">⚖️</span>
        <span><span className="brand-accent">Satya</span>Sutra</span>
      </Link>

      <ul className="navbar-links">
        <li><NavLink to="/" end className="nav-link">🏠 Dashboard</NavLink></li>
        <li><NavLink to="/evidence" className="nav-link">📁 Evidence</NavLink></li>
        <li><NavLink to="/graph" className="nav-link">🕸️ Graph</NavLink></li>
        <li><NavLink to="/timeline" className="nav-link">📅 Timeline</NavLink></li>
        <li><NavLink to="/report" className="nav-link">📄 Report</NavLink></li>
      </ul>
    </nav>
  );
}
