"""
Live Location Service
Gets user's current location using various methods
"""
import requests
import streamlit as st
from typing import Optional, Dict
from backend.config import config


def get_location_from_ip() -> Optional[Dict]:
    """
    Get approximate location from user's IP address
    This is called automatically to detect user location
    
    Returns:
        Dictionary with location data or None if failed
    """
    try:
        response = requests.get(config.IPGEOLOCATION_API, timeout=config.API_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "success":
            return {
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "city": data.get("city"),
                "region": data.get("regionName"),
                "country": data.get("country"),
                "display_name": f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}",
                "zip": data.get("zip"),
                "isp": data.get("isp"),
                "method": "ip"
            }
        return None
        
    except requests.RequestException as e:
        st.warning(f"Could not detect location from IP: {e}")
        return None
    except (KeyError, ValueError) as e:
        st.warning(f"Error parsing IP location data: {e}")
        return None


def get_live_location() -> Optional[Dict]:
    """
    Get user's live location using browser geolocation API
    Note: This requires HTTPS in production
    
    Returns:
        Dictionary with location data or None if not available
    """
    # First try IP-based location
    ip_location = get_location_from_ip()
    
    if ip_location:
        st.success(f"📍 Location detected: {ip_location['display_name']}")
        return ip_location
    
    # Fallback to default location
    st.info("📍 Using default location. You can manually set your location.")
    return {
        "lat": config.DEFAULT_LOCATION["lat"],
        "lon": config.DEFAULT_LOCATION["lon"],
        "display_name": config.DEFAULT_LOCATION["name"],
        "method": "default"
    }


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate latitude and longitude values
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        True if valid, False otherwise
    """
    try:
        lat = float(lat)
        lon = float(lon)
        
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True
        return False
        
    except (ValueError, TypeError):
        return False


def format_location_display(location: Dict) -> str:
    """
    Format location data for display (NEVER shows coordinates)
    
    Args:
        location: Location dictionary
        
    Returns:
        Formatted location string (human-readable name only)
    """
    if not location:
        return "Location not set"
    
    parts = []
    
    # Try to build from city, region, country
    if "city" in location:
        parts.append(location["city"])
    if "region" in location:
        parts.append(location["region"])
    if "country" in location:
        parts.append(location["country"])
    
    if parts:
        return ", ".join(parts)
    
    # Use display_name if available
    if "display_name" in location:
        return location["display_name"]
    
    # If we only have coordinates (no name), return generic message
    # NEVER show actual coordinates to user
    return "Custom location"
