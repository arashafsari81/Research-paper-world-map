import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Component to handle map zoom and pan
function MapController({ center, zoom }) {
  const map = useMap();
  
  useEffect(() => {
    if (center) {
      map.setView(center, zoom, { animate: true });
    }
  }, [center, zoom, map]);
  
  return null;
}

// Custom marker with text label
function CountryMarker({ country, onClick, isSelected }) {
  const map = useMap();
  
  useEffect(() => {
    const size = getMarkerSize(country.paperCount);
    const divIcon = L.divIcon({
      html: `
        <div style="
          width: ${size * 2}px;
          height: ${size * 2}px;
          border-radius: 50%;
          background-color: #0891b2;
          border: 2px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2);
          cursor: pointer;
          transition: all 0.2s ease;
        ">
          <span style="
            color: white;
            font-weight: bold;
            font-size: ${size > 12 ? '12px' : '10px'};
          ">${country.paperCount}</span>
        </div>
      `,
      className: 'custom-marker',
      iconSize: [size * 2, size * 2],
      iconAnchor: [size, size]
    });

    const marker = L.marker([country.lat, country.lng], { icon: divIcon })
      .addTo(map)
      .on('click', () => onClick(country));

    // Add hover tooltip
    marker.bindTooltip(country.name, {
      permanent: false,
      direction: 'top',
      className: 'custom-tooltip'
    });

    return () => {
      map.removeLayer(marker);
    };
  }, [country, map, onClick, isSelected]);

  return null;
}

const getMarkerSize = (paperCount) => {
  if (paperCount > 200) return 20;
  if (paperCount > 100) return 16;
  if (paperCount > 50) return 12;
  return 8;
};

const MapView = ({ countries = [], onCountryClick, selectedCountry, searchTerm, yearFilter, onSearchChange, onYearChange, stats }) => {
  const [filteredCountries, setFilteredCountries] = useState([]);
  const [mapCenter, setMapCenter] = useState([20, 0]);
  const [mapZoom, setMapZoom] = useState(2);

  useEffect(() => {
    let filtered = countries;

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(country => 
        country.name.toLowerCase().includes(term)
      );
    }

    // Note: Year filtering will be handled by the backend API in the future
    // For now, we'll just filter by country name

    setFilteredCountries(filtered);
  }, [countries, searchTerm, yearFilter]);

  useEffect(() => {
    if (selectedCountry) {
      const country = countries.find(c => c.id === selectedCountry);
      if (country) {
        setMapCenter([country.lat, country.lng]);
        setMapZoom(5);
      }
    } else {
      setMapCenter([20, 0]);
      setMapZoom(2);
    }
  }, [selectedCountry, countries]);

  return (
    <div className="relative w-full h-screen">
      {/* Map */}
      <MapContainer 
        center={mapCenter} 
        zoom={mapZoom} 
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapController center={mapCenter} zoom={mapZoom} />
        
        {filteredCountries.map(country => (
          <CountryMarker
            key={country.id}
            country={country}
            onClick={onCountryClick}
            isSelected={selectedCountry === country.id}
          />
        ))}
      </MapContainer>

      {/* Custom tooltip styles */}
      <style>{`
        .custom-tooltip {
          background-color: rgba(8, 145, 178, 0.95);
          border: none;
          border-radius: 6px;
          color: white;
          font-weight: 600;
          padding: 6px 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .custom-tooltip::before {
          border-top-color: rgba(8, 145, 178, 0.95) !important;
        }
        .custom-marker:hover > div {
          transform: scale(1.1);
          box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
        }
      `}</style>
    </div>
  );
};

export default MapView;
