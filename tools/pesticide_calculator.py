from langchain_core.tools import tool
import json

@tool
def pesticide_dilution_calculator(chemical_name: str, dosage_per_hectare: str, tank_size_liters: float, target_area_acres: float = 1.0, formulation_type: str = "liquid"):
    """
    Calculate exact pesticide mixing ratios for sprayer tank.
    
    Args:
        chemical_name (str): Name or active ingredient of the pesticide
        dosage_per_hectare (str): Recommended dosage (e.g., "2ml/L", "500g/ha", "1L/ha")
        tank_size_liters (float): Sprayer tank capacity in liters
        target_area_acres (float): Area to be sprayed in acres (default 1.0)
        formulation_type (str): Type of formulation (liquid, powder, granules)
    
    Returns:
        JSON string with mixing instructions and safety guidelines
    """
    
    # Common pesticide database with standard dosages
    pesticide_database = {
        "chlorpyrifos": {"type": "insecticide", "standard_dose": "2ml/L", "active_ingredient": "20%"},
        "imidacloprid": {"type": "insecticide", "standard_dose": "0.5ml/L", "active_ingredient": "17.8%"},
        "acetamiprid": {"type": "insecticide", "standard_dose": "1ml/L", "active_ingredient": "20%"},
        "mancozeb": {"type": "fungicide", "standard_dose": "2.5g/L", "active_ingredient": "75%"},
        "carbendazim": {"type": "fungicide", "standard_dose": "1ml/L", "active_ingredient": "50%"},
        "propiconazole": {"type": "fungicide", "standard_dose": "1ml/L", "active_ingredient": "25%"},
        "2,4-d": {"type": "herbicide", "standard_dose": "2ml/L", "active_ingredient": "58%"},
        "glyphosate": {"type": "herbicide", "standard_dose": "2ml/L", "active_ingredient": "41%"},
        "atrazine": {"type": "herbicide", "standard_dose": "2.5ml/L", "active_ingredient": "50%"},
        "cypermethrin": {"type": "insecticide", "standard_dose": "1ml/L", "active_ingredient": "10%"},
        "lambda cyhalothrin": {"type": "insecticide", "standard_dose": "1ml/L", "active_ingredient": "5%"},
        "thiamethoxam": {"type": "insecticide", "standard_dose": "0.5ml/L", "active_ingredient": "25%"}
    }
    
    def parse_dosage(dosage_str):
        """Parse dosage string to extract amount and unit"""
        dosage_str = dosage_str.lower().strip()
        
        # Common patterns: "2ml/L", "500g/ha", "1L/ha", "2.5g/L"
        if "/l" in dosage_str:
            amount = dosage_str.split("/")[0]
            if "ml" in amount:
                return float(amount.replace("ml", "")), "ml_per_liter"
            elif "g" in amount:
                return float(amount.replace("g", "")), "g_per_liter"
            elif "l" in amount:
                return float(amount.replace("l", "")) * 1000, "ml_per_liter"  # Convert L to ml
        elif "/ha" in dosage_str:
            amount = dosage_str.split("/")[0]
            if "ml" in amount:
                return float(amount.replace("ml", "")), "ml_per_hectare"
            elif "g" in amount:
                return float(amount.replace("g", "")), "g_per_hectare"
            elif "l" in amount:
                return float(amount.replace("l", "")) * 1000, "ml_per_hectare"  # Convert L to ml
            elif "kg" in amount:
                return float(amount.replace("kg", "")) * 1000, "g_per_hectare"  # Convert kg to g
        
        return None, None
    
    # Convert acres to hectares (1 acre = 0.4047 hectares)
    target_area_hectares = target_area_acres * 0.4047
    
    # Parse the dosage
    dosage_amount, dosage_unit = parse_dosage(dosage_per_hectare)
    
    if dosage_amount is None:
        return json.dumps({
            "error": "Could not parse dosage format",
            "expected_formats": ["2ml/L", "500g/ha", "1L/ha", "2.5g/L"],
            "provided": dosage_per_hectare
        })
    
    # Calculate pesticide amount needed for the tank
    if dosage_unit == "ml_per_liter":
        # Direct calculation: ml per liter × tank size
        pesticide_ml = dosage_amount * tank_size_liters
        pesticide_g = 0  # Not applicable for liquid formulations
        
    elif dosage_unit == "g_per_liter":
        # Direct calculation: grams per liter × tank size
        pesticide_g = dosage_amount * tank_size_liters
        pesticide_ml = 0  # Not applicable for powder formulations
        
    elif dosage_unit == "ml_per_hectare":
        # Calculate based on area coverage
        # Standard spray volume is 200-300 L/ha, assume 250 L/ha
        standard_spray_volume = 250  # L/ha
        pesticide_per_hectare_ml = dosage_amount
        pesticide_concentration = pesticide_per_hectare_ml / standard_spray_volume  # ml/L
        pesticide_ml = pesticide_concentration * tank_size_liters
        pesticide_g = 0
        
    elif dosage_unit == "g_per_hectare":
        # Calculate based on area coverage
        standard_spray_volume = 250  # L/ha
        pesticide_per_hectare_g = dosage_amount
        pesticide_concentration = pesticide_per_hectare_g / standard_spray_volume  # g/L
        pesticide_g = pesticide_concentration * tank_size_liters
        pesticide_ml = 0
    
    # Calculate area coverage with current tank
    spray_volume_per_hectare = 250  # Standard assumption
    area_covered_hectares = tank_size_liters / spray_volume_per_hectare
    area_covered_acres = area_covered_hectares / 0.4047
    
    # Safety and mixing guidelines
    chemical_lower = chemical_name.lower()
    pesticide_info = pesticide_database.get(chemical_lower, {"type": "unknown", "standard_dose": "N/A"})
    
    safety_guidelines = [
        "Always wear protective equipment (gloves, mask, goggles)",
        "Mix pesticide in well-ventilated area",
        "Add pesticide to water, not water to pesticide",
        "Use clean, fresh water for mixing",
        "Do not eat, drink, or smoke while handling",
        "Wash hands thoroughly after use",
        "Store unused mixture safely or dispose properly"
    ]
    
    application_tips = [
        "Spray during early morning or evening",
        "Avoid spraying in windy conditions (>10 km/h)",
        "Ensure uniform coverage of plant surfaces",
        "Clean sprayer thoroughly after use",
        "Follow pre-harvest interval (PHI) guidelines"
    ]
    
    # Calculate cost (approximate)
    pesticide_costs = {
        "insecticide": 500,  # ₹500 per liter average
        "fungicide": 400,   # ₹400 per liter average  
        "herbicide": 300    # ₹300 per liter average
    }
    
    cost_per_liter = pesticide_costs.get(pesticide_info["type"], 400)
    treatment_cost = (pesticide_ml / 1000) * cost_per_liter  # Convert ml to liters
    
    # Simple, actionable response
    response_parts = []
    response_parts.append(f"Pesticide mixing for {tank_size_liters}L tank:")
    
    if pesticide_ml > 0:
        response_parts.append(f"• Mix {round(pesticide_ml, 1)} ml of {chemical_name} in {tank_size_liters} liters water")
    elif pesticide_g > 0:
        response_parts.append(f"• Mix {round(pesticide_g, 1)} grams of {chemical_name} in {tank_size_liters} liters water")
    
    response_parts.append(f"• This will cover {round(area_covered_acres, 1)} acres")
    response_parts.append(f"• Cost: ₹{round(treatment_cost, 0)}")
    response_parts.append("• SAFETY: Wear gloves, mask, and goggles")
    response_parts.append("• Spray during early morning or evening")
    
    return "\n".join(response_parts)