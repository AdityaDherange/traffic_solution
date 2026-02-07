"""
Chatbot Component
AI-powered traffic assistant interface using Google Gemini
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime
import requests
from backend.services.chatbot import get_chatbot, TrafficChatbot


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
        return None


def get_route(start_coords, end_coords, alternatives=True):
    """Get actual road route using OSRM (Open Source Routing Machine)"""
    try:
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
                path = [[coord[1], coord[0]] for coord in coords]
                routes.append({
                    "path": path,
                    "distance": route["distance"] / 1000,
                    "duration": route["duration"] / 60,
                    "is_primary": i == 0
                })
            return routes
        return None
    except Exception as e:
        return None


def calculate_and_display_route(destination: str, start_location: dict = None):
    """Calculate route and return map HTML and route info"""
    # Default start location (Mumbai central) if not provided
    if not start_location:
        start_location = {"lat": 19.0760, "lon": 72.8777}
    
    # Geocode destination
    dest_geo = geocode_location(destination)
    if not dest_geo:
        return None, f"Could not find location: {destination}"
    
    # Get routes
    start_coords = {"lat": start_location["lat"], "lon": start_location.get("lon", start_location.get("lng", 72.8777))}
    end_coords = {"lat": dest_geo["lat"], "lon": dest_geo["lon"]}
    
    routes = get_route(start_coords, end_coords, alternatives=True)
    
    if not routes:
        return None, "Could not calculate route"
    
    # Store in session state for the route page
    st.session_state.route_start = start_coords
    st.session_state.route_dest = end_coords
    st.session_state.routes = routes
    st.session_state.start_name = "Your Location"
    st.session_state.dest_name = dest_geo["display_name"]
    
    return routes, dest_geo["display_name"]


def render_route_map(routes, start_coords, end_coords, start_name, dest_name):
    """Render a route map in the chat"""
    center_lat = (start_coords['lat'] + end_coords['lat']) / 2
    center_lon = (start_coords['lon'] + end_coords['lon']) / 2
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Add start marker
    folium.Marker(
        [start_coords['lat'], start_coords['lon']],
        popup=f"Start: {start_name}",
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)
    
    # Add destination marker
    folium.Marker(
        [end_coords['lat'], end_coords['lon']],
        popup=f"Destination: {dest_name[:50]}",
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(m)
    
    # Draw routes
    if routes:
        # Primary route in green
        primary_route = routes[0]
        folium.PolyLine(
            primary_route["path"],
            color='green', weight=6, opacity=0.8,
            popup=f"✅ Shortest Route: {primary_route['distance']:.1f} km, {primary_route['duration']:.0f} min"
        ).add_to(m)
        
        # Alternate routes in blue
        for i, route in enumerate(routes[1:], 1):
            folium.PolyLine(
                route["path"],
                color='blue', weight=4, opacity=0.5,
                popup=f"Alternate Route {i}: {route['distance']:.1f} km, {route['duration']:.0f} min"
            ).add_to(m)
    
    return m


def init_chat_session():
    """Initialize chat session state"""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'chat_input_key' not in st.session_state:
        st.session_state.chat_input_key = 0
    if 'pending_action' not in st.session_state:
        st.session_state.pending_action = None
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False


def get_session_context() -> dict:
    """Get current session state for chatbot context"""
    return {
        "analysis_done": st.session_state.get("analysis_done", False),
        "traffic_type": st.session_state.get("traffic_type"),
        "vehicle_count": st.session_state.get("vehicle_count"),
        "confidence": st.session_state.get("confidence"),
        "clear_time": st.session_state.get("clear_time"),
        "location": st.session_state.get("location"),
        "route_start": st.session_state.get("route_start"),
        "route_dest": st.session_state.get("route_dest"),
    }


def render_chat_message(role: str, content: str, timestamp: str = None):
    """Render a single chat message"""
    if role == "user":
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 12px 16px; border-radius: 18px 18px 4px 18px; 
                        max-width: 80%; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                <div style="font-size: 14px;">{content}</div>
                <div style="font-size: 10px; opacity: 0.7; text-align: right; margin-top: 4px;">
                    {timestamp or datetime.now().strftime("%I:%M %p")}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
            <div style="background: linear-gradient(135deg, #f5f7fa 0%, #e8ecef 100%); 
                        color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 4px; 
                        max-width: 80%; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        border: 1px solid #e0e0e0;">
                <div style="font-size: 14px;">{content}</div>
                <div style="font-size: 10px; opacity: 0.6; margin-top: 4px;">
                    🤖 Traffic Assistant • {timestamp or datetime.now().strftime("%I:%M %p")}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def process_chat_action(action: str, action_data: dict):
    """Process actions triggered by chatbot"""
    if action == "analyze":
        st.session_state.page = 'analysis'
        st.session_state.pending_action = "start_analysis"
        return None, "Navigating to Traffic Analysis..."
    
    elif action == "route":
        if action_data.get("destination"):
            destination = action_data["destination"]
            # Get user's current location or use default
            start_location = st.session_state.get("location", {"lat": 19.0760, "lon": 72.8777})
            
            # Calculate the route
            routes, dest_name = calculate_and_display_route(destination, start_location)
            
            if routes:
                # Store route data for display
                st.session_state.chat_route_data = {
                    "routes": routes,
                    "start_coords": st.session_state.route_start,
                    "end_coords": st.session_state.route_dest,
                    "start_name": st.session_state.start_name,
                    "dest_name": st.session_state.dest_name,
                    "show_map": True
                }
                
                primary = routes[0]
                route_info = f"""
🗺️ **Route to {dest_name[:50]}**

📍 **Shortest Route Found:**
• Distance: **{primary['distance']:.1f} km**
• Estimated Time: **{primary['duration']:.0f} minutes**

{"📌 " + str(len(routes)-1) + " alternate route(s) available" if len(routes) > 1 else ""}

*Map is displayed below* 👇
"""
                return routes, route_info
            else:
                return None, f"Sorry, I couldn't find a route to '{destination}'. Please try with a more specific location."
        
        st.session_state.page = 'route'
        return None, "Opening Route Planning page..."
    
    elif action == "heatmap":
        st.session_state.page = 'heatmap'
        return None, "Opening Heat Map..."
    
    return None, None


def chatbot_page():
    """Render full-page chatbot interface"""
    st.markdown('<div class="header-banner"><h1>🤖 AI Traffic Assistant</h1></div>', unsafe_allow_html=True)
    
    init_chat_session()
    
    # Initialize chatbot
    if st.session_state.chatbot is None:
        try:
            st.session_state.chatbot = get_chatbot()
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            return
    
    # Welcome message if no messages
    if not st.session_state.chat_messages:
        welcome_msg = """👋 Hello! I'm your AI Route & Traffic Assistant powered by **Google Gemini Pro**.

🗺️ **ROUTE FINDING (My Main Feature!):**
Just tell me where you want to go, and I'll find the **shortest route** for you!
• "Take me to Mumbai Airport"
• "How do I get to Bandra?"
• "Navigate to CST station"
• "Shortest route to Powai"

📊 **Other things I can help with:**
• **Real-time Traffic Status** - "What's the traffic at Ghatkopar?"
• **Traffic Predictions** - "Will Dadar be congested in 15 minutes?"
• **Heat Map Info** - "Show me the red zones"
• **Quick Actions** - "Execute traffic analysis now"

Where would you like to go today? 🚗"""
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": welcome_msg,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
    
    # Proactive alert check
    chatbot = st.session_state.chatbot
    alert = chatbot.get_proactive_alert(get_session_context())
    if alert:
        st.warning(alert)
    
    # Quick action buttons
    st.markdown("### ⚡ Quick Commands")
    cols = st.columns(4)
    
    quick_commands = [
        ("📸 Analyze Traffic", "Execute traffic analysis now"),
        ("🗺️ Plan Route", "I want to plan a route"),
        ("🔥 Heat Map", "Show me the heat map"),
        ("🔴 Red Zones", "Where are the red zones?")
    ]
    
    for i, (label, command) in enumerate(quick_commands):
        if cols[i].button(label, key=f"quick_cmd_{i}", use_container_width=True):
            # Add as user message and process
            st.session_state.chat_messages.append({
                "role": "user",
                "content": command,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            
            result = chatbot.process_message(command, get_session_context())
            
            if result["action"]:
                routes, action_msg = process_chat_action(result["action"], result["action_data"])
                if action_msg:
                    result["response"] = f"{result['response']}\n\n{action_msg}"
            
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": result["response"],
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            st.rerun()
    
    st.markdown("---")
    
    # Display route map if available
    if st.session_state.get("chat_route_data") and st.session_state.chat_route_data.get("show_map"):
        route_data = st.session_state.chat_route_data
        st.markdown("### 🗺️ Route Map")
        
        # Render the map
        route_map = render_route_map(
            route_data["routes"],
            route_data["start_coords"],
            route_data["end_coords"],
            route_data["start_name"],
            route_data["dest_name"]
        )
        st_folium(route_map, width=None, height=400)
        
        # Route details
        st.markdown("#### 📊 Route Details")
        for i, route in enumerate(route_data["routes"]):
            if i == 0:
                st.success(f"✅ **Shortest Route:** {route['distance']:.1f} km | {route['duration']:.0f} min")
            else:
                st.info(f"📍 **Alternate Route {i}:** {route['distance']:.1f} km | {route['duration']:.0f} min")
        
        # Google Maps link
        google_url = f"https://www.google.com/maps/dir/{route_data['start_coords']['lat']},{route_data['start_coords']['lon']}/{route_data['end_coords']['lat']},{route_data['end_coords']['lon']}"
        st.markdown(f"[🔗 Open in Google Maps]({google_url})")
        
        # Clear route button
        if st.button("❌ Clear Map", key="clear_route_map"):
            st.session_state.chat_route_data = None
            st.rerun()
        
        st.markdown("---")
    
    # Chat messages container
    st.markdown("### 💬 Conversation")
    
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            render_chat_message(msg["role"], msg["content"], msg.get("timestamp"))
    
    # Input area
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Message",
            placeholder="Ask me about traffic, routes, or say 'Take me to Mumbai Airport'...",
            key=f"chat_input_{st.session_state.chat_input_key}",
            label_visibility="collapsed"
        )
    
    with col2:
        send_btn = st.button("📤 Send", type="primary", use_container_width=True)
    
    # Process input
    if (send_btn or user_input) and user_input:
        # Add user message
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
        
        # Process with chatbot
        with st.spinner("🤔 Thinking..."):
            result = chatbot.process_message(user_input, get_session_context())
        
        # Handle actions
        if result["action"]:
            routes, action_msg = process_chat_action(result["action"], result["action_data"])
            if action_msg:
                result["response"] = f"{result['response']}\n\n{action_msg}"
        
        # Add assistant response
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": result["response"],
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
        
        # Increment key to clear input
        st.session_state.chat_input_key += 1
        
        # Rerun to show new messages and potentially navigate
        st.rerun()
    
    # Clear chat button
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            if st.session_state.chatbot:
                st.session_state.chatbot.clear_history()
            st.rerun()


def render_floating_chat():
    """Render floating chat widget in sidebar or as popup"""
    init_chat_session()
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 AI Assistant")
        
        # Initialize chatbot
        if st.session_state.chatbot is None:
            try:
                st.session_state.chatbot = get_chatbot()
            except Exception as e:
                st.error(f"Chatbot error: {e}")
                return
        
        chatbot = st.session_state.chatbot
        
        # Proactive alert
        alert = chatbot.get_proactive_alert(get_session_context())
        if alert:
            st.warning(alert, icon="🚨")
        
        # Quick questions
        st.markdown("**Quick Questions:**")
        quick_questions = [
            "Traffic at Dadar?",
            "Red zones now?",
            "Route to Airport"
        ]
        
        for q in quick_questions:
            if st.button(f"💬 {q}", key=f"sidebar_q_{q}", use_container_width=True):
                result = chatbot.process_message(q, get_session_context())
                st.session_state.last_chat_response = result["response"]
                
                if result["action"]:
                    process_chat_action(result["action"], result["action_data"])
                    st.rerun()
        
        # Show last response
        if st.session_state.get("last_chat_response"):
            st.info(st.session_state.last_chat_response[:300] + "..." if len(st.session_state.get("last_chat_response", "")) > 300 else st.session_state.get("last_chat_response", ""))
        
        # Link to full chat
        if st.button("💬 Open Full Chat", type="primary", use_container_width=True):
            st.session_state.page = 'chatbot'
            st.rerun()
