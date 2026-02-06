"""
Authentication Components
Login and Signup Pages
"""
import streamlit as st
from backend.config import config


def login_page():
    """Render login page"""
    st.markdown(
        f'<div class="header-banner"><h1>{config.APP_ICON} {config.APP_NAME}</h1>'
        '<p>AI-Powered Traffic Management & Route Optimization</p></div>',
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Login")
        username = st.text_input("Username", key="login_user", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Login", use_container_width=True):
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with c2:
            if st.button("📝 Sign Up", use_container_width=True):
                st.session_state.page = 'signup'
                st.rerun()
        
        # Demo credentials info
        with st.expander("ℹ️ Demo Credentials"):
            st.info("**Username:** demo\n\n**Password:** demo123")


def signup_page():
    """Render signup page"""
    st.markdown(
        f'<div class="header-banner"><h1>📝 Create Account</h1>'
        '<p>Join the Smart Traffic System</p></div>',
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Register")
        new_user = st.text_input("Username", key="signup_user", placeholder="Choose a username")
        new_pass = st.text_input("Password", type="password", key="signup_pass", placeholder="Choose a password")
        confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Confirm your password")
        
        # Password strength indicator
        if new_pass:
            strength = "Weak" if len(new_pass) < 6 else "Medium" if len(new_pass) < 10 else "Strong"
            color = "red" if strength == "Weak" else "orange" if strength == "Medium" else "green"
            st.markdown(f'<p style="color: {color};">Password Strength: {strength}</p>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Create Account", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("❌ Please fill all fields")
                elif len(new_pass) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif new_pass != confirm_pass:
                    st.error("❌ Passwords do not match")
                elif new_user in st.session_state.users:
                    st.error("❌ Username already exists")
                else:
                    st.session_state.users[new_user] = new_pass
                    st.success("✅ Account created successfully!")
                    st.session_state.page = 'login'
                    st.rerun()
        
        with c2:
            if st.button("⬅️ Back to Login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()
