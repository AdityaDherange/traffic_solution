"""
Dashboard Component
Main dashboard with quick actions and location setup
"""
import streamlit as st
from backend.config import config
from backend.utils import is_peak_hour, get_current_time_info
from backend.services import (
    get_live_location,
    format_location_display,
    geocode_location
)


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
    
    # Location display - show status only, not coordinates
    if st.session_state.location:
        location_text = format_location_display(st.session_state.location)
        status = "Detected" if st.session_state.location.get("method") != "manual" else "Set"
        col4.metric("📍 Location", status)
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
            # Show method instead of coordinates
            method = st.session_state.location.get('method', 'unknown')
            method_text = "Auto-detected via IP" if method == "ip" else "Manually entered" if method == "manual" else "Default location"
            st.info(f"📍 {method_text}")
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
        
        tab1, tab2 = st.tabs(["📍 Auto-Detect", "✍️ Enter Location Name"])
        
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
            st.info("Enter your city or location name:")
            location_name = st.text_input(
                "Location",
                placeholder="e.g., Mumbai, India or New York, USA or Paris, France",
                help="Enter city name, landmark, or address",
                key="manual_location_input"
            )
            
            st.caption("💡 **Examples:** 'London, UK' | 'Tokyo, Japan' | 'Times Square, New York'")
            
            if st.button("📌 Set Location", type="primary"):
                if location_name:
                    with st.spinner(f"🔍 Finding '{location_name}'..."):
                        geo_result = geocode_location(location_name)
                        
                        if geo_result:
                            st.session_state.location = {
                                "lat": geo_result["lat"],
                                "lon": geo_result["lon"],
                                "display_name": geo_result["display_name"],
                                "method": "manual"
                            }
                            st.session_state.show_location_form = False
                            st.success(f"✅ Location set: {geo_result['display_name']}")
                            st.rerun()
                        else:
                            st.error("❌ Could not find this location. Please try:\n\n• Adding country name (e.g., 'Paris, France')\n\n• Using full city name\n\n• Checking spelling")
                else:
                    st.error("❌ Please enter a location name")
    
    # System Status
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    status_cols = st.columns(4)
    status_cols[0].metric("🤖 AI Model", "Active", delta="98% Accuracy")
    status_cols[1].metric("🗺️ Map Service", "Online", delta="OSRM")
    status_cols[2].metric("📡 Location Service", "Active", delta="IP Geo")
    status_cols[3].metric("⚡ Response Time", "Fast", delta="<2s")
