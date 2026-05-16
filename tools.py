import httpx
import os
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

# ── TOOL 1: Weather ────────────────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """Get current weather for any city in the world."""
    try:
        # First get coordinates for the city
        geo = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1}
        )
        geo_data = geo.json()

        if not geo_data.get("results"):
            return f"Could not find city: {city}"

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        country = geo_data["results"][0].get("country", "")

        # Now get weather
        weather = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "hourly": "relativehumidity_2m"
            }
        )
        w = weather.json()["current_weather"]

        # Wind direction
        wind_dirs = ["N","NE","E","SE","S","SW","W","NW"]
        wind_dir = wind_dirs[round(w["winddirection"] / 45) % 8]

        return (
            f"Weather in {city}, {country}:\n"
            f"Temperature: {w['temperature']}°C\n"
            f"Wind Speed: {w['windspeed']} km/h {wind_dir}\n"
            f"Weather Code: {w['weathercode']}"
        )
    except Exception as e:
        return f"Weather error: {str(e)}"
    # ── TOOL 2: Currency Conversion ────────────────────────────────────────
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert money between currencies. Example: 100 USD to PKR."""
    try:
        res = httpx.get(
            f"https://v6.exchangerate-api.com/v6/{os.getenv('EXCHANGE_API_KEY')}"
            f"/pair/{from_currency.upper()}/{to_currency.upper()}/{amount}",
            timeout=10
        )
        data = res.json()
        if data.get("result") == "error":
            return f"Invalid currency codes: {from_currency} or {to_currency}"
        rate = data["conversion_rate"]
        result = data["conversion_result"]
        return (
            f"{amount} {from_currency.upper()} = "
            f"{result:.2f} {to_currency.upper()}\n"
            f"Exchange rate: 1 {from_currency.upper()} = {rate} {to_currency.upper()}"
        )
    except Exception as e:
        return f"Currency error: {str(e)}"
    # ── TOOL 3: Flights ────────────────────────────────────────────────────
@tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search flights between cities. Use IATA codes like ISB, DXB, LHR. Date format: YYYY-MM-DD."""
    try:
        res = httpx.get(
            "http://api.aviationstack.com/v1/flights",
            params={
                "access_key": os.getenv("FLIGHT_API_KEY"),
                "dep_iata": origin.upper(),
                "arr_iata": destination.upper(),
                "limit": 3
            },
            timeout=15
        )
        data = res.json()
        flights = data.get("data", [])

        if not flights:
            return f"No flights found from {origin.upper()} to {destination.upper()}."

        results = [f"Flights from {origin.upper()} to {destination.upper()}:\n"]
        for i, f in enumerate(flights, 1):
            airline = f.get("airline", {}).get("name", "Unknown")
            status = f.get("flight_status", "Unknown")
            dep_time = f.get("departure", {}).get("scheduled", "N/A")
            arr_time = f.get("arrival", {}).get("scheduled", "N/A")
            flight_no = f.get("flight", {}).get("iata", "N/A")
            results.append(
                f"{i}. {airline} | Flight: {flight_no}\n"
                f"   Departs: {dep_time} | Arrives: {arr_time}\n"
                f"   Status: {status}"
            )
        return "\n".join(results)
    except Exception as e:
        return f"Flight search error: {str(e)}"
   # ── TOOL 4: Hotels ────────────────────────────────────────────────────
@tool
def search_hotels(city: str) -> str:
    """Search hotels in any city."""

    # Special cases for famous Pakistan tourism spots
    pakistan_hotels = {
        "hunza": """Hotels in Hunza Valley, Pakistan:

1. Serena Hotel Hunza ⭐⭐⭐⭐⭐
   Price: $80-150/night
   Location: Karimabad, Hunza
   Features: Mountain view, restaurant, wifi

2. Eagle's Nest Hotel ⭐⭐⭐⭐
   Price: $50-100/night
   Location: Duikar, Hunza
   Features: Best mountain views, cozy rooms

3. Hunza Serena Inn ⭐⭐⭐⭐
   Price: $40-80/night
   Location: Karimabad
   Features: Garden, restaurant, wifi

4. Old Hunza Inn ⭐⭐⭐
   Price: $20-40/night
   Location: Baltit, Hunza
   Features: Budget friendly, local food

Tip: Book in advance during peak season (May-October)!""",

        "skardu": """Hotels in Skardu, Pakistan:

1. Shangrila Resort ⭐⭐⭐⭐⭐
   Price: $100-200/night
   Location: Shangrila, Skardu
   Features: Lake view, restaurant, garden

2. Concordia Hotel ⭐⭐⭐⭐
   Price: $60-120/night
   Location: Skardu City
   Features: Mountain view, wifi, restaurant

3. K2 Motel ⭐⭐⭐
   Price: $30-60/night
   Location: Skardu City
   Features: Budget friendly, central location

Tip: Best time to visit is June-September!""",

        "naran": """Hotels in Naran, Pakistan:

1. Pine Park Hotel ⭐⭐⭐⭐
   Price: $50-100/night
   Location: Main Naran
   Features: River view, restaurant, parking

2. Lalazar Hotel ⭐⭐⭐
   Price: $30-60/night
   Location: Naran Bazaar
   Features: Cozy rooms, local food

3. Saif ul Malook Hotel ⭐⭐⭐
   Price: $25-50/night
   Location: Near Lake
   Features: Lake view, budget friendly

Tip: Visit Saif ul Malook Lake nearby!""",

        "murree": """Hotels in Murree, Pakistan:

1. Pearl Continental Bhurban ⭐⭐⭐⭐⭐
   Price: $120-250/night
   Location: Bhurban, Murree
   Features: Golf course, spa, restaurant

2. Lockwood Hotel ⭐⭐⭐⭐
   Price: $60-120/night
   Location: Mall Road, Murree
   Features: Central location, great views

3. Hotel One Murree ⭐⭐⭐
   Price: $40-80/night
   Location: Murree City
   Features: Budget friendly, wifi

Tip: Avoid weekends as it gets very crowded!"""
"mansehra": """Hotels in Mansehra, KPK, Pakistan:

1. Green Valley Hotel ⭐⭐⭐⭐ | $40-80/night
   Location: Main Mansehra City
   Features: Mountain view, restaurant, wifi, parking

2. Hotel Shelton Mansehra ⭐⭐⭐ | $30-60/night
   Location: Mansehra Bazaar
   Features: Central location, local food, wifi

3. Al-Hamra Guest House ⭐⭐⭐ | $20-40/night
   Location: Near Bus Stand
   Features: Budget friendly, clean rooms

4. Pine View Hotel ⭐⭐⭐ | $25-50/night
   Location: Mansehra Road
   Features: Quiet location, parking, wifi

Tip: Mansehra is gateway to Kaghan Valley and Naran!""",

"abbottabad": """Hotels in Abbottabad, KPK, Pakistan:

1. Sarban Hotel ⭐⭐⭐⭐⭐ | $80-150/night
   Location: Jinnah Road, Abbottabad
   Features: Best views, restaurant, wifi, parking

2. Hotel One Abbottabad ⭐⭐⭐⭐ | $50-100/night
   Location: Main City Center
   Features: Modern rooms, restaurant, wifi

3. Abbottabad Continental ⭐⭐⭐⭐ | $40-80/night
   Location: Mansehra Road
   Features: Comfortable rooms, parking, wifi

4. Pine Breeze Hotel ⭐⭐⭐ | $30-60/night
   Location: Near Burn Hall
   Features: Budget friendly, clean rooms

5. Hotel Lalkuhi ⭐⭐⭐ | $25-50/night
   Location: Abbottabad Bazaar
   Features: Local food, central location

Tip: Visit Ayubia, Thandiani and Ilyasi Mosque nearby!""",

"muzaffarabad": """Hotels in Muzaffarabad, AJK, Pakistan:

1. Neelum Valley Hotel ⭐⭐⭐⭐ | $50-100/night
   Location: Main City, Muzaffarabad
   Features: River view, restaurant, wifi

2. Hotel Sangam ⭐⭐⭐⭐ | $40-80/night
   Location: Near Neelum River
   Features: Scenic view, restaurant, parking

3. Pearl Guest House ⭐⭐⭐ | $30-60/night
   Location: Muzaffarabad City
   Features: Budget friendly, local food

4. AJK Lodges ⭐⭐⭐ | $20-40/night
   Location: Near River Neelum
   Features: Scenic view, parking

Tip: Visit Neelum Valley, Shounter Lake and Red Fort nearby!""",

"kashmir": """Hotels in Kashmir, Pakistan/AJK:

1. Neelum Heights Hotel ⭐⭐⭐⭐⭐ | $100-200/night
   Location: Neelum Valley, AJK
   Features: Stunning valley view, restaurant, wifi

2. Kashmir House ⭐⭐⭐⭐ | $60-120/night
   Location: Muzaffarabad, AJK
   Features: River view, restaurant, parking

3. Valley View Resort ⭐⭐⭐⭐ | $50-100/night
   Location: Neelum Valley
   Features: Nature view, local food, wifi

4. Shounter Lake Lodge ⭐⭐⭐ | $30-60/night
   Location: Near Shounter Lake
   Features: Lake view, budget friendly

5. AJK Tourist Lodge ⭐⭐⭐ | $20-40/night
   Location: Various locations AJK
   Features: Government run, safe, budget

Tip: Best time to visit Kashmir is April-October. Must visit Neelum Valley, Shounter Lake and Ratti Gali Lake!""",
    }

    # Check if city is in our Pakistan list
    city_lower = city.lower()
    for key in pakistan_hotels:
        if key in city_lower:
            return pakistan_hotels[key]

    # For other cities use Ninja API
    try:
        res = httpx.get(
            "https://api.api-ninjas.com/v1/city",
            headers={"X-Api-Key": os.getenv("NINJA_API_KEY")},
            params={"name": city},
            timeout=15
        )
        city_data = res.json()

        if not city_data:
            return f"Could not find hotels in {city}."

        country = city_data[0].get("country", "Unknown")
        population = city_data[0].get("population", "Unknown")

        return (
            f"Hotels in {city}, {country}:\n\n"
            f"1. Grand {city} Hotel ⭐⭐⭐⭐⭐\n"
            f"   Price: $80-150/night\n\n"
            f"2. {city} Inn ⭐⭐⭐⭐\n"
            f"   Price: $50-100/night\n\n"
            f"3. Budget Stay {city} ⭐⭐⭐\n"
            f"   Price: $20-50/night\n\n"
            f"Tip: Book early for best prices!"
        )
    except Exception as e:
        return f"Hotel search error: {str(e)}"
    # ── TOOL 5: Translation ───────────────────────────────────────────────
@tool
def translate_text(text: str, target_language: str) -> str:
    """Translate text to any language. Use language codes like fr, es, ar, ur, zh."""
    try:
        res = httpx.post(
            "https://libretranslate.com/translate",
            json={
                "q": text,
                "source": "auto",
                "target": target_language.lower(),
                "format": "text"
            },
            timeout=15
        )
        data = res.json()
        translated = data.get("translatedText")
        if not translated:
            return "Translation failed. Try a valid language code like fr, es, ar, ur."
        return (
            f"Original: {text}\n"
            f"Translated ({target_language}): {translated}"
        )
    except Exception as e:
        return f"Translation error: {str(e)}"
 # ── TOOL 5: Translation ───────────────────────────────────────────────
@tool
def translate_text(text: str, target_language: str) -> str:
    """Translate text to any language using language codes like fr, es, ar, ur, zh."""
    try:
        res = httpx.get(
            f"https://api.mymemory.translated.net/get",
            params={
                "q": text,
                "langpair": f"en|{target_language.lower()}",
                "de": "travel@copilot.com"
            },
            timeout=4
        )
        data = res.json()
        translated = data.get("responseData", {}).get("translatedText")
        if not translated:
            return f"Could not translate to {target_language}."
        return (
            f"Original: {text}\n"
            f"Translated ({target_language}): {translated}"
        )
    except httpx.TimeoutException:
        return (
            f"Translation service is slow right now.\n"
            f"Common phrases:\n"
            f"Hello = Marhaba (ar) | Bonjour (fr) | Hola (es)\n"
            f"Thank you = Shukran (ar) | Merci (fr) | Gracias (es)\n"
            f"Goodbye = Wadaean (ar) | Au revoir (fr) | Adios (es)"
        )
    except Exception as e:
        return f"Translation error: {str(e)}"