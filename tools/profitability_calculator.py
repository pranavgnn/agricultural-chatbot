from langchain_core.tools import tool
import json

@tool
def profitability_calculator(crop: str, area_acres: float, seed_cost_per_acre: float, fertilizer_cost_per_acre: float, labor_cost_per_acre: float, irrigation_cost_per_acre: float, pesticide_cost_per_acre: float, other_costs_per_acre: float, expected_yield_per_acre: float, market_price_per_unit: float, yield_unit: str = "quintal"):
    """
    Calculate farming profitability and cost analysis per acre.
    
    Args:
        crop (str): Name of the crop
        area_acres (float): Total farm area in acres
        seed_cost_per_acre (float): Seed cost per acre (₹)
        fertilizer_cost_per_acre (float): Fertilizer cost per acre (₹)
        labor_cost_per_acre (float): Labor cost per acre (₹)
        irrigation_cost_per_acre (float): Irrigation cost per acre (₹)
        pesticide_cost_per_acre (float): Pesticide/chemical cost per acre (₹)
        other_costs_per_acre (float): Other miscellaneous costs per acre (₹)
        expected_yield_per_acre (float): Expected yield per acre
        market_price_per_unit (float): Current market price per unit (₹)
        yield_unit (str): Unit of yield measurement (quintal, kg, tonnes)
    
    Returns:
        JSON string with detailed profitability analysis
    """
    
    # Standard cost estimates for different crops (₹ per acre) - can be used as reference
    standard_costs = {
        "wheat": {
            "seed": 2500, "fertilizer": 4000, "labor": 8000, 
            "irrigation": 3000, "pesticide": 2000, "other": 2000,
            "total": 21500, "yield_quintal": 25, "price_per_quintal": 2200
        },
        "rice": {
            "seed": 1500, "fertilizer": 5000, "labor": 12000,
            "irrigation": 5000, "pesticide": 2500, "other": 2500,
            "total": 28500, "yield_quintal": 30, "price_per_quintal": 2000
        },
        "cotton": {
            "seed": 1200, "fertilizer": 6000, "labor": 15000,
            "irrigation": 4000, "pesticide": 4000, "other": 3000,
            "total": 33200, "yield_quintal": 12, "price_per_quintal": 6000
        },
        "maize": {
            "seed": 2000, "fertilizer": 4500, "labor": 8000,
            "irrigation": 3500, "pesticide": 2000, "other": 2000,
            "total": 22000, "yield_quintal": 35, "price_per_quintal": 1800
        },
        "sugarcane": {
            "seed": 15000, "fertilizer": 8000, "labor": 20000,
            "irrigation": 8000, "pesticide": 3000, "other": 5000,
            "total": 59000, "yield_quintal": 400, "price_per_quintal": 350
        }
    }
    
    # Convert yield to standard unit (quintal)
    if yield_unit.lower() == "kg":
        yield_quintal = expected_yield_per_acre / 100
    elif yield_unit.lower() == "tonnes":
        yield_quintal = expected_yield_per_acre * 10
    else:  # already in quintal
        yield_quintal = expected_yield_per_acre
    
    # Calculate costs per acre
    total_cost_per_acre = (
        seed_cost_per_acre + 
        fertilizer_cost_per_acre + 
        labor_cost_per_acre + 
        irrigation_cost_per_acre + 
        pesticide_cost_per_acre + 
        other_costs_per_acre
    )
    
    # Calculate revenue per acre
    revenue_per_acre = yield_quintal * market_price_per_unit
    
    # Calculate profit per acre
    profit_per_acre = revenue_per_acre - total_cost_per_acre
    profit_margin_percent = (profit_per_acre / revenue_per_acre) * 100 if revenue_per_acre > 0 else 0
    
    # Calculate for total area
    total_cost = total_cost_per_acre * area_acres
    total_revenue = revenue_per_acre * area_acres
    total_profit = profit_per_acre * area_acres
    
    # Break-even analysis
    break_even_price = total_cost_per_acre / yield_quintal if yield_quintal > 0 else 0
    break_even_yield = total_cost_per_acre / market_price_per_unit if market_price_per_unit > 0 else 0
    
    # Return on investment
    roi_percent = (profit_per_acre / total_cost_per_acre) * 100 if total_cost_per_acre > 0 else 0
    
    # Cost breakdown percentages
    cost_breakdown = {
        "seed_percent": (seed_cost_per_acre / total_cost_per_acre) * 100,
        "fertilizer_percent": (fertilizer_cost_per_acre / total_cost_per_acre) * 100,
        "labor_percent": (labor_cost_per_acre / total_cost_per_acre) * 100,
        "irrigation_percent": (irrigation_cost_per_acre / total_cost_per_acre) * 100,
        "pesticide_percent": (pesticide_cost_per_acre / total_cost_per_acre) * 100,
        "other_percent": (other_costs_per_acre / total_cost_per_acre) * 100
    }
    
    # Risk analysis
    risk_factors = []
    if profit_margin_percent < 20:
        risk_factors.append("Low profit margin - consider cost optimization")
    if break_even_price > market_price_per_unit * 0.9:
        risk_factors.append("High break-even price - vulnerable to price drops")
    if labor_cost_per_acre > total_cost_per_acre * 0.4:
        risk_factors.append("High labor dependency - consider mechanization")
    
    # Recommendations
    recommendations = []
    
    # Compare with standard costs if crop data available
    crop_lower = crop.lower()
    comparison = {}
    if crop_lower in standard_costs:
        std = standard_costs[crop_lower]
        comparison = {
            "your_cost_vs_standard": {
                "your_cost": total_cost_per_acre,
                "standard_cost": std["total"],
                "difference": total_cost_per_acre - std["total"],
                "percentage_difference": ((total_cost_per_acre - std["total"]) / std["total"]) * 100
            },
            "your_yield_vs_standard": {
                "your_yield": yield_quintal,
                "standard_yield": std["yield_quintal"],
                "difference": yield_quintal - std["yield_quintal"],
                "percentage_difference": ((yield_quintal - std["yield_quintal"]) / std["yield_quintal"]) * 100
            }
        }
        
        if total_cost_per_acre > std["total"] * 1.1:
            recommendations.append(f"Your costs are {round(((total_cost_per_acre - std['total']) / std['total']) * 100, 1)}% higher than standard - review cost optimization")
        
        if yield_quintal < std["yield_quintal"] * 0.9:
            recommendations.append(f"Your yield is {round(((std['yield_quintal'] - yield_quintal) / std['yield_quintal']) * 100, 1)}% lower than standard - focus on yield improvement")
    
    # General recommendations
    if cost_breakdown["fertilizer_percent"] > 25:
        recommendations.append("Fertilizer costs are high - consider soil testing and precision application")
    
    if cost_breakdown["labor_percent"] > 40:
        recommendations.append("Labor costs are significant - explore mechanization options")
    
    if roi_percent < 15:
        recommendations.append("Low ROI - consider alternative crops or improved practices")
    
    # Simple, actionable response
    response_parts = []
    response_parts.append(f"Profitability analysis for {area_acres} acres of {crop}:")
    response_parts.append(f"• Total cost: ₹{round(total_cost_per_acre, 0)} per acre")
    response_parts.append(f"• Expected revenue: ₹{round(revenue_per_acre, 0)} per acre")
    
    if profit_per_acre > 0:
        response_parts.append(f"• Profit: ₹{round(profit_per_acre, 0)} per acre ({round(profit_margin_percent, 1)}% margin)")
        response_parts.append(f"• Total farm profit: ₹{round(total_profit, 0)}")
        response_parts.append(f"• Return on investment: {round(roi_percent, 1)}%")
    else:
        response_parts.append(f"• Loss: ₹{round(abs(profit_per_acre), 0)} per acre")
        response_parts.append("• Consider cost reduction or better prices")
    
    response_parts.append(f"• Break-even price: ₹{round(break_even_price, 0)} per quintal")
    
    # Add key recommendation
    if roi_percent < 15:
        response_parts.append("• Recommendation: Low profitability - review costs or crop choice")
    elif profit_margin_percent > 25:
        response_parts.append("• Recommendation: Good profitability - maintain current practices")
    else:
        response_parts.append("• Recommendation: Moderate profitability - optimize costs")
    
    return "\n".join(response_parts)