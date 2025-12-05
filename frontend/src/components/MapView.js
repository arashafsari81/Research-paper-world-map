import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import ApiService from '../services/api';

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
        <div class="country-marker-wrapper" style="
          width: ${size * 2}px;
          height: ${size * 2}px;
          position: relative;
        ">
          <div style="
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background-color: #0891b2;
            border: 2px solid white;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: absolute;
            top: 0;
            left: 0;
          ">
            <span style="
              color: white;
              font-weight: bold;
              font-size: ${size > 20 ? '16px' : size > 15 ? '14px' : '12px'};
              user-select: none;
            ">${country.paperCount}</span>
          </div>
        </div>
      `,
      className: '',
      iconSize: [size * 2, size * 2],
      iconAnchor: [size, size],
      popupAnchor: [0, -size]
    });

    const marker = L.marker([country.lat, country.lng], { icon: divIcon })
      .addTo(map)
      .on('click', () => onClick(country));

    // Add hover tooltip
    marker.bindTooltip(country.name, {
      permanent: false,
      direction: 'top',
      className: 'custom-tooltip',
      offset: [0, -10]
    });

    return () => {
      map.removeLayer(marker);
    };
  }, [country, map, onClick, isSelected]);

  return null;
}

const getMarkerSize = (paperCount) => {
  if (paperCount > 2000) return 30;
  if (paperCount > 500) return 24;
  if (paperCount > 100) return 18;
  return 14;
};

const MapView = ({ onCountryClick, selectedCountry, searchTerm, yearFilter }) => {
  const [countries, setCountries] = useState([]);
  const [filteredCountries, setFilteredCountries] = useState([]);
  const [mapCenter, setMapCenter] = useState([20, 0]);
  const [mapZoom, setMapZoom] = useState(2);
  const [loading, setLoading] = useState(true);

  // Load countries on mount and when year filter changes
  useEffect(() => {
    const loadCountries = async () => {
      try {
        setLoading(true);
        // Pass yearFilter as-is (can be single year or range like "2021-2024")
        const yearParam = yearFilter !== 'all' ? yearFilter : null;
        const data = await ApiService.getCountries(yearParam);
        setCountries(data);
        setFilteredCountries(data);
      } catch (err) {
        console.error('Error loading countries:', err);
      } finally {
        setLoading(false);
      }
    };

    loadCountries();
  }, [yearFilter]);

  // Apply search and year filters
  useEffect(() => {
    if (!countries || countries.length === 0) {
      setFilteredCountries([]);
      return;
    }

    let filtered = [...countries];

    // Apply search filter - search by country name
    if (searchTerm && searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(country => 
        country.name.toLowerCase().includes(term)
      );
    }

    // Note: Year filtering requires backend support to filter papers by year
    // For now, we show all countries but the year filter will apply when viewing details

    setFilteredCountries(filtered);
  }, [searchTerm, yearFilter, countries]);

  // Update map view when country is selected
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

  const handleCountryClick = async (country) => {
    try {
      // Fetch full country data with universities (yearFilter can be single year or range)
      const yearParam = yearFilter !== 'all' ? yearFilter : null;
      const fullCountry = await ApiService.getCountry(country.id, yearParam);
      onCountryClick({...country, ...fullCountry});
    } catch (err) {
      console.error('Error loading country details:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-gray-700">Loading map data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="absolute inset-0 w-full h-full">
      <MapContainer 
        center={mapCenter} 
        zoom={mapZoom} 
        style={{ height: '100%', width: '100%' }}
        zoomControl={false}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
        <MapController center={mapCenter} zoom={mapZoom} />
        
        {filteredCountries.map(country => (
          <CountryMarker
            key={country.id}
            country={country}
            onClick={handleCountryClick}
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
