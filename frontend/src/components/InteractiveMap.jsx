import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { MapPin, Filter, Layers, Navigation } from 'lucide-react';

const CATEGORY_COLORS = {
  'Beaches': '#0ea5e9',
  'Nature/Hiking': '#8b5cf6',
  'Adventure': '#ec4899',
  'Heritage/Cultural': '#7c3aed',
  'Wildlife/Safari': '#f59e0b',
  'Scenic/Tea Country': '#a855f7',
  'Waterfalls': '#06b6d4'
};

export default function InteractiveMap({ onSelectDestination }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersLayerRef = useRef(null);

  const [destinations, setDestinations] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [categories, setCategories] = useState(['All']);

  useEffect(() => {
    // Fetch destinations
    fetch('/api/destinations/')
      .then((res) => res.json())
      .then((data) => {
        setDestinations(data);
        const uniqueCats = ['All', ...new Set(data.map((d) => d.category))];
        setCategories(uniqueCats);
      })
      .catch((err) => console.error('Failed to load destinations for map', err));
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    if (!mapInstanceRef.current) {
      // Initialize map centered on Sri Lanka
      const map = L.map(mapRef.current, {
        center: [7.8731, 80.7718],
        zoom: 8,
        minZoom: 7,
        maxZoom: 14,
        zoomControl: true
      });

      // CartoDB Voyager modern light tiles matching White & Purple AI design
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a> | OpenStreetMap',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(map);

      markersLayerRef.current = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
    }

    return () => {
      // Cleanup on unmount
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update markers when destinations or category filter changes
  useEffect(() => {
    if (!mapInstanceRef.current || !markersLayerRef.current) return;

    markersLayerRef.current.clearLayers();

    const filtered = selectedCategory === 'All'
      ? destinations
      : destinations.filter((d) => d.category === selectedCategory);

    filtered.forEach((dest) => {
      const color = CATEGORY_COLORS[dest.category] || '#7c3aed';

      // Custom SVG pin marker
      const customIcon = L.divIcon({
        className: 'custom-map-pin',
        html: `
          <div style="
            background: ${color};
            width: 28px;
            height: 28px;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35);
            border: 2px solid #ffffff;
            cursor: pointer;
          ">
            <div style="
              width: 8px;
              height: 8px;
              background: #ffffff;
              border-radius: 50%;
              transform: rotate(45deg);
            "></div>
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 28],
        popupAnchor: [0, -28]
      });

      const marker = L.marker([dest.latitude, dest.longitude], { icon: customIcon });

      const popupContent = document.createElement('div');
      popupContent.innerHTML = `
        <div style="width: 230px; font-family: 'Plus Jakarta Sans', sans-serif;">
          <img src="${dest.image_url}" style="width: 100%; height: 110px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;" />
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <strong style="color: #0f172a; font-size: 0.95rem;">${dest.name}</strong>
          </div>
          <div style="color: #7c3aed; font-size: 0.78rem; font-weight: 700; margin: 2px 0;">${dest.category} • ★ ${dest.rating}</div>
          <div style="color: #64748b; font-size: 0.78rem; margin-bottom: 8px;">${dest.district}, ${dest.province} Province</div>
          <button id="view-dest-btn-${dest.id}" style="
            width: 100%;
            background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.78rem;
            cursor: pointer;
            box-shadow: 0 3px 10px rgba(124, 58, 237, 0.3);
          ">Explore Details & Weather</button>
        </div>
      `;

      // Attach click event to popup button
      marker.bindPopup(popupContent);
      marker.on('popupopen', () => {
        const btn = document.getElementById(`view-dest-btn-${dest.id}`);
        if (btn) {
          btn.onclick = () => onSelectDestination(dest);
        }
      });

      markersLayerRef.current.addLayer(marker);
    });
  }, [destinations, selectedCategory, onSelectDestination]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '14px'
      }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', marginBottom: '4px' }}>
            Interactive Destination Map of Sri Lanka
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
            Explore tourist hotspots across all 9 provinces with category heat markers and geographical coordinates.
          </p>
        </div>

        {/* Category Filters */}
        <div className="chips-group">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              className={`chip-btn ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat !== 'All' && (
                <span style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: CATEGORY_COLORS[cat] || '#7c3aed',
                  display: 'inline-block'
                }} />
              )}
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Map Container */}
      <div className="glass-card" style={{ padding: '8px' }}>
        <div id="map-container" ref={mapRef}></div>
      </div>
    </div>
  );
}
