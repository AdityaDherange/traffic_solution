"""
Routing Service
Calculates routes between locations using OSRM
"""
import requests
import streamlit as st
from typing import Optional, List, Dict
from backend.config import config


def get_route(start_coords: Dict, end_coords: Dict, alternatives: bool = True) -> Optional[List[Dict]]:
    """
    Get actual road route using OSRM (Open Source Routing Machine)
    
    Args:
        start_coords: Dictionary with 'lat' and 'lon' keys
        end_coords: Dictionary with 'lat' and 'lon' keys
        alternatives: Whether to include alternative routes
        
    Returns:
        List of route dictionaries or None if routing fails
    """
    try:
        url = (f"{config.OSRM_API}/route/v1/driving/"
               f"{start_coords['lon']},{start_coords['lat']};"
               f"{end_coords['lon']},{end_coords['lat']}")
        
        params = {
            "overview": "full",
            "geometries": "geojson",
            "alternatives": "true" if alternatives else "false"
        }
        
        response = requests.get(url, params=params, timeout=config.API_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("code") == "Ok":
            routes = []
            for i, route in enumerate(data["routes"]):
                coords = route["geometry"]["coordinates"]
                # Convert from [lon, lat] to [lat, lon] for Folium
                path = [[coord[1], coord[0]] for coord in coords]
                
                routes.append({
                    "path": path,
                    "distance": route["distance"] / 1000,  # Convert to km
                    "duration": route["duration"] / 60,    # Convert to minutes
                    "is_primary": i == 0
                })
            return routes
        return None
        
    except requests.RequestException as e:
        st.error(f"Routing error: {e}")
        return None
    except (KeyError, ValueError) as e:
        st.error(f"Error parsing routing response: {e}")
        return None


def calculate_route_metrics(routes: List[Dict], traffic_factor: float = 1.0) -> List[Dict]:
    """
    Calculate enhanced metrics for routes considering traffic
    
    Args:
        routes: List of route dictionaries
        traffic_factor: Multiplier for duration based on traffic (1.0 = normal, >1.0 = congested)
        
    Returns:
        Routes with updated metrics
    """
    for route in routes:
        # Apply traffic factor to duration
        route["actual_duration"] = route["duration"] * traffic_factor
        
        # Calculate estimated fuel consumption (rough estimate)
        route["estimated_fuel"] = route["distance"] * 0.08  # 8 liters per 100km
        
        # Calculate difficulty score (0-100)
        base_score = min(100, (route["distance"] / 50) * 50 + (route["duration"] / 60) * 50)
        route["difficulty"] = min(100, base_score * traffic_factor)
    
    return routes


def find_midpoint(start_coords: Dict, end_coords: Dict) -> Dict:
    """
    Find the midpoint between two coordinates
    
    Args:
        start_coords: Dictionary with 'lat' and 'lon' keys
        end_coords: Dictionary with 'lat' and 'lon' keys
        
    Returns:
        Dictionary with midpoint coordinates
    """
    return {
        "lat": (start_coords["lat"] + end_coords["lat"]) / 2,
        "lon": (start_coords["lon"] + end_coords["lon"]) / 2
    }
