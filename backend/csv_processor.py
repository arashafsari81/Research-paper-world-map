import pandas as pd
import os
from typing import Dict, List, Set
from collections import defaultdict
import hashlib
import re
from country_coordinates import get_country_coordinates


class CSVProcessor:
    def __init__(self, csv_path: str, year_filter: int = None):
        self.csv_path = csv_path
        self.df = None
        self.processed_data = None
        self.year_filter = year_filter
        
    def load_csv(self):
        """Load CSV file into pandas DataFrame."""
        print(f"Loading CSV from {self.csv_path}...")
        
        # Import cleaner
        from data_cleaner import load_and_clean_csv
        
        # Load and auto-clean if needed
        self.df = load_and_clean_csv(self.csv_path)
        
        # Apply year filter if specified
        if self.year_filter:
            original_count = len(self.df)
            self.df = self.df[self.df['Year'] == self.year_filter]
            print(f"Filtered to year {self.year_filter}: {len(self.df)} papers (from {original_count})")
        
        return self
    
    def clean_text(self, text):
        """Clean text by removing extra spaces and handling NaN."""
        if pd.isna(text) or text == 'nan' or text == '':
            return None
        return str(text).strip()
    
    def generate_id(self, text: str) -> str:
        """Generate a unique ID from text."""
        if not text:
            return ""
        clean = re.sub(r'[^a-z0-9]', '', text.lower())
        return clean[:50] if len(clean) > 50 else clean
    
    def extract_author_id(self, author_text: str) -> str:
        """Extract author ID from 'Name (ID)' format."""
        if not author_text or pd.isna(author_text):
            return None
        match = re.search(r'\((\d+)\)', author_text)
        if match:
            return match.group(1)
        return self.generate_id(author_text)
    
    def extract_author_name(self, author_text: str) -> str:
        """Extract author name from 'Name (ID)' format."""
        if not author_text or pd.isna(author_text):
            return None
        # Remove ID in parentheses
        name = re.sub(r'\s*\(\d+\)\s*$', '', author_text)
        return name.strip()
    
    def normalize_author_name(self, name: str) -> str:
        """Normalize author name for matching (handles 'Last, First' and 'First Last' formats)."""
        if not name:
            return ''
        
        # Convert to lowercase and remove extra spaces
        name = ' '.join(name.lower().strip().split())
        
        # If name contains comma, it's in "Last, First" format - convert to "First Last"
        if ',' in name:
            parts = [p.strip() for p in name.split(',')]
            if len(parts) == 2:
                # "Last, First" -> "First Last"
                name = f"{parts[1]} {parts[0]}"
        
        return name
    
    def parse_affiliation(self, affiliation_text: str) -> tuple:
        """Parse 'Author Name - University' format."""
        if not affiliation_text or pd.isna(affiliation_text):
            return None, None
        parts = affiliation_text.split(' - ', 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return None, affiliation_text.strip()
    
    def process_data(self):
        """Process CSV and build hierarchical data structure."""
        print("Processing data...")
        
        # Data structures
        countries_data = defaultdict(lambda: {
            'name': '',
            'paper_ids': set(),  # Track unique papers per country
            'universities': defaultdict(lambda: {
                'name': '',
                'paper_ids': set(),  # Track unique papers per university
                'authors': defaultdict(lambda: {
                    'name': '',
                    'affiliation': '',
                    'paper_ids': set()  # Track unique papers per author
                })
            })
        })
        
        all_papers = {}
        
        # Process each paper
        for idx, row in self.df.iterrows():
            paper_id = self.clean_text(row.get('EID', f'paper_{idx}'))
            
            # Extract paper details
            paper = {
                'id': paper_id,
                'title': self.clean_text(row.get('Title', '')),
                'year': int(row.get('Year', 0)) if pd.notna(row.get('Year')) else 0,
                'source': self.clean_text(row.get('Source title', '')),
                'cited_by': int(row.get('Cited by', 0)) if pd.notna(row.get('Cited by')) else 0,
                'doi': self.clean_text(row.get('DOI', '')),
                'link': self.clean_text(row.get('Link', '')),
                'document_type': self.clean_text(row.get('Document Type', '')),
                'authors': []
            }
            
            # Extract authors with IDs
            authors_in_paper = []
            for i in range(1, 11):
                author_col = f'Author {i}'
                if author_col in row and pd.notna(row[author_col]):
                    author_text = self.clean_text(row[author_col])
                    if author_text:
                        author_name = self.extract_author_name(author_text)
                        author_id = self.extract_author_id(author_text)
                        if author_name:
                            authors_in_paper.append((author_name, author_id, i))  # Include index
            
            paper['authors'] = [name for name, _, _ in authors_in_paper]
            all_papers[paper_id] = paper
            
            # Extract countries with indices
            paper_countries = {}  # index -> country
            for i in range(1, 19):
                country_col = f'Country {i}'
                if country_col in self.df.columns and pd.notna(row.get(country_col)):
                    country = self.clean_text(row.get(country_col))
                    if country:
                        paper_countries[i] = country
            
            # Extract universities with indices
            paper_universities = {}  # index -> university
            for i in range(1, 19):
                uni_col = f'University {i}'
                if uni_col in self.df.columns and pd.notna(row.get(uni_col)):
                    uni = self.clean_text(row.get(uni_col))
                    if uni:
                        paper_universities[i] = uni
            
            # Extract author-affiliation mapping
            author_affiliations = {}  # normalized_author_name -> (original_name, university, index)
            for i in range(1, 11):
                affil_col = f'Author with Affliliation {i}'
                if affil_col in row and pd.notna(row[affil_col]):
                    affil_text = self.clean_text(row[affil_col])
                    if affil_text:
                        author_name, university = self.parse_affiliation(affil_text)
                        if author_name and university:
                            # Find the university index
                            uni_idx = None
                            for idx, uni_name in paper_universities.items():
                                if uni_name == university:
                                    uni_idx = idx
                                    break
                            if uni_idx is not None:
                                # Store with normalized name as key
                                normalized = self.normalize_author_name(author_name)
                                author_affiliations[normalized] = (author_name, university, uni_idx)
            
            # Build hierarchical structure with correct country-university association
            for uni_idx, university in paper_universities.items():
                # University N is associated with Country N
                if uni_idx in paper_countries:
                    country = paper_countries[uni_idx]
                    country_id = self.generate_id(country)
                    countries_data[country_id]['name'] = country
                    countries_data[country_id]['paper_ids'].add(paper_id)
                    
                    uni_id = self.generate_id(university)
                    countries_data[country_id]['universities'][uni_id]['name'] = university
                    countries_data[country_id]['universities'][uni_id]['paper_ids'].add(paper_id)
                    
                    # Find authors from this university
                    authors_added_to_uni = False
                    for author_name, author_id_num, author_idx in authors_in_paper:
                        # Normalize author name for matching
                        normalized_author = self.normalize_author_name(author_name)
                        if normalized_author in author_affiliations:
                            original_name, affil_uni, affil_uni_idx = author_affiliations[normalized_author]
                            # Match by university name
                            if affil_uni == university:
                                author_id = author_id_num if author_id_num else self.generate_id(author_name)
                                author_data = countries_data[country_id]['universities'][uni_id]['authors'][author_id]
                                author_data['name'] = author_name  # Use name from Author column (with ID format)
                                author_data['affiliation'] = university
                                author_data['paper_ids'].add(paper_id)
                                authors_added_to_uni = True
                    
                    # If no authors were matched to this university, add all authors from the paper
                    # This handles cases where university is listed but author affiliations don't specify it
                    if not authors_added_to_uni and len(authors_in_paper) > 0:
                        for author_name, author_id_num, author_idx in authors_in_paper:
                            author_id = author_id_num if author_id_num else self.generate_id(author_name)
                            author_data = countries_data[country_id]['universities'][uni_id]['authors'][author_id]
                            author_data['name'] = author_name
                            author_data['affiliation'] = university
                            author_data['paper_ids'].add(paper_id)
        
        # Build final structure with UNIQUE counts
        result = []
        for country_id, country_data in countries_data.items():
            universities = []
            
            for uni_id, uni_data in country_data['universities'].items():
                authors = []
                
                for author_id, author_data in uni_data['authors'].items():
                    paper_ids = list(author_data['paper_ids'])  # Already a set, so unique
                    author_papers = [all_papers[pid] for pid in paper_ids if pid in all_papers]
                    author_citations = sum(p['cited_by'] for p in author_papers)
                    
                    authors.append({
                        'id': author_id,
                        'name': author_data['name'],
                        'affiliation': author_data['affiliation'],
                        'paperCount': len(paper_ids),
                        'citationCount': author_citations,
                        'papers': author_papers
                    })
                
                # Calculate university citations
                uni_papers_set = uni_data['paper_ids']
                uni_citations = sum(all_papers[pid]['cited_by'] for pid in uni_papers_set if pid in all_papers)
                
                # Include universities even without author details (papers are tracked)
                universities.append({
                    'id': uni_id,
                    'name': uni_data['name'],
                    'paperCount': len(uni_data['paper_ids']),  # Unique papers for this university
                    'citationCount': uni_citations,
                    'authors': sorted(authors, key=lambda x: x['paperCount'], reverse=True) if authors else []
                })
            
            if universities:  # Only include countries with universities
                coords = get_country_coordinates(country_data['name'])
                result.append({
                    'id': country_id,
                    'name': country_data['name'],
                    'lat': coords['lat'],
                    'lng': coords['lng'],
                    'paperCount': len(country_data['paper_ids']),  # Unique papers for this country
                    'universities': sorted(universities, key=lambda x: x['paperCount'], reverse=True)
                })
        
        self.processed_data = sorted(result, key=lambda x: x['paperCount'], reverse=True)
        print(f"Processed {len(self.processed_data)} countries")
        return self
    
    def get_processed_data(self):
        """Get the processed data."""
        return self.processed_data
    
    def get_stats(self):
        """Calculate statistics from processed data."""
        if not self.processed_data:
            return None
        
        # Count unique papers, universities, and authors
        all_papers = set()
        total_universities = 0
        all_authors = set()
        total_citations = 0
        
        for country in self.processed_data:
            # Add unique papers from this country
            all_papers.add(country['paperCount'])  # This is already unique count per country
            
            total_universities += len(country['universities'])
            for uni in country['universities']:
                for author in uni['authors']:
                    all_authors.add(author['id'])
                    # Add citations from this author's papers
                    for paper in author['papers']:
                        total_citations += paper.get('cited_by', 0)
        
        # Get total unique papers from the source (since each country may have overlapping papers)
        total_unique_papers = len(self.df)  # Total papers in original CSV
        
        # Calculate total citations from original dataframe (to avoid duplicates)
        total_unique_citations = int(self.df['Cited by'].sum())
        
        return {
            'totalPapers': total_unique_papers,
            'totalCountries': len(self.processed_data),
            'totalUniversities': total_universities,
            'totalAuthors': len(all_authors),
            'totalCitations': total_unique_citations
        }


if __name__ == '__main__':
    # Test the processor
    csv_path = '/app/APU_publications_2021_2025_cleaned_Final.csv'
    if os.path.exists(csv_path):
        processor = CSVProcessor(csv_path)
        processor.load_csv().process_data()
        stats = processor.get_stats()
        print(f"\nStats: {stats}")
        print(f"\nSample country: {processor.get_processed_data()[0]['name']}")
    else:
        print(f"CSV file not found at {csv_path}")
