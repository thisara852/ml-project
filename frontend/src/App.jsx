import React, { useState } from 'react';
import Navbar from './components/Navbar';
import RecommendationView from './components/RecommendationView';
import InteractiveMap from './components/InteractiveMap';
import TripPlannerView from './components/TripPlannerView';
import AdminBenchmarkView from './components/AdminBenchmarkView';
import DestinationModal from './components/DestinationModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('recommendations');
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [tripCart, setTripCart] = useState([]);
  const [toastMessage, setToastMessage] = useState('');

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3500);
  };

  const handleAddToTrip = (dest) => {
    if (!tripCart.some((d) => d.id === dest.id)) {
      setTripCart([...tripCart, dest]);
      showToast(`Added "${dest.name}" to your trip plan!`);
    } else {
      showToast(`"${dest.name}" is already in your trip plan.`);
    }
  };

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {activeTab === 'recommendations' && (
          <RecommendationView
            onSelectDestination={(dest) => setSelectedDestination(dest)}
            onAddToTrip={handleAddToTrip}
          />
        )}

        {activeTab === 'map' && (
          <InteractiveMap
            onSelectDestination={(dest) => setSelectedDestination(dest)}
          />
        )}

        {activeTab === 'planner' && (
          <TripPlannerView
            tripCart={tripCart}
            onSelectDestination={(dest) => setSelectedDestination(dest)}
          />
        )}

        {activeTab === 'benchmarks' && (
          <AdminBenchmarkView />
        )}
      </main>

      {/* Destination Details & Live Weather Modal */}
      {selectedDestination && (
        <DestinationModal
          destination={selectedDestination}
          onClose={() => setSelectedDestination(null)}
          onFavoriteToggle={() => showToast('Favorite updated!')}
        />
      )}

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          background: 'linear-gradient(135deg, #7c3aed 0%, #9333ea 100%)',
          color: '#ffffff',
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          boxShadow: '0 10px 30px rgba(124, 58, 237, 0.35)',
          zIndex: 3000,
          fontWeight: 600,
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          animation: 'fadeIn 0.3s ease-in-out'
        }}>
          <span>✨</span> {toastMessage}
        </div>
      )}
    </div>
  );
}
