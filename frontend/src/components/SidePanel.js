import React from 'react';
import { X, ChevronRight, ExternalLink, FileText, User, Building2, Globe } from 'lucide-react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';

const SidePanel = ({ 
  isOpen, 
  onClose, 
  selectedCountry, 
  selectedUniversity, 
  selectedAuthor,
  onUniversityClick,
  onAuthorClick,
  onBack,
  searchTerm = '',
  yearFilter = 'all'
}) => {
  const [localSearchFilter, setLocalSearchFilter] = React.useState('');
  
  if (!isOpen) return null;
  
  // Helper function to filter papers by year
  const filterPapersByYear = (papers) => {
    if (!papers || yearFilter === 'all') return papers;
    const year = parseInt(yearFilter);
    return papers.filter(paper => paper.year === year);
  };
  
  // Helper function to check if text matches search
  const matchesSearch = (text) => {
    if (!searchTerm) return true;
    return text.toLowerCase().includes(searchTerm.toLowerCase());
  };

  const renderBreadcrumb = () => {
    const items = [];
    
    if (selectedCountry) {
      items.push(
        <Button 
          key="country" 
          variant="ghost" 
          size="sm" 
          onClick={() => onBack('country')}
          className="text-white hover:text-white hover:bg-white/20 font-semibold"
        >
          <Globe className="w-4 h-4 mr-1" />
          {selectedCountry.name}
        </Button>
      );
    }
    
    if (selectedUniversity) {
      items.push(
        <ChevronRight key="arrow1" className="w-4 h-4 text-white" />,
        <Button 
          key="university" 
          variant="ghost" 
          size="sm" 
          onClick={() => onBack('university')}
          className="text-white hover:text-white hover:bg-white/20 font-semibold"
        >
          <Building2 className="w-4 h-4 mr-1" />
          {selectedUniversity.name.length > 30 ? selectedUniversity.name.substring(0, 30) + '...' : selectedUniversity.name}
        </Button>
      );
    }
    
    if (selectedAuthor) {
      items.push(
        <ChevronRight key="arrow2" className="w-4 h-4 text-white" />,
        <span key="author" className="text-sm font-semibold text-white flex items-center px-3">
          <User className="w-4 h-4 mr-1" />
          {selectedAuthor.name}
        </span>
      );
    }
    
    return <div className="flex items-center gap-2 flex-wrap">{items}</div>;
  };

  const renderContent = () => {
    // Author Details View
    if (selectedAuthor && selectedUniversity && selectedCountry) {
      // Filter papers by year and search term
      let filteredPapers = filterPapersByYear(selectedAuthor.papers || []);
      
      if (searchTerm) {
        filteredPapers = filteredPapers.filter(paper => 
          matchesSearch(paper.title) || 
          matchesSearch(paper.source) ||
          (paper.authors && paper.authors.some(author => matchesSearch(author)))
        );
      }
      
      return (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">{selectedAuthor.name}</h2>
                <p className="text-sm text-gray-600 flex items-center">
                  <Building2 className="w-4 h-4 mr-1" />
                  {selectedAuthor.affiliation}
                </p>
              </div>
              <Badge variant="secondary" className="bg-cyan-100 text-cyan-700">
                {filteredPapers.length} Papers {yearFilter !== 'all' && `(${yearFilter})`}
              </Badge>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <FileText className="w-5 h-5 mr-2 text-cyan-600" />
              Publications
            </h3>
            {filteredPapers.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No papers found matching the filters</p>
            ) : (
              <div className="space-y-4">
                {filteredPapers.map(paper => (
                <div key={paper.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:border-cyan-300 transition-all duration-200">
                  <h4 className="font-semibold text-gray-800 mb-2 leading-snug">{paper.title}</h4>
                  <div className="space-y-1 text-sm text-gray-600 mb-3">
                    <p><strong>Year:</strong> {paper.year}</p>
                    <p><strong>Source:</strong> {paper.source}</p>
                    <p><strong>Cited by:</strong> {paper.cited_by}</p>
                    <p className="text-xs text-gray-500"><strong>DOI:</strong> {paper.doi}</p>
                  </div>
                  <div className="mb-3">
                    <p className="text-xs font-medium text-gray-700 mb-1">Co-authors:</p>
                    <div className="flex flex-wrap gap-1">
                      {paper.authors.map((author, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {author}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <a 
                    href={paper.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-sm text-cyan-600 hover:text-cyan-700 font-medium"
                  >
                    View on Scopus <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                </div>
              ))}
              </div>
            )}
          </div>
        </div>
      );
    }

    // University Authors View
    if (selectedUniversity && selectedCountry) {
      return (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">{selectedUniversity.name}</h2>
            <p className="text-sm text-gray-600 flex items-center">
              <Globe className="w-4 h-4 mr-1" />
              {selectedCountry.name}
            </p>
            <Badge variant="secondary" className="bg-cyan-100 text-cyan-700 mt-3">
              {selectedUniversity.paperCount} Papers
            </Badge>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <User className="w-5 h-5 mr-2 text-cyan-600" />
              Authors ({selectedUniversity.authors.length})
            </h3>
            <div className="grid gap-3">
              {selectedUniversity.authors.map(author => (
                <button
                  key={author.id}
                  onClick={() => onAuthorClick(author)}
                  className="bg-white border border-gray-200 rounded-lg p-4 hover:border-cyan-300 hover:shadow-md transition-all duration-200 text-left group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800 mb-1 group-hover:text-cyan-600 transition-colors">
                        {author.name}
                      </h4>
                      <p className="text-sm text-gray-600">{author.affiliation}</p>
                      <Badge variant="outline" className="mt-2">
                        {author.paperCount} {author.paperCount === 1 ? 'Paper' : 'Papers'}
                      </Badge>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-cyan-600 transition-colors" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      );
    }

    // Country Universities View  
    if (selectedCountry) {
      // Filter universities based on search
      const filteredUniversities = searchFilter 
        ? selectedCountry.universities.filter(uni =>
            uni.name.toLowerCase().includes(searchFilter.toLowerCase())
          )
        : selectedCountry.universities;
      
      return (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">{selectedCountry.name}</h2>
            <Badge variant="secondary" className="bg-cyan-100 text-cyan-700">
              {selectedCountry.paperCount} Total Papers
            </Badge>
          </div>
          
          {/* Search within country */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search universities..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <Building2 className="w-5 h-5 mr-2 text-cyan-600" />
              Universities ({filteredUniversities.length})
            </h3>
            <div className="grid gap-3">
              {filteredUniversities.map(university => (
                <button
                  key={university.id}
                  onClick={() => onUniversityClick(university)}
                  className="bg-white border border-gray-200 rounded-lg p-4 hover:border-cyan-300 hover:shadow-md transition-all duration-200 text-left group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800 mb-1 group-hover:text-cyan-600 transition-colors">
                        {university.name}
                      </h4>
                      <div className="flex gap-3 mt-2">
                        <Badge variant="outline">
                          {university.paperCount} Papers
                        </Badge>
                        <Badge variant="outline">
                          {university.authors} {university.authors === 1 ? 'Author' : 'Authors'}
                        </Badge>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-cyan-600 transition-colors" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-30 z-[1001] transition-opacity duration-300"
        onClick={onClose}
      />
      
      {/* Side Panel */}
      <div className="fixed right-0 top-0 h-full w-full md:w-[500px] lg:w-[600px] bg-white shadow-2xl z-[1002] transform transition-transform duration-300">
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="bg-gradient-to-r from-cyan-600 to-teal-500 p-6 text-white">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Research Papers Explorer</h2>
              <Button 
                variant="ghost" 
                size="icon"
                onClick={onClose}
                className="text-white hover:bg-white/20"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
            {renderBreadcrumb()}
          </div>

          {/* Content */}
          <ScrollArea className="flex-1 p-6">
            {renderContent()}
          </ScrollArea>
        </div>
      </div>
    </>
  );
};

export default SidePanel;
