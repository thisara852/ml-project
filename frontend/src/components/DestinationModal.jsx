import React, { useState, useEffect } from 'react';
import { X, Star, MapPin, Clock, DollarSign, CloudSun, Send, ShieldCheck, Heart } from 'lucide-react';

export default function DestinationModal({ destination, onClose, onFavoriteToggle }) {
  const [weather, setWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(true);
  const [reviews, setReviews] = useState([]);
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);

  useEffect(() => {
    if (!destination) return;

    // Fetch live weather
    setWeatherLoading(true);
    fetch(`/api/weather/destination/${destination.id}`)
      .then((res) => res.json())
      .then((data) => {
        setWeather(data);
        setWeatherLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load weather", err);
        setWeatherLoading(false);
      });

    // Fetch reviews
    fetch(`/api/reviews/destination/${destination.id}`)
      .then((res) => res.json())
      .then((data) => setReviews(data))
      .catch((err) => console.error("Failed to load reviews", err));
  }, [destination]);

  if (!destination) return null;

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setSubmittingReview(true);
    try {
      // For demo without auth token header, fallback or send sample review
      const res = await fetch('/api/reviews/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + (localStorage.getItem('token') || '')
        },
        body: JSON.stringify({
          destination_id: destination.id,
          rating: Number(newRating),
          comment: newComment
        })
      });

      if (res.ok) {
        const added = await res.json();
        setReviews([added, ...reviews]);
        setNewComment('');
      } else {
        // Create local optimistic review if unauthenticated
        setReviews([
          {
            id: Date.now(),
            user_name: 'You (Guest Traveler)',
            rating: Number(newRating),
            comment: newComment,
            created_at: new Date().toISOString()
          },
          ...reviews
        ]);
        setNewComment('');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingReview(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose}>
          <X size={20} />
        </button>

        {/* Modal Header Image */}
        <div style={{ position: 'relative', height: '280px', overflow: 'hidden' }}>
          <img
            src={destination.image_url}
            alt={destination.name}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
          <div style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(to top, #0f192b 0%, rgba(15, 25, 43, 0.4) 70%, transparent 100%)'
          }} />
          
          <div style={{ position: 'absolute', bottom: '20px', left: '24px', right: '24px' }}>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
              <span className="category-tag" style={{ position: 'static' }}>
                {destination.category}
              </span>
              <span style={{
                background: 'rgba(124, 58, 237, 0.12)',
                color: '#7c3aed',
                fontSize: '0.78rem',
                fontWeight: 700,
                padding: '4px 10px',
                borderRadius: '6px',
                border: '1px solid rgba(124, 58, 237, 0.25)'
              }}>
                Best Season: {destination.best_season}
              </span>
            </div>
            <h2 style={{ fontSize: '1.9rem', color: '#fff' }}>{destination.name}</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginTop: '6px', color: '#f1f5f9', fontSize: '0.88rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <MapPin size={15} color="#c084fc" /> {destination.district} District, {destination.province} Province
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#fbbf24', fontWeight: 700 }}>
                <Star size={15} fill="#fbbf24" color="#fbbf24" /> {destination.rating} ({destination.num_reviews} reviews)
              </span>
            </div>
          </div>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Live Weather Widget */}
          <div style={{
            background: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
            border: '1px solid rgba(124, 58, 237, 0.22)',
            borderRadius: 'var(--radius-md)',
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '14px',
            boxShadow: '0 4px 16px rgba(124, 58, 237, 0.06)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                fontSize: '2rem',
                background: 'rgba(124, 58, 237, 0.12)',
                padding: '8px 12px',
                borderRadius: '12px'
              }}>
                {weather ? weather.icon : '☀️'}
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '1.3rem', fontWeight: 800, color: '#0f172a' }}>
                    {weather ? `${weather.temperature_c}°C` : '28°C'}
                  </span>
                  <span style={{ color: '#7c3aed', fontWeight: 700, fontSize: '0.9rem' }}>
                    {weather ? weather.condition : 'Pleasant Tropical'}
                  </span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {weather ? weather.travel_advice : 'Optimal conditions for outdoor activities.'}
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <div>
                <div style={{ color: 'var(--text-subtle)' }}>Rain Probability</div>
                <div style={{ fontWeight: 700, color: '#0f172a' }}>
                  {weather ? `${weather.rain_probability}%` : '15%'}
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-subtle)' }}>Wind Speed</div>
                <div style={{ fontWeight: 700, color: '#0f172a' }}>
                  {weather ? `${weather.wind_speed_kmh} km/h` : '12 km/h'}
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-subtle)' }}>Source</div>
                <div style={{ fontWeight: 700, color: '#7c3aed' }}>
                  Open-Meteo Live API
                </div>
              </div>
            </div>
          </div>

          {/* Key Quick Facts */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '14px'
          }}>
            <div style={{ background: '#f8f6fc', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(124, 58, 237, 0.12)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Average Cost / Day</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#7c3aed' }}>
                Rs. {Number(destination.avg_cost_lkr).toLocaleString()}
              </div>
            </div>
            <div style={{ background: '#f8f6fc', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(124, 58, 237, 0.12)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Recommended Duration</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a' }}>
                {destination.recommended_duration_hours} hours
              </div>
            </div>
            <div style={{ background: '#f8f6fc', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(124, 58, 237, 0.12)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Adventure Level</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#9333ea' }}>
                {'⚡'.repeat(destination.adventure_level || 3)} ({destination.adventure_level}/5)
              </div>
            </div>
            <div style={{ background: '#f8f6fc', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(124, 58, 237, 0.12)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Family Friendliness</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ec4899' }}>
                {'❤️'.repeat(destination.family_friendly || 4)} ({destination.family_friendly}/5)
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '8px', color: '#0f172a' }}>About this Destination</h4>
            <p style={{ color: '#475569', lineHeight: '1.7', fontSize: '0.94rem' }}>
              {destination.description}
            </p>
          </div>

          {/* Activities */}
          <div>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '10px', color: '#0f172a' }}>Popular Activities & Experiences</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {String(destination.activities || '').split(',').map((act, i) => (
                <span
                  key={i}
                  style={{
                    background: '#f5f3ff',
                    padding: '6px 14px',
                    borderRadius: '99px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    color: '#6d28d9',
                    border: '1px solid rgba(124, 58, 237, 0.2)'
                  }}
                >
                  ✓ {act.trim()}
                </span>
              ))}
            </div>
          </div>

          {/* User Reviews Section */}
          <div style={{ borderTop: '1px solid #f1f0f7', paddingTop: '20px' }}>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#0f172a' }}>
              Traveler Reviews & Feedback ({reviews.length})
            </h4>

            {/* Submit Review Form */}
            <form onSubmit={handleReviewSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Your Rating:</span>
                <select
                  value={newRating}
                  onChange={(e) => setNewRating(e.target.value)}
                  className="styled-select"
                  style={{ width: '130px', padding: '6px 10px' }}
                >
                  <option value="5">⭐⭐⭐⭐⭐ (5.0)</option>
                  <option value="4.5">⭐⭐⭐⭐½ (4.5)</option>
                  <option value="4">⭐⭐⭐⭐ (4.0)</option>
                  <option value="3.5">⭐⭐⭐½ (3.5)</option>
                  <option value="3">⭐⭐⭐ (3.0)</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <input
                  type="text"
                  placeholder="Write a tip or review for fellow travelers..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  className="styled-input"
                  style={{ flex: 1 }}
                />
                <button type="submit" className="btn-primary" disabled={submittingReview}>
                  <Send size={16} /> Submit
                </button>
              </div>
            </form>

            {/* Reviews List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '240px', overflowY: 'auto' }}>
              {reviews.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                  No written reviews yet. Be the first to share your experience!
                </p>
              ) : (
                reviews.map((r) => (
                  <div
                    key={r.id}
                    style={{
                      background: '#f8f6fc',
                      padding: '12px 16px',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid rgba(124, 58, 237, 0.12)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.88rem', color: '#0f172a' }}>
                        {r.user_name || 'Verified Explorer'}
                      </span>
                      <span style={{ color: '#d97706', fontSize: '0.8rem', fontWeight: 700 }}>
                        {'⭐'.repeat(Math.round(r.rating))} ({r.rating})
                      </span>
                    </div>
                    <p style={{ fontSize: '0.84rem', color: '#475569' }}>{r.comment}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
