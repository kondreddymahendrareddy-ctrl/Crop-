import sys
sys.path.insert(0, '.')
from modules.weather_service import get_weather_data

cities = ['Madurai', 'Hyderabad', 'Delhi', 'Tamil Nadu', 'Bangalore', 'Vijayawada']
for city in cities:
    ok, r = get_weather_data(city)
    if ok:
        print(f"OK  {city:15} -> {r['resolved_name']} | {r['temperature']}C | {r['weather_description']}")
    else:
        print(f"ERR {city:15} -> {r}")
