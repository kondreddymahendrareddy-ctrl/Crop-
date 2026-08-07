import streamlit as st
from utils.database import get_db_connection

def get_dashboard_metrics(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM analysis_history WHERE user_id=?", (user_id,))
    total_analyses = c.fetchone()[0]
    
    c.execute("SELECT recommended_crop, created_at FROM analysis_history WHERE user_id=? ORDER BY created_at DESC LIMIT 1", (user_id,))
    last_analysis = c.fetchone()
    conn.close()
    
    last_crop = last_analysis['recommended_crop'] if last_analysis else "N/A"
    last_date = last_analysis['created_at'] if last_analysis else "N/A"
    
    return total_analyses, last_crop, last_date

def render_home(user):
    st.markdown("<h2 style='color: #2e7d32;'>User Dashboard 🌱</h2>", unsafe_allow_html=True)
    st.write("Welcome to the Intelligent Crop System. Use the sidebar to navigate through the modules.")
    
    total_analyses, last_crop, last_date = get_dashboard_metrics(user['id'])
    
    st.markdown("### Your Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Analyses", total_analyses)
    with col2:
        st.metric("Last Recommended Crop", last_crop.capitalize() if last_crop != "N/A" else "N/A")
    with col3:
        st.metric("Latest Activity", last_date.split(" ")[0] if last_date != "N/A" else "N/A")
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🌱 Recommend Crop", use_container_width=True):
            st.session_state['current_page'] = "Crop Recommendation"
            st.rerun()
    with col2:
        if st.button("🧪 Analyze Soil", use_container_width=True):
            st.session_state['current_page'] = "Soil Analysis"
            st.rerun()
    with col3:
        if st.button("💧 Fertilizer Guidance", use_container_width=True):
            st.session_state['current_page'] = "Fertilizer Guidance"
            st.rerun()
    with col4:
        if st.button("📜 View History", use_container_width=True):
            st.session_state['current_page'] = "History"
            st.rerun()
            
    st.markdown("---")
    st.info("💡 **Tip:** Start by recommending a crop based on your soil and weather data, then check the detailed soil analysis to get actionable improvement advice.")
