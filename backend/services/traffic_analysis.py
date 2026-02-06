"""
Traffic Analysis Service
Analyzes traffic conditions and provides recommendations
"""
from typing import Dict
from backend.config import config


def estimate_clear_time(
    vehicle_count: int,
    traffic_type: str,
    peak_hour: bool,
    weather: str
) -> int:
    """
    Estimate time to clear traffic based on multiple factors
    
    Args:
        vehicle_count: Number of vehicles
        traffic_type: Type of traffic condition
        peak_hour: Whether it's peak hour
        weather: Current weather condition
        
    Returns:
        Estimated clear time in minutes
    """
    # Base calculation: 15 seconds per vehicle
    base_time = vehicle_count * 0.25
    
    # Traffic type multiplier
    type_multiplier = {
        "Clear": 0.5,
        "Light Traffic": 1.0,
        "Heavy Traffic": 2.2,
        "Accident": 3.8,
        "Fire": 4.5,
        "Construction": 2.8
    }
    base_time *= type_multiplier.get(traffic_type, 1.0)
    
    # Peak hour impact
    if peak_hour:
        base_time *= 1.6
    
    # Weather impact
    weather_multiplier = {
        "Clear": 1.0,
        "Rain": 1.5,
        "Fog": 1.7,
        "Snow": 2.0
    }
    base_time *= weather_multiplier.get(weather, 1.0)
    
    return int(base_time)


def analyze_traffic_condition(
    traffic_type: str,
    vehicle_count: int,
    confidence: float
) -> Dict:
    """
    Comprehensive traffic condition analysis
    
    Args:
        traffic_type: Type of traffic condition
        vehicle_count: Number of vehicles
        confidence: Prediction confidence
        
    Returns:
        Dictionary with analysis results
    """
    # Determine severity
    is_critical = traffic_type in ["Accident", "Fire"]
    is_heavy = traffic_type == "Heavy Traffic"
    is_clear = traffic_type in ["Clear", "Light Traffic"]
    
    # Determine density level
    if vehicle_count < config.LOW_TRAFFIC_THRESHOLD:
        density = "Low"
        density_color = "green"
    elif vehicle_count < config.MEDIUM_TRAFFIC_THRESHOLD:
        density = "Medium"
        density_color = "orange"
    else:
        density = "High"
        density_color = "red"
    
    # Generate recommendation
    if is_critical:
        recommendation = f"⚠️ AVOID THIS ROUTE! {traffic_type} detected. Find alternate route immediately."
        priority = "critical"
    elif is_heavy:
        recommendation = "🚗 Heavy traffic ahead. Consider taking an alternate route if available."
        priority = "high"
    elif density == "High":
        recommendation = "⚡ High vehicle density. Expect delays. Alternate route recommended."
        priority = "medium"
    else:
        recommendation = "✅ Route is clear. Safe to proceed."
        priority = "low"
    
    return {
        "is_critical": is_critical,
        "is_heavy": is_heavy,
        "is_clear": is_clear,
        "density": density,
        "density_color": density_color,
        "recommendation": recommendation,
        "priority": priority,
        "confidence_level": "High" if confidence > 0.85 else "Medium" if confidence > 0.70 else "Low"
    }


def should_reroute(traffic_type: str, vehicle_count: int) -> bool:
    """
    Determine if rerouting is necessary
    
    Args:
        traffic_type: Type of traffic condition
        vehicle_count: Number of vehicles
        
    Returns:
        True if rerouting recommended
    """
    critical_types = ["Accident", "Fire", "Heavy Traffic"]
    
    if traffic_type in critical_types:
        return True
    
    if vehicle_count > config.MEDIUM_TRAFFIC_THRESHOLD:
        return True
    
    return False


def generate_traffic_alert(traffic_type: str, location: str = "current location") -> str:
    """
    Generate alert message for traffic condition
    
    Args:
        traffic_type: Type of traffic condition
        location: Location description
        
    Returns:
        Alert message string
    """
    alert_templates = {
        "Accident": f"🚨 ACCIDENT reported at {location}! Seek alternate route immediately.",
        "Fire": f"🔥 FIRE incident at {location}! Route blocked. Emergency services en route.",
        "Heavy Traffic": f"⚠️ HEAVY TRAFFIC at {location}. Significant delays expected.",
        "Construction": f"🚧 Construction work at {location}. Lane closures possible.",
        "Light Traffic": f"🟡 Light traffic at {location}. Minor delays possible.",
        "Clear": f"✅ All clear at {location}. No issues detected."
    }
    
    return alert_templates.get(traffic_type, f"Traffic condition: {traffic_type} at {location}")
