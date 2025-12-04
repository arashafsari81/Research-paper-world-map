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
        """Extract all unique (university, country) pairs from affiliations text.
        
        Format: "LastName, FirstName, Univ1, City1, Country1, Univ2, City2, Country2; NextAuthor..."
        """
        universities_countries = []
        seen = set()
        
        # Split by semicolon (separates different authors)
        author_entries = affiliations_text.split(';')
        
        for entry in author_entries:
            entry = entry.strip()
            if not entry:
                continue
            
            # Split by comma
            parts = [p.strip() for p in entry.split(',')]
            
            if len(parts) < 4:  # Need at least: LastName, FirstName, Institution, Country
                continue
            
            # Skip first two parts (author name: LastName, FirstName)
            affiliation_parts = parts[2:]
            
            # Parse multiple affiliations within this author's entry
            # Typically groups of 3: Institution, City/State, Country
            i = 0
            while i < len(affiliation_parts):
                # Look for institution (contains university keywords OR is followed by a city/country)
                current_part = affiliation_parts[i]
                
                # Check if this looks like an institution
                has_uni_keyword = any(keyword in current_part.lower() for keyword in 
                                    ['university', 'college', 'institute', 'school', 'polytechnic', 'academy', 'center', 'centre'])
                
                if has_uni_keyword or i == 0:
                    # This is likely an institution
                    university = current_part
                    
                    # Next 1-2 parts are location (city, maybe state)
                    # Last part before next institution is country
                    country = None
                    
                    # Look ahead to find the country
                    if i + 1 < len(affiliation_parts):
                        # Check if next part is also an institution (rare case)
                        next_has_keyword = any(keyword in affiliation_parts[i+1].lower() for keyword in 
                                             ['university', 'college', 'institute', 'school'])
                        
                        if next_has_keyword:
                            # Next part is another institution, current one has no country
                            # Skip this one
                            i += 1
                            continue
                        
                        # Typical case: Institution, City, Country OR Institution, City, State, Country
                        if i + 2 < len(affiliation_parts):
                            # Check if i+3 is an institution
                            if i + 3 < len(affiliation_parts):
                                part_3 = affiliation_parts[i+3]
                                if any(keyword in part_3.lower() for keyword in ['university', 'college', 'institute', 'school']):
                                    # Pattern: Inst, City, Country, NextInst
                                    country = affiliation_parts[i+2]
                                    i += 3
                                else:
                                    # Pattern: Inst, City, State, Country
                                    country = affiliation_parts[i+3] if i+3 < len(affiliation_parts) else affiliation_parts[i+2]
                                    i += 4
                            else:
                                # End of list: Inst, City, Country
                                country = affiliation_parts[i+2]
                                i += 3
                        else:
                            # Only one more part: Inst, Country
                            country = affiliation_parts[i+1]
                            i += 2
                    else:
                        # No more parts
                        i += 1
                        continue
                    
                    if country:
                        key = (university.lower(), country.lower())
                        if key not in seen:
                            seen.add(key)
                            universities_countries.append((university, country))
                else:
                    # Not an institution, skip
                    i += 1
        
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
