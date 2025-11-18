import React, { useState } from 'react';
import './App.css';
import MapView from './components/MapView';
import SidePanel from './components/SidePanel';

function App() {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [selectedUniversity, setSelectedUniversity] = useState(null);
  const [selectedAuthor, setSelectedAuthor] = useState(null);

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
      <MapView 
        onCountryClick={handleCountryClick}
        selectedCountry={selectedCountry?.id}
      />
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
