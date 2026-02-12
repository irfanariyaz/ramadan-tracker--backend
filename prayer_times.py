import httpx
from datetime import date
from sqlalchemy.orm import Session
import crud


async def get_prayer_times(db: Session, entry_date: date, city: str = None, country: str = None, 
                          latitude: str = None, longitude: str = None):
    """
    Get prayer times from Aladhan API with caching
    """
    # Create location key for caching
    if city and country:
        location_key = f"{city}_{country}"
        url = f"http://api.aladhan.com/v1/timingsByCity/{entry_date.strftime('%d-%m-%Y')}"
        params = {"city": city, "country": country}
    elif latitude and longitude:
        location_key = f"{latitude}_{longitude}"
        url = f"http://api.aladhan.com/v1/timings/{entry_date.strftime('%d-%m-%Y')}"
        params = {"latitude": latitude, "longitude": longitude}
    else:
        # Default to a common location if none provided
        location_key = "default_mecca_saudi_arabia"
        url = f"http://api.aladhan.com/v1/timingsByCity/{entry_date.strftime('%d-%m-%Y')}"
        params = {"city": "Mecca", "country": "Saudi Arabia"}
    
    # Check cache first
    cached = crud.get_cached_prayer_times(db, entry_date, location_key)
    if cached:
        return {
            "date": entry_date.strftime('%Y-%m-%d'),
            "fajr": cached.fajr,
            "dhuhr": cached.dhuhr,
            "asr": cached.asr,
            "maghrib": cached.maghrib,
            "isha": cached.isha
        }
    
    # Fetch from API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 200:
                timings = data['data']['timings']
                prayer_times = {
                    "fajr": timings['Fajr'],
                    "dhuhr": timings['Dhuhr'],
                    "asr": timings['Asr'],
                    "maghrib": timings['Maghrib'],
                    "isha": timings['Isha']
                }
                
                # Cache the results
                crud.cache_prayer_times(db, entry_date, location_key, prayer_times)
                
                return {
                    "date": entry_date.strftime('%Y-%m-%d'),
                    **prayer_times
                }
    except Exception as e:
        print(f"Error fetching prayer times: {e}")
        # Return default times if API fails
        return {
            "date": entry_date.strftime('%Y-%m-%d'),
            "fajr": "05:00",
            "dhuhr": "12:30",
            "asr": "15:45",
            "maghrib": "18:15",
            "isha": "19:30"
        }
