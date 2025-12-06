import streamlit as st
import pandas as pd
from core.finance_queries import get_accounts, add_transfer
from core.navigation import setup_navigation_with_context
import datetime

setup_navigation_with_context("Finance")

st.title("💸 Fund Transfer")

# --- Fetch Accounts ---
accounts_df = get_accounts()

if not accounts_df.empty:
    accounts_list = accounts_df['name'].tolist()
    # Create a map of account name to full row data (id, currency)
    accounts_data = accounts_df.set_index('name').to_dict('index')
    
    with st.form("transfer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.date.today())
            amount = st.number_input("Amount (Source Currency)", min_value=0.01, step=10.0)
            
        with col2:
            source_name = st.selectbox("From Account", accounts_list)
            # Show all accounts to avoid confusion, validate on submit
            dest_name = st.selectbox("To Account", accounts_list, index=1 if len(accounts_list) > 1 else 0)
            
        # Currency Check
        source_curr = accounts_data[source_name].get('currency', 'EUR')
        dest_curr = accounts_data[dest_name].get('currency', 'EUR')
        
        dest_amount = None
        exchange_rate = 1.0
        
        if source_curr != dest_curr:
            st.divider()
            st.info(f"💱 Cross-Currency Transfer: {source_curr} ➡️ {dest_curr}")
            
            c_rate, c_dest = st.columns(2)
            with c_rate:
                # TODO: Fetch live rate if possible, for now default to 1.0 or user input
                exchange_rate = st.number_input(f"Exchange Rate (1 {source_curr} = ? {dest_curr})", min_value=0.000001, value=1.0, format="%.6f")
            
            with c_dest:
                estimated_dest = amount * exchange_rate
                dest_amount = st.number_input(f"Amount Received ({dest_curr})", min_value=0.01, value=float(estimated_dest), step=10.0)
                
            # Recalculate rate if dest_amount changes manually (approximate)
            if dest_amount > 0 and amount > 0:
                implied_rate = dest_amount / amount
                if abs(implied_rate - exchange_rate) > 0.0001:
                    st.caption(f"Implied Rate: 1 {source_curr} = {implied_rate:.6f} {dest_curr}")
                    exchange_rate = implied_rate

        notes = st.text_area("Notes (Optional)")
        
        submitted = st.form_submit_button("Confirm Transfer")
        
        if submitted:
            if source_name == dest_name:
                st.error("Source and Destination accounts cannot be the same.")
            else:
                source_id = accounts_data[source_name]['id']
                dest_id = accounts_data[dest_name]['id']
                
                # Call backend
                res = add_transfer(date, amount, int(source_id), int(dest_id), notes, dest_amount, exchange_rate)
                
                if res:
                    msg = f"Successfully transferred {amount} {source_curr} from {source_name} to {dest_name}"
                    if dest_amount:
                        msg += f" (Received {dest_amount} {dest_curr})"
                    st.success(msg + "!")
                    st.balloons()
                else:
                    st.error("Transfer failed. Please check the logs.")

    st.info("ℹ️ Transfers move money between accounts and do not affect your Income/Expenses (P&L).")

else:
    st.warning("No accounts found. Please add accounts in the System module first.")
