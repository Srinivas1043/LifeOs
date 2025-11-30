import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client using secrets."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        return None
