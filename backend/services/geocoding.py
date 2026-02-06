"""
Geocoding Service
Converts location names to coordinates and vice versa
"""
import requests
import streamlit as st
from typing import Optional, Dict
from backend.config import config


def geocode_location(location_name: str) -> Optional[Dict]:
    """
    Convert location name to coordinates using OpenStreetMap Nominatim
    
    Args:
        location_name: Name of the location to geocode
        
    Returns:
        Dictionary with lat, lon, and display_name or None if not found
    """
    try:
        url = f"{config.NOMINATIM_API}/search"
        params = {
            "q": location_name,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": f"{config.APP_NAME}/{config.APP_VERSION}"}
        
        response = requests.get(
            url, 
            params=params, 
            headers=headers, 
            timeout=config.API_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"]),
                "display_name": data[0]["display_name"]
            }
        return None
        
    except requests.RequestException as e:
        st.error(f"Geocoding error: {e}")
        return None
    except (KeyError, IndexError, ValueError) as e:
        st.error(f"Error parsing geocoding response: {e}")
        return None


def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Convert coordinates to location name
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Location name or None if not found
    """
    try:
        url = f"{config.NOMINATIM_API}/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        headers = {"User-Agent": f"{config.APP_NAME}/{config.APP_VERSION}"}
        
        response = requests.get(
            url, 
            params=params, 
            headers=headers, 
            timeout=config.API_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "display_name" in data:
            return data["display_name"]
        return None
        
    except requests.RequestException as e:
        st.error(f"Reverse geocoding error: {e}")
        return None
    except (KeyError, ValueError) as e:
        st.error(f"Error parsing reverse geocoding response: {e}")
        return None
