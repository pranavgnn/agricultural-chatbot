from langchain_core.tools import tool
import json
import math

@tool
def seed_requirement_calculator(crop: str, farm_area_acres: float, row_spacing_cm: float = 0, plant_spacing_cm: float = 0, seed_rate_kg_per_acre: float = 0):
    """
    Calculate seed quantity needed based on crop, spacing, and farm area.
    
    Args:
        crop (str): Name of the crop (e.g., wheat, rice, cotton, maize)
        farm_area_acres (float): Total farm area in acres
        row_spacing_cm (float): Distance between rows in centimeters (optional)
        plant_spacing_cm (float): Distance between plants in centimeters (optional)
        seed_rate_kg_per_acre (float): Custom seed rate in kg per acre (optional, overrides default)
    
    Returns:
        JSON string with seed requirement calculations
    """
    
    # Standard seed rates and spacing for different crops (kg per acre)
    crop_data = {
        "wheat": {
            "seed_rate": 50,
            "row_spacing": 20,
            "plant_spacing": 2,
            "seeds_per_kg": 33000,
            "germination_rate": 85
        },
        "rice": {
            "seed_rate": 25,
            "row_spacing": 20,
            "plant_spacing": 15,
            "seeds_per_kg": 45000,
            "germination_rate": 80
        },
        "cotton": {
            "seed_rate": 5,
            "row_spacing": 45,
            "plant_spacing": 15,
            "seeds_per_kg": 8000,
            "germination_rate": 75
        },
        "maize": {
            "seed_rate": 20,
            "row_spacing": 60,
            "plant_spacing": 20,
            "seeds_per_kg": 3500,
            "germination_rate": 90
        },
        "sugarcane": {
            "seed_rate": 3750,  # kg of sets per acre
            "row_spacing": 90,
            "plant_spacing": 30,
            "seeds_per_kg": 1,  # Sets, not seeds
            "germination_rate": 70
        },
        "soybean": {
            "seed_rate": 30,
            "row_spacing": 30,
            "plant_spacing": 5,
            "seeds_per_kg": 6000,
            "germination_rate": 85
        },
        "groundnut": {
            "seed_rate": 100,
            "row_spacing": 30,
            "plant_spacing": 10,
            "seeds_per_kg": 2200,
            "germination_rate": 75
        },
        "mustard": {
            "seed_rate": 4,
            "row_spacing": 30,
            "plant_spacing": 10,
            "seeds_per_kg": 300000,
            "germination_rate": 80
        },
        "onion": {
            "seed_rate": 4,
            "row_spacing": 15,
            "plant_spacing": 10,
            "seeds_per_kg": 300000,
            "germination_rate": 70
        },
        "tomato": {
            "seed_rate": 0.2,  # For nursery, then transplant
            "row_spacing": 60,
            "plant_spacing": 45,
            "seeds_per_kg": 350000,
            "germination_rate": 85
        },
        "potato": {
            "seed_rate": 1200,  # kg of seed tubers
            "row_spacing": 60,
            "plant_spacing": 20,
            "seeds_per_kg": 25,  # Tubers per kg
            "germination_rate": 90
        }
    }
    
    crop_lower = crop.lower()
    if crop_lower not in crop_data:
        return json.dumps({
            "error": f"Crop '{crop}' not found in database",
            "available_crops": list(crop_data.keys())
        })
    
    crop_info = crop_data[crop_lower]
    
    # Use custom values if provided, otherwise use defaults
    final_seed_rate = seed_rate_kg_per_acre if seed_rate_kg_per_acre > 0 else crop_info["seed_rate"]
    final_row_spacing = row_spacing_cm if row_spacing_cm > 0 else crop_info["row_spacing"]
    final_plant_spacing = plant_spacing_cm if plant_spacing_cm > 0 else crop_info["plant_spacing"]
    
    # Calculate total seed requirement
    total_seed_kg = final_seed_rate * farm_area_acres
    
    # Calculate based on spacing (alternative method)
    # 1 acre = 4047 square meters
    area_per_acre_sqm = 4047
    area_per_plant_sqm = (final_row_spacing / 100) * (final_plant_spacing / 100)
    plants_per_acre = area_per_acre_sqm / area_per_plant_sqm
    total_plants_needed = plants_per_acre * farm_area_acres
    
    # Account for germination rate
    germination_factor = crop_info["germination_rate"] / 100
    seeds_needed_with_buffer = total_plants_needed / germination_factor
    
    # Calculate seed weight based on spacing method
    seeds_per_kg = crop_info["seeds_per_kg"]
    seed_kg_by_spacing = seeds_needed_with_buffer / seeds_per_kg if seeds_per_kg > 0 else 0
    
    # Cost calculation (approximate Indian market prices per kg)
    seed_costs = {
        "wheat": 25, "rice": 40, "cotton": 4000, "maize": 250,
        "sugarcane": 2, "soybean": 60, "groundnut": 80, "mustard": 120,
        "onion": 800, "tomato": 15000, "potato": 15
    }
    
    cost_per_kg = seed_costs.get(crop_lower, 50)
    total_cost = total_seed_kg * cost_per_kg
    
    # Recommendations based on crop type
    recommendations = []
    if crop_lower in ["wheat", "rice", "mustard"]:
        recommendations.append("Sow seeds at 2-3 cm depth")
        recommendations.append("Ensure proper seed bed preparation")
    elif crop_lower == "cotton":
        recommendations.append("Treat seeds with fungicide before sowing")
        recommendations.append("Maintain 4-5 cm sowing depth")
    elif crop_lower == "maize":
        recommendations.append("Plant 2-3 seeds per hill, thin to 1 plant later")
        recommendations.append("Sow at 3-4 cm depth")
    elif crop_lower == "tomato":
        recommendations.append("Raise seedlings in nursery first")
        recommendations.append("Transplant 25-30 day old seedlings")
    
    # Simple, actionable response
    response_parts = []
    response_parts.append(f"Seed requirement for {farm_area_acres} acres of {crop}:")
    response_parts.append(f"• Total seed needed: {total_seed_kg} kg")
    response_parts.append(f"• Estimated cost: ₹{round(total_cost, 0)}")
    response_parts.append(f"• Plant spacing: {final_row_spacing}cm × {final_plant_spacing}cm")
    
    if crop_lower == "tomato":
        response_parts.append("• Raise seedlings in nursery first, then transplant")
    elif crop_lower == "cotton":
        response_parts.append("• Treat seeds with fungicide before sowing")
    elif crop_lower == "maize":
        response_parts.append("• Plant 2-3 seeds per hill, thin to 1 plant later")
    else:
        response_parts.append(f"• Sow at 2-3 cm depth")
    
    return "\n".join(response_parts)