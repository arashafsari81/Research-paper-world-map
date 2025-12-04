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
        """Parse 'Authors with affiliations' field into structured data.
        
        Extracts ALL unique universities and countries, creating separate entries
        for each institution mentioned in the paper.
        """
        # Get raw data
        authors_with_affil = str(row.get('Authors with affiliations', ''))
        author_ids_str = str(row.get('Author(s) ID', ''))
        author_full_names = str(row.get('Author full names', ''))
        
        if authors_with_affil == 'nan' or not authors_with_affil:
            return []
        
        # Parse author IDs
        author_ids = [aid.strip() for aid in author_ids_str.split(';') if aid.strip() and aid != 'nan']
        
        # Parse author names with IDs from "Author full names"
        author_name_id_map = {}
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
                    if ',' in full_name:
                        last_name = full_name.split(',')[0].strip()
                        author_name_id_map[last_name] = (full_name, author_id)
                    author_name_id_map[full_name] = (full_name, author_id)
        
        # Parse Authors with affiliations to extract ALL affiliations
        # Format: "LastName, FirstName, Institution1, City1, State1, Country1, Institution2, City2, Country2; NextAuthor..."
        affiliation_entries = authors_with_affil.split(';')
        
        # Track unique universities and countries from this paper
        universities_countries = []  # List of (university, country) tuples
        
        for entry in affiliation_entries:
            entry = entry.strip()
            if not entry:
                continue
            
            parts = [p.strip() for p in entry.split(',')]
            if len(parts) < 3:
                continue
            
            # Check if starts with author name (first part looks like last name, second like first name)
            first_part_words = parts[0].split()
            second_part_words = parts[1].split() if len(parts) > 1 else []
            
            is_author_name = (
                len(first_part_words) <= 3 and 
                len(second_part_words) <= 2 and
                not any(word in parts[0].lower() for word in ['university', 'college', 'school', 'institute', 'department', 'center', 'centre'])
            )
            
            if is_author_name:
                # This entry starts with an author name
                # Format: LastName, FirstName, Inst1, City1, State1, Country1, [Inst2, City2, Country2, ...]
                # Parse all institutions for this author
                remaining_parts = parts[2:]  # Everything after FirstName
                
                # Group remaining parts by institution (every ~3-4 parts is one affiliation)
                # Strategy: Country is typically last, work backwards
                i = 0
                while i < len(remaining_parts):
                    # Look for country (last element in group)
                    # Typically: Institution, City, [State], Country
                    if i + 2 < len(remaining_parts):
                        # Try to identify where this affiliation ends
                        # Country names are typically short and don't contain keywords
                        potential_country = remaining_parts[i+2] if i+2 < len(remaining_parts) else None
                        
                        # Check if next element looks like an institution (starts new affiliation)
                        if i+3 < len(remaining_parts):
                            next_part = remaining_parts[i+3]
                            next_looks_like_institution = any(word in next_part.lower() for word in ['university', 'college', 'school', 'institute', 'department'])
                            
                            if next_looks_like_institution:
                                # Current group: Institution, City, Country
                                university = remaining_parts[i]
                                country = remaining_parts[i+2] if i+2 < len(remaining_parts) else remaining_parts[-1]
                                universities_countries.append((university, country))
                                i += 3
                                continue
                        
                        # Default: take 3-4 elements as one affiliation
                        university = remaining_parts[i]
                        country = remaining_parts[min(i+3, len(remaining_parts)-1)]
                        universities_countries.append((university, country))
                        i += 4
                    else:
                        # Not enough parts, skip
                        break
        
        # Now create author entries for each unique university-country combination
        authors_data = []
        seen_universities = set()
        
        for university, country in universities_countries:
            # Avoid duplicate universities
            uni_key = university.lower()
            if uni_key in seen_universities:
                continue
            seen_universities.add(uni_key)
            
            # Assign authors to this university (distribute all authors across all universities)
            for idx, (full_name, author_id) in enumerate(author_list):
                if len(authors_data) < 100:  # Reasonable limit
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
