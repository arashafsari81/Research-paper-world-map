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
    
    def _parse_authors_with_affiliations(self, row) -> List[Dict]:
        """Parse 'Authors with affiliations' field into structured data."""
        authors_data = []
        
        # Get raw data
        authors_with_affil = str(row.get('Authors with affiliations', ''))
        author_ids_str = str(row.get('Author(s) ID', ''))
        author_full_names = str(row.get('Author full names', ''))
        
        if authors_with_affil == 'nan' or not authors_with_affil:
            return authors_data
        
        # Parse author IDs
        author_ids = [aid.strip() for aid in author_ids_str.split(';') if aid.strip() and aid != 'nan']
        
        # Parse author names with IDs from "Author full names"
        author_name_id_map = {}
        if author_full_names and author_full_names != 'nan':
            # Format: "Name1 (ID1); Name2 (ID2); ..."
            parts = author_full_names.split(';')
            for part in parts:
                part = part.strip()
                match = re.search(r'^(.+?)\s*\((\d+)\)$', part)
                if match:
                    name = match.group(1).strip()
                    author_id = match.group(2).strip()
                    author_name_id_map[name] = author_id
        
        # Parse Authors with affiliations
        # Format: "Author1, Univ1, City1, Country1; Author2, Univ2, City2, Country2; ..."
        affiliation_entries = authors_with_affil.split(';')
        
        for entry in affiliation_entries:
            entry = entry.strip()
            if not entry:
                continue
            
            # Split by comma
            parts = [p.strip() for p in entry.split(',')]
            
            if len(parts) >= 4:  # Author, University, City, Country (minimum)
                author_name = parts[0]
                
                # Find university (could be multiple words before city/country)
                # Strategy: Last part is country, second-to-last is city, rest is university
                country = parts[-1]
                city = parts[-2]
                university_parts = parts[1:-2]
                university = ', '.join(university_parts) if university_parts else parts[1]
                
                # Get author ID
                author_id = author_name_id_map.get(author_name, '')
                if not author_id and author_ids:
                    # Try to match by position
                    if len(authors_data) < len(author_ids):
                        author_id = author_ids[len(authors_data)]
                
                authors_data.append({
                    'name': author_name,
                    'id': author_id,
                    'university': university,
                    'city': city,
                    'country': country
                })
            elif len(parts) >= 2:  # At least Author, University
                author_name = parts[0]
                university = parts[1] if len(parts) > 1 else ''
                country = parts[-1] if len(parts) >= 3 else ''
                
                author_id = author_name_id_map.get(author_name, '')
                if not author_id and author_ids:
                    if len(authors_data) < len(author_ids):
                        author_id = author_ids[len(authors_data)]
                
                authors_data.append({
                    'name': author_name,
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
