import pandas as pd
import os
from typing import Dict, List, Set
from collections import defaultdict
import hashlib
import re
from country_coordinates import get_country_coordinates


class CSVProcessor:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
        self.processed_data = None
        
    def load_csv(self):
        """Load CSV file into pandas DataFrame."""
        print(f"Loading CSV from {self.csv_path}...")
        self.df = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.df)} papers")
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
        """Normalize author name for matching (convert 'Last, First' to 'First Last')."""
        if not name:
            return name
        # If name contains comma, assume it's "Last, First" format
        if ',' in name:
            parts = name.split(',', 1)
            if len(parts) == 2:
                last = parts[0].strip()
                first = parts[1].strip()
                return f"{first} {last}"
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
            'universities': defaultdict(lambda: {
                'name': '',
                'authors': defaultdict(lambda: {
                    'name': '',
                    'affiliation': '',
                    'papers': []
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
            
            # Extract authors
            authors_in_paper = []
            for i in range(1, 11):
                author_col = f'Author {i}'
                if author_col in row and pd.notna(row[author_col]):
                    author_text = self.clean_text(row[author_col])
                    if author_text:
                        author_name = self.extract_author_name(author_text)
                        author_id = self.extract_author_id(author_text)
                        if author_name:
                            authors_in_paper.append(author_name)
            
            paper['authors'] = authors_in_paper
            all_papers[paper_id] = paper
            
            # Extract countries
            paper_countries = set()
            for i in range(1, 19):
                country_col = f'Country {i}'
                if country_col in row and pd.notna(row[country_col]):
                    country = self.clean_text(row[country_col])
                    if country:
                        paper_countries.add(country)
            
            # Extract universities
            paper_universities = []
            for i in range(1, 19):
                uni_col = f'University {i}'
                if uni_col in row and pd.notna(row[uni_col]):
                    uni = self.clean_text(row[uni_col])
                    if uni:
                        paper_universities.append(uni)
            
            # Extract author-affiliation mapping
            author_affiliations = {}
            for i in range(1, 11):
                affil_col = f'Author with Affliliation {i}'
                if affil_col in row and pd.notna(row[affil_col]):
                    affil_text = self.clean_text(row[affil_col])
                    if affil_text:
                        author_name, university = self.parse_affiliation(affil_text)
                        if author_name and university:
                            author_affiliations[author_name] = university
            
            # Build hierarchical structure
            for country in paper_countries:
                country_id = self.generate_id(country)
                countries_data[country_id]['name'] = country
                
                # Associate paper with universities in this country
                for university in paper_universities:
                    uni_id = self.generate_id(university)
                    countries_data[country_id]['universities'][uni_id]['name'] = university
                    
                    # Find authors from this university
                    for author_name in authors_in_paper:
                        # Normalize author name for matching
                        normalized_name = self.normalize_author_name(author_name)
                        if normalized_name in author_affiliations:
                            if author_affiliations[normalized_name] == university:
                                author_id = self.generate_id(author_name)
                                author_data = countries_data[country_id]['universities'][uni_id]['authors'][author_id]
                                author_data['name'] = author_name
                                author_data['affiliation'] = university
                                author_data['papers'].append(paper_id)
        
        # Build final structure with counts
        result = []
        for country_id, country_data in countries_data.items():
            universities = []
            total_country_papers = 0
            
            for uni_id, uni_data in country_data['universities'].items():
                authors = []
                total_uni_papers = 0
                
                for author_id, author_data in uni_data['authors'].items():
                    paper_ids = list(set(author_data['papers']))  # Remove duplicates
                    authors.append({
                        'id': author_id,
                        'name': author_data['name'],
                        'affiliation': author_data['affiliation'],
                        'paperCount': len(paper_ids),
                        'papers': [all_papers[pid] for pid in paper_ids if pid in all_papers]
                    })
                    total_uni_papers += len(paper_ids)
                
                if authors:  # Only include universities with authors
                    universities.append({
                        'id': uni_id,
                        'name': uni_data['name'],
                        'paperCount': total_uni_papers,
                        'authors': sorted(authors, key=lambda x: x['paperCount'], reverse=True)
                    })
                    total_country_papers += total_uni_papers
            
            if universities:  # Only include countries with universities
                coords = get_country_coordinates(country_data['name'])
                result.append({
                    'id': country_id,
                    'name': country_data['name'],
                    'lat': coords['lat'],
                    'lng': coords['lng'],
                    'paperCount': total_country_papers,
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
        
        total_papers = 0
        total_universities = 0
        all_authors = set()
        
        for country in self.processed_data:
            total_universities += len(country['universities'])
            for uni in country['universities']:
                for author in uni['authors']:
                    all_authors.add(author['id'])
                    total_papers += author['paperCount']
        
        return {
            'totalPapers': total_papers,
            'totalCountries': len(self.processed_data),
            'totalUniversities': total_universities,
            'totalAuthors': len(all_authors)
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
