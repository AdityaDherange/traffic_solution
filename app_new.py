"""
Smart Traffic Congestion Analysis & Route Recommendation System
Main Application Entry Point
Version: 2.0
"""

import streamlit as st
from backend.config import config
from backend.services import get_live_location
from frontend.components import (
    login_page,
    signup_page,
    dashboard_page,
    analysis_page,
    route_planning_page,
    heatmap_page,
    render_sidebar,
    chatbot_page
)
from frontend.styles import apply_theme


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session():
    """Initialize session state variables"""
    defaults = {
        # Authentication
        'logged_in': False,
        'username': '',
        'users': config.DEFAULT_USERS.copy(),
        
        # Navigation
        'page': 'login',
        
        # Settings
        'theme': 'light',
        'voice_enabled': True,
        
        # Location
        'location': None,
        'show_location_form': False,
        
        # Traffic Analysis
        'image': None,
        'analysis_done': False,
        'traffic_type': None,
        'confidence': None,
        'vehicle_count': None,
        'clear_time': None,
        
        # Route Planning
        'route_start': None,
        'route_dest': None,
        'routes': None,
        'start_name': '',
        'dest_name': '',
        
        # Heatmap
        'heatmap_data': None,
        'heatmap_timestamp': None,
        'heatmap_location': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Initialize session state
init_session()


# ============================================================================
# APPLY THEME
# ============================================================================

apply_theme()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Check authentication
    if not st.session_state.logged_in:
        # Show login or signup page
        if st.session_state.page == 'signup':
            signup_page()
        else:
            login_page()
    else:
        # Render sidebar for authenticated users
        render_sidebar()
        
        # Route to appropriate page
        page = st.session_state.page
        
        if page == 'dashboard':
            dashboard_page()
        elif page == 'analysis':
            analysis_page()
        elif page == 'route':
            route_planning_page()
        elif page == 'heatmap':
            heatmap_page()
        elif page == 'chatbot':
            chatbot_page()
        else:
            # Default to dashboard
            dashboard_page()


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
