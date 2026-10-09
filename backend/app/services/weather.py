"""
Weather-Aware Recommendation Service.
Fetches real-time weather and 7-day forecast from Open-Meteo API for Sri Lankan destinations.
Provides rain warnings, seasonal advice, and fallback defaults.
"""

import httpx
from datetime import datetime


WEATHER_CODE_MAP = {
    0: ("Clear Sky", "☀️", "Sunny and dry, perfect for outdoors and photography."),
    1: ("Mainly Clear", "🌤️", "Good weather for sightseeing and travel."),
    2: ("Partly Cloudy", "⛅", "Pleasant weather with scattered clouds."),
    3: ("Overcast", "☁️", "Cloudy skies, mild heat."),
    45: ("Foggy", "🌫️", "Misty conditions, especially in hill country."),
    48: ("Depositing Rime Fog", "🌫️", "Misty mountain passes."),
    51: ("Light Drizzle", "🌦️", "Light drizzle, carry an umbrella."),
    53: ("Moderate Drizzle", "🌧️", "Intermittent drizzle."),
    55: ("Dense Drizzle", "🌧️", "Wet conditions."),
    61: ("Slight Rain", "🌦️", "Occasional light rain showers."),
    63: ("Moderate Rain", "🌧️", "Noticeable rain; prioritize sheltered activities."),
    65: ("Heavy Rain", "⛈️", "Heavy rainfall; beach & hiking caution advised."),
    80: ("Rain Showers", "🌧️", "Passing tropical showers."),
    81: ("Moderate Showers", "🌧️", "Frequent rain showers."),
    82: ("Violent Showers", "⛈️", "Severe tropical downpour."),
    95: ("Thunderstorm", "⚡", "Thunderstorms; avoid open water and mountain summits.")
}


async def get_live_weather(lat: float, lon: float) -> dict:
    """
    Fetch current weather and 24-hour summary for given coordinates.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Asia%2FColombo"

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                code = current.get("weather_code", 0)
                condition_label, icon, advice = WEATHER_CODE_MAP.get(
                    code, ("Pleasant", "☀️", "Good travel conditions.")
                )

                daily = data.get("daily", {})
                max_temp = daily.get("temperature_2m_max", [29.0])[0]
                min_temp = daily.get("temperature_2m_min", [24.0])[0]
                rain_prob = daily.get("precipitation_probability_max", [15])[0]

                return {
                    "temperature_c": round(current.get("temperature_2m", 28.5), 1),
                    "condition": condition_label,
                    "icon": icon,
                    "wind_speed_kmh": round(current.get("wind_speed_10m", 12.0), 1),
                    "humidity": current.get("relative_humidity_2m", 75),
                    "rain_probability": rain_prob,
                    "temp_max": max_temp,
                    "temp_min": min_temp,
                    "travel_advice": advice,
                    "is_rainy": code >= 61,
                    "source": "Open-Meteo Live API"
                }
    except Exception as e:
        # Fallback to seasonal climate estimate for Sri Lanka
        pass

    # Fallback response
    return {
        "temperature_c": 28.0,
        "condition": "Partly Cloudy",
        "icon": "⛅",
        "wind_speed_kmh": 14.0,
        "humidity": 72,
        "rain_probability": 20,
        "temp_max": 31.0,
        "temp_min": 24.0,
        "travel_advice": "Pleasant tropical climate; great time to explore.",
        "is_rainy": False,
        "source": "Seasonal Historical Baseline"
    }
