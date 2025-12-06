import streamlit as st
import pandas as pd
from core.supabase_client import init_supabase
from core.navigation import setup_navigation_with_context

setup_navigation_with_context("System")
supabase = init_supabase()

st.title("🛡️ Admin Dashboard")

# Security Check (Simple Email Check for now)
# In a real app, you'd check a 'role' in a 'profiles' table
admin_email = "admin@lifeos.com" # Replace with your email after signup
user_email = st.session_state.get('user', {}).email if 'user' in st.session_state else ""

if user_email != admin_email:
    st.warning(f"Access Denied. You are logged in as {user_email}, but this page requires Admin privileges.")
    st.info(f"To test this, sign up as '{admin_email}' or change the code in `pages/admin.py`.")
    st.stop()

st.success(f"Welcome, Admin ({user_email})")

# --- System Stats ---
st.subheader("System Statistics")
col1, col2, col3 = st.columns(3)

# Note: With RLS, normal queries only return YOUR data. 
# To get global stats, you need a Postgres Function with SECURITY DEFINER 
# or a Service Role Key (not safe in client).
# For now, we show what YOU can see (which is everything if you are the only user, or just your data).

try:
    # Mocking global stats for demonstration as we can't bypass RLS easily here without SQL functions
    col1.metric("Total Users", "1 (You)") 
    col2.metric("System Health", "Healthy", "100%")
    col3.metric("Database Connection", "Active")
    
    st.divider()
    
    st.subheader("User Management")
    st.info("User management requires a 'profiles' table or Supabase Admin API access.")
    
    # Example of what you would do:
    # users = supabase.table("profiles").select("*").execute()
    # st.dataframe(users.data)

except Exception as e:
    st.error(f"Error loading admin data: {e}")
