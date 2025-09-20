from langchain_core.tools import tool
import requests
import json
import os

@tool
def weather_data(district_name: str):
    """
    Fetch weather data for a given district in Rajasthan using WeatherAPI.
    Returns a JSON string with weather details or an error message in Hindi.

    Args:
    district_name (str): Name of the district in Rajasthan.
    """

    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        return "Weather API key not configured."
    
    response = requests.get(
        f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={district_name}&aqi=no"
    )

    if response.status_code != 200:
        return "माफ़ करें, मौसम डेटा उपलब्ध नहीं है।"
    
    data = response.json()

    if "error" in data:
        return "माफ़ करें, मौसम डेटा उपलब्ध नहीं है।"
    
    return json.dumps(data)