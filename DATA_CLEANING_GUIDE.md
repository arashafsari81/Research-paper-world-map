# Data Cleaning & Processing Guide

## System Now Handles Both Cleaned and Uncleaned Datasets!

The system automatically detects the format and cleans the data if needed.

## Supported Formats

### 1. Cleaned Format (Original)
**Structure**: Pre-processed columns
```
- Author 1, Author 2, ..., Author 10
- University 1, University 2, ..., University 18
- Country 1, Country 2, ..., Country 18
- Author with Affliliation 1, ..., Author with Affliliation 10
```

**Example File**: `APU_publications_2021_2025_cleaned_Final.csv`
- 1,512 papers
- Already structured for processing
- No cleaning needed

### 2. Uncleaned Format (New - Scopus Export)
**Structure**: Raw Scopus export
```
- Authors with affiliations (combined field)
- Author(s) ID (semicolon-separated)
- Author full names (with IDs)
- Affiliations
```

**Example File**: `Scopus_Data_APU_2021_Dec_2025_Complete.csv`
- 1,668 papers (156 more than cleaned version!)
- Automatically cleaned on load
- Parses complex affiliation strings

## How It Works

### Automatic Detection
The system checks for presence of cleaned columns:
- If `Author 1`, `University 1`, `Country 1` exist → **Cleaned format** (no processing)
- Otherwise → **Uncleaned format** (automatic cleaning)

### Cleaning Process for Uncleaned Data

**Input Format**:
```
Authors with affiliations: "LastName, FirstName, University, City, State, Country; NextAuthor, ..."
Author(s) ID: "12345; 67890; ..."
Author full names: "LastName, FirstName (12345); ..."
```

**Output Format**:
```
Author 1: "LastName, FirstName (12345)"
University 1: "University Name"
Country 1: "Country Name"
Author with Affliliation 1: "LastName, FirstName - University Name"
```

### Parsing Logic
1. **Split by semicolon** - Each author's entry
2. **Identify author names** - First two comma-separated parts
3. **Extract affiliation** - Remaining parts (Institution, City, Country)
4. **Map IDs** - Match author IDs from "Author(s) ID" field
5. **Handle multiple affiliations** - Author can have multiple institutions

## Current Dataset Statistics

### New Dataset (Uncleaned → Cleaned)
- **Papers**: 1,668 (+156 from previous)
- **Countries**: 82 (+6)
- **Universities**: 1,217 (+426!)
- **Authors**: 3,274
- **Citations**: 10,333 (+996)

### Old Dataset (Pre-cleaned)
- **Papers**: 1,512
- **Countries**: 76
- **Universities**: 791
- **Authors**: 3,318
- **Citations**: 9,337

## Updating the Dataset

### Option 1: Replace with New Uncleaned File
```bash
cp your_new_scopus_export.csv /app/Scopus_Data_APU_2021_Dec_2025_Complete.csv
sudo supervisorctl restart backend
```
System will auto-clean on startup!

### Option 2: Replace with Pre-cleaned File
```bash
cp your_cleaned_file.csv /app/APU_publications_2021_2025_cleaned_Final.csv
# Update server.py to point to this file
sudo supervisorctl restart backend
```

## File Priority
The system checks files in this order:
1. `/app/Scopus_Data_APU_2021_Dec_2025_Complete.csv` (uncleaned)
2. `/app/APU_publications_2021_2025_cleaned_Final.csv` (cleaned)

## Quality Assurance

### Validation Checks
- ✅ Author IDs correctly mapped
- ✅ Universities extracted from affiliations
- ✅ Countries identified from affiliation strings
- ✅ Multiple affiliations per author handled
- ✅ Year filtering works on both formats
- ✅ Export functionality works on both formats

### Known Limitations
1. **Complex affiliations**: Some authors have 2+ institutions - we take the first one as primary
2. **Name variations**: Author names must match between fields for ID mapping
3. **Country names**: Must exist in `country_coordinates.py` for map display

## Adding New Countries
If new countries appear in dataset:
1. Edit `/app/backend/country_coordinates.py`
2. Add: `'country_name': {'lat': X.XXXX, 'lng': Y.YYYY}`
3. Restart backend

## Performance
- **Cleaning**: ~2-3 seconds for 1,668 papers
- **Processing**: ~10-15 seconds for full dataset
- **Caching**: Cleaned data cached per year filter
- **Memory**: ~50MB for full dataset

## Troubleshooting

### Issue: Authors not showing
**Solution**: Check "Authors with affiliations" format in CSV

### Issue: Wrong country/university
**Solution**: Verify comma-separated format in affiliations field

### Issue: Missing papers
**Solution**: Ensure CSV has Title, Year, DOI columns

## Future Enhancements
- Support for more Scopus export formats
- Automatic country detection from affiliation text
- Duplicate author detection and merging
- Affiliation disambiguation
