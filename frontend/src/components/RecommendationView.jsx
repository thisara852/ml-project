import React, { useState, useEffect } from 'react';
import { Sparkles, MapPin, DollarSign, Calendar, Users, Sliders, ChevronRight, Compass, ShieldCheck, Sun } from 'lucide-react';

const INTEREST_OPTIONS = [
  'Nature/Hiking',
  'Beaches',
  'Adventure',
  'Heritage/Cultural',
  'Wildlife/Safari',
  'Scenic/Tea Country',
  'Waterfalls',
  'Surfing',
  'Photography'
];

const STARTING_HUBS = [
  { id: 'Colombo', label: 'Colombo (Commercial Capital)' },
  { id: 'Katunayake', label: 'Katunayake (Intl Airport - BIA)' },
  { id: 'Kandy', label: 'Kandy (Central Highlands)' },
  { id: 'Galle', label: 'Galle (Southern Coast)' },
  { id: 'Ella', label: 'Ella (Mountain Hub)' },
  { id: 'Jaffna', label: 'Jaffna (Northern Province)' },
  { id: 'Trincomalee', label: 'Trincomalee (East Coast)' }
];

export default function RecommendationView({ onSelectDestination, onAddToTrip }) {
  const [selectedInterests, setSelectedInterests] = useState(['Nature/Hiking', 'Adventure']);
  const [budgetTotal, setBudgetTotal] = useState(45000);
  const [durationDays, setDurationDays] = useState(3);
  const [travelers, setTravelers] = useState(2);
  const [startingLocation, setStartingLocation] = useState('Colombo');
  const [travelMonth, setTravelMonth] = useState(new Date().getMonth() + 1);

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/recommendations/hybrid', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interests: selectedInterests,
          budget_total_lkr: Number(budgetTotal),
          duration_days: Number(durationDays),
          num_travelers: Number(travelers),
          starting_location: startingLocation,
          travel_month: Number(travelMonth),
          top_n: 9
        })
      });
      const data = await res.json();
      if (Array.isArray(data)) {
        setRecommendations(data);
      }
    } catch (err) {
      console.error('Failed to fetch recommendations', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const toggleInterest = (interest) => {
    if (selectedInterests.includes(interest)) {
      if (selectedInterests.length > 1) {
        setSelectedInterests(selectedInterests.filter((i) => i !== interest));
      }
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  const dailyAllowance = Math.round(budgetTotal / (travelers * durationDays));

  return (
    <div>
      {/* Hero Banner */}
      <div className="hero-banner">
        <div className="hero-content">
          <div className="hero-tag">
            <Sparkles size={14} /> Hybrid Recommendation Engine
          </div>
          <h1 className="hero-title">
            Personalized Sri Lankan Journeys Powered by Machine Learning
          </h1>
          <p className="hero-desc">
            Our hybrid AI engine blends Content-Based interest matching, Collaborative Filtering, and K-Means Persona Clustering with real-time weather and budget constraints to curate your perfect island itinerary.
          </p>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <span className="explanation-pill">
              ✨ TF-IDF & Cosine Similarity
            </span>
            <span className="explanation-pill">
              👥 SVD Matrix Factorization
            </span>
            <span className="explanation-pill">
              🎯 K-Means Persona Archetypes
            </span>
            <span className="explanation-pill">
              🌦️ Live Weather-Aware
            </span>
          </div>
        </div>
      </div>

      <div className="content-grid">
        {/* Sidebar Parameters Panel */}
        <aside className="sidebar-panel">
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sliders size={18} color="#7c3aed" /> Trip Parameters
              </h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Real-time Re-rank</span>
            </div>

            {/* Travel Interests */}
            <div>
              <label className="filter-section-title">
                <span>Select Your Interests</span>
              </label>
              <div className="chips-group">
                {INTEREST_OPTIONS.map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    className={`chip-btn ${selectedInterests.includes(opt) ? 'active' : ''}`}
                    onClick={() => toggleInterest(opt)}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            {/* Starting Location */}
            <div className="input-group">
              <label className="input-label" htmlFor="starting-hub-select">Starting Hub / City</label>
              <select
                id="starting-hub-select"
                className="styled-select"
                value={startingLocation}
                onChange={(e) => setStartingLocation(e.target.value)}
              >
                {STARTING_HUBS.map((hub) => (
                  <option key={hub.id} value={hub.id}>{hub.label}</option>
                ))}
              </select>
            </div>

            {/* Duration Slider */}
            <div className="slider-container">
              <div className="slider-val-display">
                <span className="input-label">Travel Duration</span>
                <span>{durationDays} Days</span>
              </div>
              <input
                type="range"
                min="1"
                max="14"
                value={durationDays}
                onChange={(e) => setDurationDays(Number(e.target.value))}
              />
            </div>

            {/* Travelers Picker */}
            <div className="slider-container">
              <div className="slider-val-display">
                <span className="input-label">Travelers</span>
                <span>{travelers} {travelers === 1 ? 'Solo' : 'People'}</span>
              </div>
              <input
                type="range"
                min="1"
                max="8"
                value={travelers}
                onChange={(e) => setTravelers(Number(e.target.value))}
              />
            </div>

            {/* Total Budget Slider */}
            <div className="slider-container">
              <div className="slider-val-display">
                <span className="input-label">Total Budget (LKR)</span>
                <span>Rs. {budgetTotal.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="15000"
                max="250000"
                step="5000"
                value={budgetTotal}
                onChange={(e) => setBudgetTotal(Number(e.target.value))}
              />
              <div style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                <span>Daily allowance:</span>
                <span style={{ color: '#7c3aed', fontWeight: 700 }}>
                  Rs. {dailyAllowance.toLocaleString()} / person / day
                </span>
              </div>
            </div>

            {/* Month Picker */}
            <div className="input-group">
              <label className="input-label" htmlFor="month-select">Planned Travel Month</label>
              <select
                id="month-select"
                className="styled-select"
                value={travelMonth}
                onChange={(e) => setTravelMonth(Number(e.target.value))}
              >
                {[
                  'January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December'
                ].map((m, idx) => (
                  <option key={idx + 1} value={idx + 1}>{m}</option>
                ))}
              </select>
            </div>

            <button
              type="button"
              className="btn-primary"
              onClick={fetchRecommendations}
              disabled={loading}
              style={{ width: '100%' }}
            >
              <Sparkles size={18} /> {loading ? 'Computing Rankings...' : 'Update Recommendations'}
            </button>
          </div>
        </aside>

        {/* Right Feed: Ranked Destinations */}
        <section>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            background: '#ffffff',
            padding: '14px 20px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--bg-card-border)',
            boxShadow: 'var(--shadow-subtle)'
          }}>
            <div style={{ fontSize: '0.92rem', color: '#334155' }}>
              Showing top <strong style={{ color: '#0f172a' }}>{recommendations.length}</strong> ML ranked destinations for{' '}
              <span style={{ color: '#7c3aed', fontWeight: 700 }}>{selectedInterests.join(', ')}</span>
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-subtle)' }}>
              From {startingLocation}
            </div>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '12px' }}>🔄</div>
              <p>Executing Hybrid ML algorithms (TF-IDF + SVD + K-Means)...</p>
            </div>
          ) : (
            <div className="destinations-grid">
              {recommendations.map((dest) => (
                <div
                  key={dest.id}
                  className="dest-card"
                  onClick={() => onSelectDestination(dest)}
                >
                  <div className="dest-image-wrapper">
                    <img src={dest.image_url} alt={dest.name} className="dest-image" />
                    <div className="dest-image-overlay" />
                    
                    <span className="category-tag">
                      {dest.category}
                    </span>

                    <span className="match-badge">
                      <Sparkles size={13} /> {dest.match_percentage}% Match
                    </span>
                  </div>

                  <div className="dest-card-body">
                    <div className="dest-card-title">
                      <span>{dest.name}</span>
                      <span className="dest-rating">
                        ★ {dest.rating}
                      </span>
                    </div>

                    <div className="dest-meta-row">
                      <span className="dest-meta-item">
                        <MapPin size={14} color="#7c3aed" /> {dest.district} ({dest.distance_km} km)
                      </span>
                      <span className="dest-meta-item">
                        <DollarSign size={14} color="#9333ea" /> Rs. {Number(dest.avg_cost_lkr).toLocaleString()}
                      </span>
                    </div>

                    <p className="dest-description">{dest.description}</p>

                    <div className="dest-tags-list">
                      {dest.explanation_tags && dest.explanation_tags.map((tag, idx) => (
                        <span key={idx} className="explanation-pill">
                          {tag}
                        </span>
                      ))}
                    </div>

                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      marginTop: '8px',
                      borderTop: '1px solid #f1f0f7',
                      paddingTop: '12px'
                    }}>
                      <button
                        type="button"
                        className="btn-secondary"
                        style={{ flex: 1, padding: '8px', fontSize: '0.82rem', justifyContent: 'center' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectDestination(dest);
                        }}
                      >
                        View Details & Weather
                      </button>
                      <button
                        type="button"
                        className="btn-primary"
                        style={{ padding: '8px 14px', fontSize: '0.82rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onAddToTrip(dest);
                        }}
                      >
                        + Trip
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
