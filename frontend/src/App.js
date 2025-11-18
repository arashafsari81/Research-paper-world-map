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

  const handleCountryClick = (country) => {
    setSelectedCountry(country);
    setSelectedUniversity(null);
    setSelectedAuthor(null);
    setIsPanelOpen(true);
  };

  const handleUniversityClick = (university) => {
    setSelectedUniversity(university);
    setSelectedAuthor(null);
  };

  const handleAuthorClick = (author) => {
    setSelectedAuthor(author);
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
