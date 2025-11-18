import React, { useState, useEffect } from 'react';
import './App.css';
import MapView from './components/MapView';
import SidePanel from './components/SidePanel';
import Header from './components/Header';
import ApiService from './services/api';

function App() {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [selectedUniversity, setSelectedUniversity] = useState(null);
  const [selectedAuthor, setSelectedAuthor] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [yearFilter, setYearFilter] = useState('all');
  const [stats, setStats] = useState(null);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [statsData, countriesData] = await Promise.all([
          ApiService.fetchStats(),
          ApiService.fetchCountries()
        ]);
        setStats(statsData);
        setCountries(countriesData);
        setError(null);
      } catch (err) {
        console.error('Failed to load data:', err);
        setError('Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleCountryClick = async (countryData) => {
    try {
      // If we only have basic country data, fetch full details
      let fullCountryData = countryData;
      if (!countryData.universities) {
        fullCountryData = await ApiService.fetchCountry(countryData.id);
      }
      
      setSelectedCountry(fullCountryData);
      setSelectedUniversity(null);
      setSelectedAuthor(null);
      setIsPanelOpen(true);
    } catch (err) {
      console.error('Failed to load country details:', err);
      setError('Failed to load country details.');
    }
  };

  const handleUniversityClick = async (university) => {
    try {
      // Fetch full university details with authors
      const fullUniversityData = await ApiService.fetchUniversity(
        selectedCountry.id, 
        university.id
      );
      setSelectedUniversity(fullUniversityData);
      setSelectedAuthor(null);
    } catch (err) {
      console.error('Failed to load university details:', err);
      setError('Failed to load university details.');
    }
  };

  const handleAuthorClick = async (author) => {
    try {
      // Fetch full author details with papers
      const fullAuthorData = await ApiService.fetchAuthor(
        selectedCountry.id,
        selectedUniversity.id,
        author.id
      );
      setSelectedAuthor(fullAuthorData);
    } catch (err) {
      console.error('Failed to load author details:', err);
      setError('Failed to load author details.');
    }
  };

  const handleBack = (level) => {
    if (level === 'country') {
      setSelectedUniversity(null);
      setSelectedAuthor(null);
    } else if (level === 'university') {
      setSelectedAuthor(null);
    }
  };

  const handleClosePanel = () => {
    setIsPanelOpen(false);
    setTimeout(() => {
      setSelectedCountry(null);
      setSelectedUniversity(null);
      setSelectedAuthor(null);
    }, 300);
  };

  if (loading) {
    return (
      <div className="App flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading research data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Error Loading Data</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Header 
        searchTerm={searchTerm}
        yearFilter={yearFilter}
        onSearchChange={setSearchTerm}
        onYearChange={setYearFilter}
        stats={stats}
      />
      <div className="pt-32">
        <MapView 
          countries={countries}
          onCountryClick={handleCountryClick}
          selectedCountry={selectedCountry?.id}
          searchTerm={searchTerm}
          yearFilter={yearFilter}
          onSearchChange={setSearchTerm}
          onYearChange={setYearFilter}
          stats={stats}
        />
      </div>
      <SidePanel
        isOpen={isPanelOpen}
        onClose={handleClosePanel}
        selectedCountry={selectedCountry}
        selectedUniversity={selectedUniversity}
        selectedAuthor={selectedAuthor}
        onUniversityClick={handleUniversityClick}
        onAuthorClick={handleAuthorClick}
        onBack={handleBack}
      />
    </div>
  );
}

export default App;
