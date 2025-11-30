import streamlit as st
import pandas as pd
from core.finance_queries import get_categories, get_accounts, add_investment, get_investments
from core.navigation import setup_navigation

setup_navigation()

st.title("📈 Investments")

# Fetch dropdown data
categories_df = get_categories("investment")
accounts_df = get_accounts()

if categories_df.empty or accounts_df.empty:
    st.warning("⚠️ Please configure Categories (Type: Investment) and Accounts in 'Settings' first.")
else:
    with st.expander("➕ Add Investment Transaction", expanded=True):
        with st.form("add_inv_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date")
                action = st.selectbox("Action", ["buy", "sell"])
                instrument = st.text_input("Instrument Name (e.g. S&P 500)")
                inv_type = st.selectbox("Type", ["equity", "crypto", "mutual_fund", "etf", "fd", "gold"])
                
            with col2:
                col_amt, col_curr = st.columns([2, 1])
                with col_amt:
                    amount = st.number_input("Total Amount", min_value=0.01, step=0.01)
                with col_curr:
                    currency = st.selectbox("Currency", ["EUR", "USD", "INR", "GBP"])
                
                units = st.number_input("Units", min_value=0.0, step=0.001)
                price = st.number_input("Price per Unit", min_value=0.0, step=0.01)
                account = st.selectbox("Account", accounts_df['name'])
                category = st.selectbox("Category", categories_df['name'])

            submitted = st.form_submit_button("Record Transaction")
            if submitted:
                cat_id = int(categories_df[categories_df['name'] == category].iloc[0]['id'])
                acc_id = int(accounts_df[accounts_df['name'] == account].iloc[0]['id'])
                
                res = add_investment(date, amount, instrument, inv_type, action, acc_id, cat_id, units, price, currency)
                if res:
                    st.success("Investment recorded!")
                    st.rerun()

# Portfolio Overview
st.subheader("💼 Portfolio")
inv_data = get_investments()
if not inv_data.empty:
    # Hide technical columns
    display_cols = [c for c in inv_data.columns if c not in ['id', 'user_id', 'created_at', 'category_id', 'account_id']]
    st.dataframe(inv_data[display_cols], use_container_width=True)
else:
    st.info("No investments recorded.")
