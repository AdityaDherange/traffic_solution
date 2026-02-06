"""
Traffic Analysis Component
Image upload and traffic analysis interface
"""
import streamlit as st
from PIL import Image
from backend.models import predict_traffic, count_vehicles
from backend.services import estimate_clear_time, analyze_traffic_condition
from backend.utils import is_peak_hour, get_density_level, announce_voice


def analysis_page():
    """Render traffic analysis page"""
    st.markdown('<div class="header-banner"><h1>📸 Traffic Image Analysis</h1></div>', unsafe_allow_html=True)
    
    # Image Input Section
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 📤 Upload Image")
        uploaded = st.file_uploader(
            "Choose traffic image",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a traffic image for analysis"
        )
        if uploaded:
            image = Image.open(uploaded)
            st.session_state.image = image
            st.image(image, caption="Uploaded Image", use_container_width=True)
    
    with c2:
        st.markdown("### 📷 Live Camera")
        camera = st.camera_input("Capture from camera")
        if camera:
            image = Image.open(camera)
            st.session_state.image = image
            st.image(image, caption="Camera Capture", use_container_width=True)
    
    # Analysis Section
    if st.session_state.image:
        st.markdown("---")
        
        # Weather and analysis button
        col1, col2 = st.columns([2, 1])
        
        with col1:
            weather = st.selectbox(
                "Current Weather Condition",
                ["Clear", "Rain", "Fog", "Snow"],
                key="weather_select_analysis",
                help="Select current weather to improve time estimation"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            analyze_btn = st.button("🔍 Analyze Traffic", type="primary", use_container_width=True)
        
        if analyze_btn:
            with st.spinner("🤖 Analyzing traffic image..."):
                # Predict traffic type
                traffic_type, confidence = predict_traffic(st.session_state.image)
                
                # Count vehicles
                vehicle_count = count_vehicles(st.session_state.image)
                
                # Check peak hour
                peak, _ = is_peak_hour()
                
                # Estimate clear time
                clear_time = estimate_clear_time(vehicle_count, traffic_type, peak, weather)
                
                # Store results in session
                st.session_state.traffic_type = traffic_type
                st.session_state.confidence = confidence
                st.session_state.vehicle_count = vehicle_count
                st.session_state.clear_time = clear_time
                st.session_state.analysis_done = True
                
                # Voice announcement
                announce_voice(
                    f"Traffic analysis complete. {traffic_type} detected with {int(confidence*100)} percent confidence.",
                    st.session_state.voice_enabled
                )
                
                st.success("✅ Analysis Complete!")
    
    # Display Results
    if st.session_state.analysis_done:
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        
        # Get comprehensive analysis
        analysis = analyze_traffic_condition(
            st.session_state.traffic_type,
            st.session_state.vehicle_count,
            st.session_state.confidence
        )
        
        # Critical Alert
        if analysis["is_critical"]:
            st.markdown(
                f'<div class="alert-critical">🚨 EMERGENCY: {st.session_state.traffic_type.upper()} DETECTED!</div>',
                unsafe_allow_html=True
            )
        elif analysis["is_heavy"]:
            st.markdown(
                '<div class="alert-critical">⚠️ HEAVY TRAFFIC AHEAD!</div>',
                unsafe_allow_html=True
            )
        
        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        
        confidence_color = "green" if st.session_state.confidence > 0.85 else "orange"
        c1.markdown(
            f'<div class="metric-box"><h3>🎯 Confidence</h3>'
            f'<h2 style="color: {confidence_color};">{st.session_state.confidence*100:.1f}%</h2></div>',
            unsafe_allow_html=True
        )
        
        c2.markdown(
            f'<div class="metric-box"><h3>🚗 Vehicles</h3>'
            f'<h2>{st.session_state.vehicle_count}</h2></div>',
            unsafe_allow_html=True
        )
        
        density, d_color = get_density_level(st.session_state.vehicle_count)
        c3.markdown(
            f'<div class="metric-box"><h3>📊 Density</h3>'
            f'<h2 style="color: {d_color};">{density}</h2></div>',
            unsafe_allow_html=True
        )
        
        c4.markdown(
            f'<div class="metric-box"><h3>⏱️ Clear Time</h3>'
            f'<h2>{st.session_state.clear_time} min</h2></div>',
            unsafe_allow_html=True
        )
        
        # Detailed Analysis
        st.markdown("### 🚦 Traffic Condition")
        
        if analysis["is_critical"]:
            st.markdown(
                f'<div class="danger-box">🚨 <strong>{st.session_state.traffic_type}</strong> - '
                f'AVOID THIS ROUTE immediately! Emergency services may be required.</div>',
                unsafe_allow_html=True
            )
        elif analysis["is_heavy"]:
            st.markdown(
                f'<div class="warning-box">⚠️ <strong>{st.session_state.traffic_type}</strong> - '
                f'Consider taking an alternate route to avoid delays.</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="success-box">✅ <strong>{st.session_state.traffic_type}</strong> - '
                f'Safe to proceed. No major issues detected.</div>',
                unsafe_allow_html=True
            )
        
        # Recommendation
        st.markdown("### 💡 Recommendation")
        st.info(analysis["recommendation"])
        
        # Action Buttons
        if analysis["is_critical"] or analysis["is_heavy"]:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗺️ Find Alternate Route", use_container_width=True):
                    st.session_state.page = 'route'
                    st.rerun()
            with col2:
                if st.button("🔄 Analyze Another Image", use_container_width=True):
                    st.session_state.analysis_done = False
                    st.session_state.image = None
                    st.rerun()
        else:
            if st.button("🔄 Analyze Another Image", use_container_width=True):
                st.session_state.analysis_done = False
                st.session_state.image = None
                st.rerun()
