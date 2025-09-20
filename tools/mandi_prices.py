from langchain_core.tools import tool
import requests
import os
import json
from datetime import datetime, timedelta

@tool
def mandi_prices(state_name: str):
    """
    Fetches the latest mandi prices for a given state from the ENAM website.
    Returns a JSON string with mandi price details or an error message.

    Args:
    state_name (str): Name of the Indian state (e.g., "RAJASTHAN", "WEST BENGAL").
    """

    today_date = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")

    response = requests.post("https://enam.gov.in/web/Ajax_ctrl/trade_data_list", data={
        "stateName": state_name.upper(),
        "apmcName": "-- Select APMCs --",
        "commodityName": "-- Select Commodity --",
        "fromDate": yesterday_date,
        "toDate": today_date,
    })

    if response.status_code != 200:
        return "Sorry, information not available."

    data = response.json()

    if "data" not in data or not data["data"]:
        return "Sorry, information not available."
    
    return json.dumps(data["data"])
