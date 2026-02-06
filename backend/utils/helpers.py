"""
Helper Utility Functions
"""
from typing import Tuple
from backend.config import config


def get_density_level(count: int) -> Tuple[str, str]:
    """
    Determine traffic density level from vehicle count
    
    Args:
        count: Vehicle count
        
    Returns:
        Tuple of (density_level, color)
    """
    if count < config.LOW_TRAFFIC_THRESHOLD:
        return "Low", "green"
    elif count < config.MEDIUM_TRAFFIC_THRESHOLD:
        return "Medium", "orange"
    return "High", "red"


def announce_voice(text: str, enabled: bool = True):
    """
    Announce text using voice (if enabled)
    
    Args:
        text: Text to announce
        enabled: Whether voice is enabled
    """
    if not enabled:
        return
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except ImportError:
        # pyttsx3 not installed, skip voice
        pass
    except Exception:
        # Voice engine error, skip silently
        pass


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_distance(km: float) -> str:
    """
    Format distance in a human-readable format
    
    Args:
        km: Distance in kilometers
        
    Returns:
        Formatted distance string
    """
    if km < 1.0:
        meters = int(km * 1000)
        return f"{meters} m"
    
    return f"{km:.1f} km"


def get_confidence_color(confidence: float) -> str:
    """
    Get color based on confidence level
    
    Args:
        confidence: Confidence value (0-1)
        
    Returns:
        Color name
    """
    if confidence > 0.85:
        return "green"
    elif confidence > 0.70:
        return "orange"
    else:
        return "red"
