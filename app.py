import streamlit as st
import os
from modules.authentication import login_ui, signup_ui, logout
from modules.dashboard import render_home
from modules.crop_recommendation import render_crop_recommendation
from modules.soil_diagnosis import render_soil_diagnosis
from modules.fertilizer_guidance import render_fertilizer_guidance
from modules.history import render_history
from modules.reports import render_reports
from modules.admin import render_admin
from modules.profile import render_profile

# Page config
st.set_page_config(
    page_title="Intelligent Crop System",
    page_icon="🌱",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "Home"

# Load Custom CSS
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    load_css('assets/style.css')
    
    if not st.session_state['logged_in']:
        # Entry Page
        st.markdown("<h1 style='text-align: center; color: #2e7d32;'>Intelligent Crop Recommendation System</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #558b2f;'>Smart Soil Analysis • Crop Prediction • Fertilizer Guidance</h3>", unsafe_allow_html=True)
        st.write("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            with tab1:
                login_ui()
            with tab2:
                signup_ui()
    else:
        # Dashboard routing
        user = st.session_state['user']
        
        st.sidebar.title(f"Welcome, {user['full_name']}!")
        st.sidebar.write(f"Role: {user['role']}")
        st.sidebar.write("---")
        
        if user['role'] == 'ADMIN':
            menu = ["Admin Dashboard", "Logout"]
        else:
            menu = ["Home", "Crop Recommendation", "Soil Analysis", "Fertilizer Guidance", "History", "Reports", "Profile", "Logout"]
            
        choice = st.sidebar.radio("Navigation", menu, index=menu.index(st.session_state.get('current_page', 'Home')))
        st.session_state['current_page'] = choice
        
        if choice == "Logout":
            logout()
        elif choice == "Home":
            render_home(user)
        elif choice == "Crop Recommendation":
            render_crop_recommendation(user)
        elif choice == "Soil Analysis":
            render_soil_diagnosis(user)
        elif choice == "Fertilizer Guidance":
            render_fertilizer_guidance(user)
        elif choice == "History":
            render_history(user)
        elif choice == "Reports":
            render_reports(user)
        elif choice == "Admin Dashboard":
            render_admin()
        elif choice == "Profile":
            render_profile(user)
        else:
            st.title(choice)
            st.info("Module under construction.")

if __name__ == '__main__':
    main()
