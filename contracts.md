# Research Papers World Map - API Contracts & Integration Plan

## Data Processing Strategy

### CSV Structure
- **Papers**: Each row represents one paper with multiple authors/countries/universities
- **Country 1-18**: Multiple countries per paper
- **University 1-18**: Multiple universities per paper  
- **Author 1-10**: Multiple authors per paper
- **Author with Affiliation 1-10**: Links authors to their universities

### Backend Processing Logic
1. Parse CSV once and build hierarchical data structure
2. Handle many-to-many relationships (papers ↔ countries, papers ↔ universities, papers ↔ authors)
3. Aggregate counts at each level (country → universities → authors → papers)
4. Calculate unique author IDs to avoid duplicates

## MongoDB Collections

### 1. Papers Collection
```json
{
  "_id": ObjectId,
  "title": String,
  "year": Number,
  "source": String,
  "cited_by": Number,
  "doi": String,
  "link": String,
  "document_type": String,
  "eid": String,
  "authors": [
    {
      "id": String,
      "name": String,
      "affiliation": String
    }
  ],
  "countries": [String],
  "universities": [String]
}
```

### 2. Aggregated Data Collection (for performance)
```json
{
  "_id": "aggregated_data",
  "countries": [
    {
      "id": String,
      "name": String,
      "lat": Number,
      "lng": Number,
      "paperCount": Number,
      "universities": [
        {
          "id": String,
          "name": String,
          "paperCount": Number,
          "authors": [
            {
              "id": String,
              "name": String,
              "affiliation": String,
              "paperCount": Number,
              "paperIds": [String]
            }
          ]
        }
      ]
    }
  ],
  "lastUpdated": Date
}
```

## API Endpoints

### 1. GET /api/data/countries
**Purpose**: Get all countries with paper counts and coordinates
**Response**:
```json
{
  "countries": [
    {
      "id": "malaysia",
      "name": "Malaysia", 
      "lat": 4.2105,
      "lng": 101.9758,
      "paperCount": 342
    }
  ]
}
```

### 2. GET /api/data/country/:countryId
**Purpose**: Get universities for a specific country
**Response**:
```json
{
  "country": {
    "id": "malaysia",
    "name": "Malaysia",
    "paperCount": 342,
    "universities": [
      {
        "id": "apu",
        "name": "Asia Pacific University...",
        "paperCount": 156,
        "authorCount": 3
      }
    ]
  }
}
```

### 3. GET /api/data/university/:countryId/:universityId
**Purpose**: Get authors for a specific university
**Response**:
```json
{
  "university": {
    "id": "apu",
    "name": "Asia Pacific University...",
    "country": "Malaysia",
    "paperCount": 156,
    "authors": [
      {
        "id": "56127745700",
        "name": "Mohammad Reza Maghami",
        "affiliation": "Asia Pacific University...",
        "paperCount": 8
      }
    ]
  }
}
```

### 4. GET /api/data/author/:authorId
**Purpose**: Get papers for a specific author
**Response**:
```json
{
  "author": {
    "id": "56127745700",
    "name": "Mohammad Reza Maghami",
    "affiliation": "Asia Pacific University...",
    "paperCount": 8,
    "papers": [
      {
        "id": "1",
        "title": "Net zero energy buildings...",
        "year": 2025,
        "source": "Energy Reports",
        "citedBy": 0,
        "doi": "10.1016/...",
        "link": "https://...",
        "authors": ["Mohammad Reza Maghami", ...]
      }
    ]
  }
}
```

### 5. GET /api/search?q={query}&year={year}
**Purpose**: Search across all data
**Response**: Filtered countries array matching search criteria

### 6. GET /api/stats
**Purpose**: Get overall statistics
**Response**:
```json
{
  "totalPapers": 1456,
  "totalCountries": 7,
  "totalUniversities": 15,
  "totalAuthors": 234
}
```

## Frontend Integration Changes

### Replace mock.js with API calls:
1. **App.js**: Fetch stats from `/api/stats` on mount
2. **MapView.js**: 
   - Fetch countries from `/api/data/countries` on mount
   - Apply client-side search/filter on fetched data
3. **SidePanel.js**:
   - Fetch universities when country clicked: `/api/data/country/:id`
   - Fetch authors when university clicked: `/api/data/university/:countryId/:uniId`
   - Fetch papers when author clicked: `/api/data/author/:id`

### Data Processing Script
- Create `/app/backend/scripts/process_csv.py` to:
  1. Read CSV file
  2. Parse and clean data
  3. Build hierarchical structure
  4. Get country coordinates from geocoding service or static mapping
  5. Store in MongoDB
  6. Can be run on dataset change

## Maintainability Features
1. **CSV Upload Endpoint** (optional): POST /api/admin/upload-csv
2. **Reprocess Data**: POST /api/admin/reprocess
3. **Country Coordinates**: Use static mapping file that can be updated
4. **Flexible Schema**: MongoDB allows easy schema changes

## Mock Data Removal
Files to update:
- `/app/frontend/src/data/mock.js` - Remove or keep for development
- Replace all `mockCountries` imports with API calls
- Add loading states and error handling
