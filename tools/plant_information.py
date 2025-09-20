from langchain_core.tools import tool
from .search import search

@tool
def plant_information(plant_name: str):
    """
    Searches the web for information about a specific plant in India.
    Returns search results or an error message in Hindi.

    Args:
    plant_name (str): Name of the plant to search for.
    """
    search_query = f"{plant_name} plant information in India"

    search_results = search.run(search_query)

    if not search_results:
        return "माफ़ करें, जानकारी उपलब्ध नहीं है।"
    
    return search_results