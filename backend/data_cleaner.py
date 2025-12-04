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
    
    def _extract_universities_and_countries(self, affiliations_text: str) -> List[Tuple[str, str]]:
        """Extract all unique (university, country) pairs from affiliations text."""
        universities_countries = []
        seen = set()
        
        # Split by semicolon
        parts = affiliations_text.split(';')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Split by comma
            comma_parts = [p.strip() for p in part.split(',')]
            
            # Country is typically the last element
            if len(comma_parts) >= 2:
                country = comma_parts[-1]
                
                # Find university (look for parts containing university keywords)
                university = None
                for cp in comma_parts:
                    if any(keyword in cp.lower() for keyword in ['university', 'college', 'institute', 'school', 'polytechnic', 'academy']):
                        university = cp
                        break
                
                # If no keyword found, take the part after name (usually index 2)
                if not university and len(comma_parts) >= 3:
                    university = comma_parts[2]
                
                if university and country:
                    key = (university.lower(), country.lower())
                    if key not in seen:
                        seen.add(key)
                        universities_countries.append((university, country))
        
        return universities_countries
    
    def _parse_authors_with_affiliations(self, row) -> List[Dict]:
        """Parse 'Authors with affiliations' field.
        
        Strategy: Extract ALL unique universities and countries, then assign
        ALL authors to EACH university (since we don't know exact author-university mapping).
        """
        # Get raw data
        authors_with_affil = str(row.get('Authors with affiliations', ''))
        author_full_names = str(row.get('Author full names', ''))
        
        if authors_with_affil == 'nan' or not authors_with_affil:
            return []
        
        # Parse all authors with IDs
        author_list = []
        if author_full_names and author_full_names != 'nan':
            parts = author_full_names.split(';')
            for part in parts:
                part = part.strip()
                match = re.search(r'^(.+?)\s*\((\d+)\)$', part)
                if match:
                    full_name = match.group(1).strip()
                    author_id = match.group(2).strip()
                    author_list.append((full_name, author_id))
        
        # Extract all unique (university, country) pairs
        universities_countries = self._extract_universities_and_countries(authors_with_affil)
        
        # Create author entries: each author × each university
        authors_data = []
        for university, country in universities_countries:
            for full_name, author_id in author_list:
                authors_data.append({
                    'name': full_name,
                    'id': author_id,
                    'university': university,
                    'country': country
                })
        
        return authors_data


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
