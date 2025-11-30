import streamlit as st
from core.supabase_client import init_supabase
from core.navigation import setup_navigation
import time

# Setup basic config (no sidebar yet)
st.set_page_config(page_title="Life OS - Login", page_icon="🔐", layout="centered")

# Custom CSS for Login
st.markdown("""
<style>
    .stTextInput input {
        background-color: #0D1117;
        color: white;
    }
    div[data-testid="stForm"] {
        background-color: #161B22;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #30363D;
    }
</style>
""", unsafe_allow_html=True)

supabase = init_supabase()

st.title("🔐 Login to Life OS")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if st.session_state['authenticated']:
    st.success("You are already logged in!")
    time.sleep(1)
    st.switch_page("app.py")

tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary")
        
        if submitted:
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if response.user:
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = response.user
                    st.session_state['access_token'] = response.session.access_token
                    st.success("Login successful!")
                    time.sleep(1)
                    st.switch_page("app.py")
            except Exception as e:
                st.error(f"Login failed: {e}")

with tab2:
    st.markdown("### Create a new account")
    with st.form("signup_form"):
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        full_name = st.text_input("Full Name")
        signup_submitted = st.form_submit_button("Sign Up")
        
        if signup_submitted:
            if not new_email or not new_password or not full_name:
                st.error("Please fill in all fields.")
            else:
                try:
                    # Pass full_name in metadata for the trigger to use
                    response = supabase.auth.sign_up({
                        "email": new_email, 
                        "password": new_password,
                        "options": {
                            "data": {
                                "full_name": full_name
                            }
                        }
                    })
                    if response.user:
                        st.success("Signup successful! Please check your email to confirm.")
                        st.info("After confirming, switch to the Login tab.")
                except Exception as e:
                    st.error(f"Signup failed: {e}")
