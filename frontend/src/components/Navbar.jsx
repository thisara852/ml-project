import React from 'react';
import { Compass, Sparkles, MapPin, Calendar, BarChart3, UserCheck } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'recommendations', label: 'ML Recommendations', icon: Sparkles },
    { id: 'map', label: 'Interactive Map', icon: MapPin },
    { id: 'planner', label: 'Trip Planner & Budget', icon: Calendar },
    { id: 'benchmarks', label: 'ML Benchmarks & Admin', icon: BarChart3 },
  ];

  return (
    <header className="navbar">
      <div className="brand-section" onClick={() => setActiveTab('recommendations')}>
        <div className="brand-logo-icon">
          <Compass size={24} />
        </div>
        <div>
          <div className="brand-title">
            CeylonVoyage <span className="brand-badge">ML Core</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
            Sri Lanka Personalized Tourism & Itinerary System
          </p>
        </div>
      </div>

      <nav className="nav-tabs">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              id={`nav-tab-${item.id}`}
              className={`nav-tab-btn ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="nav-right">
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          background: '#f5f3ff',
          borderRadius: '99px',
          fontSize: '0.84rem',
          fontWeight: 600,
          color: '#6d28d9',
          border: '1px solid rgba(124, 58, 237, 0.25)'
        }}>
          <UserCheck size={16} color="#7c3aed" />
          <span>Kasun Perera</span>
        </div>
      </div>
    </header>
  );
}
