import streamlit as st
import bcrypt as _bcrypt  # raw bcrypt library — NOT passlib
import re
from utils.database import get_db_connection


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    return True, ""


def hash_password(password: str) -> str:
    """Hash a password using bcrypt. Always encodes to bytes first."""
    pw_bytes = password.encode('utf-8')
    salt = _bcrypt.gensalt()
    hashed = _bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    pw_bytes = password.encode('utf-8')
    hash_bytes = hashed.encode('utf-8')
    return _bcrypt.checkpw(pw_bytes, hash_bytes)


def create_user(full_name, email, password, role='USER'):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            return False, "Email already exists."

        password_hash = hash_password(password)
        c.execute(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (full_name, email, password_hash, role)
        )
        conn.commit()
        return True, "User registered successfully."
    except Exception as e:
        return False, f"Registration failed: {e}"
    finally:
        conn.close()


def authenticate_user(email, password):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        if user and verify_password(password, user['password_hash']):
            return True, dict(user)
        return False, "Invalid email or password."
    except Exception as e:
        return False, f"Login error: {e}"
    finally:
        conn.close()


def login_ui():
    st.subheader("Login to your account")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                success, result = authenticate_user(email, password)
                if success:
                    st.session_state['user'] = result
                    st.session_state['logged_in'] = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error(result)


def signup_ui():
    st.subheader("Create a new account")
    with st.form("signup_form"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")

        if submit:
            if not full_name or not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                is_strong, msg = is_strong_password(password)
                if not is_strong:
                    st.error(msg)
                else:
                    success, msg = create_user(full_name, email, password)
                    if success:
                        st.success("Account created! You can now login.")
                    else:
                        st.error(msg)


def logout():
    st.session_state['user'] = None
    st.session_state['logged_in'] = False
    st.rerun()
