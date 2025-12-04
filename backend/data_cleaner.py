import pandas as pd
import re
from typing import Dict, List, Tuple

class DataCleaner:
    """Clean and normalize Scopus dataset to standard format."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.is_cleaned = self._detect_format()
        
    def _detect_format(self) -> bool:
        """Detect if data is already in cleaned format."""
        # Check if cleaned format columns exist
        has_author_cols = any('Author 1' in str(col) for col in self.df.columns)
        has_university_cols = any('University 1' in str(col) for col in self.df.columns)
        has_country_cols = any('Country 1' in str(col) for col in self.df.columns)
        
        return has_author_cols and has_university_cols and has_country_cols
    
    def clean_and_normalize(self) -> pd.DataFrame:
        """Clean and normalize data to standard format."""
        if self.is_cleaned:
            print("Data is already in cleaned format")
            return self.df
        
        print("Cleaning uncleaned dataset...")
        cleaned_df = self.df.copy()
        
        # Parse Authors with affiliations
        for idx, row in cleaned_df.iterrows():
            authors_data = self._parse_authors_with_affiliations(row)
            
            # Add parsed data to row
            for i, author_data in enumerate(authors_data, 1):
                if i <= 10:  # Limit to 10 authors
                    # Author column
                    if 'name' in author_data and 'id' in author_data:
                        cleaned_df.at[idx, f'Author {i}'] = f"{author_data['name']} ({author_data['id']})"
                    
                    # Author with Affiliation column
                    if 'name' in author_data and 'university' in author_data:
                        cleaned_df.at[idx, f'Author with Affliliation {i}'] = f"{author_data['name']} - {author_data['university']}"
                    
                    # University column
                    if 'university' in author_data:
                        cleaned_df.at[idx, f'University {i}'] = author_data['university']
                    
                    # Country column
                    if 'country' in author_data:
                        cleaned_df.at[idx, f'Country {i}'] = author_data['country']
        
        print(f"Cleaning complete. Dataset now has {len(cleaned_df)} papers.")
        return cleaned_df
    
    def _is_likely_country(self, text: str) -> bool:
        """Check if a text part is likely a country name."""
        # Common countries in academic publications
        countries = {
            'malaysia', 'china', 'united states', 'united kingdom', 'australia', 
            'india', 'singapore', 'japan', 'south korea', 'taiwan', 'thailand',
            'indonesia', 'vietnam', 'philippines', 'canada', 'germany', 'france',
            'italy', 'spain', 'netherlands', 'sweden', 'norway', 'denmark', 'finland',
            'switzerland', 'austria', 'belgium', 'poland', 'russia', 'brazil',
            'mexico', 'argentina', 'chile', 'south africa', 'egypt', 'saudi arabia',
            'united arab emirates', 'turkey', 'iran', 'pakistan', 'bangladesh',
            'new zealand', 'ireland', 'portugal', 'greece', 'czech republic',
            'hungary', 'romania', 'ukraine', 'israel', 'jordan', 'lebanon',
            'oman', 'qatar', 'kuwait', 'bahrain', 'hong kong', 'macao'
        }
        text_lower = text.lower().strip()
        return text_lower in countries
    
    def _is_likely_institution(self, text: str) -> bool:
        """Check if a text part is likely an institution name."""
        text_lower = text.lower()
        institution_keywords = [
            'university', 'college', 'institute', 'school', 'academy',
            'center', 'centre', 'department', 'faculty', 'laboratory',
            'research', 'program', 'programme'
        ]
        return any(keyword in text_lower for keyword in institution_keywords)
    
    def _parse_author_affiliations(self, author_section: str) -> List[Tuple[str, str, str]]:
        """Parse a single author's affiliation section.
        
        Returns: List of (author_name, institution, country) tuples
        """
        parts = [p.strip() for p in author_section.split(',')]
        
        if len(parts) < 3:
            return []
        
        # First two parts are LastName, FirstName
        last_name = parts[0]
        first_name = parts[1]
        author_name = f"{first_name} {last_name}"
        
        # Remaining parts are affiliations
        affiliation_parts = parts[2:]
        
        # Find all country indices in the remaining parts
        country_indices = []
        for i, part in enumerate(affiliation_parts):
            if self._is_likely_country(part):
                country_indices.append(i)
        
        if not country_indices:
            # No countries found, can't parse affiliations properly
            return []
        
        # Extract (institution, country) pairs
        results = []
        
        for country_idx in country_indices:
            country = affiliation_parts[country_idx]
            
            # Look backwards from country to find the institution
            # The institution is typically 1-3 positions before the country
            institution = None
            
            # Search backwards up to 4 positions to find institution keyword
            search_start = max(0, country_idx - 4)
            for i in range(country_idx - 1, search_start - 1, -1):
                if self._is_likely_institution(affiliation_parts[i]):
                    institution = affiliation_parts[i]
                    break
            
            # If no institution found, take the part immediately before country
            # (might be a city, but better than nothing)
            if not institution and country_idx > 0:
                institution = affiliation_parts[country_idx - 1]
            
            if institution:
                results.append((author_name, institution, country))
        
        return results
    
    def _extract_universities_and_countries(self, affiliations_text: str) -> List[Tuple[str, str, str]]:
        """Extract ALL (author_name, university, country) tuples from affiliations text.
        
        Returns: List of (author_name, institution, country) tuples
        """
        results = []
        seen = set()
        
        # Split by semicolon (each author's affiliations)
        author_entries = affiliations_text.split(';')
        
        for entry in author_entries:
            entry = entry.strip()
            if not entry:
                continue
            
            # Parse this author's affiliations
            author_affiliations = self._parse_author_affiliations(entry)
            
            # Add unique combinations
            for author_name, institution, country in author_affiliations:
                key = (author_name.lower(), institution.lower(), country.lower())
                if key not in seen:
                    seen.add(key)
                    results.append((author_name, institution, country))
        
        return results
    
    def _parse_authors_with_affiliations(self, row) -> List[Dict]:
        """Parse 'Authors with affiliations' field.
        
        Strategy: Extract author-specific affiliations from the complex field.
        """
        # Get raw data
        authors_with_affil = str(row.get('Authors with affiliations', ''))
        author_full_names = str(row.get('Author full names', ''))
        
        if authors_with_affil == 'nan' or not authors_with_affil:
            return []
        
        # Build a mapping of author names to IDs from "Author full names" field
        author_id_map = {}
        if author_full_names and author_full_names != 'nan':
            parts = author_full_names.split(';')
            for part in parts:
                part = part.strip()
                match = re.search(r'^(.+?)\s*\((\d+)\)$', part)
                if match:
                    full_name = match.group(1).strip()
                    author_id = match.group(2).strip()
                    # Normalize name for matching (handle both "Last, First" and "First Last" formats)
                    name_normalized = self._normalize_name_for_matching(full_name)
                    author_id_map[name_normalized] = (full_name, author_id)
        
        # Extract all (author_name, university, country) tuples
        affiliations = self._extract_universities_and_countries(authors_with_affil)
        
        # Create author entries with matched IDs
        authors_data = []
        for affil_author_name, university, country in affiliations:
            # Try to match this author to get their ID
            name_normalized = self._normalize_name_for_matching(affil_author_name)
            
            if name_normalized in author_id_map:
                full_name, author_id = author_id_map[name_normalized]
            else:
                # Use the name from affiliations if no match
                full_name = affil_author_name
                author_id = None
            
            authors_data.append({
                'name': full_name,
                'id': author_id,
                'university': university,
                'country': country
            })
        
        return authors_data
    
    def _normalize_name_for_matching(self, name: str) -> str:
        """Normalize a name for fuzzy matching between different formats.
        
        Handles: "Last, First" and "First Last" formats
        """
        if not name:
            return ''
        
        name = name.lower().strip()
        
        # If name contains comma, it's "Last, First" - convert to "first last"
        if ',' in name:
            parts = [p.strip() for p in name.split(',', 1)]
            if len(parts) == 2:
                name = f"{parts[1]} {parts[0]}"
        
        # Remove extra whitespace and special characters
        name = ' '.join(name.split())
        name = re.sub(r'[^\w\s]', '', name)
        
        return name


def load_and_clean_csv(csv_path: str) -> pd.DataFrame:
    """Load CSV and automatically clean if needed."""
    print(f"Loading CSV from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} papers")
    
    cleaner = DataCleaner(df)
    cleaned_df = cleaner.clean_and_normalize()
    
    return cleaned_df


if __name__ == '__main__':
    # Test the cleaner
    df = load_and_clean_csv('/app/Scopus_Data_APU_2021_Dec_2025_Complete.csv')
    
    print(f"\n=== Sample cleaned row ===")
    row = df.iloc[0]
    print(f"Author 1: {row.get('Author 1', 'N/A')}")
    print(f"University 1: {row.get('University 1', 'N/A')}")
    print(f"Country 1: {row.get('Country 1', 'N/A')}")
    print(f"Author with Affiliation 1: {row.get('Author with Affliliation 1', 'N/A')}")
