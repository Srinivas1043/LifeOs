import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from core.finance_queries import get_categories, get_accounts, add_income, get_income
from core.navigation import setup_navigation_with_context

setup_navigation_with_context("Finance")

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
                col_amt, col_curr = st.columns([2, 1])
                with col_amt:
                    amount = st.number_input("Amount", min_value=0.01, step=0.01)
                with col_curr:
                    currency = st.selectbox("Currency", ["EUR", "USD", "INR", "GBP"])
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
                
                res = add_income(date, amount, cat_id, acc_id, source, currency, notes)
                if res:
                    st.success("Income added successfully!")
                    st.rerun()

# View Income
with st.expander("📊 History & Analysis", expanded=False):
    st.subheader("Income Analysis")
    income_data = get_income()
    
    # --- Currency Config ---
    display_currency = st.session_state.get('currency', 'EUR')
    conversion_rate = st.session_state.get('conversion_rate', 1.0)
    if conversion_rate == 0: conversion_rate = 1.0
    
    if not income_data.empty:
        # Pre-process
        income_data['date'] = pd.to_datetime(income_data['date'])
        income_data['month'] = income_data['date'].dt.month
        income_data['year'] = income_data['date'].dt.year
        income_data['amount_eur'] = income_data.get('amount_eur', income_data['amount']).fillna(income_data['amount'])
        
        # --- Filters ---
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            unique_years = sorted(income_data['year'].unique(), reverse=True)
            selected_year = st.selectbox("Year", unique_years)
            
        with col_f2:
            available_months = sorted(income_data[income_data['year'] == selected_year]['month'].unique())
            default_ix = len(available_months) - 1 if available_months else 0
            selected_month = st.selectbox("Month", available_months, index=default_ix, format_func=lambda x: datetime.date(1900, x, 1).strftime('%B'))
            
        with col_f3:
            categories = ["All"] + sorted(income_data['category'].unique().tolist())
            selected_category = st.selectbox("Category Filter", categories)
            
        # --- Apply Filters ---
        mask = (income_data['year'] == selected_year) & (income_data['month'] == selected_month)
        if selected_category != "All":
            mask = mask & (income_data['category'] == selected_category)
            
        filtered_df = income_data[mask].copy()
        
        if not filtered_df.empty:
            # --- Metrics ---
            total_income_eur = filtered_df['amount_eur'].sum()
            total_income_display = total_income_eur / conversion_rate
            
            m1, m2 = st.columns(2)
            m1.metric(f"Total Income ({display_currency})", f"{total_income_display:,.2f}")
            m2.metric("Transaction Count", len(filtered_df))
            
            st.divider()
            
            # --- Charts ---
            c1, c2 = st.columns(2)
            
            with c1:
                st.caption("Income Trend")
                daily_trend = filtered_df.groupby('date')['amount_eur'].sum().reset_index()
                daily_trend['amount_display'] = daily_trend['amount_eur'] / conversion_rate
                fig_trend = px.bar(daily_trend, x='date', y='amount_display', color_discrete_sequence=['#00CC96'])
                fig_trend.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_trend, use_container_width=True)
                
            with c2:
                st.caption("Category Split")
                cat_split = filtered_df.groupby('category')['amount_eur'].sum().reset_index()
                cat_split['amount_display'] = cat_split['amount_eur'] / conversion_rate
                fig_cat = px.pie(cat_split, values='amount_display', names='category', hole=0.4, color_discrete_sequence=px.colors.sequential.Emrld)
                fig_cat.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_cat, use_container_width=True)
                
            # --- Data Table ---
            st.subheader("Detailed Transactions")
            
            display_df = filtered_df[['date', 'category', 'source', 'amount_eur', 'account', 'notes']].copy()
            display_df['amount'] = display_df['amount_eur'] / conversion_rate
            display_df = display_df.drop(columns=['amount_eur'])
            display_df = display_df.rename(columns={
                'date': 'Date', 
                'category': 'Category', 
                'source': 'Source', 
                'amount': f'Amount ({display_currency})',
                'account': 'Account',
                'notes': 'Notes'
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
            st.info("No income found for this selection.")
    
    else:
        st.info("No income recorded yet.")
