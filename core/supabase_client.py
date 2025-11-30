import streamlit as st
from supabase import create_client, Client

def init_supabase() -> Client:
    """Initialize Supabase client using secrets."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        return None

def get_authenticated_client() -> Client:
    """Get a Supabase client authenticated with the current user's token."""
    client = init_supabase()
    if 'access_token' in st.session_state:
        client.postgrest.auth(st.session_state['access_token'])
    return client
