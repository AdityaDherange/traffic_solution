"""
Smart Traffic Congestion Analysis & Route Recommendation System
Complete Streamlit Application - Single File
Author: Senior Python Full-Stack Developer
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime
import random
from PIL import Image
import io
import base64
import requests

# Import chatbot components
try:
    from frontend.components.chatbot import chatbot_page, render_floating_chat, init_chat_session
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Smart Traffic System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ML BLACK-BOX FUNCTIONS (STUBS)
# ============================================================================

def predict_traffic(image):
    """ML BLACK-BOX: Traffic type prediction"""
    traffic_types = ["Clear", "Light Traffic", "Heavy Traffic", "Accident", "Fire", "Construction"]
    traffic_type = random.choice(traffic_types)
    confidence = random.uniform(0.78, 0.97)
    return traffic_type, confidence

def count_vehicles(image):
    """ML BLACK-BOX: Vehicle counting"""
    vehicle_count = random.randint(8, 145)
    return vehicle_count

def estimate_clear_time(vehicle_count, traffic_type, peak_hour, weather):
    """ML BLACK-BOX: Estimate time to clear traffic"""
    base_time = vehicle_count * 0.25
    
    type_multiplier = {
        "Clear": 0.5, "Light Traffic": 1.0, "Heavy Traffic": 2.2,
        "Accident": 3.8, "Fire": 4.5, "Construction": 2.8
    }
    base_time *= type_multiplier.get(traffic_type, 1.0)
    
    if peak_hour:
        base_time *= 1.6
    
    weather_multiplier = {"Clear": 1.0, "Rain": 1.5, "Fog": 1.7}
    base_time *= weather_multiplier.get(weather, 1.0)
    
    return int(base_time)

# ============================================================================
# GEOCODING & ROUTING FUNCTIONS
# ============================================================================

def geocode_location(location_name):
    """Convert location name to coordinates using OpenStreetMap Nominatim"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location_name,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "SmartTrafficSystem/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        if data:
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"]),
                "display_name": data[0]["display_name"]
            }
        return None
    except Exception as e:
        st.error(f"Geocoding error: {e}")
        return None

def get_route(start_coords, end_coords, alternatives=True):
    """Get actual road route using OSRM (Open Source Routing Machine)"""
    try:
        # OSRM API endpoint
        url = f"https://router.project-osrm.org/route/v1/driving/{start_coords['lon']},{start_coords['lat']};{end_coords['lon']},{end_coords['lat']}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "alternatives": "true" if alternatives else "false"
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if data["code"] == "Ok":
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
    except Exception as e:
        st.error(f"Routing error: {e}")
        return None

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session():
    defaults = {
        'logged_in': False,
        'username': '',
        'users': {'admin': 'admin123'},
        'page': 'login',
        'theme': 'light',
        'location': None,
        'image': None,
        'analysis_done': False,
        'traffic_type': None,
        'confidence': None,
        'vehicle_count': None,
        'clear_time': None,
        'voice_enabled': True,
        'route_start': None,
        'route_dest': None,
        'chat_messages': [],
        'chatbot': None,
        'chat_input_key': 0,
        'pending_action': None,
        'show_chat': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# ============================================================================
# THEME & STYLING
# ============================================================================

def apply_theme():
    if st.session_state.theme == 'dark':
        bg, text, card, accent = "#1a1a1a", "#ffffff", "#2d2d2d", "#00d2ff"
        metric_text = "#ffffff"
        metric_label = "#b0b0b0"
    else:
        bg, text, card, accent = "#f5f7fa", "#1a1a1a", "#ffffff", "#0066cc"
        metric_text = "#1a1a1a"
        metric_label = "#555555"
    
    st.markdown(f"""
    <style>
        .main {{background-color: {bg}; color: {text};}}
        .stButton>button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 10px;
            padding: 12px 28px; font-weight: 600; font-size: 16px;
        }}
        .stButton>button:hover {{opacity: 0.85; transform: scale(1.02);}}
        .header-banner {{
            background: linear-gradient(90deg, #00d2ff 0%, #3a47d5 100%);
            padding: 35px; border-radius: 15px; color: white;
            text-align: center; margin-bottom: 25px;
        }}
        .metric-box {{
            background: {card}; padding: 20px; border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 4px solid {accent}; margin: 10px 0;
            min-height: 120px;
        }}
        .metric-box h3 {{
            color: {metric_label} !important;
            font-size: 14px !important;
            margin-bottom: 10px !important;
        }}
        .metric-box h2 {{
            color: {metric_text} !important;
            font-size: 28px !important;
            margin-top: 10px !important;
        }}
        }}
        .alert-critical {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white; padding: 25px; border-radius: 12px;
            text-align: center; font-size: 22px; font-weight: bold;
            margin: 20px 0; animation: pulse 2s infinite;
        }}
        @keyframes pulse {{0%, 100% {{transform: scale(1);}} 50% {{transform: scale(1.03);}}}}
        .success-box {{background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;}}
        .warning-box {{background: #fff3cd; color: #856404; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;}}
        .danger-box {{background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545;}}
        .info-box {{background: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8;}}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_peak_hour():
    hour = datetime.now().hour
    if 8 <= hour <= 11:
        return True, "Morning Peak (8-11 AM)"
    elif 17 <= 21:
        return True, "Evening Peak (5-9 PM)"
    return False, "Off-Peak"

def get_density_level(count):
    if count < 30:
        return "Low", "green"
    elif count < 80:
        return "Medium", "orange"
    return "High", "red"

def announce_voice(text):
    if st.session_state.voice_enabled:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except:
            pass

# ============================================================================
# AUTHENTICATION
# ============================================================================

def login_page():
    st.markdown('<div class="header-banner"><h1>🚦 Smart Traffic System</h1><p>AI-Powered Traffic Management & Route Optimization</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Login", use_container_width=True):
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with c2:
            if st.button("📝 Sign Up", use_container_width=True):
                st.session_state.page = 'signup'
                st.rerun()

def signup_page():
    st.markdown('<div class="header-banner"><h1>📝 Create Account</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Register")
        new_user = st.text_input("Username", key="signup_user")
        new_pass = st.text_input("Password", type="password", key="signup_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Create", use_container_width=True):
                if new_user and new_pass and new_pass == confirm_pass:
                    if new_user not in st.session_state.users:
                        st.session_state.users[new_user] = new_pass
                        st.success("✅ Account created!")
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error("❌ Username exists")
                else:
                    st.error("❌ Invalid input")
        
        with c2:
            if st.button("⬅️ Back", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()

# ============================================================================
# DASHBOARD
# ============================================================================

def dashboard_page():
    st.markdown('<div class="header-banner"><h1>🚦 Traffic Control Dashboard</h1></div>', unsafe_allow_html=True)
    st.markdown(f"### Welcome, **{st.session_state.username}**! 👋")
    
    peak, peak_msg = is_peak_hour()
    current_time = datetime.now()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🕐 Time", current_time.strftime("%I:%M %p"))
    col2.metric("📅 Date", current_time.strftime("%b %d, %Y"))
    col3.metric("⚠️ Peak Status", peak_msg)
    col4.metric("🌐 Location", "Set Location" if not st.session_state.location else "Active")
    
    st.markdown("### 🚀 Quick Actions")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("📸 Analyze Traffic", use_container_width=True):
        st.session_state.page = 'analysis'
        st.rerun()
    if c2.button("🗺️ Plan Route", use_container_width=True):
        st.session_state.page = 'route'
        st.rerun()
    if c3.button("🔥 Heat Map", use_container_width=True):
        st.session_state.page = 'heatmap'
        st.rerun()
    if c4.button("🤖 AI Assistant", use_container_width=True):
        st.session_state.page = 'chatbot'
        st.rerun()
    
    if not st.session_state.location:
        st.warning("⚠️ Set your location for full features")
        st.markdown("### 📍 Location Setup")
        
        location_input = st.text_input(
            "Enter your location",
            placeholder="e.g., Ghatkopar West, Mumbai",
            help="Enter your area, landmark, or address"
        )
        
        if st.button("📌 Set Location", type="primary"):
            if location_input:
                with st.spinner("🔍 Finding location..."):
                    geo_result = geocode_location(location_input)
                    if geo_result:
                        st.session_state.location = {
                            "lat": geo_result["lat"],
                            "lon": geo_result["lon"],
                            "name": geo_result["display_name"]
                        }
                        st.success(f"✅ Location set: {geo_result['display_name'][:60]}...")
                        st.rerun()
                    else:
                        st.error("❌ Could not find location. Try a more specific address.")
            else:
                st.warning("Please enter a location name")
    else:
        # Show current location
        location_name = st.session_state.location.get("name", "Custom Location")
        st.success(f"📍 Current Location: **{location_name[:60]}**")
        if st.button("🔄 Change Location"):
            st.session_state.location = None
            st.rerun()

# ============================================================================
# IMAGE ANALYSIS
# ============================================================================

def analysis_page():
    st.markdown('<div class="header-banner"><h1>📸 Traffic Image Analysis</h1></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📤 Upload Image")
        uploaded = st.file_uploader("Choose image", type=['jpg', 'jpeg', 'png'])
        if uploaded:
            image = Image.open(uploaded)
            st.session_state.image = image
            st.image(image, caption="Uploaded", use_container_width=True)
    
    with c2:
        st.markdown("### 📷 Camera")
        camera = st.camera_input("Capture")
        if camera:
            image = Image.open(camera)
            st.session_state.image = image
    
    if st.session_state.image:
        if st.button("🔍 Analyze Traffic", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                traffic_type, confidence = predict_traffic(st.session_state.image)
                vehicle_count = count_vehicles(st.session_state.image)
                peak, _ = is_peak_hour()
                weather = st.selectbox("Current Weather", ["Clear", "Rain", "Fog"], key="weather_select")
                clear_time = estimate_clear_time(vehicle_count, traffic_type, peak, weather)
                
                st.session_state.traffic_type = traffic_type
                st.session_state.confidence = confidence
                st.session_state.vehicle_count = vehicle_count
                st.session_state.clear_time = clear_time
                st.session_state.analysis_done = True
                
                announce_voice(f"Traffic analysis complete. {traffic_type} detected with {int(confidence*100)} percent confidence.")
                st.success("✅ Analysis Complete!")
    
    if st.session_state.analysis_done:
        st.markdown("---")
        st.markdown("## 📊 Results")
        
        if st.session_state.traffic_type in ['Accident', 'Fire']:
            st.markdown(f'<div class="alert-critical">🚨 EMERGENCY: {st.session_state.traffic_type.upper()} DETECTED!</div>', unsafe_allow_html=True)
        elif st.session_state.traffic_type == 'Heavy Traffic':
            st.markdown('<div class="alert-critical">⚠️ HEAVY TRAFFIC AHEAD!</div>', unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-box"><h3>🎯 Confidence</h3><h2 style="color: {"green" if st.session_state.confidence > 0.85 else "orange"};">{st.session_state.confidence*100:.1f}%</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-box"><h3>🚗 Vehicles</h3><h2>{st.session_state.vehicle_count}</h2></div>', unsafe_allow_html=True)
        
        density, d_color = get_density_level(st.session_state.vehicle_count)
        c3.markdown(f'<div class="metric-box"><h3>📊 Density</h3><h2 style="color: {d_color};">{density}</h2></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-box"><h3>⏱️ Clear Time</h3><h2>{st.session_state.clear_time} min</h2></div>', unsafe_allow_html=True)
        
        st.markdown("### 🚦 Condition")
        if st.session_state.traffic_type in ['Accident', 'Fire']:
            st.markdown(f'<div class="danger-box">🚨 <strong>{st.session_state.traffic_type}</strong> - AVOID THIS ROUTE immediately!</div>', unsafe_allow_html=True)
        elif st.session_state.traffic_type == 'Heavy Traffic':
            st.markdown(f'<div class="warning-box">⚠️ <strong>{st.session_state.traffic_type}</strong> - Consider alternate route</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-box">✅ <strong>{st.session_state.traffic_type}</strong> - Safe to proceed</div>', unsafe_allow_html=True)
        
        if st.session_state.traffic_type in ['Accident', 'Fire', 'Heavy Traffic']:
            if st.button("🗺️ Find Alternate Route", use_container_width=True):
                st.session_state.page = 'route'
                st.rerun()

# ============================================================================
# ROUTE PLANNING
# ============================================================================

def route_planning_page():
    st.markdown('<div class="header-banner"><h1>🗺️ Smart Route Planning</h1></div>', unsafe_allow_html=True)
    
    # Initialize session state for routes
    if 'routes' not in st.session_state:
        st.session_state.routes = None
    if 'start_name' not in st.session_state:
        st.session_state.start_name = ""
    if 'dest_name' not in st.session_state:
        st.session_state.dest_name = ""
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📍 Start Location")
        start_input = st.text_input("Enter starting location", 
                                     placeholder="e.g., Vidya Vihar, Mumbai",
                                     key="start_location_input")
    
    with c2:
        st.markdown("### 🎯 Destination")
        dest_input = st.text_input("Enter destination", 
                                    placeholder="e.g., Kanjur Marg, Mumbai",
                                    key="dest_location_input")
    
    if st.button("🔍 Find Route", type="primary", use_container_width=True):
        if start_input and dest_input:
            with st.spinner("🔄 Finding locations..."):
                start_geo = geocode_location(start_input)
                dest_geo = geocode_location(dest_input)
                
                if start_geo and dest_geo:
                    st.session_state.route_start = {"lat": start_geo["lat"], "lon": start_geo["lon"]}
                    st.session_state.route_dest = {"lat": dest_geo["lat"], "lon": dest_geo["lon"]}
                    st.session_state.start_name = start_geo["display_name"]
                    st.session_state.dest_name = dest_geo["display_name"]
                    st.session_state.location = st.session_state.route_start
                    
                    # Get actual routes from OSRM
                    with st.spinner("🛣️ Calculating routes..."):
                        routes = get_route(st.session_state.route_start, st.session_state.route_dest, alternatives=True)
                        st.session_state.routes = routes
                    
                    if routes:
                        st.success(f"✅ Found {len(routes)} route(s)!")
                    else:
                        st.warning("⚠️ Could not find routes. Showing direct path.")
                else:
                    if not start_geo:
                        st.error(f"❌ Could not find location: {start_input}")
                    if not dest_geo:
                        st.error(f"❌ Could not find location: {dest_input}")
        else:
            st.warning("⚠️ Please enter both start and destination locations")
    
    if st.session_state.route_start and st.session_state.route_dest:
        st.markdown("### 🗺️ Navigation Map")
        
        # Show resolved location names
        if st.session_state.start_name:
            st.info(f"📍 **Start:** {st.session_state.start_name}")
        if st.session_state.dest_name:
            st.info(f"🎯 **Destination:** {st.session_state.dest_name}")
        
        should_reroute = st.session_state.analysis_done and st.session_state.traffic_type in ['Heavy Traffic', 'Accident', 'Fire']
        
        center_lat = (st.session_state.route_start['lat'] + st.session_state.route_dest['lat']) / 2
        center_lon = (st.session_state.route_start['lon'] + st.session_state.route_dest['lon']) / 2
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='CartoDB dark_matter' if st.session_state.theme == 'dark' else 'OpenStreetMap'
        )
        
        # Add start marker
        folium.Marker(
            [st.session_state.route_start['lat'], st.session_state.route_start['lon']],
            popup="Start: " + (st.session_state.start_name[:50] + "..." if len(st.session_state.start_name) > 50 else st.session_state.start_name),
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        # Add destination marker
        folium.Marker(
            [st.session_state.route_dest['lat'], st.session_state.route_dest['lon']],
            popup="Destination: " + (st.session_state.dest_name[:50] + "..." if len(st.session_state.dest_name) > 50 else st.session_state.dest_name),
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
        
        # Draw actual routes
        if st.session_state.routes:
            routes = st.session_state.routes
            
            if should_reroute and len(routes) > 1:
                # Primary route is jammed (red), show alternate (green)
                primary_route = routes[0]
                folium.PolyLine(
                    primary_route["path"],
                    color='red', weight=6, opacity=0.7,
                    popup=f"❌ Jammed Route: {primary_route['distance']:.1f} km, {primary_route['duration']:.0f} min"
                ).add_to(m)
                
                # Add alternate routes in green
                for i, route in enumerate(routes[1:], 1):
                    folium.PolyLine(
                        route["path"],
                        color='green', weight=6, opacity=0.8,
                        popup=f"✅ Alternate Route {i}: {route['distance']:.1f} km, {route['duration']:.0f} min"
                    ).add_to(m)
                
                # Add traffic marker at midpoint of primary route
                mid_idx = len(primary_route["path"]) // 2
                mid_point = primary_route["path"][mid_idx]
                folium.Marker(mid_point, popup="⚠️ Traffic/Incident", 
                             icon=folium.Icon(color='orange', icon='exclamation-triangle', prefix='fa')).add_to(m)
            else:
                # Show primary route as clear (green)
                primary_route = routes[0]
                folium.PolyLine(
                    primary_route["path"],
                    color='green', weight=6, opacity=0.8,
                    popup=f"✅ Route: {primary_route['distance']:.1f} km, {primary_route['duration']:.0f} min"
                ).add_to(m)
                
                # Show alternate routes in lighter color
                for i, route in enumerate(routes[1:], 1):
                    folium.PolyLine(
                        route["path"],
                        color='blue', weight=4, opacity=0.5,
                        popup=f"Alternate Route {i}: {route['distance']:.1f} km, {route['duration']:.0f} min"
                    ).add_to(m)
        else:
            # Fallback to direct line if no routes found
            folium.PolyLine(
                [[st.session_state.route_start['lat'], st.session_state.route_start['lon']],
                 [st.session_state.route_dest['lat'], st.session_state.route_dest['lon']]],
                color='green', weight=6, opacity=0.8, popup="Direct Path"
            ).add_to(m)
        
        st_folium(m, width=None, height=500)
        
        # Show route information
        if st.session_state.routes:
            st.markdown("### 📊 Route Details")
            for i, route in enumerate(st.session_state.routes):
                if i == 0:
                    if should_reroute:
                        st.markdown(f'<div class="danger-box">❌ <strong>Primary Route (Jammed):</strong> {route["distance"]:.1f} km | {route["duration"]:.0f} min</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="success-box">✅ <strong>Primary Route:</strong> {route["distance"]:.1f} km | {route["duration"]:.0f} min</div>', unsafe_allow_html=True)
                else:
                    if should_reroute:
                        st.markdown(f'<div class="success-box">✅ <strong>Alternate Route {i} (Recommended):</strong> {route["distance"]:.1f} km | {route["duration"]:.0f} min</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info-box">ℹ️ <strong>Alternate Route {i}:</strong> {route["distance"]:.1f} km | {route["duration"]:.0f} min</div>', unsafe_allow_html=True)
        
        if should_reroute:
            st.markdown('<div class="alert-critical">🚨 MAIN ROUTE JAMMED!</div>', unsafe_allow_html=True)
            st.markdown('<div class="danger-box">⚠️ <strong>Primary route has issues</strong> — Take alternate route (GREEN path)</div>', unsafe_allow_html=True)
            announce_voice("Main route is jammed. Taking alternate route shown in green.")
        else:
            st.markdown('<div class="success-box">✅ Route is clear — Proceed on the recommended path</div>', unsafe_allow_html=True)
        
        google_url = f"https://www.google.com/maps/dir/{st.session_state.route_start['lat']},{st.session_state.route_start['lon']}/{st.session_state.route_dest['lat']},{st.session_state.route_dest['lon']}"
        st.markdown(f'<a href="{google_url}" target="_blank"><button style="background: #4285f4; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px;">🗺️ Open in Google Maps</button></a>', unsafe_allow_html=True)
        st.info("ℹ️ Routes follow actual roads using OpenStreetMap routing")

# ============================================================================
# HEAT MAP
# ============================================================================

def generate_heatmap_data(center_lat, center_lon):
    """Generate heatmap data points - called only when data needs refresh"""
    data_points = []
    random.seed(int(datetime.now().timestamp() // 60))  # Seed changes every minute
    for _ in range(40):
        lat_offset = random.uniform(-0.05, 0.05)
        lon_offset = random.uniform(-0.05, 0.05)
        lat = center_lat + lat_offset
        lon = center_lon + lon_offset
        
        distance = (lat_offset**2 + lon_offset**2)**0.5
        intensity = max(0.3, 1.0 - (distance * 12))
        
        if intensity > 0.7:
            color, label = 'red', 'High Traffic'
        elif intensity > 0.5:
            color, label = 'orange', 'Medium Traffic'
        else:
            color, label = 'green', 'Low Traffic'
        
        data_points.append({
            'lat': lat,
            'lon': lon,
            'intensity': intensity,
            'color': color,
            'label': label
        })
    random.seed()  # Reset seed to normal random behavior
    return data_points

def heatmap_page():
    st.markdown('<div class="header-banner"><h1>🔥 Traffic Heat Map</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.location:
        st.warning("⚠️ Set location first")
        return
    
    # Initialize heatmap data in session state
    current_minute = int(datetime.now().timestamp() // 60)
    
    # Check if we need to refresh data (every 1 minute)
    if 'heatmap_data' not in st.session_state or \
       'heatmap_timestamp' not in st.session_state or \
       st.session_state.heatmap_timestamp != current_minute or \
       'heatmap_location' not in st.session_state or \
       st.session_state.heatmap_location != st.session_state.location:
        
        st.session_state.heatmap_data = generate_heatmap_data(
            st.session_state.location['lat'],
            st.session_state.location['lon']
        )
        st.session_state.heatmap_timestamp = current_minute
        st.session_state.heatmap_location = st.session_state.location.copy()
    
    # Calculate time until next refresh
    seconds_until_refresh = 60 - (int(datetime.now().timestamp()) % 60)
    
    st.info(f"🎨 Traffic density visualization • Next refresh in {seconds_until_refresh} seconds")
    
    # Manual refresh button
    if st.button("🔄 Refresh Now"):
        st.session_state.heatmap_timestamp = None  # Force refresh
        st.rerun()
    
    m = folium.Map(
        location=[st.session_state.location['lat'], st.session_state.location['lon']],
        zoom_start=12,
        tiles='CartoDB dark_matter' if st.session_state.theme == 'dark' else 'OpenStreetMap'
    )
    
    # Use cached heatmap data
    for point in st.session_state.heatmap_data:
        folium.CircleMarker(
            [point['lat'], point['lon']], 
            radius=point['intensity'] * 12, 
            popup=point['label'],
            color=point['color'], 
            fill=True, 
            fillColor=point['color'], 
            fillOpacity=0.4
        ).add_to(m)
    
    folium.Marker(
        [st.session_state.location['lat'], st.session_state.location['lon']],
        popup="Your Location", icon=folium.Icon(color='blue', icon='user', prefix='fa')
    ).add_to(m)
    
    st_folium(m, width=None, height=500)
    
    st.markdown("### 🎨 Legend")
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div style="background: green; color: white; padding: 15px; border-radius: 8px; text-align: center;">🟢 Low<br>Free Flow</div>', unsafe_allow_html=True)
    c2.markdown('<div style="background: orange; color: white; padding: 15px; border-radius: 8px; text-align: center;">🟠 Medium<br>Moderate</div>', unsafe_allow_html=True)
    c3.markdown('<div style="background: red; color: white; padding: 15px; border-radius: 8px; text-align: center;">🔴 High<br>Congested</div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🚦 Navigation")
        st.success(f"👤 {st.session_state.username}")
        
        pages = {
            'dashboard': '🏠 Dashboard',
            'analysis': '📸 Analysis',
            'route': '🗺️ Route Plan',
            'heatmap': '🔥 Heat Map',
            'chatbot': '🤖 AI Assistant'
        }
        
        for key, name in pages.items():
            if st.button(name, use_container_width=True, key=f"nav_{key}"):
                st.session_state.page = key
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎨 Settings")
        
        theme = st.radio("Theme", ["Light", "Dark"], 
                        index=0 if st.session_state.theme == 'light' else 1)
        if (theme == "Dark" and st.session_state.theme == 'light') or \
           (theme == "Light" and st.session_state.theme == 'dark'):
            st.session_state.theme = theme.lower()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔊 Voice Assistant")
        
        voice_status = "🔊 ON" if st.session_state.voice_enabled else "🔇 OFF"
        st.write(f"Status: {voice_status}")
        
        if st.button("Toggle Voice"):
            st.session_state.voice_enabled = not st.session_state.voice_enabled
            st.rerun()
        
        if st.session_state.analysis_done and st.button("🎤 Announce Results"):
            msg = f"{st.session_state.traffic_type} detected. {st.session_state.vehicle_count} vehicles counted. Estimated clear time: {st.session_state.clear_time} minutes."
            announce_voice(msg)
            st.success("✅ Announced")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = 'login'
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        ### ℹ️ About
        **Smart Traffic System v1.0**
        
        AI-powered traffic analysis and route optimization.
        
        **Features:**
        - Traffic prediction
        - Route planning
        - Heat maps
        - Voice alerts
        """)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    if not st.session_state.logged_in:
        if st.session_state.page == 'signup':
            signup_page()
        else:
            login_page()
    else:
        render_sidebar()
        
        if st.session_state.page == 'dashboard':
            dashboard_page()
        elif st.session_state.page == 'analysis':
            analysis_page()
        elif st.session_state.page == 'route':
            route_planning_page()
        elif st.session_state.page == 'heatmap':
            heatmap_page()
        elif st.session_state.page == 'chatbot':
            if CHATBOT_AVAILABLE:
                chatbot_page()
            else:
                st.error("❌ Chatbot not available. Please install google-generativeai package.")
                st.code("pip install google-generativeai", language="bash")
        else:
            dashboard_page()

if __name__ == "__main__":
    main()