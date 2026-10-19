import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import EvidenceUpload from './pages/EvidenceUpload';
import GraphView from './pages/GraphView';
import Timeline from './pages/Timeline';
import Report from './pages/Report';
import './App.css';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Navbar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/evidence" element={<EvidenceUpload />} />
            <Route path="/graph" element={<GraphView />} />
            <Route path="/timeline" element={<Timeline />} />
            <Route path="/report" element={<Report />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
