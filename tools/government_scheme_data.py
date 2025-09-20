from langchain_core.tools import tool
from .all_government_schemes import schemes

@tool
def government_scheme_data(scheme_name: str):
    """
    Fetch information about a specific government agricultural scheme in India.
    Returns a description of the scheme or an error message in Hindi.

    Args:
    scheme_name (str): Name of the government scheme. eg: Paramparagat Krishi Vikas Yojana (PKVY)
    """

    scheme_info = schemes.get(scheme_name)
    if not scheme_info:
        return "Sorry, information not available."
    
    return scheme_info