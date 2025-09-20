from langchain_core.tools import tool
import requests
import json
import os

@tool
def weather_data(location_name: str):
    """
    Fetch weather data for any location worldwide using WeatherAPI.
    Returns a JSON string with weather details or an error message.

    Args:
    location_name (str): Name of the city, district, state, or country (e.g., "Mumbai", "Delhi", "Rajasthan", "New York").
    """

    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        return "Weather API key not configured."
    
    response = requests.get(
        f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location_name}&aqi=no"
    )

    if response.status_code != 200:
        return "Sorry, information not available."
    
    data = response.json()

    if "error" in data:
        return "Sorry, information not available."
    
    return json.dumps(data)