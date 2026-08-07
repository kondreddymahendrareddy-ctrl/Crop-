import streamlit as st
import pandas as pd
from utils.database import get_db_connection
import plotly.express as px

def get_admin_metrics():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM analysis_history")
    total_analyses = c.fetchone()[0]
    
    c.execute("SELECT recommended_crop, COUNT(*) as count FROM analysis_history GROUP BY recommended_crop ORDER BY count DESC LIMIT 5")
    top_crops = c.fetchall()
    
    c.execute("""
        SELECT u.full_name, a.recommended_crop, a.created_at 
        FROM analysis_history a 
        JOIN users u ON a.user_id = u.id 
        ORDER BY a.created_at DESC LIMIT 10
    """)
    recent_analyses = c.fetchall()
    
    c.execute("SELECT recommended_crop, COUNT(*) as count FROM analysis_history GROUP BY recommended_crop")
    crop_dist = c.fetchall()
    
    conn.close()
    return total_users, total_analyses, top_crops, recent_analyses, crop_dist

def render_admin():
    st.markdown("<h2 style='color: #d32f2f;'>Admin Dashboard 📊</h2>", unsafe_allow_html=True)
    
    total_users, total_analyses, top_crops, recent_analyses, crop_dist = get_admin_metrics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registered Users", total_users)
    with col2:
        st.metric("Total Analyses Performed", total_analyses)
    with col3:
        top_crop_name = top_crops[0]['recommended_crop'].capitalize() if top_crops else "None"
        st.metric("Top Recommended Crop", top_crop_name)
        
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Crop Recommendation Distribution")
        if crop_dist:
            df_dist = pd.DataFrame([dict(row) for row in crop_dist])
            fig = px.pie(df_dist, values='count', names='recommended_crop', title="Crop Prediction Breakdown")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No prediction data available yet.")
            
    with col2:
        st.subheader("Model & Dataset Info")
        st.write("**Crop Dataset:** `Crop_recommendation.csv` (2200 records, 22 classes)")
        st.write("**Crop Model Performance:** Random Forest (Accuracy: ~99.5%)")
        st.write("**Fertilizer Dataset:** `MISSING`")
        st.write("**Fertilizer Model Performance:** `N/A (Using Heuristic Fallback)`")
        
        st.subheader("Most Recommended Crops")
        if top_crops:
            for row in top_crops:
                st.write(f"- **{row['recommended_crop'].capitalize()}**: {row['count']} times")
                
    st.markdown("---")
    st.subheader("Recent System Activity")
    if recent_analyses:
        df_recent = pd.DataFrame([dict(row) for row in recent_analyses])
        df_recent.rename(columns={
            'full_name': 'User Name',
            'recommended_crop': 'Recommended Crop',
            'created_at': 'Timestamp'
        }, inplace=True)
        st.dataframe(df_recent, hide_index=True, use_container_width=True)
    else:
        st.info("No recent activity.")
