# Smart Traffic Congestion Analysis & Route Recommendation System

## 🚦 Overview

An AI-powered traffic management system that provides real-time traffic analysis, intelligent route planning, and traffic density visualization. Built with Streamlit, this application helps users navigate through congested areas efficiently.

## ✨ Features

### 🎯 Core Features
- **📸 Traffic Image Analysis** - Upload or capture traffic images for AI-powered analysis
- **🗺️ Smart Route Planning** - Real-time route calculation with alternate route suggestions
- **🔥 Traffic Heat Map** - Visual representation of traffic density in your area
- **📍 Live Location Detection** - Automatic location detection using IP geolocation
- **🔊 Voice Announcements** - Audio alerts for traffic conditions
- **🎨 Dark/Light Theme** - Customizable user interface

### 🤖 AI Capabilities
- Traffic condition classification (Clear, Light, Heavy, Accidents, Fire, Construction)
- Vehicle counting and density analysis
- Clear time estimation based on multiple factors
- Intelligent rerouting recommendations

## 📁 Project Structure

```
traffic_solution/
├── backend/                         # Backend Logic
│   ├── config/                     # Configuration
│   │   ├── __init__.py
│   │   └── settings.py             # App settings and constants
│   │
│   ├── models/                     # ML Models
│   │   ├── __init__.py
│   │   ├── traffic_predictor.py    # Traffic classification
│   │   └── vehicle_counter.py      # Vehicle counting
│   │
│   ├── services/                   # Business Logic
│   │   ├── __init__.py
│   │   ├── geocoding.py            # Location services
│   │   ├── routing.py              # Route calculation
│   │   ├── location.py             # Live location detection
│   │   └── traffic_analysis.py     # Traffic analysis logic
│   │
│   └── utils/                      # Utilities
│       ├── __init__.py
│       ├── time_utils.py           # Time-related functions
│       └── helpers.py              # Helper functions
│
├── frontend/                        # Frontend UI
│   ├── components/                 # UI Components
│   │   ├── __init__.py
│   │   ├── auth.py                 # Login/Signup
│   │   ├── dashboard.py            # Main dashboard
│   │   ├── analysis.py             # Traffic analysis UI
│   │   ├── route_planning.py       # Route planning UI
│   │   ├── heatmap.py              # Heatmap visualization
│   │   └── sidebar.py              # Sidebar navigation
│   │
│   └── styles/                     # Styling
│       ├── __init__.py
│       └── theme.py                # Custom CSS themes
│
├── data/                           # Data Storage
│   └── models/                     # ML model files
│       ├── trafficnet_image_model.h5
│       └── yolov8n.pt
│
├── app_new.py                      # Main application entry point
├── app.py                          # Legacy single-file version
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd traffic_solution
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Install ML models for actual predictions**
   ```bash
   # For TensorFlow models
   pip install tensorflow
   
   # For YOLO models
   pip install ultralytics torch
   
   # For voice assistant
   pip install pyttsx3
   ```

## 🎮 Usage

### Running the Application

1. **Using the modular version** (recommended)
   ```bash
   streamlit run app_new.py
   ```

2. **Using the legacy single-file version**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser**
   - The application will automatically open at `http://localhost:8501`

### Default Credentials

For demo purposes, use these credentials:

- **Username:** `demo`
- **Password:** `demo123`

Or:

- **Username:** `admin`
- **Password:** `admin123`

### First Time Setup

1. **Login** with demo credentials
2. **Set your location** - The app will auto-detect using IP geolocation
3. **Start analyzing** traffic or planning routes

## 📖 User Guide

### 1. Dashboard
- View current time and peak hour status
- Quick access to all features
- Manage your location settings

### 2. Traffic Analysis
- Upload a traffic image or capture from camera
- Select current weather conditions
- Click "Analyze Traffic" to get:
  - Traffic type classification
  - Vehicle count
  - Traffic density level
  - Estimated clear time
  - Safety recommendations

### 3. Route Planning
- Enter start location and destination
- View multiple route options
- See traffic-aware routing with:
  - Green routes (recommended/clear)
  - Red routes (jammed/avoid)
  - Distance and duration estimates
- Open in Google Maps for navigation

### 4. Heat Map
- Visual traffic density map
- Real-time updates (every minute)
- Color-coded traffic levels:
  - 🟢 Green: Low traffic
  - 🟠 Orange: Medium traffic
  - 🔴 Red: High traffic

## 🔧 Configuration

### Customizing Settings

Edit `backend/config/settings.py` to customize:

```python
# Peak hours
MORNING_PEAK_START = 8
MORNING_PEAK_END = 11
EVENING_PEAK_START = 17
EVENING_PEAK_END = 21

# Traffic thresholds
LOW_TRAFFIC_THRESHOLD = 30
MEDIUM_TRAFFIC_THRESHOLD = 80

# Default location
DEFAULT_LOCATION = {
    'lat': 19.0760,
    'lon': 72.8777,
    'name': 'Mumbai, India'
}
```

### Adding API Keys

For production deployment with enhanced features:

1. **IP Geolocation API** - Already using free ip-api.com
2. **OpenStreetMap Nominatim** - No API key required
3. **OSRM Routing** - Public server available

## 🤖 Implementing ML Models

The current version uses stub functions for ML predictions. To integrate actual models:

### 1. Traffic Prediction Model

Edit `backend/models/traffic_predictor.py`:

```python
from tensorflow import keras
from backend.config import config

# Load model
model = keras.models.load_model(config.TRAFFICNET_MODEL)

def predict_traffic(image):
    # Preprocess image
    img_array = preprocess_image(image)
    
    # Predict
    predictions = model.predict(img_array)
    
    # Get class and confidence
    class_idx = np.argmax(predictions[0])
    confidence = predictions[0][class_idx]
    
    return traffic_types[class_idx], float(confidence)
```

### 2. Vehicle Counter

Edit `backend/models/vehicle_counter.py`:

```python
from ultralytics import YOLO
from backend.config import config

# Load YOLO model
model = YOLO(config.YOLO_MODEL)

def count_vehicles(image):
    results = model(image)
    return len(results[0].boxes)
```

## 🌐 Deployment

### Local Network Access

```bash
streamlit run app_new.py --server.address 0.0.0.0
```

### Cloud Deployment

#### Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy from repository

#### Heroku
1. Add `Procfile`:
   ```
   web: streamlit run app_new.py --server.port=$PORT
   ```
2. Deploy using Heroku CLI

#### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app_new.py"]
```

## 🔒 Security Notes

- Default credentials are for demo only
- Implement proper authentication for production
- Use environment variables for sensitive data
- Enable HTTPS for location services
- Add rate limiting for API calls

## 🐛 Troubleshooting

### Common Issues

1. **Module not found error**
   ```bash
   pip install -r requirements.txt
   ```

2. **Location detection not working**
   - Check internet connection
   - Try manual location entry
   - IP-based geolocation may not work on localhost

3. **Voice assistant not working**
   ```bash
   pip install pyttsx3
   ```

4. **Map not displaying**
   - Check internet connection
   - Clear browser cache
   - Try different browser

## 📝 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📧 Support

For questions or support, please open an issue in the repository.

## 🙏 Acknowledgments

- **OpenStreetMap** - Map data and tiles
- **OSRM** - Routing engine
- **Streamlit** - Web framework
- **Folium** - Map visualization
- **ip-api.com** - IP geolocation

---

Made with ❤️ for smarter traffic management
