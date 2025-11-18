import React, { useState, useMemo } from 'react';
import './App.css';
import MapView from './components/MapView';
import SidePanel from './components/SidePanel';
import Header from './components/Header';
import { mockCountries } from './data/mock';

function App() {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [selectedUniversity, setSelectedUniversity] = useState(null);
  const [selectedAuthor, setSelectedAuthor] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [yearFilter, setYearFilter] = useState('all');

  // Calculate statistics
  const stats = useMemo(() => {
    let totalPapers = 0;
    let totalUniversities = 0;
    let totalAuthors = 0;
    const uniqueAuthors = new Set();

    mockCountries.forEach(country => {
      totalUniversities += country.universities.length;
      country.universities.forEach(uni => {
        uni.authors.forEach(author => {
          uniqueAuthors.add(author.id);
          totalPapers += author.papers.length;
        });
      });
    });

    return {
      totalPapers,
      totalCountries: mockCountries.length,
      totalUniversities,
      totalAuthors: uniqueAuthors.size
    };
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
