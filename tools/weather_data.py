from langchain_core.tools import tool
import requests
import json
import os

@tool
def weather_data(location_name: str):
    """
    Fetch weather data for Indian cities and locations. Prioritizes Indian locations and provides farmer-friendly weather information.
    
    Args:
    location_name (str): Name of the city, district, or state in India (e.g., "Mumbai", "Delhi", "Punjab", "Jaipur").
    """

    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        return "Weather API key not configured."
    
    # Add India suffix for better location matching
    search_location = location_name
    if not any(country in location_name.lower() for country in ['india', 'pakistan', 'bangladesh', 'nepal', 'sri lanka']):
        search_location = f"{location_name}, India"
    
    response = requests.get(
        f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={search_location}&aqi=no"
    )

    if response.status_code != 200:
        return "Sorry, weather information not available for this location."
    
    data = response.json()

    if "error" in data:
        return "Sorry, weather information not available for this location."
    
    return json.dumps(data)