import streamlit as st
from utils.database import get_db_connection
from modules.authentication import hash_password

def render_profile(user):
    st.markdown("<h2 style='color: #2e7d32;'>User Profile 👤</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Profile Information")
        st.write(f"**Full Name:** {user['full_name']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Role:** {user['role']}")
        st.write(f"**Joined:** {user['created_at']}")
        
    with col2:
        st.subheader("Update Profile")
        with st.form("update_profile_form"):
            new_name = st.text_input("New Full Name", value=user['full_name'])
            new_password = st.text_input("New Password", type="password", help="Leave blank if you do not want to change it.")
            submit = st.form_submit_button("Update")
            
            if submit:
                conn = get_db_connection()
                c = conn.cursor()
                try:
                    if new_password:
                        pwd_hash = hash_password(new_password)
                        c.execute("UPDATE users SET full_name=?, password_hash=? WHERE id=?", (new_name, pwd_hash, user['id']))
                    else:
                        c.execute("UPDATE users SET full_name=? WHERE id=?", (new_name, user['id']))
                    
                    conn.commit()
                    
                    # Update session state user
                    user['full_name'] = new_name
                    st.session_state['user'] = user
                    
                    st.success("Profile updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating profile: {e}")
                finally:
                    conn.close()
