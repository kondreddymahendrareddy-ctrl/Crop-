import streamlit as st
import pandas as pd
from utils.database import get_db_connection
import plotly.graph_objects as go

def fetch_user_history(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM analysis_history WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_history_record(record_id, user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM analysis_history WHERE id=? AND user_id=?", (record_id, user_id))
    conn.commit()
    conn.close()

def render_history(user):
    st.markdown("<h2 style='color: #2e7d32;'>Analysis History 📜</h2>", unsafe_allow_html=True)
    
    history_data = fetch_user_history(user['id'])
    
    if not history_data:
        st.info("No analysis history found. Run a Crop Recommendation to get started.")
        return
        
    df = pd.DataFrame(history_data)
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    st.subheader("Your Past Analyses")
    
    display_df = df[['id', 'created_at', 'location', 'recommended_crop', 'prediction_confidence']].copy()
    display_df.rename(columns={
        'id': 'ID',
        'created_at': 'Date',
        'location': 'Location',
        'recommended_crop': 'Recommended Crop',
        'prediction_confidence': 'Confidence'
    }, inplace=True)
    
    display_df['Recommended Crop'] = display_df['Recommended Crop'].str.capitalize()
    display_df['Confidence'] = (display_df['Confidence'] * 100).map('{:.1f}%'.format)
    
    st.dataframe(display_df, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Compare Analyses")
    if len(df) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            id1 = st.selectbox("Select first analysis (ID)", df['id'].tolist(), key='cmp1')
        with col2:
            id2 = st.selectbox("Select second analysis (ID)", df['id'].tolist(), index=1, key='cmp2')
            
        if id1 and id2:
            rec1 = df[df['id'] == id1].iloc[0]
            rec2 = df[df['id'] == id2].iloc[0]
            
            categories = ['Nitrogen', 'Phosphorus', 'Potassium', 'pH']
            val1 = [rec1['nitrogen'], rec1['phosphorus'], rec1['potassium'], rec1['ph']]
            val2 = [rec2['nitrogen'], rec2['phosphorus'], rec2['potassium'], rec2['ph']]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name=f"Analysis {id1} ({rec1['created_at']})", x=categories, y=val1))
            fig.add_trace(go.Bar(name=f"Analysis {id2} ({rec2['created_at']})", x=categories, y=val2))
            fig.update_layout(title="NPK & pH Comparison", barmode='group')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show crop changes
            c1, c2 = st.columns(2)
            c1.info(f"**Analysis {id1} Crop:** {rec1['recommended_crop'].capitalize()}")
            c2.info(f"**Analysis {id2} Crop:** {rec2['recommended_crop'].capitalize()}")
            
    else:
        st.info("You need at least 2 analyses to use the comparison feature.")
        
    st.markdown("---")
    st.subheader("Manage History")
    del_id = st.selectbox("Select analysis ID to delete", df['id'].tolist())
    if st.button("Delete Record", type="primary"):
        delete_history_record(del_id, user['id'])
        st.success(f"Record {del_id} deleted successfully.")
        st.rerun()
