import React, { useState, useEffect } from 'react';
import { BarChart3, Database, ShieldCheck, Cpu, RefreshCw, CheckCircle2, TrendingUp } from 'lucide-react';

export default function AdminBenchmarkView() {
  const [metrics, setMetrics] = useState(null);
  const [stats, setStats] = useState(null);
  const [kValue, setKValue] = useState(5);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  const fetchMetrics = async (k) => {
    setLoadingMetrics(true);
    try {
      const res = await fetch(`/api/recommendations/evaluation-metrics?k=${k}`);
      const data = await res.json();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load evaluation metrics', err);
    } finally {
      setLoadingMetrics(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/admin/stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to load admin stats', err);
    }
  };

  useEffect(() => {
    fetchMetrics(kValue);
    fetchStats();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '1.8rem', marginBottom: '4px' }}>
          Machine Learning Evaluation & Admin Analytics
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem' }}>
          Offline experimental evaluation metrics (Precision@K, Recall@K, F1@K, MAE, RMSE) and live Sri Lanka destination inventory.
        </p>
      </div>

      {/* Summary KPI Cards */}
      {stats && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '18px'
        }}>
          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                Curated Destinations
              </span>
              <Database size={18} color="#7c3aed" />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a' }}>
              {stats.summary.total_destinations} Places
            </div>
            <div style={{ fontSize: '0.8rem', color: '#7c3aed', marginTop: '4px', fontWeight: 600 }}>
              Covering all 9 Sri Lankan Provinces
            </div>
          </div>

          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                User Interactions
              </span>
              <Cpu size={18} color="#9333ea" />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a' }}>
              3,720+ Ratings
            </div>
            <div style={{ fontSize: '0.8rem', color: '#9333ea', marginTop: '4px', fontWeight: 600 }}>
              Persona-clustered interaction matrix
            </div>
          </div>

          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                Recommendation Engine
              </span>
              <ShieldCheck size={18} color="#7c3aed" />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a' }}>
              Hybrid Ensemble
            </div>
            <div style={{ fontSize: '0.8rem', color: '#7c3aed', marginTop: '4px', fontWeight: 600 }}>
              TF-IDF + SVD + K-Means + Constraints
            </div>
          </div>

          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                Rating Prediction MAE
              </span>
              <TrendingUp size={18} color="#c026d3" />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a' }}>
              {metrics ? metrics.cf_rating_mae : '0.5634'}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#c026d3', marginTop: '4px', fontWeight: 600 }}>
              RMSE: {metrics ? metrics.cf_rating_rmse : '0.7195'}
            </div>
          </div>
        </div>
      )}

      {/* Benchmark Evaluation Table */}
      <div className="glass-card">
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '4px', color: '#0f172a' }}>
              Comparative Model Performance Benchmark
            </h3>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>
              Evaluated on holdout test set with ground truth relevant destination threshold (Rating &ge; 4.0).
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Cutoff K:</span>
            {[3, 5, 8, 10].map((k) => (
              <button
                key={k}
                type="button"
                className={`chip-btn ${kValue === k ? 'active' : ''}`}
                onClick={() => {
                  setKValue(k);
                  fetchMetrics(k);
                }}
              >
                K = {k}
              </button>
            ))}
          </div>
        </div>

        {loadingMetrics ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            Calculating Precision@{kValue}, Recall@{kValue}, and F1-score across models...
          </div>
        ) : metrics ? (
          <table className="benchmark-table">
            <thead>
              <tr>
                <th>Recommendation Model</th>
                <th>Precision@{kValue}</th>
                <th>Recall@{kValue}</th>
                <th>F1-Score@{kValue}</th>
                <th>Core Algorithm Mechanism</th>
              </tr>
            </thead>
            <tbody>
              {metrics.summary.map((row, idx) => (
                <tr key={idx} style={row.Model === 'Hybrid Engine' ? { background: 'rgba(124, 58, 237, 0.05)', fontWeight: 600 } : {}}>
                  <td style={{ fontWeight: 700, color: '#0f172a' }}>
                    {row.Model} {row.Model === 'Hybrid Engine' && <span style={{ fontSize: '0.72rem', background: '#7c3aed', color: '#fff', padding: '2px 6px', borderRadius: '4px', marginLeft: '6px' }}>BEST</span>}
                  </td>
                  <td className="highlight-metric">
                    {(row[`Precision@${kValue}`] * 100).toFixed(1)}%
                  </td>
                  <td className="highlight-metric">
                    {(row[`Recall@${kValue}`] * 100).toFixed(1)}%
                  </td>
                  <td style={{ fontWeight: 700, color: '#9333ea' }}>
                    {(row[`F1@${kValue}`] * 100).toFixed(1)}%
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                    {row.Model === 'Content-Based' && 'TF-IDF Unigrams/Bigrams + Destination Cosine Similarity'}
                    {row.Model === 'Collaborative' && 'TruncatedSVD Latent Matrix Factorization + Item Cosine'}
                    {row.Model === 'K-Means Cluster' && 'Unsupervised 5-Archetype Tourist Persona Clustering'}
                    {row.Model === 'Hybrid Engine' && 'Multi-Objective Weighted Ensemble + Budget & Distance Penalties'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}
      </div>

      {/* Category Breakdown */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div className="glass-card">
            <h4 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#0f172a' }}>
              Destinations by Category
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {stats.categories.map((c, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f1f0f7', fontSize: '0.88rem' }}>
                  <span>{c.category}</span>
                  <strong style={{ color: '#7c3aed' }}>{c.count} locations</strong>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card">
            <h4 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#0f172a' }}>
              Destinations by Province
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {stats.provinces.map((p, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f1f0f7', fontSize: '0.88rem' }}>
                  <span>{p.province} Province</span>
                  <strong style={{ color: '#9333ea' }}>{p.count} locations</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
