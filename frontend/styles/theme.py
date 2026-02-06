"""
Theme and Styling
Custom CSS for the application
"""
import streamlit as st


def apply_theme():
    """Apply custom theme and styling"""
    
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
        /* Main container */
        .main {{
            background-color: {bg};
            color: {text};
        }}
        
        /* Buttons */
        .stButton>button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 28px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
        }}
        
        .stButton>button:hover {{
            opacity: 0.85;
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        /* Header banner */
        .header-banner {{
            background: linear-gradient(90deg, #00d2ff 0%, #3a47d5 100%);
            padding: 35px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 8px 20px rgba(0, 210, 255, 0.3);
        }}
        
        .header-banner h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        
        .header-banner p {{
            margin: 10px 0 0 0;
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        /* Metric boxes */
        .metric-box {{
            background: {card};
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 4px solid {accent};
            margin: 10px 0;
            min-height: 120px;
            transition: transform 0.2s;
        }}
        
        .metric-box:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        }}
        
        .metric-box h3 {{
            color: {metric_label} !important;
            font-size: 14px !important;
            margin-bottom: 10px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric-box h2 {{
            color: {metric_text} !important;
            font-size: 28px !important;
            margin-top: 10px !important;
            font-weight: bold;
        }}
        
        /* Alert boxes */
        .alert-critical {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            margin: 20px 0;
            animation: pulse 2s infinite;
            box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.03); }}
        }}
        
        /* Status boxes */
        .success-box {{
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
            margin: 10px 0;
        }}
        
        .warning-box {{
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin: 10px 0;
        }}
        
        .danger-box {{
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #dc3545;
            margin: 10px 0;
        }}
        
        .info-box {{
            background: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #17a2b8;
            margin: 10px 0;
        }}
        
        /* Input fields */
        .stTextInput>div>div>input {{
            border-radius: 8px;
            border: 2px solid {accent};
        }}
        
        .stSelectbox>div>div>select {{
            border-radius: 8px;
            border: 2px solid {accent};
        }}
        
        /* File uploader */
        .stFileUploader>div {{
            border-radius: 8px;
            border: 2px dashed {accent};
            padding: 20px;
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background: {card};
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background: {card};
            border-radius: 8px;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }}
        
        /* Camera input */
        .stCameraInput>div {{
            border-radius: 8px;
        }}
        
        /* Metric styling */
        [data-testid="stMetricValue"] {{
            font-size: 24px;
            font-weight: bold;
        }}
        
        /* Links */
        a {{
            color: {accent};
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
    </style>
    """, unsafe_allow_html=True)
