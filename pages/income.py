import streamlit as st
import pandas as pd
from core.finance_queries import add_income, get_income, get_categories, get_accounts

st.title("💰 Income")

# Fetch dropdown data
categories_df = get_categories("income")
accounts_df = get_accounts()

if categories_df.empty or accounts_df.empty:
    st.warning("⚠️ Please configure Categories (Type: Income) and Accounts in 'Settings' first.")
else:
    with st.expander("➕ Add New Income", expanded=True):
        with st.form("add_income_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date")
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
                category = st.selectbox("Category", categories_df['name'], key='cat_select')
                
            with col2:
                account = st.selectbox("Deposit To (Account)", accounts_df['name'], key='acc_select')
                source = st.text_input("Source (e.g. Salary, Freelance)")
            
            notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("Add Income")
            if submitted:
                # Get IDs
                cat_id = int(categories_df[categories_df['name'] == category].iloc[0]['id'])
                acc_id = int(accounts_df[accounts_df['name'] == account].iloc[0]['id'])
                
                res = add_income(date, amount, cat_id, acc_id, source, notes)
                if res:
                    st.success("Income added successfully!")
                    st.rerun()

# View Income
st.subheader("📜 Income History")
income_data = get_income()
if not income_data.empty:
    st.dataframe(income_data, use_container_width=True)
else:
    st.info("No income recorded yet.")
