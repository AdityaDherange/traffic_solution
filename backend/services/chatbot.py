"""
AI Chatbot Service
Powered by Google Gemini for intelligent traffic assistance
"""
import google.generativeai as genai
from datetime import datetime
import random
import re
from typing import Optional, Dict, Any, Tuple


class TrafficChatbot:
    """
    AI-powered traffic assistant chatbot using Google Gemini
    Integrates with traffic analysis, route planning, and heatmap features
    """
    
    def __init__(self, api_key: str):
        """Initialize the chatbot with Gemini API"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Use Gemini Pro model
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Chat history for context
        self.chat_history = []
        
        # System context for the chatbot
        self.system_context = """You are an intelligent AI Route & Traffic Assistant integrated into the Smart Traffic System in Mumbai, India.

You are specialized in finding the SHORTEST and FASTEST routes to destinations. You are powered by Google Gemini Pro.

🚦 TRAFFIC & TRANSPORTATION (Primary Focus):
- **ROUTE PLANNING (MAIN FEATURE):** When users ask for directions, navigation, or how to get somewhere, you help them find the shortest and fastest route. You can handle natural language requests like:
  - "Take me to Mumbai Airport"
  - "How do I get to Bandra?"
  - "Navigate to CST station"
  - "I want to go to Dadar"
  - "What's the shortest route to Powai?"
  - "Find directions to Andheri"
- Real-time traffic status inquiries - providing current traffic density, vehicle counts, and estimated delays
- Predictive traffic advice - warning about upcoming congestion based on patterns
- Anomaly and incident alerts - notifying about accidents, fires, or unusual traffic spikes
- Historical traffic data queries - summarizing past traffic patterns
- Traffic analysis interpretation - explaining analysis results

Mumbai locations you know well: Ghatkopar, Dadar, Kanjurmarg, Andheri, Bandra, Kurla, 
Vidya Vihar, Mulund, Thane, Powai, BKC, Worli, Lower Parel, CST, Churchgate, Marine Drive,
Borivali, Malad, Goregaon, Jogeshwari, Santacruz, Vile Parle, Mumbai Airport, Chembur,
Navi Mumbai, Panvel, Vashi, Nerul, Kharghar, CBD Belapur, Airoli, Ghansoli, Kopar Khairane.

🌐 GENERAL KNOWLEDGE & ASSISTANCE:
- Answer questions on ANY topic: science, technology, history, geography, math, coding, etc.
- Help with programming, debugging, and technical problems
- Provide explanations, tutorials, and educational content
- Creative writing, brainstorming, and idea generation
- General advice and recommendations
- Current events and general knowledge

ROUTE PLANNING GUIDELINES:
- When a user mentions ANY destination or asks how to get somewhere, ALWAYS trigger the route action
- Provide helpful context about the destination (landmarks, what's nearby)
- Mention estimated travel time and distance when available
- Suggest best times to travel to avoid traffic
- For popular destinations, mention useful tips

GUIDELINES:
- Be helpful, accurate, and comprehensive in your responses
- Use emojis to make responses engaging 😊
- For traffic-related queries, provide specific data when available
- For general questions, provide detailed and informative answers
- If asked to perform traffic actions (analyze, route, heatmap), indicate which action should be triggered
- Always be friendly and conversational

You can answer ANY question the user asks - you are not limited to traffic topics only!"""

    def _get_mock_traffic_data(self, location: str) -> Dict[str, Any]:
        """Generate realistic mock traffic data for a location"""
        # Seed based on location and current time for consistency
        seed = hash(location + datetime.now().strftime("%Y%m%d%H"))
        random.seed(seed)
        
        hour = datetime.now().hour
        is_peak = 8 <= hour <= 11 or 17 <= hour <= 21
        
        # Base vehicle count varies by peak hours
        if is_peak:
            vehicle_count = random.randint(80, 180)
        else:
            vehicle_count = random.randint(20, 80)
        
        # Determine density level
        if vehicle_count < 50:
            density = "Low"
            delay = random.randint(2, 8)
            color = "green"
        elif vehicle_count < 100:
            density = "Medium"
            delay = random.randint(10, 20)
            color = "orange"
        else:
            density = "High"
            delay = random.randint(22, 45)
            color = "red"
        
        # Random anomaly chance (5%)
        anomaly = None
        if random.random() < 0.05:
            anomaly = random.choice(["accident", "vehicle stall", "road work"])
        
        random.seed()  # Reset seed
        
        return {
            "location": location,
            "vehicle_count": vehicle_count,
            "density": density,
            "delay_minutes": delay,
            "color": color,
            "anomaly": anomaly,
            "is_peak_hour": is_peak,
            "timestamp": datetime.now().strftime("%I:%M %p")
        }

    def _get_prediction_data(self, location: str, minutes_ahead: int = 15) -> Dict[str, Any]:
        """Generate traffic prediction for future"""
        current_data = self._get_mock_traffic_data(location)
        
        hour = datetime.now().hour
        future_hour = (hour + (minutes_ahead // 60)) % 24
        
        # Check if moving into or out of peak hours
        entering_peak = not current_data["is_peak_hour"] and (8 <= future_hour <= 11 or 17 <= future_hour <= 21)
        exiting_peak = current_data["is_peak_hour"] and not (8 <= future_hour <= 11 or 17 <= future_hour <= 21)
        
        if entering_peak:
            prediction = "increasing"
            expected_density = "High" if current_data["density"] != "High" else "Very High"
        elif exiting_peak:
            prediction = "decreasing"
            expected_density = "Medium" if current_data["density"] == "High" else "Low"
        else:
            prediction = "stable"
            expected_density = current_data["density"]
        
        return {
            "location": location,
            "current_density": current_data["density"],
            "prediction": prediction,
            "expected_density": expected_density,
            "minutes_ahead": minutes_ahead
        }

    def _get_historical_summary(self, location: str, day: str = "Monday") -> Dict[str, Any]:
        """Generate historical traffic summary"""
        return {
            "location": location,
            "day": day,
            "peak_hours": {
                "morning": "8:30 AM - 10:30 AM",
                "evening": "6:00 PM - 8:30 PM"
            },
            "busiest_hour": "9:00 AM" if day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] else "11:00 AM",
            "average_vehicles": {
                "peak": random.randint(120, 160),
                "off_peak": random.randint(30, 60)
            },
            "recommended_travel_times": ["Before 7:30 AM", "11:00 AM - 4:00 PM", "After 9:30 PM"]
        }

    def _get_red_zones(self) -> list:
        """Get current red (high traffic) zones"""
        # Mumbai locations with simulated high traffic
        all_locations = [
            "Dadar", "Ghatkopar", "Andheri", "Kurla", "Bandra",
            "BKC", "Worli", "Lower Parel", "Thane", "Mulund"
        ]
        
        red_zones = []
        for loc in all_locations:
            data = self._get_mock_traffic_data(loc)
            if data["density"] == "High":
                red_zones.append({
                    "location": loc,
                    "vehicles": data["vehicle_count"],
                    "delay": data["delay_minutes"]
                })
        
        return red_zones if red_zones else [{"location": "No critical zones currently", "vehicles": 0, "delay": 0}]

    def _detect_intent(self, message: str) -> Tuple[str, Dict[str, Any]]:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Action intents
        if any(phrase in message_lower for phrase in ["analyze traffic", "run analysis", "execute traffic analysis", "analyze now"]):
            return "action_analyze", {}
        
        # Enhanced route detection with more natural language patterns
        route_triggers = [
            "plan route", "take me to", "navigate to", "go to", "route to", 
            "directions to", "how do i get to", "how to get to", "how to reach",
            "shortest route to", "fastest route to", "best route to", "way to",
            "i want to go to", "i need to go to", "i want to reach", "bring me to",
            "drive me to", "travel to", "get me to", "find route to", "show route to",
            "path to", "road to", "distance to", "commute to"
        ]
        
        if any(phrase in message_lower for phrase in route_triggers):
            # Extract destination with more patterns
            patterns = [
                r"take me to (.+)",
                r"navigate to (.+)",
                r"go to (.+)",
                r"route to (.+)",
                r"directions to (.+)",
                r"plan route to (.+)",
                r"how do i get to (.+)",
                r"how to get to (.+)",
                r"how to reach (.+)",
                r"shortest route to (.+)",
                r"fastest route to (.+)",
                r"best route to (.+)",
                r"way to (.+)",
                r"i want to go to (.+)",
                r"i need to go to (.+)",
                r"i want to reach (.+)",
                r"bring me to (.+)",
                r"drive me to (.+)",
                r"travel to (.+)",
                r"get me to (.+)",
                r"find route to (.+)",
                r"show route to (.+)",
                r"path to (.+)",
                r"road to (.+)",
                r"distance to (.+)",
                r"commute to (.+)"
            ]
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    destination = match.group(1).strip().rstrip("?.,!")
                    return "action_route", {"destination": destination}
            return "action_route", {}
        
        if any(phrase in message_lower for phrase in ["heat map", "heatmap", "show heatmap"]):
            return "action_heatmap", {}
        
        if any(phrase in message_lower for phrase in ["red zone", "red zones", "congested areas", "high traffic areas"]):
            return "query_red_zones", {}
        
        # Query intents - traffic status
        if any(phrase in message_lower for phrase in ["traffic at", "traffic in", "traffic density", "current traffic", "status at", "status in", "how is traffic"]):
            # Extract location
            locations = ["ghatkopar", "dadar", "andheri", "bandra", "kurla", "kanjurmarg", 
                        "vidya vihar", "mulund", "thane", "powai", "bkc", "worli", "lower parel",
                        "cst", "churchgate", "marine drive", "borivali", "malad", "goregaon",
                        "jogeshwari", "santacruz", "vile parle", "mumbai airport", "chembur"]
            for loc in locations:
                if loc in message_lower:
                    return "query_traffic", {"location": loc.title()}
            return "query_traffic", {}
        
        # Prediction intent
        if any(phrase in message_lower for phrase in ["will be congested", "prediction", "predict", "going to be busy", "will there be traffic"]):
            locations = ["ghatkopar", "dadar", "andheri", "bandra", "kurla", "kanjurmarg",
                        "vidya vihar", "mulund", "thane", "powai", "bkc", "worli"]
            for loc in locations:
                if loc in message_lower:
                    return "query_prediction", {"location": loc.title()}
            return "query_prediction", {}
        
        # Historical data intent
        if any(phrase in message_lower for phrase in ["peak hours", "last monday", "last week", "historical", "busiest time", "best time to travel"]):
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            day = "Monday"
            for d in days:
                if d in message_lower:
                    day = d.title()
                    break
            return "query_historical", {"day": day}
        
        # General conversation
        return "general", {}

    def process_message(self, user_message: str, session_state: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user message and return response with any actions to trigger
        
        Args:
            user_message: The user's input message
            session_state: Optional session state with current analysis data
            
        Returns:
            Dict with 'response', 'action', and 'action_data' keys
        """
        intent, intent_data = self._detect_intent(user_message)
        action = None
        action_data = {}
        
        # Build context based on intent
        context = self.system_context + "\n\n"
        
        if intent == "action_analyze":
            action = "analyze"
            context += "User wants to trigger traffic analysis. Acknowledge and indicate the analysis will start."
        
        elif intent == "action_route":
            action = "route"
            if "destination" in intent_data:
                action_data["destination"] = intent_data["destination"]
                context += f"User wants to plan a route to {intent_data['destination']}. Acknowledge and indicate route planning will start."
            else:
                context += "User wants to plan a route but didn't specify destination. Ask for the destination."
        
        elif intent == "action_heatmap":
            action = "heatmap"
            context += "User wants to see the heat map. Acknowledge and indicate the heatmap will be shown."
        
        elif intent == "query_red_zones":
            red_zones = self._get_red_zones()
            context += f"Current red (high traffic) zones data: {red_zones}\n"
            context += "Provide information about current red zones based on this data."
        
        elif intent == "query_traffic":
            if "location" in intent_data:
                traffic_data = self._get_mock_traffic_data(intent_data["location"])
                context += f"Current traffic data for {intent_data['location']}: {traffic_data}\n"
                context += "Provide a helpful response about traffic conditions using this data."
            else:
                context += "User asked about traffic but didn't specify location. Ask which location they want to know about."
        
        elif intent == "query_prediction":
            if "location" in intent_data:
                prediction = self._get_prediction_data(intent_data["location"])
                context += f"Traffic prediction for {intent_data['location']}: {prediction}\n"
                context += "Provide a helpful prediction response and suggest if they should avoid or use alternate routes."
            else:
                context += "User asked for prediction but didn't specify location. Ask which location they want predictions for."
        
        elif intent == "query_historical":
            historical = self._get_historical_summary("General Mumbai", intent_data.get("day", "Monday"))
            context += f"Historical traffic data: {historical}\n"
            context += "Provide a summary of historical traffic patterns based on this data."
        
        else:
            # Include current session state if available
            if session_state:
                if session_state.get("analysis_done"):
                    context += f"""
Current analysis results (if relevant):
- Traffic Type: {session_state.get('traffic_type', 'N/A')}
- Vehicle Count: {session_state.get('vehicle_count', 'N/A')}
- Confidence: {session_state.get('confidence', 0) * 100:.1f}%
- Clear Time: {session_state.get('clear_time', 'N/A')} minutes
"""
                if session_state.get("location"):
                    context += f"\nUser's current location: Lat {session_state['location'].get('lat')}, Lon {session_state['location'].get('lon')}"
        
        # Add chat history for context
        history_context = ""
        for entry in self.chat_history[-6:]:  # Last 3 exchanges
            history_context += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n"
        
        if history_context:
            context += f"\n\nRecent conversation:\n{history_context}"
        
        # Generate response using Gemini
        try:
            prompt = f"{context}\n\nUser message: {user_message}\n\nProvide a helpful, concise response:"
            response = self.model.generate_content(prompt)
            response_text = response.text
        except Exception as e:
            response_text = f"I'm having trouble connecting to my AI service right now. Error: {str(e)[:100]}. Please try again in a moment."
        
        # Store in history
        self.chat_history.append({
            "user": user_message,
            "assistant": response_text
        })
        
        # Keep history manageable
        if len(self.chat_history) > 20:
            self.chat_history = self.chat_history[-20:]
        
        return {
            "response": response_text,
            "action": action,
            "action_data": action_data
        }

    def get_proactive_alert(self, session_state: Dict) -> Optional[str]:
        """
        Generate proactive alerts based on current conditions
        
        Args:
            session_state: Current session state with analysis data
            
        Returns:
            Alert message if conditions warrant, None otherwise
        """
        alerts = []
        
        # Check for anomalies in analysis
        if session_state.get("analysis_done"):
            traffic_type = session_state.get("traffic_type", "")
            vehicle_count = session_state.get("vehicle_count", 0)
            
            if traffic_type in ["Accident", "Fire"]:
                alerts.append(f"🚨 **ALERT:** {traffic_type} detected in your analyzed image! Consider alternate routes immediately.")
            
            elif traffic_type == "Heavy Traffic" and vehicle_count > 100:
                alerts.append(f"⚠️ **Traffic Advisory:** High congestion detected ({vehicle_count} vehicles). Estimated delay: {session_state.get('clear_time', 20)} minutes.")
        
        # Check predictions for user's routes
        if session_state.get("route_dest"):
            # Simulate prediction alert
            hour = datetime.now().hour
            if 7 <= hour <= 8 or 16 <= hour <= 17:
                alerts.append("📊 **Prediction:** Based on current trends, your route may experience increased congestion in 15-20 minutes.")
        
        return alerts[0] if alerts else None

    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []


# Singleton instance
_chatbot_instance = None
_current_api_key = None

def get_chatbot(api_key: str = "AIzaSyDYXCcP_myiqq6dI0UYsBN8NQx23dzqrBM") -> TrafficChatbot:
    """Get or create chatbot instance"""
    global _chatbot_instance, _current_api_key
    # Reset instance if API key changed or instance doesn't exist
    if _chatbot_instance is None or _current_api_key != api_key:
        _chatbot_instance = TrafficChatbot(api_key)
        _current_api_key = api_key
    return _chatbot_instance
