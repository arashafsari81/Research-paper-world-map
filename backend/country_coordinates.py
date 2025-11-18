# Static country coordinates mapping
# Used for displaying countries on the world map

COUNTRY_COORDINATES = {
    'malaysia': {'lat': 4.2105, 'lng': 101.9758},
    'china': {'lat': 35.8617, 'lng': 104.1954},
    'turkey': {'lat': 38.9637, 'lng': 35.2433},
    'united kingdom': {'lat': 55.3781, 'lng': -3.4360},
    'uk': {'lat': 55.3781, 'lng': -3.4360},
    'united states': {'lat': 37.0902, 'lng': -95.7129},
    'usa': {'lat': 37.0902, 'lng': -95.7129},
    'india': {'lat': 20.5937, 'lng': 78.9629},
    'iran': {'lat': 32.4279, 'lng': 53.6880},
    'viet nam': {'lat': 14.0583, 'lng': 108.2772},
    'vietnam': {'lat': 14.0583, 'lng': 108.2772},
    'south africa': {'lat': -30.5595, 'lng': 22.9375},
    'botswana': {'lat': -22.3285, 'lng': 24.6849},
    'sweden': {'lat': 60.1282, 'lng': 18.6435},
    'bangladesh': {'lat': 23.6850, 'lng': 90.3563},
    'indonesia': {'lat': -0.7893, 'lng': 113.9213},
    'oman': {'lat': 21.4735, 'lng': 55.9754},
    'jordan': {'lat': 30.5852, 'lng': 36.2384},
    'bahrain': {'lat': 26.0667, 'lng': 50.5577},
    'canada': {'lat': 56.1304, 'lng': -106.3468},
    'australia': {'lat': -25.2744, 'lng': 133.7751},
    'germany': {'lat': 51.1657, 'lng': 10.4515},
    'france': {'lat': 46.2276, 'lng': 2.2137},
    'japan': {'lat': 36.2048, 'lng': 138.2529},
    'south korea': {'lat': 35.9078, 'lng': 127.7669},
    'brazil': {'lat': -14.2350, 'lng': -51.9253},
    'mexico': {'lat': 23.6345, 'lng': -102.5528},
    'italy': {'lat': 41.8719, 'lng': 12.5674},
    'spain': {'lat': 40.4637, 'lng': -3.7492},
    'netherlands': {'lat': 52.1326, 'lng': 5.2913},
    'singapore': {'lat': 1.3521, 'lng': 103.8198},
    'thailand': {'lat': 15.8700, 'lng': 100.9925},
    'pakistan': {'lat': 30.3753, 'lng': 69.3451},
    'egypt': {'lat': 26.8206, 'lng': 30.8025},
    'saudi arabia': {'lat': 23.8859, 'lng': 45.0792},
    'uae': {'lat': 23.4241, 'lng': 53.8478},
    'united arab emirates': {'lat': 23.4241, 'lng': 53.8478},
    'russia': {'lat': 61.5240, 'lng': 105.3188},
    'poland': {'lat': 51.9194, 'lng': 19.1451},
    'philippines': {'lat': 12.8797, 'lng': 121.7740},
}

def get_country_coordinates(country_name: str) -> dict:
    """Get coordinates for a country name (case-insensitive)."""
    key = country_name.lower().strip()
    return COUNTRY_COORDINATES.get(key, {'lat': 0, 'lng': 0})
