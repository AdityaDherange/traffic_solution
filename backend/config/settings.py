"""
Application Configuration Settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Model paths
MODEL_DIR = BASE_DIR / "data" / "models"
TRAFFICNET_MODEL = MODEL_DIR / "trafficnet_image_model.h5"
YOLO_MODEL = MODEL_DIR / "yolov8n.pt"

# API Configuration
NOMINATIM_API = "https://nominatim.openstreetmap.org"
OSRM_API = "https://router.project-osrm.org"
IPGEOLOCATION_API = "http://ip-api.com/json/"

# App Configuration
APP_NAME = "Smart Traffic System"
APP_VERSION = "2.0"
APP_ICON = "🚦"

# Default Users (for demo purposes)
DEFAULT_USERS = {
    'admin': 'admin123',
    'demo': 'demo123'
}

# Peak Hour Configuration
MORNING_PEAK_START = 8
MORNING_PEAK_END = 11
EVENING_PEAK_START = 17
EVENING_PEAK_END = 21

# Traffic Density Thresholds
LOW_TRAFFIC_THRESHOLD = 30
MEDIUM_TRAFFIC_THRESHOLD = 80

# Default Location (Mumbai, India)
DEFAULT_LOCATION = {
    'lat': 19.0760,
    'lon': 72.8777,
    'name': 'Mumbai, India'
}

# Request Timeout
API_TIMEOUT = 15

class Config:
    """Configuration class"""
    
    def __init__(self):
        self.BASE_DIR = BASE_DIR
        self.MODEL_DIR = MODEL_DIR
        self.TRAFFICNET_MODEL = TRAFFICNET_MODEL
        self.YOLO_MODEL = YOLO_MODEL
        self.NOMINATIM_API = NOMINATIM_API
        self.OSRM_API = OSRM_API
        self.IPGEOLOCATION_API = IPGEOLOCATION_API
        self.APP_NAME = APP_NAME
        self.APP_VERSION = APP_VERSION
        self.APP_ICON = APP_ICON
        self.DEFAULT_USERS = DEFAULT_USERS
        self.MORNING_PEAK_START = MORNING_PEAK_START
        self.MORNING_PEAK_END = MORNING_PEAK_END
        self.EVENING_PEAK_START = EVENING_PEAK_START
        self.EVENING_PEAK_END = EVENING_PEAK_END
        self.LOW_TRAFFIC_THRESHOLD = LOW_TRAFFIC_THRESHOLD
        self.MEDIUM_TRAFFIC_THRESHOLD = MEDIUM_TRAFFIC_THRESHOLD
        self.DEFAULT_LOCATION = DEFAULT_LOCATION
        self.API_TIMEOUT = API_TIMEOUT

config = Config()
