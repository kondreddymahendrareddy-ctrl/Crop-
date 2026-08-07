import requests
from datetime import datetime

# Map common Indian state names to their capital/major city
INDIA_STATE_TO_CITY = {
    "tamil nadu": "Chennai", "andhra pradesh": "Hyderabad", "telangana": "Hyderabad",
    "karnataka": "Bangalore", "kerala": "Thiruvananthapuram", "maharashtra": "Mumbai",
    "gujarat": "Ahmedabad", "rajasthan": "Jaipur", "madhya pradesh": "Bhopal",
    "uttar pradesh": "Lucknow", "bihar": "Patna", "west bengal": "Kolkata",
    "odisha": "Bhubaneswar", "jharkhand": "Ranchi", "chhattisgarh": "Raipur",
    "punjab": "Chandigarh", "haryana": "Chandigarh", "himachal pradesh": "Shimla",
    "uttarakhand": "Dehradun", "assam": "Guwahati", "meghalaya": "Shillong",
    "manipur": "Imphal", "nagaland": "Kohima", "tripura": "Agartala",
    "mizoram": "Aizawl", "arunachal pradesh": "Itanagar", "sikkim": "Gangtok",
    "goa": "Panaji", "jammu and kashmir": "Srinagar", "ladakh": "Leh",
    "delhi": "Delhi", "ap": "Hyderabad", "tn": "Chennai",
}

WMO_WEATHER_CODES = {
    0: "Clear Sky ☀️", 1: "Mainly Clear 🌤️", 2: "Partly Cloudy ⛅",
    3: "Overcast ☁️", 45: "Foggy 🌫️", 48: "Icy Fog 🌫️",
    51: "Light Drizzle 🌦️", 53: "Moderate Drizzle 🌦️", 55: "Dense Drizzle 🌧️",
    61: "Slight Rain 🌧️", 63: "Moderate Rain 🌧️", 65: "Heavy Rain 🌧️",
    71: "Light Snow ❄️", 73: "Moderate Snow ❄️", 75: "Heavy Snow ❄️",
    80: "Rain Showers 🌦️", 81: "Moderate Showers 🌧️", 82: "Violent Showers ⛈️",
    95: "Thunderstorm ⛈️", 96: "Thunderstorm with Hail ⛈️",
}


def _geocode(query: str, count: int = 5):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": query, "count": count, "language": "en", "format": "json"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("results", [])


def _resolve_query(location_name: str):
    """Return the best search query, handling state names → city."""
    key = location_name.strip().lower()
    if key in INDIA_STATE_TO_CITY:
        return INDIA_STATE_TO_CITY[key], True
    return location_name.strip(), False


def _fetch_weather_coords(lat, lon, name):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    current = data.get("current", {})
    daily = data.get("daily", {})

    wcode = current.get("weather_code", 0)
    rainfall = (daily.get("precipitation_sum") or [0.0])[0] or 0.0
    temp_max = (daily.get("temperature_2m_max") or [None])[0]
    temp_min = (daily.get("temperature_2m_min") or [None])[0]

    return {
        "resolved_name": name,
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "wind_speed": current.get("wind_speed_10m"),
        "rainfall": round(rainfall, 2),
        "temp_max": temp_max,
        "temp_min": temp_min,
        "weather_code": wcode,
        "weather_description": WMO_WEATHER_CODES.get(wcode, "Unknown"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_weather_exact_coords(lat, lon):
    """Fetches user's exact location weather using HTML5 Geolocation coordinates."""
    try:
        # Reverse geocode to get city name for UI
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10}
        headers = {"User-Agent": "IntelligentCropSystem/1.0"}
        
        city = "Exact GPS Location"
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                address = data.get("address", {})
                city_name = address.get("city") or address.get("town") or address.get("county") or address.get("state")
                if city_name:
                    city = f"{city_name} (GPS)"
        except Exception:
            pass # Fallback to generic name if reverse geocoding fails
            
        weather_data = _fetch_weather_coords(lat, lon, city)
        return True, weather_data
    except Exception as e:
        return False, f"GPS Location Error: {e}"


def get_weather_by_ip():
    """Fetches user's current location via IP and gets weather for those coordinates."""
    try:
        # Get location from IP
        resp = requests.get("http://ip-api.com/json/", timeout=5)
        resp.raise_for_status()
        loc_data = resp.json()
        
        if loc_data.get("status") != "success":
            return False, "Could not determine live location from IP."
            
        lat = loc_data.get("lat")
        lon = loc_data.get("lon")
        city = loc_data.get("city", "Unknown City")
        region = loc_data.get("regionName", "")
        country = loc_data.get("country", "")
        
        resolved_name = f"{city}, {region}, {country}" if region else f"{city}, {country}"
        
        # Fetch weather for coordinates
        weather_data = _fetch_weather_coords(lat, lon, resolved_name)
        return True, weather_data
        
    except Exception as e:
        return False, f"Live Location Error: {e}"


def get_weather_data(location_name: str):
    """
    Fetch real-time weather for any city, district, or Indian state name.
    """
    try:
        search_query, remapped = _resolve_query(location_name)
        results = _geocode(search_query, count=5)

        if not results and " " in search_query:
            results = _geocode(search_query.split()[0], count=5)

        if not results:
            return False, (
                f"Location **'{location_name}'** not found on the geocoding API. "
                f"Please enter a **city name** (e.g., Chennai, Hyderabad, Mumbai)."
            )

        best = max(results, key=lambda r: r.get("population") or 0)
        lat, lon = best["latitude"], best["longitude"]
        city = best.get("name", search_query)
        admin1 = best.get("admin1", "")
        country = best.get("country", "")
        resolved = f"{city}, {admin1}, {country}" if admin1 else f"{city}, {country}"

        if remapped:
            resolved = f"{resolved}  *(auto-mapped from '{location_name}')*"

        return True, _fetch_weather_coords(lat, lon, resolved)

    except requests.exceptions.ConnectionError:
        return False, "❌ No internet connection. Please check your network."
    except requests.exceptions.Timeout:
        return False, "⏱️ Weather API timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        return False, f"🌐 API HTTP error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def get_location_suggestions(query: str):
    try:
        search, _ = _resolve_query(query)
        results = _geocode(search, count=8)
        suggestions = []
        for r in results:
            name = r.get("name", "")
            admin1 = r.get("admin1", "")
            country = r.get("country", "")
            label = f"{name}, {admin1}, {country}" if admin1 else f"{name}, {country}"
            suggestions.append({"label": label, "lat": r["latitude"], "lon": r["longitude"]})
        return suggestions
    except Exception:
        return []
