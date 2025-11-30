import streamlit as st
import pandas as pd
from core.finance_queries import add_account, add_category, get_accounts, get_categories
from core.supabase_client import init_supabase
from core.navigation import setup_navigation

setup_navigation()
supabase = init_supabase()

st.title("⚙️ Settings")

tab1, tab2 = st.tabs(["Accounts", "Categories"])

with tab1:
    st.header("Manage Accounts")
    
    # Add Account Form
    with st.form("add_account_form"):
        st.subheader("Add New Account")
        name = st.text_input("Account Name (e.g., ABN AMRO Current, ABN AMRO Savings)")
        type_ = st.selectbox("Type", ["bank", "credit_card", "wallet", "cash", "investment"])
        balance = st.number_input("Initial Balance", min_value=0.0, step=0.01)
        currency = st.selectbox("Currency", ["EUR", "USD", "INR", "GBP"], index=0)
        
        submitted = st.form_submit_button("Add Account")
        if submitted:
            if name:
                try:
                    data = {"name": name, "type": type_, "balance": balance, "currency": currency}
                    supabase.table("accounts").insert(data).execute()
                    st.success(f"Account '{name}' added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter a name.")

    # List Accounts
    st.subheader("Existing Accounts")
    try:
        response = supabase.table("accounts").select("*").execute()
        if response.data:
            st.dataframe(pd.DataFrame(response.data))
        else:
            st.info("No accounts found.")
    except Exception as e:
        st.error(f"Error fetching accounts: {e}")

with tab2:
    st.header("Manage Categories")
    
    # Add Category Form
    with st.form("add_category_form"):
        st.subheader("Add New Category")
        cat_name = st.text_input("Category Name (e.g., Groceries)")
        cat_type = st.selectbox("Type", ["expense", "income", "investment", "saving"])
        
        cat_submitted = st.form_submit_button("Add Category")
        if cat_submitted:
            if cat_name:
                try:
                    data = {"name": cat_name, "type": cat_type}
                    supabase.table("categories").insert(data).execute()
                    st.success(f"Category '{cat_name}' added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter a name.")

    # List Categories
    st.subheader("Existing Categories")
    try:
        response = supabase.table("categories").select("*").execute()
        if response.data:
            st.dataframe(pd.DataFrame(response.data))
        else:
            st.info("No categories found.")
    except Exception as e:
        st.error(f"Error fetching categories: {e}")
