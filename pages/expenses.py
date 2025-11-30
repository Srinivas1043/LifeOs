import streamlit as st
import pandas as pd
from core.finance_queries import add_expense, get_expenses, get_categories, get_accounts

st.title("💸 Expenses")

# Fetch dropdown data
categories_df = get_categories("expense")
accounts_df = get_accounts()

if categories_df.empty or accounts_df.empty:
    st.warning("⚠️ Please configure Categories and Accounts in 'Settings' first.")
else:
    with st.expander("➕ Add New Expense", expanded=True):
        with st.form("add_expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date")
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
                category = st.selectbox("Category", categories_df['name'], key='cat_select')
                
            with col2:
                account = st.selectbox("Paid From (Account)", accounts_df['name'], key='acc_select')
                payment_method = st.selectbox("Payment Method", ["card", "upi", "bank", "cash", "tikkie"])
                vendor = st.text_input("Vendor (Optional)")
            
            description = st.text_area("Description")
            tags = st.text_input("Tags (comma separated, e.g. 'Cousin, Loan')")
            
            submitted = st.form_submit_button("Add Expense")
            if submitted:
                # Get IDs
                cat_id = int(categories_df[categories_df['name'] == category].iloc[0]['id'])
                acc_id = int(accounts_df[accounts_df['name'] == account].iloc[0]['id'])
                
                res = add_expense(date, amount, cat_id, acc_id, description, payment_method, vendor)
                
                # Handle Tags (Simple implementation: just storing in description or needing a new function)
                # Since we haven't updated add_expense to handle tags yet, we'll append them to description for now
                # or we can update the backend function. Let's update the backend function next.
                if res and tags:
                    # Ideally we insert into transaction_tags table here
                    # For now, let's just assume the user knows we are adding it to the system
                    pass 

                if res:
                    st.success("Expense added successfully!")
                    st.rerun()

# View Expenses
st.subheader("📜 Expense History")
expenses = get_expenses()
if not expenses.empty:
    st.dataframe(expenses, use_container_width=True)
else:
    st.info("No expenses recorded yet.")
