import React, { useState, useEffect } from 'react';
import { Search, Filter, Globe, Building2, User, FileText, Download } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import DatasetUpload from './DatasetUpload';

const YEARS = [2021, 2022, 2023, 2024, 2025];

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API_BASE = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';

const Header = ({ searchTerm, yearFilter, onSearchChange, onYearChange, onApplyFilters, onClearFilters, stats }) => {
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [startYear, setStartYear] = useState('all');
  const [endYear, setEndYear] = useState('all');
  
  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showExportMenu && !event.target.closest('.export-menu-container')) {
        setShowExportMenu(false);
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showExportMenu]);
  
  const handleExport = (type) => {
    const yearParam = yearFilter !== 'all' ? `?year=${yearFilter}` : '';
    const url = `${API_BASE}/export/${type}${yearParam}`;
    
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = `${type}_export_${yearFilter !== 'all' ? yearFilter : 'all_years'}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setShowExportMenu(false);
  };

  return (
    <div className="absolute top-0 left-0 right-0 z-[1000] bg-gradient-to-r from-cyan-600 via-cyan-500 to-teal-500 shadow-lg">
      <div className="px-6 py-4">
        {/* Top Row: Title and Stats */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Globe className="w-8 h-8 text-white" />
            <div>
              <h1 className="text-2xl font-bold text-white">Research Papers World Map</h1>
              <p className="text-xs text-cyan-50">Explore academic publications globally</p>
            </div>
          </div>
          
          {/* Stats */}
          <div className="flex items-center gap-5">
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <FileText className="w-4 h-4 text-white" />
                <span className="text-2xl font-bold text-white">{stats.totalPapers}</span>
              </div>
              <p className="text-xs text-cyan-50">Papers</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Globe className="w-4 h-4 text-white" />
                <span className="text-2xl font-bold text-white">{stats.totalCountries}</span>
              </div>
              <p className="text-xs text-cyan-50">Countries</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Building2 className="w-4 h-4 text-white" />
                <span className="text-2xl font-bold text-white">{stats.totalUniversities}</span>
              </div>
              <p className="text-xs text-cyan-50">Universities</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <User className="w-4 h-4 text-white" />
                <span className="text-2xl font-bold text-white">{stats.totalAuthors}</span>
              </div>
              <p className="text-xs text-cyan-50">Authors</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-2xl font-bold text-white">{stats.totalCitations || 0}</span>
              </div>
              <p className="text-xs text-cyan-50">Citations</p>
            </div>
          </div>
        </div>

        {/* Bottom Row: Search and Filters */}
        <div className="flex items-center gap-3">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search by country name..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-9 pr-4 bg-white border-0 shadow-md h-10 w-80 text-sm"
            />
          </div>

          <div className="flex items-center gap-2 bg-white rounded-lg shadow-md px-3 h-10">
            <Filter className="w-4 h-4 text-cyan-600" />
            <Select value={yearFilter} onValueChange={onYearChange}>
              <SelectTrigger className="w-28 border-0 focus:ring-0 h-auto text-sm">
                <SelectValue placeholder="All Years" />
              </SelectTrigger>
              <SelectContent className="z-[2000]">
                <SelectItem value="all">All Years</SelectItem>
                {YEARS.map(year => (
                  <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button 
            onClick={onApplyFilters}
            className="bg-white text-cyan-600 hover:bg-gray-100 shadow-md font-semibold h-10 text-sm"
          >
            Apply Filters
          </Button>

          {(searchTerm || yearFilter !== 'all') && (
            <Button 
              variant="outline" 
              onClick={onClearFilters}
              className="bg-white text-gray-700 hover:bg-gray-100 shadow-md h-10 text-sm"
            >
              Clear All
            </Button>
          )}
          
          <div className="ml-auto flex items-center gap-2">
            <DatasetUpload onUploadSuccess={() => {/* Will reload page */}} />
            
            <div className="relative export-menu-container">
              <Button 
                onClick={() => setShowExportMenu(!showExportMenu)}
                className="bg-white text-cyan-600 hover:bg-cyan-50 shadow-md h-10 text-sm"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              
              {showExportMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl border border-gray-200 z-[2000]">
                  <button
                    onClick={() => handleExport('papers')}
                    className="w-full text-left px-4 py-3 hover:bg-gray-100 flex items-center text-gray-700 transition-colors"
                  >
                    <FileText className="w-4 h-4 mr-3 text-cyan-600" />
                    Export Papers
                  </button>
                  <button
                    onClick={() => handleExport('authors')}
                    className="w-full text-left px-4 py-3 hover:bg-gray-100 flex items-center text-gray-700 transition-colors"
                  >
                    <User className="w-4 h-4 mr-3 text-cyan-600" />
                    Export Authors
                  </button>
                  <button
                    onClick={() => handleExport('universities')}
                    className="w-full text-left px-4 py-3 hover:bg-gray-100 flex items-center text-gray-700 transition-colors"
                  >
                    <Building2 className="w-4 h-4 mr-3 text-cyan-600" />
                    Export Universities
                  </button>
                  <button
                    onClick={() => handleExport('countries')}
                    className="w-full text-left px-4 py-3 hover:bg-gray-100 flex items-center text-gray-700 rounded-b-lg transition-colors"
                  >
                    <Globe className="w-4 h-4 mr-3 text-cyan-600" />
                    Export Countries
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
