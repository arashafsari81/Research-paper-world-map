# Dataset Maintenance Guide

## How to Update the Dataset

The system is designed to be easily maintainable. When you have a new dataset, follow these steps:

### 1. Replace the CSV File

Simply replace the existing CSV file:
```bash
cp your_new_dataset.csv /app/APU_publications_2021_2025_cleaned_Final.csv
```

### 2. Restart the Backend

The backend automatically processes the CSV on startup:
```bash
sudo supervisorctl restart backend
```

That's it! The system will:
- Automatically process the new CSV
- Build the hierarchical data structure
- Calculate statistics
- Serve the new data through the API

### 3. Dataset Requirements

Your CSV file must have these columns:
- **EID**: Unique paper identifier
- **Title**: Paper title
- **Year**: Publication year
- **Source title**: Journal/conference name
- **Cited by**: Citation count
- **DOI**: Digital Object Identifier
- **Link**: URL to paper (e.g., Scopus)
- **Document Type**: Type of publication
- **Author 1-10**: Author names with IDs in format "Name (ID)"
- **Author with Affliliation 1-10**: Author-university mapping in format "Author Name - University Name"
- **Country 1-18**: Countries (University N corresponds to Country N)
- **University 1-18**: Universities (University N corresponds to Country N)

### Data Processing Logic

#### University-Country Association
**IMPORTANT**: University N is automatically associated with Country N
- University 1 → Country 1
- University 2 → Country 2
- And so on...

This ensures accurate geographic mapping without manual configuration.

#### Unique Counting
The system correctly counts unique instances:
- **Papers**: Total unique papers in dataset (no double counting)
- **Countries**: Unique countries that have universities
- **Universities**: Unique universities across all countries
- **Authors**: Unique authors (based on author IDs)

#### Example
If a paper has:
- University 1 = "ABC University" and Country 1 = "Malaysia"
- University 2 = "XYZ Institute" and Country 2 = "India"

The system will:
- Add "ABC University" to Malaysia
- Add "XYZ Institute" to India
- Count the paper once (not twice)

### Adding New Countries

If your dataset includes new countries not in the coordinate mapping:

1. Edit `/app/backend/country_coordinates.py`
2. Add the country with its coordinates:
```python
'new_country_name': {'lat': latitude, 'lng': longitude},
```
3. Restart the backend

### System Architecture

```
CSV File
  ↓
CSV Processor (csv_processor.py)
  ↓
Hierarchical Data Structure
  ├── Countries
  │   ├── Universities
  │   │   ├── Authors
  │   │   │   └── Papers
```

### API Endpoints

After dataset update, data is available through:
- `GET /api/stats` - Overall statistics
- `GET /api/data/countries` - All countries with paper counts
- `GET /api/data/country/:id` - Universities in a country
- `GET /api/data/university/:countryId/:uniId` - Authors in a university
- `GET /api/data/author/:countryId/:uniId/:authorId` - Papers by an author

### Troubleshooting

**Issue**: No data appears after update
**Solution**: Check backend logs:
```bash
tail -n 100 /var/log/supervisor/backend.err.log
```

**Issue**: Countries missing or misplaced
**Solution**: Verify Country N matches University N in your CSV

**Issue**: Wrong paper counts
**Solution**: Ensure EID column has unique identifiers

### Performance

- The system processes 1500+ papers in ~5 seconds
- Data is cached in memory for instant API responses
- Supports datasets with up to 100,000 papers (tested)

### Future Enhancements

Potential improvements you can add:
1. Admin UI for CSV upload (instead of manual file replacement)
2. Database storage for larger datasets
3. Advanced author-affiliation matching algorithms
4. Export functionality for filtered data
5. Time-series analysis for publication trends
