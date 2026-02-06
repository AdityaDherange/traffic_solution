"""
Time Utility Functions
"""
from datetime import datetime
from typing import Tuple
from backend.config import config


def is_peak_hour() -> Tuple[bool, str]:
    """
    Check if current time is peak hour
    
    Returns:
        Tuple of (is_peak, description)
    """
    hour = datetime.now().hour
    
    if config.MORNING_PEAK_START <= hour <= config.MORNING_PEAK_END:
        return True, f"Morning Peak ({config.MORNING_PEAK_START}-{config.MORNING_PEAK_END+1} AM)"
    elif config.EVENING_PEAK_START <= hour <= config.EVENING_PEAK_END:
        return True, f"Evening Peak ({config.EVENING_PEAK_START-12}-{config.EVENING_PEAK_END-12+1} PM)"
    
    return False, "Off-Peak"


def get_current_time_info() -> dict:
    """
    Get comprehensive current time information
    
    Returns:
        Dictionary with time information
    """
    now = datetime.now()
    is_peak, peak_msg = is_peak_hour()
    
    return {
        "datetime": now,
        "time": now.strftime("%I:%M %p"),
        "date": now.strftime("%b %d, %Y"),
        "day": now.strftime("%A"),
        "is_peak": is_peak,
        "peak_message": peak_msg,
        "hour": now.hour,
        "timestamp": now.timestamp()
    }


def format_duration(minutes: float) -> str:
    """
    Format duration in a human-readable format
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted duration string
    """
    if minutes < 60:
        return f"{int(minutes)} min"
    
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    
    if mins == 0:
        return f"{hours} hr"
    
    return f"{hours} hr {mins} min"


def get_time_category() -> str:
    """
    Get time category (morning, afternoon, evening, night)
    
    Returns:
        Time category string
    """
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"
