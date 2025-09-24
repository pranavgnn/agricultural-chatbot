from langchain_core.tools import tool
import json

agricultural_helplines = {
    "national": {
        "Kisan Call Centre": "1800-180-1551",
        "NAFED Farmer Helpline": "1800-111-622",
        "eNAM Help Desk": "1800-270-0224",
        "Agricultural Transport Call Centre": ["1800-180-4200", "14488"]
    },
    "states": {
        "Andhra Pradesh": "040-23317191",
        "Arunachal Pradesh": "0360-2243935",
        "Assam": "0361-2265264",
        "Bihar": "0612-221359",
        "Chhattisgarh": "0771-2234584",
        "Delhi": "011-120-23713399",
        "Goa": "0832-226445",
        "Gujarat": "079-23256204",
        "Haryana": "0172-705600",
        "Himachal Pradesh": "0177-2623678",
        "Jammu & Kashmir (Winter)": "0191-2552145",
        "Jammu & Kashmir (Summer)": "0191-2552145",
        "Jharkhand": "0651-2233549",
        "Karnataka": "080-22253758",
        "Kerala": "0471-2305318",
        "Madhya Pradesh": "0751-324811",
        "Maharashtra": "020-26121041",
        "Manipur": "0385-310202",
        "Meghalaya": "0364-2227520",
        "Mizoram": "0389-322437",
        "Nagaland": "0370-22243116",
        "Odisha": "0674-2391295",
        "Punjab": "0181-254935",
        "Puducherry": "0413-248816",
        "Rajasthan": "0141-2227709",
        "Sikkim": "03592-31877",
        "Tamil Nadu": "044-24341929",
        "Tripura": "0381-2323778",
        "Uttarakhand": "0135-2711909",
        "Uttar Pradesh": "0522-205210"
    },
    "agristack_state_specific": {
        "Uttar Pradesh": "0522-2720548",
        "Maharashtra": "022-6789001",
        "Gujarat": "079-23200112",
        "Rajasthan": "0141-2710200"
    }
}

@tool
def helpline_numbers(state = "national") -> str:
    """
    Fetch agricultural helpline numbers for a specific Indian state or national level.

    Args:
        state (str): Name of the Indian state or "national" for national helplines. Defaults to "national".
    Returns:
        str: JSON string of helpline numbers or an error message if state is not found.
    """

    state_lower = state.strip().lower()
    if state_lower == "national":
        result = {"national": agricultural_helplines["national"]}
    elif state_lower in (s.lower() for s in agricultural_helplines["states"]):
        for s, number in agricultural_helplines["states"].items():
            if s.lower() == state_lower:
                result = {s: number}
                break
    elif state_lower in (s.lower() for s in agricultural_helplines["agristack_state_specific"]):
        for s, number in agricultural_helplines["agristack_state_specific"].items():
            if s.lower() == state_lower:
                result = {s: number}
                break
    else:
        result = agricultural_helplines

    return json.dumps(result, indent=2)