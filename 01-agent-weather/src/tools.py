from typing import Any, Dict

import requests


def get_weather_data_stub(location: str) -> dict:
    # just a placeholder for testing
    return {
        "location": location,
        "temperature": "22 Celsius degrees",
        "humidity": "40%",
        "condition": "Sunny",
    }


# !!! The Open-Meteo API wrappers are kindly offered by LeChat !!!
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


# Minimal weather-code mapping (Open-Meteo uses WMO codes)
WMO_WEATHER = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherToolError(RuntimeError):
    pass


def _geocode(location: str, timeout_s: float = 10.0) -> Dict[str, Any]:
    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json",
    }
    r = requests.get(GEOCODE_URL, params=params, timeout=timeout_s)
    r.raise_for_status()
    data = r.json()

    results = data.get("results") or []
    if not results:
        raise WeatherToolError(f"Could not find location '{location}'")
    return results[0]


def _forecast_current(lat: float, lon: float, timezone: str, timeout_s: float = 10.0) -> Dict[str, Any]:
    params = {
        "latitude": lat,
        "longitude": lon,
        # current weather fields
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m",
        # helpful metadata for time formatting
        "timezone": timezone,
    }
    r = requests.get(FORECAST_URL, params=params, timeout=timeout_s)
    r.raise_for_status()
    return r.json()


def get_weather_open_meteo(
    location: str,
    *,
    timezone: str = "Europe/Paris",
    timeout_s: float = 10.0,
) -> Dict[str, Any]:
    """
    No API key required.

    Returns a stable dict you can store in agent memory.
    Raises WeatherToolError on user-facing failures.
    Raises requests.HTTPError on network/HTTP failures.
    """
    loc = _geocode(location, timeout_s=timeout_s)
    lat = float(loc["latitude"])
    lon = float(loc["longitude"])

    forecast = _forecast_current(
        lat, lon, timezone=timezone, timeout_s=timeout_s)
    current = forecast.get("current") or {}

    code = current.get("weather_code")
    desc = WMO_WEATHER.get(code, "Unknown conditions") if isinstance(
        code, int) else "Unknown conditions"

    # Build a compact, agent-friendly result
    return {
        "location": {
            "query": location,
            "name": loc.get("name"),
            "country": loc.get("country"),
            "admin1": loc.get("admin1"),
            "latitude": lat,
            "longitude": lon,
            "timezone": forecast.get("timezone", timezone),
        },
        "current": {
            "time": current.get("time"),
            "temperature_c": current.get("temperature_2m"),
            "apparent_temperature_c": current.get("apparent_temperature"),
            "weather_code": code,
            "weather_description": desc,
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "wind_direction_deg": current.get("wind_direction_10m"),
        },
        "source": "open-meteo.com",
    }


if __name__ == "__main__":
    # simple test
    location = "Venezia, Italy"
    weather = get_weather_open_meteo(location)
    print('Location:', location)
    print('Weather:', weather)
