import React, { useState, useEffect } from 'react';
import { Calendar, Clock, DollarSign, Car, Hotel, Utensils, Ticket, ShieldAlert, CheckCircle2, BookmarkCheck, ArrowRight } from 'lucide-react';

export default function TripPlannerView({ tripCart, onSelectDestination }) {
  const [durationDays, setDurationDays] = useState(3);
  const [startingLocation, setStartingLocation] = useState('Colombo');
  const [travelStyle, setTravelStyle] = useState('mid_range');
  const [transportMode, setTransportMode] = useState('car_with_driver');
  const [numTravelers, setNumTravelers] = useState(2);
  const [budgetLkr, setBudgetLkr] = useState(60000);

  const [itineraryData, setItineraryData] = useState(null);
  const [budgetData, setBudgetData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const generateTripPlan = async () => {
    setLoading(true);
    setSavedSuccess(false);
    try {
      const destIds = tripCart.map((d) => d.id);
      const res = await fetch('/api/trips/generate-itinerary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          destination_ids: destIds.length > 0 ? destIds : null,
          duration_days: Number(durationDays),
          starting_location: startingLocation,
          budget_total_lkr: Number(budgetLkr),
          num_travelers: Number(numTravelers)
        })
      });

      const data = await res.json();
      setItineraryData(data.itinerary);
      setBudgetData(data.budget_estimation);
    } catch (err) {
      console.error('Failed to generate trip plan', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateTripPlan();
  }, []);

  const handleSaveTrip = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 4000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', marginBottom: '4px' }}>
            Intelligent Travel Itinerary & Budget Planner
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem' }}>
            Automated multi-day scheduling optimized by geographic proximity, transit corridors, and itemized Sri Lankan travel costs.
          </p>
        </div>

        {itineraryData && (
          <button
            type="button"
            className="btn-primary"
            onClick={handleSaveTrip}
          >
            <BookmarkCheck size={18} /> {savedSuccess ? 'Saved to Profile!' : 'Save This Itinerary'}
          </button>
        )}
      </div>

      {/* Control Configuration Bar */}
      <div className="glass-card" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
        gap: '16px',
        alignItems: 'end'
      }}>
        <div className="input-group">
          <label className="input-label">Starting Location</label>
          <select
            className="styled-select"
            value={startingLocation}
            onChange={(e) => setStartingLocation(e.target.value)}
          >
            <option value="Colombo">Colombo</option>
            <option value="Katunayake">Katunayake (Airport)</option>
            <option value="Kandy">Kandy</option>
            <option value="Galle">Galle</option>
            <option value="Ella">Ella</option>
          </select>
        </div>

        <div className="input-group">
          <label className="input-label">Duration</label>
          <select
            className="styled-select"
            value={durationDays}
            onChange={(e) => setDurationDays(Number(e.target.value))}
          >
            <option value="1">1 Day Express</option>
            <option value="2">2 Days Weekend</option>
            <option value="3">3 Days Classic</option>
            <option value="4">4 Days Explorer</option>
            <option value="5">5 Days Scenic</option>
            <option value="7">7 Days Grand Tour</option>
          </select>
        </div>

        <div className="input-group">
          <label className="input-label">Travel Style</label>
          <select
            className="styled-select"
            value={travelStyle}
            onChange={(e) => setTravelStyle(e.target.value)}
          >
            <option value="budget">Budget Backpacker</option>
            <option value="mid_range">Comfort Mid-Range</option>
            <option value="luxury">Luxury Boutique & Resorts</option>
          </select>
        </div>

        <div className="input-group">
          <label className="input-label">Transport Mode</label>
          <select
            className="styled-select"
            value={transportMode}
            onChange={(e) => setTransportMode(e.target.value)}
          >
            <option value="car_with_driver">Private Car + English Driver</option>
            <option value="public_transit">Scenic Train & Intercity Bus</option>
            <option value="tuktuk">Local Tuk-tuk</option>
          </select>
        </div>

        <div className="input-group">
          <label className="input-label">Travelers</label>
          <select
            className="styled-select"
            value={numTravelers}
            onChange={(e) => setNumTravelers(Number(e.target.value))}
          >
            <option value="1">Solo Explorer (1)</option>
            <option value="2">Couple / Pair (2)</option>
            <option value="3">Small Group (3)</option>
            <option value="4">Family (4)</option>
          </select>
        </div>

        <button
          type="button"
          className="btn-primary"
          style={{ height: '46px' }}
          onClick={generateTripPlan}
          disabled={loading}
        >
          {loading ? 'Optimizing Route...' : 'Regenerate Itinerary'}
        </button>
      </div>

      {/* Main Itinerary & Budget Two-Column Display */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '24px', alignItems: 'start' }}>
        {/* Left Column: Day-by-Day Timeline */}
        <div>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '12px' }}>🗺️</div>
              <p>Sequencing travel corridor and daily morning/evening schedules...</p>
            </div>
          ) : itineraryData ? (
            <div className="timeline-container">
              {itineraryData.days.map((day) => (
                <div key={day.day} className="timeline-day-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '14px' }}>
                    <div>
                      <span style={{
                        background: 'rgba(124, 58, 237, 0.12)',
                        color: '#7c3aed',
                        padding: '4px 10px',
                        borderRadius: '99px',
                        fontSize: '0.8rem',
                        fontWeight: 800,
                        marginRight: '8px',
                        border: '1px solid rgba(124, 58, 237, 0.25)'
                      }}>
                        DAY {day.day}
                      </span>
                      <strong style={{ fontSize: '1.25rem', color: '#0f172a' }}>
                        {day.title}
                      </strong>
                    </div>
                    <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                      Est. Transit: ~{day.estimated_transit_hours} hrs
                    </span>
                  </div>

                  {/* Morning */}
                  <div className="timeline-slot">
                    <div className="timeline-time-badge">
                      <Clock size={15} /> {day.schedule.morning.time}
                    </div>
                    <div>
                      <h4 style={{ color: '#0f172a', fontSize: '0.98rem', marginBottom: '4px' }}>
                        {day.schedule.morning.activity}
                      </h4>
                      <p style={{ color: '#475569', fontSize: '0.86rem', lineHeight: '1.5', marginBottom: '4px' }}>
                        {day.schedule.morning.description}
                      </p>
                      <div style={{ fontSize: '0.78rem', color: '#7c3aed', fontWeight: 600 }}>
                        💡 Tip: {day.schedule.morning.tip}
                      </div>
                    </div>
                  </div>

                  {/* Afternoon */}
                  <div className="timeline-slot">
                    <div className="timeline-time-badge">
                      <Clock size={15} /> {day.schedule.afternoon.time}
                    </div>
                    <div>
                      <h4 style={{ color: '#0f172a', fontSize: '0.98rem', marginBottom: '4px' }}>
                        {day.schedule.afternoon.activity}
                      </h4>
                      <p style={{ color: '#475569', fontSize: '0.86rem', lineHeight: '1.5', marginBottom: '4px' }}>
                        {day.schedule.afternoon.description}
                      </p>
                      <div style={{ fontSize: '0.78rem', color: '#7c3aed', fontWeight: 600 }}>
                        💡 Tip: {day.schedule.afternoon.tip}
                      </div>
                    </div>
                  </div>

                  {/* Evening */}
                  <div className="timeline-slot">
                    <div className="timeline-time-badge">
                      <Clock size={15} /> {day.schedule.evening.time}
                    </div>
                    <div>
                      <h4 style={{ color: '#0f172a', fontSize: '0.98rem', marginBottom: '4px' }}>
                        {day.schedule.evening.activity}
                      </h4>
                      <p style={{ color: '#475569', fontSize: '0.86rem', lineHeight: '1.5', marginBottom: '4px' }}>
                        {day.schedule.evening.description}
                      </p>
                      <div style={{ fontSize: '0.78rem', color: '#9333ea', fontWeight: 600 }}>
                        🌙 Overnight: {day.recommended_overnight_stay}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        {/* Right Column: Itemized Budget Estimator */}
        {budgetData && (
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px', position: 'sticky', top: '96px' }}>
            <div>
              <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '4px' }}>
                Estimated Trip Expenditure
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                <span style={{ fontSize: '2rem', fontWeight: 800, color: '#7c3aed' }}>
                  Rs. {Number(budgetData.total_estimated_lkr).toLocaleString()}
                </span>
                <span style={{ fontSize: '0.95rem', color: 'var(--text-muted)' }}>
                  (~${budgetData.total_estimated_usd} USD)
                </span>
              </div>
              <div style={{ fontSize: '0.82rem', color: '#7c3aed', fontWeight: 600, marginTop: '2px' }}>
                Rs. {Number(budgetData.cost_per_person_lkr).toLocaleString()} per person ({numTravelers} travelers)
              </div>
            </div>

            {/* Budget status alert */}
            <div style={{
              background: '#f5f3ff',
              border: '1px solid rgba(124, 58, 237, 0.25)',
              borderRadius: 'var(--radius-sm)',
              padding: '10px 14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '0.84rem',
              color: '#6d28d9',
              fontWeight: 600
            }}>
              <CheckCircle2 size={16} color="#7c3aed" />
              <span>{budgetData.budget_status}</span>
            </div>

            {/* Expense Breakdown Rows */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {/* Accommodation */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', marginBottom: '4px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#0f172a', fontWeight: 600 }}>
                    <Hotel size={14} color="#6366f1" /> Accommodation ({budgetData.breakdown.accommodation.percentage}%)
                  </span>
                  <span style={{ fontWeight: 700 }}>
                    Rs. {Number(budgetData.breakdown.accommodation.amount_lkr).toLocaleString()}
                  </span>
                </div>
                <div style={{ height: '6px', background: '#f1f0f7', borderRadius: '99px', overflow: 'hidden' }}>
                  <div style={{ width: `${budgetData.breakdown.accommodation.percentage}%`, height: '100%', background: '#6366f1' }} />
                </div>
              </div>

              {/* Transportation */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', marginBottom: '4px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#0f172a', fontWeight: 600 }}>
                    <Car size={14} color="#f59e0b" /> Transport ({budgetData.breakdown.transportation.percentage}%)
                  </span>
                  <span style={{ fontWeight: 700 }}>
                    Rs. {Number(budgetData.breakdown.transportation.amount_lkr).toLocaleString()}
                  </span>
                </div>
                <div style={{ height: '6px', background: '#f1f0f7', borderRadius: '99px', overflow: 'hidden' }}>
                  <div style={{ width: `${budgetData.breakdown.transportation.percentage}%`, height: '100%', background: '#f59e0b' }} />
                </div>
              </div>

              {/* Food */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', marginBottom: '4px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#0f172a', fontWeight: 600 }}>
                    <Utensils size={14} color="#7c3aed" /> Dining & Food ({budgetData.breakdown.food_and_dining.percentage}%)
                  </span>
                  <span style={{ fontWeight: 700 }}>
                    Rs. {Number(budgetData.breakdown.food_and_dining.amount_lkr).toLocaleString()}
                  </span>
                </div>
                <div style={{ height: '6px', background: '#f1f0f7', borderRadius: '99px', overflow: 'hidden' }}>
                  <div style={{ width: `${budgetData.breakdown.food_and_dining.percentage}%`, height: '100%', background: '#7c3aed' }} />
                </div>
              </div>

              {/* Activities */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', marginBottom: '4px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#0f172a', fontWeight: 600 }}>
                    <Ticket size={14} color="#c026d3" /> Tickets & Safaris ({budgetData.breakdown.activities_and_tickets.percentage}%)
                  </span>
                  <span style={{ fontWeight: 700 }}>
                    Rs. {Number(budgetData.breakdown.activities_and_tickets.amount_lkr).toLocaleString()}
                  </span>
                </div>
                <div style={{ height: '6px', background: '#f1f0f7', borderRadius: '99px', overflow: 'hidden' }}>
                  <div style={{ width: `${budgetData.breakdown.activities_and_tickets.percentage}%`, height: '100%', background: '#c026d3' }} />
                </div>
              </div>

              {/* Contingency */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', marginBottom: '4px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#64748b' }}>
                    <ShieldAlert size={14} color="#94a3b8" /> Contingency buffer (8%)
                  </span>
                  <span style={{ fontWeight: 700, color: '#64748b' }}>
                    Rs. {Number(budgetData.breakdown.contingency_buffer.amount_lkr).toLocaleString()}
                  </span>
                </div>
                <div style={{ height: '6px', background: '#f1f0f7', borderRadius: '99px', overflow: 'hidden' }}>
                  <div style={{ width: `${budgetData.breakdown.contingency_buffer.percentage}%`, height: '100%', background: '#94a3b8' }} />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
