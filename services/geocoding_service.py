import os
import requests
from typing import Optional, Dict, Tuple

# In-memory cache for geocoded addresses
_geocode_cache: Dict[str, Tuple[float, float]] = {}


def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Convert address to lat/lng using Google Geocoding API.
    Returns (latitude, longitude) tuple or None if geocoding fails.
    """
    if not address:
        return None

    if address in _geocode_cache:
        return _geocode_cache[address]

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_MAPS_API_KEY environment variable not set")
        return None

    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK" and data["results"]:
            location = data["results"][0]["geometry"]["location"]
            coords = (location["lat"], location["lng"])
            _geocode_cache[address] = coords
            return coords
        return None
    except Exception as e:
        print(f"Geocoding error for {address}: {e}")
        return None
