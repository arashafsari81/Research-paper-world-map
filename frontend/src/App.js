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
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [yearFilter, setYearFilter] = useState('all');
  const [appliedSearchTerm, setAppliedSearchTerm] = useState('');
  const [appliedYearFilter, setAppliedYearFilter] = useState('all');
  
  const [stats, setStats] = useState({
    totalPapers: 0,
    totalCountries: 0,
    totalUniversities: 0,
    totalAuthors: 0,
    totalCitations: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load stats on mount and when year filter changes
  useEffect(() => {
    const loadStats = async () => {
      try {
        setLoading(true);
        // Pass the year filter as-is (can be single year or range like "2021-2024")
        const yearParam = appliedYearFilter !== 'all' ? appliedYearFilter : null;
        const data = await ApiService.getStats(yearParam);
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Error loading stats:', err);
        setError('Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, [appliedYearFilter]);

  // Handle apply filters
  const handleApplyFilters = () => {
    setAppliedSearchTerm(searchTerm);
    setAppliedYearFilter(yearFilter);
    // Close panel when filters change
    setIsPanelOpen(false);
    setSelectedCountry(null);
    setSelectedUniversity(null);
    setSelectedAuthor(null);
  };

  // Handle clear filters
  const handleClearFilters = () => {
    setSearchTerm('');
    setYearFilter('all');
    setAppliedSearchTerm('');
    setAppliedYearFilter('all');
  };

  const handleCountryClick = (country) => {
    setSelectedCountry(country);
    setSelectedUniversity(null);
    setSelectedAuthor(null);
    setIsPanelOpen(true);
  };

  const handleUniversityClick = async (university) => {
    try {
      // Fetch full university data with authors (yearFilter can be single year or range)
      const yearParam = appliedYearFilter !== 'all' ? appliedYearFilter : null;
      const fullUniversity = await ApiService.getUniversity(selectedCountry.id, university.id, yearParam);
      setSelectedUniversity({...university, ...fullUniversity});
      setSelectedAuthor(null);
    } catch (err) {
      console.error('Error loading university:', err);
    }
  };

  const handleAuthorClick = async (author) => {
    try {
      // Fetch full author data with papers (yearFilter can be single year or range)
      const yearParam = appliedYearFilter !== 'all' ? appliedYearFilter : null;
      const fullAuthor = await ApiService.getAuthor(
        selectedCountry.id, 
        selectedUniversity.id, 
        author.id,
        yearParam
      );
      setSelectedAuthor(fullAuthor);
    } catch (err) {
      console.error('Error loading author:', err);
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
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-cyan-50 to-teal-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-700">Loading Research Data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-red-50 to-orange-50">
        <div className="text-center p-8 bg-white rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Data</h2>
          <p className="text-gray-700 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-6 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <div className="flex-shrink-0">
        <Header 
          searchTerm={searchTerm}
          yearFilter={yearFilter}
          onSearchChange={setSearchTerm}
          onYearChange={setYearFilter}
          onApplyFilters={handleApplyFilters}
          onClearFilters={handleClearFilters}
          stats={stats}
        />
      </div>
      <div className="flex-1 relative overflow-hidden">
        <MapView 
          onCountryClick={handleCountryClick}
          selectedCountry={selectedCountry?.id}
          searchTerm={appliedSearchTerm}
          yearFilter={appliedYearFilter}
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
        searchTerm={appliedSearchTerm}
        yearFilter={appliedYearFilter}
      />
    </div>
  );
}

export default App;
