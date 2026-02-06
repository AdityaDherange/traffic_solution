"""
Heatmap Component
Traffic density visualization on map
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime
import random


def generate_heatmap_data(center_lat: float, center_lon: float):
    """
    Generate heatmap data points around center location
    
    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        
    Returns:
        List of data points with location and intensity
    """
    data_points = []
    
    # Use time-based seed for consistent data per minute
    random.seed(int(datetime.now().timestamp() // 60))
    
    for _ in range(40):
        lat_offset = random.uniform(-0.05, 0.05)
        lon_offset = random.uniform(-0.05, 0.05)
        lat = center_lat + lat_offset
        lon = center_lon + lon_offset
        
        # Calculate intensity based on distance from center
        distance = (lat_offset**2 + lon_offset**2)**0.5
        intensity = max(0.3, 1.0 - (distance * 12))
        
        # Determine color and label based on intensity
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
    
    random.seed()  # Reset seed
    return data_points


def heatmap_page():
    """Render traffic heatmap page"""
    st.markdown('<div class="header-banner"><h1>🔥 Traffic Heat Map</h1></div>', unsafe_allow_html=True)
    
    # Check if location is set
    if not st.session_state.location:
        st.warning("⚠️ Location not set. Please set your location from the dashboard first.")
        if st.button("🏠 Go to Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
        return
    
    # Initialize heatmap data in session state
    current_minute = int(datetime.now().timestamp() // 60)
    
    # Check if we need to refresh data (every 1 minute)
    needs_refresh = (
        'heatmap_data' not in st.session_state or
        'heatmap_timestamp' not in st.session_state or
        st.session_state.heatmap_timestamp != current_minute or
        'heatmap_location' not in st.session_state or
        st.session_state.heatmap_location != st.session_state.location
    )
    
    if needs_refresh:
        st.session_state.heatmap_data = generate_heatmap_data(
            st.session_state.location['lat'],
            st.session_state.location['lon']
        )
        st.session_state.heatmap_timestamp = current_minute
        st.session_state.heatmap_location = st.session_state.location.copy()
    
    # Calculate time until next refresh
    seconds_until_refresh = 60 - (int(datetime.now().timestamp()) % 60)
    
    # Info bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"🎨 Real-time traffic density visualization • Auto-refresh in {seconds_until_refresh}s")
    with col2:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.session_state.heatmap_timestamp = None  # Force refresh
            st.rerun()
    
    # Create map
    m = folium.Map(
        location=[st.session_state.location['lat'], st.session_state.location['lon']],
        zoom_start=12,
        tiles='CartoDB dark_matter' if st.session_state.theme == 'dark' else 'OpenStreetMap'
    )
    
    # Add heatmap circles
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
    
    # Add user location marker
    folium.Marker(
        [st.session_state.location['lat'], st.session_state.location['lon']],
        popup="Your Location",
        icon=folium.Icon(color='blue', icon='user', prefix='fa')
    ).add_to(m)
    
    # Display map
    st_folium(m, width=None, height=500)
    
    # Legend
    st.markdown("### 🎨 Traffic Density Legend")
    c1, c2, c3 = st.columns(3)
    
    c1.markdown(
        '<div style="background: green; color: white; padding: 15px; '
        'border-radius: 8px; text-align: center;">'
        '🟢 <strong>Low Traffic</strong><br>Free Flow<br>< 30 vehicles</div>',
        unsafe_allow_html=True
    )
    
    c2.markdown(
        '<div style="background: orange; color: white; padding: 15px; '
        'border-radius: 8px; text-align: center;">'
        '🟠 <strong>Medium Traffic</strong><br>Moderate Flow<br>30-80 vehicles</div>',
        unsafe_allow_html=True
    )
    
    c3.markdown(
        '<div style="background: red; color: white; padding: 15px; '
        'border-radius: 8px; text-align: center;">'
        '🔴 <strong>High Traffic</strong><br>Congested<br>> 80 vehicles</div>',
        unsafe_allow_html=True
    )
    
    # Statistics
    st.markdown("---")
    st.markdown("### 📊 Area Statistics")
    
    # Calculate statistics from heatmap data
    high_traffic = sum(1 for p in st.session_state.heatmap_data if p['color'] == 'red')
    medium_traffic = sum(1 for p in st.session_state.heatmap_data if p['color'] == 'orange')
    low_traffic = sum(1 for p in st.session_state.heatmap_data if p['color'] == 'green')
    
    stat_cols = st.columns(4)
    stat_cols[0].metric("📍 Total Points", len(st.session_state.heatmap_data))
    stat_cols[1].metric("🔴 High Traffic", high_traffic)
    stat_cols[2].metric("🟠 Medium Traffic", medium_traffic)
    stat_cols[3].metric("🟢 Low Traffic", low_traffic)
    
    # Overall assessment
    if high_traffic > medium_traffic + low_traffic:
        st.error("⚠️ High congestion in the area. Consider alternate routes.")
    elif medium_traffic > low_traffic:
        st.warning("🟡 Moderate traffic in the area. Some delays expected.")
    else:
        st.success("✅ Good traffic conditions in the area.")
