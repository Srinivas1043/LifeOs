import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from core.finance_queries import get_categories, get_accounts, add_expense, get_expenses
from core.navigation import setup_navigation_with_context

setup_navigation_with_context("Finance")

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
                col_amt, col_curr = st.columns([2, 1])
                with col_amt:
                    amount = st.number_input("Amount", min_value=0.01, step=0.01)
                with col_curr:
                    currency = st.selectbox("Currency", ["EUR", "USD", "INR", "GBP"])
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
                
                res = add_expense(date, amount, cat_id, acc_id, description, payment_method, currency, vendor)
                
                if res:
                    st.success("Expense added successfully!")
                    st.rerun()

# View Expenses
# View Expenses
with st.expander("📊 History & Analysis", expanded=False):
    st.subheader("Expense Analysis")
    expenses = get_expenses()
    
    # --- Currency Config ---
    display_currency = st.session_state.get('currency', 'EUR')
    conversion_rate = st.session_state.get('conversion_rate', 1.0)
    if conversion_rate == 0: conversion_rate = 1.0
    
    if not expenses.empty:
        # Pre-process
        expenses['date'] = pd.to_datetime(expenses['date'])
        expenses['month'] = expenses['date'].dt.month
        expenses['year'] = expenses['date'].dt.year
        expenses['amount_eur'] = expenses.get('amount_eur', expenses['amount']).fillna(expenses['amount'])
        
        # --- Filters ---
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            unique_years = sorted(expenses['year'].unique(), reverse=True)
            selected_year = st.selectbox("Year", unique_years)
            
        with col_f2:
            # Filter months available in selected year
            available_months = sorted(expenses[expenses['year'] == selected_year]['month'].unique())
            # Default to latest month
            default_ix = len(available_months) - 1 if available_months else 0
            selected_month = st.selectbox("Month", available_months, index=default_ix, format_func=lambda x: datetime.date(1900, x, 1).strftime('%B'))
            
        with col_f3:
            categories = ["All"] + sorted(expenses['category'].unique().tolist())
            selected_category = st.selectbox("Category Filter", categories)
            
        # --- Apply Filters ---
        mask = (expenses['year'] == selected_year) & (expenses['month'] == selected_month)
        if selected_category != "All":
            mask = mask & (expenses['category'] == selected_category)
            
        filtered_df = expenses[mask].copy()
        
        if not filtered_df.empty:
            # --- Metrics ---
            total_spend_eur = filtered_df['amount_eur'].sum()
            total_spend_display = total_spend_eur / conversion_rate
            
            # Daily Average
            days_in_month = pd.Period(f"{selected_year}-{selected_month}").days_in_month
            # If current month, use days passed so far for more accurate "current pace", or just standard days in month?
            # Let's use days in month for standard "budgeting" view, or max date in data?
            # Standard: Days in month
            daily_avg = total_spend_display / days_in_month
            
            m1, m2, m3 = st.columns(3)
            m1.metric(f"Total Spend ({display_currency})", f"{total_spend_display:,.2f}")
            m2.metric(f"Daily Average ({display_currency})", f"{daily_avg:,.2f}")
            m3.metric("Transaction Count", len(filtered_df))
            
            st.divider()
            
            # --- Charts ---
            c1, c2 = st.columns(2)
            
            with c1:
                st.caption("Daily Trend")
                daily_trend = filtered_df.groupby('date')['amount_eur'].sum().reset_index()
                daily_trend['amount_display'] = daily_trend['amount_eur'] / conversion_rate
                fig_trend = px.bar(daily_trend, x='date', y='amount_display', color_discrete_sequence=['#FF4B4B'])
                fig_trend.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_trend, use_container_width=True)
                
            with c2:
                st.caption("Category Split")
                cat_split = filtered_df.groupby('category')['amount_eur'].sum().reset_index()
                cat_split['amount_display'] = cat_split['amount_eur'] / conversion_rate
                fig_cat = px.pie(cat_split, values='amount_display', names='category', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                fig_cat.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_cat, use_container_width=True)
                
            # --- Data Table ---
            st.subheader("Detailed Transactions")
            
            # Prepare for display
            display_df = filtered_df[['date', 'category', 'description', 'amount_eur', 'account', 'payment_method', 'vendor']].copy()
            display_df['amount'] = display_df['amount_eur'] / conversion_rate
            display_df = display_df.drop(columns=['amount_eur'])
            display_df = display_df.rename(columns={
                'date': 'Date', 
                'category': 'Category', 
                'description': 'Description', 
                'amount': f'Amount ({display_currency})',
                'account': 'Account',
                'payment_method': 'Method',
                'vendor': 'Vendor'
            })
            
            st.dataframe(
                display_df.sort_values('Date', ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    f"Amount ({display_currency})": st.column_config.NumberColumn(format="%.2f")
                }
            )
            
        else:
            st.info("No expenses found for this selection.")
    
    else:
        st.info("No expenses recorded yet.")
