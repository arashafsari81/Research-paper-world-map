import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Search, Filter } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { mockCountries, mockYears } from '../data/mock';

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

const MapView = ({ onCountryClick, selectedCountry }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [yearFilter, setYearFilter] = useState('all');
  const [filteredCountries, setFilteredCountries] = useState(mockCountries);
  const [mapCenter, setMapCenter] = useState([20, 0]);
  const [mapZoom, setMapZoom] = useState(2);

  useEffect(() => {
    let filtered = mockCountries;

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(country => 
        country.name.toLowerCase().includes(term) ||
        country.universities.some(uni => 
          uni.name.toLowerCase().includes(term) ||
          uni.authors.some(author => 
            author.name.toLowerCase().includes(term) ||
            author.papers.some(paper => 
              paper.title.toLowerCase().includes(term)
            )
          )
        )
      );
    }

    // Apply year filter
    if (yearFilter !== 'all') {
      const year = parseInt(yearFilter);
      filtered = filtered.map(country => ({
        ...country,
        universities: country.universities.map(uni => ({
          ...uni,
          authors: uni.authors.map(author => ({
            ...author,
            papers: author.papers.filter(paper => paper.year === year)
          })).filter(author => author.papers.length > 0)
        })).filter(uni => uni.authors.length > 0)
      })).filter(country => country.universities.length > 0);
    }

    setFilteredCountries(filtered);
  }, [searchTerm, yearFilter]);

  useEffect(() => {
    if (selectedCountry) {
      const country = mockCountries.find(c => c.id === selectedCountry);
      if (country) {
        setMapCenter([country.lat, country.lng]);
        setMapZoom(5);
      }
    } else {
      setMapCenter([20, 0]);
      setMapZoom(2);
    }
  }, [selectedCountry]);

  const getMarkerSize = (paperCount) => {
    if (paperCount > 200) return 20;
    if (paperCount > 100) return 16;
    if (paperCount > 50) return 12;
    return 8;
  };

  const getMarkerColor = (paperCount) => {
    if (paperCount > 200) return '#0891b2';
    if (paperCount > 100) return '#14b8a6';
    if (paperCount > 50) return '#2dd4bf';
    return '#5eead4';
  };

  return (
    <div className="relative w-full h-screen">
      {/* Search and Filter Bar */}
      <div className="absolute top-6 left-6 z-[1000] bg-white rounded-lg shadow-xl p-4 w-96 space-y-3">
        <div className="flex items-center gap-2">
          <Search className="w-5 h-5 text-cyan-600" />
          <h3 className="font-semibold text-gray-800">Search & Filter</h3>
        </div>
        
        <div className="relative">
          <Input
            type="text"
            placeholder="Search country, university, author, or paper..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-cyan-600" />
          <Select value={yearFilter} onValueChange={setYearFilter}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Filter by year" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Years</SelectItem>
              {mockYears.map(year => (
                <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {searchTerm && (
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setSearchTerm('')}
            className="w-full"
          >
            Clear Search
          </Button>
        )}
      </div>

      {/* Legend */}
      <div className="absolute bottom-6 left-6 z-[1000] bg-white rounded-lg shadow-xl p-4 w-64">
        <h4 className="font-semibold text-gray-800 mb-3">Paper Count Legend</h4>
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-full" style={{ backgroundColor: '#5eead4' }}></div>
            <span className="text-sm text-gray-600">1-50 papers</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-full" style={{ backgroundColor: '#2dd4bf' }}></div>
            <span className="text-sm text-gray-600">51-100 papers</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-full" style={{ backgroundColor: '#14b8a6' }}></div>
            <span className="text-sm text-gray-600">101-200 papers</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-full" style={{ backgroundColor: '#0891b2' }}></div>
            <span className="text-sm text-gray-600">200+ papers</span>
          </div>
        </div>
      </div>

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
          <CircleMarker
            key={country.id}
            center={[country.lat, country.lng]}
            radius={getMarkerSize(country.paperCount)}
            fillColor={getMarkerColor(country.paperCount)}
            color="#fff"
            weight={2}
            opacity={1}
            fillOpacity={0.8}
            eventHandlers={{
              click: () => onCountryClick(country)
            }}
          >
            <Popup>
              <div className="text-center">
                <h3 className="font-semibold text-gray-800">{country.name}</h3>
                <p className="text-sm text-gray-600">{country.paperCount} papers</p>
                <p className="text-xs text-gray-500 mt-1">Click marker to view details</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapView;
