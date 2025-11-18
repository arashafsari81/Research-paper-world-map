import React from 'react';
import { Search, Filter, Globe, Building2, User, FileText } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

const YEARS = [2021, 2022, 2023, 2024, 2025];

const Header = ({ searchTerm, yearFilter, onSearchChange, onYearChange, stats }) => {
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
          <div className="flex items-center gap-6">
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
          </div>
        </div>

        {/* Bottom Row: Search and Filters */}
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Search country, university, author, or paper title..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-10 bg-white border-0 shadow-md h-11"
            />
          </div>

          <div className="flex items-center gap-2 bg-white rounded-lg shadow-md px-3 py-2">
            <Filter className="w-4 h-4 text-cyan-600" />
            <Select value={yearFilter} onValueChange={onYearChange}>
              <SelectTrigger className="w-32 border-0 focus:ring-0">
                <SelectValue placeholder="All Years" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Years</SelectItem>
                {YEARS.map(year => (
                  <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {searchTerm && (
            <Button 
              variant="secondary" 
              size="sm" 
              onClick={() => onSearchChange('')}
              className="bg-white hover:bg-gray-100 shadow-md"
            >
              Clear
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Header;
