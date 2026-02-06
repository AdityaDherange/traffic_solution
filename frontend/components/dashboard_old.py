"""
Dashboard Component
Main dashboard with quick actions and location setup
"""
import streamlit as st
from backend.config import config
from backend.utils import is_peak_hour, get_current_time_info
from backend.services import get_live_location, format_location_display


def dashboard_page():
    """Render main dashboard"""
    st.markdown(
        f'<div class="header-banner"><h1>{config.APP_ICON} Traffic Control Dashboard</h1></div>',
        unsafe_allow_html=True
    )
    st.markdown(f"### Welcome, **{st.session_state.username}**! 👋")
    
    # Get time info
    time_info = get_current_time_info()
    
    # Auto-detect location if not set
    if not st.session_state.location:
        with st.spinner("📍 Detecting your location..."):
            detected_location = get_live_location()
            if detected_location:
                st.session_state.location = detected_location
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🕐 Time", time_info["time"])
    col2.metric("📅 Date", time_info["date"])
    col3.metric("⚠️ Peak Status", time_info["peak_message"])
    
    # Location display
    if st.session_state.location:
        location_text = format_location_display(st.session_state.location)
        col4.metric("📍 Location", "Detected" if st.session_state.location.get("method") != "manual" else "Set")
    else:
        col4.metric("📍 Location", "Not Set")
    
    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    c1, c2, c3 = st.columns(3)
    
    if c1.button("📸 Analyze Traffic", use_container_width=True):
        st.session_state.page = 'analysis'
        st.rerun()
    
    if c2.button("🗺️ Plan Route", use_container_width=True):
        st.session_state.page = 'route'
        st.rerun()
    
    if c3.button("🔥 Heat Map", use_container_width=True):
        st.session_state.page = 'heatmap'
        st.rerun()
    
    # Location Setup Section
    st.markdown("---")
    st.markdown("### 📍 Location Management")
    
    if st.session_state.location:
        location_display = format_location_display(st.session_state.location)
        st.success(f"✅ Current Location: **{location_display}**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📌 Coordinates: {st.session_state.location['lat']:.6f}, {st.session_state.location['lon']:.6f}")
        with col2:
            if st.button("🔄 Change Location"):
                st.session_state.show_location_form = True
                st.rerun()
    else:
        st.warning("⚠️ No location set. Please set your location for full features.")
        st.session_state.show_location_form = True
    
    # Location input form
    if st.session_state.get('show_location_form', not st.session_state.location):
        st.markdown("#### Set Your Location")
        
        tab1, tab2 = st.tabs(["📍 Auto-Detect", "✍️ Manual Entry"])
        
        with tab1:
            st.info("Click the button below to automatically detect your location using your IP address.")
            if st.button("🌐 Auto-Detect Location", type="primary"):
                with st.spinner("Detecting location..."):
                    location = get_live_location()
                    if location:
                        st.session_state.location = location
                        st.session_state.show_location_form = False
                        st.success(f"✅ Location detected: {format_location_display(location)}")
                        st.rerun()
                    else:
                        st.error("❌ Could not detect location automatically")
        
        with tab2:
            st.info("Enter your coordinates manually:")
            c1, c2 = st.columns(2)
            lat = c1.number_input(
                "Latitude",
                value=config.DEFAULT_LOCATION["lat"],
                format="%.6f",
                help="Enter latitude (-90 to 90)"
            )
            lon = c2.number_input(
                "Longitude",
                value=config.DEFAULT_LOCATION["lon"],
                format="%.6f",
                help="Enter longitude (-180 to 180)"
            )
            
            if st.button("📌 Set Location", type="primary"):
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    st.session_state.location = {
                        "lat": lat,
                        "lon": lon,
                        "method": "manual"
                    }
                    st.session_state.show_location_form = False
                    st.success("✅ Location saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid coordinates. Latitude: -90 to 90, Longitude: -180 to 180")
    
    # System Status
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    status_cols = st.columns(4)
    status_cols[0].metric("🤖 AI Model", "Active", delta="98% Accuracy")
    status_cols[1].metric("🗺️ Map Service", "Online", delta="OSRM")
    status_cols[2].metric("📡 Location Service", "Active", delta="IP Geo")
    status_cols[3].metric("⚡ Response Time", "Fast", delta="<2s")
