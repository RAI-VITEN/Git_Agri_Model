"""
Recommendations module
Generates planting recommendations based on predictions
"""

from typing import Dict, List


CROP_INFO = {
    "maize": {
        "name": "Maize (Corn)",
        "growing_period": "120 days",
        "spacing": "75cm x 25cm",
        "seed_rate": "25kg/hectare",
        "rainfall_needed": "500-1200mm",
        "temp_range": "15-32°C",
    },
    "beans": {
        "name": "Beans",
        "growing_period": "90 days",
        "spacing": "45cm x 15cm",
        "seed_rate": "60kg/hectare",
        "rainfall_needed": "400-1000mm",
        "temp_range": "16-28°C",
    },
}


def get_recommendation(
    crop: str, suitability: float, rainfall: float, temperature: float
) -> Dict:
    """
    Generate detailed recommendation for a crop

    Args:
        crop: Crop name ('maize' or 'beans')
        suitability: Suitability score (0-1)
        rainfall: Rainfall in mm
        temperature: Temperature in °C

    Returns:
        Dictionary with recommendation details
    """
    if crop not in CROP_INFO:
        return {"error": f"Unknown crop: {crop}"}

    info = CROP_INFO[crop]

    # Determine recommendation level
    if suitability >= 0.8:
        recommendation = "HIGHLY RECOMMENDED"
        action = "Plant immediately"
        color = "green"
        icon = "✅"
    elif suitability >= 0.6:
        recommendation = "RECOMMENDED"
        action = "Plant within 1-2 weeks"
        color = "lime"
        icon = "✔"
    elif suitability >= 0.4:
        recommendation = "MARGINAL"
        action = "Plant if no better option available"
        color = "yellow"
        icon = "⚠"
    else:
        recommendation = "NOT RECOMMENDED"
        action = "Wait for better conditions"
        color = "red"
        icon = "❌"

    # Generate reasoning
    reasoning = []

    if crop == "maize":
        if rainfall < 500:
            reasoning.append("Rainfall below optimal range - may need irrigation")
        elif rainfall > 1200:
            reasoning.append("High rainfall - ensure good drainage")
        else:
            reasoning.append("Rainfall conditions are favorable")

        if temperature < 15:
            reasoning.append("Temperature too low - wait for warming")
        elif temperature > 32:
            reasoning.append("Temperature too high - risk of heat stress")
        else:
            reasoning.append("Temperature conditions are optimal")

    elif crop == "beans":
        if rainfall < 400:
            reasoning.append("Rainfall insufficient - requires supplementary irrigation")
        elif rainfall > 1000:
            reasoning.append("High rainfall - monitor for fungal diseases")
        else:
            reasoning.append("Rainfall conditions are suitable")

        if temperature < 16:
            reasoning.append("Temperature too low for germination")
        elif temperature > 28:
            reasoning.append("Temperature approaching upper limit")
        else:
            reasoning.append("Temperature is within ideal range")

    return {
        "crop": crop,
        "crop_name": info["name"],
        "suitability_score": round(suitability, 3),
        "recommendation": recommendation,
        "action": action,
        "color": color,
        "icon": icon,
        "reasoning": reasoning,
        "crop_details": {
            "growing_period": info["growing_period"],
            "spacing": info["spacing"],
            "seed_rate": info["seed_rate"],
            "rainfall_needed": info["rainfall_needed"],
            "temperature_range": info["temp_range"],
        },
    }


def generate_recommendations(
    predictions: Dict, rainfall: float, temperature: float
) -> List[Dict]:
    """
    Generate recommendations for all crops

    Args:
        predictions: Dictionary with maize_suitability and beans_suitability
        rainfall: Rainfall in mm
        temperature: Temperature in °C

    Returns:
        List of recommendations sorted by suitability
    """
    recommendations = []

    # Maize recommendation
    if "maize_suitability" in predictions:
        maize_rec = get_recommendation(
            "maize", predictions["maize_suitability"], rainfall, temperature
        )
        recommendations.append(maize_rec)

    # Beans recommendation
    if "beans_suitability" in predictions:
        beans_rec = get_recommendation(
            "beans", predictions["beans_suitability"], rainfall, temperature
        )
        recommendations.append(beans_rec)

    # Sort by suitability (highest first)
    recommendations.sort(
        key=lambda x: x["suitability_score"], reverse=True
    )

    return recommendations


def get_advisory_summary(
    predictions: Dict, rainfall: float, temperature: float
) -> str:
    """
    Generate a human-readable advisory summary

    Args:
        predictions: Model predictions
        rainfall: Rainfall in mm
        temperature: Temperature in °C

    Returns:
        String with advisory summary
    """
    recommendations = generate_recommendations(predictions, rainfall, temperature)

    if not recommendations:
        return "Unable to generate recommendations"

    best = recommendations[0]
    summary = f"""
🌾 PLANTING ADVISORY SUMMARY
{'='*50}

Current Conditions:
  • Rainfall: {rainfall:.1f} mm
  • Temperature: {temperature:.1f}°C

Top Recommendation: {best['crop_name']}
  • Status: {best['recommendation']}
  • Suitability Score: {best['suitability_score']:.1%}
  • Action: {best['action']}

Details:
  • Growing Period: {best['crop_details']['growing_period']}
  • Spacing: {best['crop_details']['spacing']}
  • Seed Rate: {best['crop_details']['seed_rate']}

Reasoning:
"""
    for reason in best["reasoning"]:
        summary += f"  • {reason}\n"

    summary += f"\n{'='*50}"
    return summary


if __name__ == "__main__":
    # Example usage
    predictions = {
        "maize_suitability": 0.85,
        "beans_suitability": 0.65,
    }

    recs = generate_recommendations(
        predictions, rainfall=800, temperature=22
    )

    print("\n📋 RECOMMENDATIONS:")
    for rec in recs:
        print(f"\n{rec['icon']} {rec['crop_name']}")
        print(f"   Status: {rec['recommendation']}")
        print(f"   Score: {rec['suitability_score']:.1%}")
        print(f"   Action: {rec['action']}")

    print(get_advisory_summary(predictions, 800, 22))
