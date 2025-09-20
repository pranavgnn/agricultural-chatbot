from langchain_core.tools import tool
import json

@tool
def fertilizer_dosage_calculator(crop: str, area_acres: float, nitrogen_ppm: float = 0, phosphorus_ppm: float = 0, potassium_ppm: float = 0, soil_ph: float = 7.0):
    """
    Calculate fertilizer dosage (urea, DAP, MOP) based on crop, area, and soil test values.
    
    Args:
        crop (str): Name of the crop (e.g., wheat, rice, cotton, maize, sugarcane)
        area_acres (float): Farm area in acres
        nitrogen_ppm (float): Available nitrogen in soil (ppm), default 0
        phosphorus_ppm (float): Available phosphorus in soil (ppm), default 0  
        potassium_ppm (float): Available potassium in soil (ppm), default 0
        soil_ph (float): Soil pH level, default 7.0
    
    Returns:
        JSON string with fertilizer recommendations
    """
    
    # Crop nutrient requirements (N-P-K kg per acre)
    crop_requirements = {
        "wheat": {"N": 120, "P": 60, "K": 40},
        "rice": {"N": 100, "P": 50, "K": 50},
        "cotton": {"N": 150, "P": 75, "K": 75},
        "maize": {"N": 120, "P": 60, "K": 50},
        "sugarcane": {"N": 200, "P": 80, "K": 100},
        "soybean": {"N": 40, "P": 80, "K": 50},  # Lower N due to nitrogen fixation
        "groundnut": {"N": 25, "P": 50, "K": 75},
        "mustard": {"N": 80, "P": 40, "K": 40},
        "barley": {"N": 80, "P": 40, "K": 30},
        "gram": {"N": 20, "P": 50, "K": 30},  # Legume, low N requirement
        "tomato": {"N": 150, "P": 100, "K": 120},
        "onion": {"N": 100, "P": 50, "K": 100},
        "potato": {"N": 150, "P": 75, "K": 150}
    }
    
    crop_lower = crop.lower()
    if crop_lower not in crop_requirements:
        return json.dumps({
            "error": f"Crop '{crop}' not found in database",
            "available_crops": list(crop_requirements.keys())
        })
    
    requirements = crop_requirements[crop_lower]
    
    # Convert soil test values (ppm) to available nutrients (kg/acre)
    # Conversion factor: 1 ppm = 2 lbs/acre = 0.9 kg/acre (approximate)
    available_N = nitrogen_ppm * 0.9
    available_P = phosphorus_ppm * 0.9  
    available_K = potassium_ppm * 0.9
    
    # Calculate nutrient deficit
    N_needed = max(0, requirements["N"] - available_N)
    P_needed = max(0, requirements["P"] - available_P)
    K_needed = max(0, requirements["K"] - available_K)
    
    # pH adjustment factor
    ph_factor = 1.0
    if soil_ph < 6.0:
        ph_factor = 1.2  # Increase dose for acidic soil
    elif soil_ph > 8.0:
        ph_factor = 1.1  # Slight increase for alkaline soil
    
    # Apply pH factor
    N_needed *= ph_factor
    P_needed *= ph_factor
    K_needed *= ph_factor
    
    # Calculate fertilizer quantities
    # Urea: 46% N
    urea_kg = (N_needed / 0.46) * area_acres
    
    # DAP: 18% N, 46% P2O5
    # Convert P to P2O5: P * 2.29 = P2O5
    P2O5_needed = P_needed * 2.29
    dap_kg = (P2O5_needed / 0.46) * area_acres
    
    # Adjust urea if DAP provides some nitrogen
    nitrogen_from_dap = dap_kg * 0.18 / area_acres
    adjusted_N_needed = max(0, N_needed - nitrogen_from_dap)
    urea_kg = (adjusted_N_needed / 0.46) * area_acres
    
    # MOP (Muriate of Potash): 60% K2O
    # Convert K to K2O: K * 1.2 = K2O
    K2O_needed = K_needed * 1.2
    mop_kg = (K2O_needed / 0.60) * area_acres
    
    # Round to practical values
    urea_kg = round(urea_kg, 1)
    dap_kg = round(dap_kg, 1)
    mop_kg = round(mop_kg, 1)
    
    # Calculate costs (approximate Indian market prices)
    urea_cost = urea_kg * 6.5  # ₹6.5 per kg
    dap_cost = dap_kg * 27     # ₹27 per kg
    mop_cost = mop_kg * 17     # ₹17 per kg
    total_cost = urea_cost + dap_cost + mop_cost
    
    # Simple, actionable response
    if urea_kg == 0 and dap_kg == 0 and mop_kg == 0:
        return f"For {area_acres} acres of {crop}: Your soil has sufficient nutrients. No additional fertilizer needed right now."
    
    response_parts = []
    response_parts.append(f"Fertilizer recommendation for {area_acres} acres of {crop}:")
    
    if urea_kg > 0:
        response_parts.append(f"• Urea: {urea_kg} kg (₹{round(urea_cost, 0)})")
    if dap_kg > 0:
        response_parts.append(f"• DAP: {dap_kg} kg (₹{round(dap_cost, 0)})")
    if mop_kg > 0:
        response_parts.append(f"• MOP: {mop_kg} kg (₹{round(mop_cost, 0)})")
    
    response_parts.append(f"Total cost: ₹{round(total_cost, 0)}")
    response_parts.append("Apply DAP during land preparation, split urea in 3 doses.")
    
    return "\n".join(response_parts)