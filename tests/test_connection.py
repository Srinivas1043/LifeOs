import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.supabase_client import init_supabase
import pandas as pd

# Mock secrets for local testing if not running via streamlit run
if not st.secrets:
    try:
        import toml
        secrets = toml.load(".streamlit/secrets.toml")
        st.secrets = secrets
    except:
        print("Could not load secrets.")

def test_connection():
    supabase = init_supabase()
    if not supabase:
        print("Failed to initialize Supabase client.")
        return

    print("Successfully initialized Supabase client.")

    # Test fetching accounts
    try:
        response = supabase.table("accounts").select("*").limit(1).execute()
        print("Accounts table accessible.")
        print(f"Data: {response.data}")
    except Exception as e:
        print(f"Error accessing accounts table: {e}")

    # Test fetching categories
    try:
        response = supabase.table("categories").select("*").limit(1).execute()
        print("Categories table accessible.")
        print(f"Data: {response.data}")
    except Exception as e:
        print(f"Error accessing categories table: {e}")

if __name__ == "__main__":
    test_connection()
