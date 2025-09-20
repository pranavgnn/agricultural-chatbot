from langchain_core.tools import tool
import json

@tool
def irrigation_calculator(crop: str, area_acres: float, irrigation_method: str, growth_stage: str = "vegetative", season: str = "kharif"):
    """
    Calculate irrigation water requirement based on crop type, area, and irrigation method.
    
    Args:
        crop (str): Name of the crop (e.g., wheat, rice, cotton, maize)
        area_acres (float): Farm area in acres
        irrigation_method (str): Method of irrigation (drip, sprinkler, flood, furrow)
        growth_stage (str): Current growth stage (sowing, vegetative, flowering, maturity)
        season (str): Growing season (kharif, rabi, summer)
    
    Returns:
        JSON string with irrigation recommendations
    """
    
    # Water requirements by crop (mm per day during peak growth)
    crop_water_requirements = {
        "wheat": {"peak_mm_day": 5.5, "total_mm": 450, "critical_stages": ["tillering", "flowering"]},
        "rice": {"peak_mm_day": 7.5, "total_mm": 1200, "critical_stages": ["tillering", "panicle_initiation"]},
        "cotton": {"peak_mm_day": 6.0, "total_mm": 700, "critical_stages": ["flowering", "boll_formation"]},
        "maize": {"peak_mm_day": 6.5, "total_mm": 500, "critical_stages": ["tasseling", "grain_filling"]},
        "sugarcane": {"peak_mm_day": 8.0, "total_mm": 1800, "critical_stages": ["tillering", "grand_growth"]},
        "soybean": {"peak_mm_day": 5.0, "total_mm": 450, "critical_stages": ["flowering", "pod_filling"]},
        "groundnut": {"peak_mm_day": 4.5, "total_mm": 500, "critical_stages": ["flowering", "pod_development"]},
        "mustard": {"peak_mm_day": 4.0, "total_mm": 300, "critical_stages": ["flowering", "pod_filling"]},
        "onion": {"peak_mm_day": 4.5, "total_mm": 350, "critical_stages": ["bulb_initiation", "bulb_development"]},
        "tomato": {"peak_mm_day": 5.5, "total_mm": 400, "critical_stages": ["flowering", "fruit_development"]},
        "potato": {"peak_mm_day": 5.0, "total_mm": 350, "critical_stages": ["tuber_initiation", "tuber_bulking"]}
    }
    
    # Irrigation efficiency by method
    irrigation_efficiency = {
        "drip": 0.90,        # 90% efficiency
        "sprinkler": 0.75,   # 75% efficiency
        "flood": 0.45,       # 45% efficiency
        "furrow": 0.60,      # 60% efficiency
        "micro": 0.85        # 85% efficiency (micro sprinklers)
    }
    
    # Growth stage multipliers
    stage_multipliers = {
        "sowing": 0.3,
        "vegetative": 0.7,
        "flowering": 1.0,
        "fruiting": 1.0,
        "maturity": 0.4
    }
    
    # Season multipliers
    season_multipliers = {
        "kharif": 0.8,    # Monsoon season, some natural rainfall
        "rabi": 1.0,      # Winter season, full irrigation needed
        "summer": 1.3     # Summer season, higher evaporation
    }
    
    crop_lower = crop.lower()
    irrigation_method_lower = irrigation_method.lower()
    
    if crop_lower not in crop_water_requirements:
        return json.dumps({
            "error": f"Crop '{crop}' not found in database",
            "available_crops": list(crop_water_requirements.keys())
        })
    
    if irrigation_method_lower not in irrigation_efficiency:
        return json.dumps({
            "error": f"Irrigation method '{irrigation_method}' not supported",
            "available_methods": list(irrigation_efficiency.keys())
        })
    
    crop_info = crop_water_requirements[crop_lower]
    efficiency = irrigation_efficiency[irrigation_method_lower]
    stage_factor = stage_multipliers.get(growth_stage.lower(), 0.7)
    season_factor = season_multipliers.get(season.lower(), 1.0)
    
    # Calculate daily water requirement
    peak_requirement_mm = crop_info["peak_mm_day"]
    adjusted_requirement_mm = peak_requirement_mm * stage_factor * season_factor
    
    # Convert to practical units
    # 1 mm of water over 1 acre = 4047 liters
    water_per_acre_liters = adjusted_requirement_mm * 4047
    total_water_liters = water_per_acre_liters * area_acres
    
    # Account for irrigation efficiency
    actual_water_needed_liters = total_water_liters / efficiency
    
    # Convert to different units
    water_cubic_meters = actual_water_needed_liters / 1000
    water_gallons = actual_water_needed_liters * 0.264172  # US gallons
    
    # Calculate irrigation frequency and duration
    irrigation_frequencies = {
        "drip": {"frequency_days": 1, "hours_per_day": 2},
        "sprinkler": {"frequency_days": 3, "hours_per_day": 4},
        "flood": {"frequency_days": 7, "hours_per_day": 6},
        "furrow": {"frequency_days": 5, "hours_per_day": 5},
        "micro": {"frequency_days": 2, "hours_per_day": 3}
    }
    
    freq_info = irrigation_frequencies[irrigation_method_lower]
    
    # Calculate water application rate (liters per hour)
    application_rate_lph = actual_water_needed_liters / freq_info["hours_per_day"]
    
    # Cost calculation (approximate Indian rates)
    # Electricity/diesel costs for irrigation
    irrigation_costs_per_1000l = {
        "drip": 2.5,      # Most efficient
        "sprinkler": 4.0,
        "flood": 8.0,     # Highest cost due to inefficiency
        "furrow": 6.0,
        "micro": 3.5
    }
    
    cost_per_1000l = irrigation_costs_per_1000l[irrigation_method_lower]
    daily_irrigation_cost = (actual_water_needed_liters / 1000) * cost_per_1000l
    
    # Simple, actionable response
    response_parts = []
    response_parts.append(f"Irrigation plan for {area_acres} acres of {crop} using {irrigation_method}:")
    response_parts.append(f"• Daily water need: {round(actual_water_needed_liters, 0)} liters")
    response_parts.append(f"• Irrigate every {freq_info['frequency_days']} days for {freq_info['hours_per_day']} hours")
    response_parts.append(f"• Daily cost: ₹{round(daily_irrigation_cost, 0)}")
    
    if growth_stage.lower() in ["flowering", "fruiting"]:
        response_parts.append(f"• Critical stage: Don't skip watering during {growth_stage}")
    
    response_parts.append("• Best time: Early morning or evening")
    
    return "\n".join(response_parts)