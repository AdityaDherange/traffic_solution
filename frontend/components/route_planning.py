"""
Route Planning Component
Smart route planning with real-time traffic integration
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
from backend.services import geocode_location, get_route, should_reroute
from backend.utils import announce_voice


def route_planning_page():
    """Render route planning page"""
    st.markdown('<div class="header-banner"><h1>🗺️ Smart Route Planning</h1></div>', unsafe_allow_html=True)
    
    # Initialize session state for routes
    if 'routes' not in st.session_state:
        st.session_state.routes = None
    if 'start_name' not in st.session_state:
        st.session_state.start_name = ""
    if 'dest_name' not in st.session_state:
        st.session_state.dest_name = ""
    
    # Input Section
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 📍 Start Location")
        start_input = st.text_input(
            "Enter starting location",
            placeholder="e.g., Vidya Vihar, Mumbai",
            key="start_location_input",
            help="Enter city, landmark, or address"
        )
    
    with c2:
        st.markdown("### 🎯 Destination")
        dest_input = st.text_input(
            "Enter destination",
            placeholder="e.g., Kanjur Marg, Mumbai",
            key="dest_location_input",
            help="Enter city, landmark, or address"
        )
    
    # Find Route Button
    if st.button("🔍 Find Best Route", type="primary", use_container_width=True):
        if start_input and dest_input:
            with st.spinner("🔄 Searching locations..."):
                start_geo = geocode_location(start_input)
                dest_geo = geocode_location(dest_input)
                
                if start_geo and dest_geo:
                    st.session_state.route_start = {"lat": start_geo["lat"], "lon": start_geo["lon"]}
                    st.session_state.route_dest = {"lat": dest_geo["lat"], "lon": dest_geo["lon"]}
                    st.session_state.start_name = start_geo["display_name"]
                    st.session_state.dest_name = dest_geo["display_name"]
                    st.session_state.location = st.session_state.route_start
                    
                    # Get actual routes from OSRM
                    with st.spinner("🛣️ Calculating optimal routes..."):
                        routes = get_route(
                            st.session_state.route_start,
                            st.session_state.route_dest,
                            alternatives=True
                        )
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
    
    # Display Route Map
    if st.session_state.route_start and st.session_state.route_dest:
        st.markdown("---")
        st.markdown("### 🗺️ Navigation Map")
        
        # Show resolved location names
        if st.session_state.start_name:
            st.info(f"📍 **Start:** {st.session_state.start_name[:100]}")
        if st.session_state.dest_name:
            st.info(f"🎯 **Destination:** {st.session_state.dest_name[:100]}")
        
        # Check if rerouting needed based on traffic analysis
        needs_reroute = (
            st.session_state.analysis_done and
            should_reroute(
                st.session_state.get('traffic_type', ''),
                st.session_state.get('vehicle_count', 0)
            )
        )
        
        # Calculate map center
        center_lat = (st.session_state.route_start['lat'] + st.session_state.route_dest['lat']) / 2
        center_lon = (st.session_state.route_start['lon'] + st.session_state.route_dest['lon']) / 2
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='CartoDB dark_matter' if st.session_state.theme == 'dark' else 'OpenStreetMap'
        )
        
        # Add start marker
        folium.Marker(
            [st.session_state.route_start['lat'], st.session_state.route_start['lon']],
            popup="Start: " + st.session_state.start_name[:50],
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        # Add destination marker
        folium.Marker(
            [st.session_state.route_dest['lat'], st.session_state.route_dest['lon']],
            popup="Destination: " + st.session_state.dest_name[:50],
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
        
        # Draw routes
        if st.session_state.routes:
            routes = st.session_state.routes
            
            if needs_reroute and len(routes) > 1:
                # Primary route is jammed (red), show alternates (green)
                primary_route = routes[0]
                folium.PolyLine(
                    primary_route["path"],
                    color='red',
                    weight=6,
                    opacity=0.7,
                    popup=f"❌ Jammed Route: {primary_route['distance']:.1f} km, {primary_route['duration']:.0f} min"
                ).add_to(m)
                
                # Alternate routes in green
                for i, route in enumerate(routes[1:], 1):
                    folium.PolyLine(
                        route["path"],
                        color='green',
                        weight=6,
                        opacity=0.8,
                        popup=f"✅ Alternate Route {i}: {route['distance']:.1f} km, {route['duration']:.0f} min"
                    ).add_to(m)
                
                # Add traffic marker
                mid_idx = len(primary_route["path"]) // 2
                mid_point = primary_route["path"][mid_idx]
                folium.Marker(
                    mid_point,
                    popup="⚠️ Traffic/Incident",
                    icon=folium.Icon(color='orange', icon='exclamation-triangle', prefix='fa')
                ).add_to(m)
            else:
                # All routes clear
                for i, route in enumerate(routes):
                    color = 'green' if i == 0 else 'blue'
                    weight = 6 if i == 0 else 4
                    opacity = 0.8 if i == 0 else 0.5
                    label = "Primary Route" if i == 0 else f"Alternate Route {i}"
                    
                    folium.PolyLine(
                        route["path"],
                        color=color,
                        weight=weight,
                        opacity=opacity,
                        popup=f"{label}: {route['distance']:.1f} km, {route['duration']:.0f} min"
                    ).add_to(m)
        else:
            # Fallback: direct line
            folium.PolyLine(
                [[st.session_state.route_start['lat'], st.session_state.route_start['lon']],
                 [st.session_state.route_dest['lat'], st.session_state.route_dest['lon']]],
                color='green',
                weight=6,
                opacity=0.8,
                popup="Direct Path"
            ).add_to(m)
        
        # Display map
        st_folium(m, width=None, height=500)
        
        # Route Information
        if st.session_state.routes:
            st.markdown("### 📊 Route Details")
            
            for i, route in enumerate(st.session_state.routes):
                if i == 0:
                    if needs_reroute:
                        st.markdown(
                            f'<div class="danger-box">❌ <strong>Primary Route (Jammed):</strong> '
                            f'{route["distance"]:.1f} km | {route["duration"]:.0f} min</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="success-box">✅ <strong>Recommended Route:</strong> '
                            f'{route["distance"]:.1f} km | {route["duration"]:.0f} min</div>',
                            unsafe_allow_html=True
                        )
                else:
                    box_class = "success-box" if needs_reroute else "info-box"
                    icon = "✅" if needs_reroute else "ℹ️"
                    label = "RECOMMENDED" if needs_reroute else "Option"
                    
                    st.markdown(
                        f'<div class="{box_class}">{icon} <strong>Alternate Route {i} ({label}):</strong> '
                        f'{route["distance"]:.1f} km | {route["duration"]:.0f} min</div>',
                        unsafe_allow_html=True
                    )
        
        # Alert for rerouting
        if needs_reroute:
            st.markdown(
                '<div class="alert-critical">🚨 MAIN ROUTE JAMMED!</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="danger-box">⚠️ <strong>Primary route has issues</strong> '
                '— Take alternate route (GREEN path)</div>',
                unsafe_allow_html=True
            )
            announce_voice(
                "Main route is jammed. Taking alternate route shown in green.",
                st.session_state.voice_enabled
            )
        else:
            st.markdown(
                '<div class="success-box">✅ Route is clear — Proceed on the recommended path</div>',
                unsafe_allow_html=True
            )
        
        # Google Maps link
        google_url = (
            f"https://www.google.com/maps/dir/"
            f"{st.session_state.route_start['lat']},{st.session_state.route_start['lon']}/"
            f"{st.session_state.route_dest['lat']},{st.session_state.route_dest['lon']}"
        )
        st.markdown(
            f'<a href="{google_url}" target="_blank">'
            '<button style="background: #4285f4; color: white; padding: 12px 24px; '
            'border: none; border-radius: 8px; cursor: pointer; font-size: 16px;">'
            '🗺️ Open in Google Maps</button></a>',
            unsafe_allow_html=True
        )
        
        st.info("ℹ️ Routes calculated using OpenStreetMap routing engine (OSRM)")
