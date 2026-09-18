import urllib.request
import json

CITY_COORDS = {
    "tashkent": (41.2995, 69.2401),
    "toshkent": (41.2995, 69.2401),
    "samarkand": (39.6542, 66.9597),
    "samarqand": (39.6542, 66.9597),
    "bukhara": (39.7747, 64.4286),
    "buxoro": (39.7747, 64.4286),
    "fergana": (40.3842, 71.7843),
    "farg'ona": (40.3842, 71.7843),
    "andijan": (40.7821, 72.3442),
    "andijon": (40.7821, 72.3442),
    "namangan": (40.9983, 71.6726),
    "khiva": (41.3783, 60.3639),
    "xorazm": (41.3783, 60.3639),
    "urgench": (41.5562, 60.6317),
    "nukus": (42.4602, 59.6166),
    "navoi": (40.0844, 65.3792),
    "navoiy": (40.0844, 65.3792),
    "jizzakh": (40.1158, 67.8422),
    "jizzax": (40.1158, 67.8422),
    "qarshi": (38.8606, 65.7891),
    "termiz": (37.2242, 67.2783)
}


def weather_action(city: str = "Toshkent") -> str:
    city_lower = city.lower().strip()
    coords = CITY_COORDS.get(city_lower, (41.2995, 69.2401))
    lat, lon = coords
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            current = data.get("current", {})
            temp = current.get("temperature_2m", "N/A")
            app_temp = current.get("apparent_temperature", "N/A")
            humidity = current.get("relative_humidity_2m", "N/A")
            wind = current.get("wind_speed_10m", "N/A")
            
            return f"{city.capitalize()}da ob-havo: Harorat {temp}?C (his qilinishi {app_temp}?C), Namlik {humidity}%, Shamol tezligi {wind} km/soat."
    except Exception as e:
        return f"Ob-havo ma'lumotini olishda xatolik: {e}"
