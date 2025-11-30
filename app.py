import streamlit as st
import pandas as pd
import plotly.express as px
from core.finance_queries import get_expenses, get_income, get_investments, get_accounts, get_exchange_rates
from core.navigation import setup_navigation

# Setup Navigation & Theme
setup_navigation()

st.title("💰 Financial Overview")

# --- Data Loading ---
with st.spinner("Loading financial data..."):
    expenses_df = get_expenses()
    income_df = get_income()
    investments_df = get_investments()
    accounts_df = get_accounts()
    rates = get_exchange_rates()

# --- Currency Config ---
# Get currency from session state (set in navigation)
display_currency = st.session_state.get('currency', 'EUR')
conversion_rate = st.session_state.get('conversion_rate', 1.0)
if conversion_rate == 0: conversion_rate = 1.0

# Calculate Metrics
# Use amount_eur if available, else fallback to amount (assuming EUR for legacy)
if not income_df.empty:
    income_df['amount_eur'] = income_df.get('amount_eur', income_df['amount']).fillna(income_df['amount'])
    total_income_eur = income_df['amount_eur'].sum()
else:
    total_income_eur = 0

if not expenses_df.empty:
    expenses_df['amount_eur'] = expenses_df.get('amount_eur', expenses_df['amount']).fillna(expenses_df['amount'])
    total_expenses_eur = expenses_df['amount_eur'].sum()
else:
    total_expenses_eur = 0

net_savings_eur = total_income_eur - total_expenses_eur

if not investments_df.empty:
    investments_df['amount_eur'] = investments_df.get('amount_eur', investments_df['amount']).fillna(investments_df['amount'])
    total_invested_eur = investments_df['amount_eur'].sum()
else:
    total_invested_eur = 0

# Account Balance (Already converted to EUR in previous step, let's refine that loop)
total_balance_eur = 0
if not accounts_df.empty:
    for index, row in accounts_df.iterrows():
        currency = row.get('currency', 'EUR')
        balance = row['balance']
        rate = rates.get(currency, 1.0)
        total_balance_eur += balance * rate

# --- Convert to Display Currency ---
total_income = total_income_eur / conversion_rate
total_expenses = total_expenses_eur / conversion_rate
net_savings = net_savings_eur / conversion_rate
total_invested = total_invested_eur / conversion_rate
total_balance = total_balance_eur / conversion_rate

# Display Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label=f"Total Balance ({display_currency})", value=f"{total_balance:,.2f}")

with col2:
    st.metric(label=f"Net Savings ({display_currency})", value=f"{net_savings:,.2f}", delta=f"{((net_savings/total_income)*100) if total_income > 0 else 0:.1f}% Rate")

with col3:
    st.metric(label=f"Total Invested ({display_currency})", value=f"{total_invested:,.2f}")

with col4:
    st.metric(label=f"Monthly Spend ({display_currency})", value=f"{total_expenses:,.2f}")

# --- Visualizations ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(f"Spending by Category ({display_currency})")
    if not expenses_df.empty:
        # Convert individual rows for the chart
        expenses_df['amount_display'] = expenses_df['amount_eur'] / conversion_rate
        fig_exp = px.pie(expenses_df, values='amount_display', names='category', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_exp, use_container_width=True)
    else:
        st.info("No expense data available.")

with col_right:
    st.subheader("My Accounts")
    if not accounts_df.empty:
        for index, row in accounts_df.iterrows():
            # Convert balance
            currency = row.get('currency', 'EUR')
            balance = row['balance']
            rate = rates.get(currency, 1.0)
            balance_eur = balance * rate
            balance_display = balance_eur / conversion_rate
            
            with st.container():
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"{row['type']}")
                with c2:
                    st.markdown(f"**{display_currency} {balance_display:,.2f}**")
                st.divider()
    else:
        st.info("No accounts configured.")

# --- Recent Transactions ---
st.subheader("Recent Activity")
if not expenses_df.empty:
    recent = expenses_df.head(5).copy()
    recent['amount_display'] = recent['amount_eur'] / conversion_rate
    
    for index, row in recent.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.markdown(f"**{row['description']}**")
                st.caption(f"{row['category']} • {row['date']}")
            with c2:
                st.text(row['account'])
            with c3:
                st.markdown(f"**{display_currency} {row['amount_display']:,.2f}**")
            st.divider()
else:
    st.text("No recent transactions.")
