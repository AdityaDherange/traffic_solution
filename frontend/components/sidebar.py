"""
Sidebar Component
Navigation and settings sidebar
"""
import streamlit as st
from backend.config import config
from backend.utils import announce_voice


def render_sidebar():
    """Render application sidebar"""
    with st.sidebar:
        # Logo and title
        st.markdown(f"## {config.APP_ICON} {config.APP_NAME}")
        st.success(f"👤 **{st.session_state.username}**")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        pages = {
            'dashboard': '🏠 Dashboard',
            'analysis': '📸 Traffic Analysis',
            'route': '🗺️ Route Planning',
            'heatmap': '🔥 Heat Map'
        }
        
        for key, name in pages.items():
            # Highlight current page
            button_type = "primary" if st.session_state.page == key else "secondary"
            
            if st.button(name, use_container_width=True, key=f"nav_{key}"):
                st.session_state.page = key
                st.rerun()
        
        st.markdown("---")
        
        # Theme Settings
        st.markdown("### 🎨 Appearance")
        
        theme = st.radio(
            "Theme",
            ["Light", "Dark"],
            index=0 if st.session_state.theme == 'light' else 1,
            key="theme_radio"
        )
        
        if (theme == "Dark" and st.session_state.theme == 'light') or \
           (theme == "Light" and st.session_state.theme == 'dark'):
            st.session_state.theme = theme.lower()
            st.rerun()
        
        st.markdown("---")
        
        # Voice Assistant Settings
        st.markdown("### 🔊 Voice Assistant")
        
        voice_status = "🔊 Enabled" if st.session_state.voice_enabled else "🔇 Disabled"
        st.write(f"**Status:** {voice_status}")
        
        if st.button("🔄 Toggle Voice", use_container_width=True):
            st.session_state.voice_enabled = not st.session_state.voice_enabled
            status = "enabled" if st.session_state.voice_enabled else "disabled"
            st.success(f"Voice assistant {status}")
            st.rerun()
        
        # Announce results button (only if analysis is done)
        if st.session_state.get('analysis_done', False):
            if st.button("🎤 Announce Results", use_container_width=True):
                msg = (
                    f"{st.session_state.traffic_type} detected. "
                    f"{st.session_state.vehicle_count} vehicles counted. "
                    f"Estimated clear time: {st.session_state.clear_time} minutes."
                )
                announce_voice(msg, st.session_state.voice_enabled)
                st.success("✅ Announced!")
        
        st.markdown("---")
        
        # Quick Stats
        if st.session_state.get('analysis_done', False):
            st.markdown("### 📊 Last Analysis")
            st.metric("Traffic Type", st.session_state.traffic_type)
            st.metric("Vehicle Count", st.session_state.vehicle_count)
            st.metric("Confidence", f"{st.session_state.confidence*100:.1f}%")
        
        st.markdown("---")
        
        # Logout Button
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            # Clear session
            st.session_state.logged_in = False
            st.session_state.page = 'login'
            st.session_state.username = ''
            st.session_state.location = None
            st.session_state.analysis_done = False
            st.rerun()
        
        st.markdown("---")
        
        # About Section
        st.markdown("### ℹ️ About")
        st.markdown(f"""
        **{config.APP_NAME}**  
        Version {config.APP_VERSION}
        
        AI-powered traffic analysis and route optimization system.
        
        **Features:**
        - 📸 Traffic Image Analysis
        - 🗺️ Smart Route Planning
        - 🔥 Real-time Heat Maps
        - 🔊 Voice Announcements
        - 📍 Live Location Detection
        
        **Tech Stack:**
        - Streamlit
        - TensorFlow / YOLO
        - OpenStreetMap
        - OSRM Routing
        """)
        
        st.markdown("---")
        st.caption(f"© 2024 {config.APP_NAME}")
