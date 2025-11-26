from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from csv_processor import CSVProcessor


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Global data cache - stores data for each year filter
cached_data = {}  # year -> processed_data
cached_stats = {}  # year -> stats

def load_data(year_filter: Optional[int] = None):
    """Load and process CSV data with optional year filter."""
    global cached_data, cached_stats
    
    cache_key = year_filter if year_filter else 'all'
    
    # Return cached data if available
    if cache_key in cached_data:
        return cached_data[cache_key], cached_stats[cache_key]
    
    csv_path = '/app/APU_publications_2021_2025_cleaned_Final.csv'
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found at {csv_path}")
        return None, None
    
    try:
        processor = CSVProcessor(csv_path, year_filter=year_filter)
        processor.load_csv().process_data()
        data = processor.get_processed_data()
        stats = processor.get_stats()
        
        # Cache the results
        cached_data[cache_key] = data
        cached_stats[cache_key] = stats
        
        logger.info(f"Data loaded successfully for year={year_filter}: {stats}")
        return data, stats
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        import traceback
        traceback.print_exc()
        return None, None


# Routes
@api_router.get("/")
async def root():
    return {"message": "Research Papers World Map API"}

@api_router.get("/stats")
async def get_stats(year: Optional[int] = None):
    """Get overall statistics with optional year filter."""
    data, stats = load_data(year_filter=year)
    
    if stats is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Count only countries with valid coordinates (that appear on map)
    countries_on_map = 0
    if data:
        for country in data:
            if country['lat'] != 0 or country['lng'] != 0:
                countries_on_map += 1
    
    return {
        **stats,
        'totalCountries': countries_on_map  # Only show countries visible on map
    }

@api_router.get("/data/countries")
async def get_countries(year: Optional[int] = None):
    """Get all countries with paper counts and coordinates, with optional year filter."""
    data, stats = load_data(year_filter=year)
    
    if data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Return simplified country data for map
    countries = []
    for country in data:
        countries.append({
            'id': country['id'],
            'name': country['name'],
            'lat': country['lat'],
            'lng': country['lng'],
            'paperCount': country['paperCount']
        })
    
    return {'countries': countries}

@api_router.get("/data/country/{country_id}")
async def get_country(country_id: str, year: Optional[int] = None):
    """Get universities for a specific country with optional year filter."""
    data, stats = load_data(year_filter=year)
    
    if data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Find country
    country = None
    for c in data:
        if c['id'] == country_id:
            country = c
            break
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Return country with simplified universities (without full author data)
    universities = []
    for uni in country['universities']:
        universities.append({
            'id': uni['id'],
            'name': uni['name'],
            'paperCount': uni['paperCount'],
            'authors': len(uni['authors'])
        })
    
    return {
        'country': {
            'id': country['id'],
            'name': country['name'],
            'paperCount': country['paperCount'],
            'universities': universities
        }
    }

@api_router.get("/data/university/{country_id}/{university_id}")
async def get_university(country_id: str, university_id: str):
    """Get authors for a specific university."""
    if cached_data is None:
        load_data()
    
    if cached_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Find country and university
    country = None
    for c in cached_data:
        if c['id'] == country_id:
            country = c
            break
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    university = None
    for uni in country['universities']:
        if uni['id'] == university_id:
            university = uni
            break
    
    if not university:
        raise HTTPException(status_code=404, detail="University not found")
    
    # Return university with simplified authors (without papers)
    authors = []
    for author in university['authors']:
        authors.append({
            'id': author['id'],
            'name': author['name'],
            'affiliation': author['affiliation'],
            'paperCount': author['paperCount']
        })
    
    return {
        'university': {
            'id': university['id'],
            'name': university['name'],
            'country': country['name'],
            'paperCount': university['paperCount'],
            'authors': authors
        }
    }

@api_router.get("/data/author/{country_id}/{university_id}/{author_id}")
async def get_author(country_id: str, university_id: str, author_id: str):
    """Get papers for a specific author."""
    if cached_data is None:
        load_data()
    
    if cached_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Find country, university, and author
    country = None
    for c in cached_data:
        if c['id'] == country_id:
            country = c
            break
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    university = None
    for uni in country['universities']:
        if uni['id'] == university_id:
            university = uni
            break
    
    if not university:
        raise HTTPException(status_code=404, detail="University not found")
    
    author = None
    for a in university['authors']:
        if a['id'] == author_id:
            author = a
            break
    
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    return {'author': author}

@api_router.get("/search")
async def search(q: Optional[str] = None, year: Optional[int] = None):
    """Search across all data."""
    if cached_data is None:
        load_data()
    
    if cached_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    results = cached_data
    
    # Note: Search filtering should be done on frontend for better performance
    # This endpoint returns all data, frontend will filter
    return {'countries': results}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()