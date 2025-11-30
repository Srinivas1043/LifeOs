import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from core.finance_queries import get_expenses, get_income
from core.navigation import setup_navigation

setup_navigation()

st.title("📅 Monthly Report")

# --- Currency Config ---
display_currency = st.session_state.get('currency', 'EUR')
conversion_rate = st.session_state.get('conversion_rate', 1.0)
if conversion_rate == 0: conversion_rate = 1.0

# --- Date Selection ---
today = datetime.date.today()
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Year", range(today.year, today.year - 5, -1))
with col2:
    selected_month = st.selectbox("Month", range(1, 13), index=today.month - 1)

# --- Data Loading ---
expenses_df = get_expenses()
income_df = get_income()

# Filter Data
start_date = datetime.date(selected_year, selected_month, 1)
if selected_month == 12:
    end_date = datetime.date(selected_year + 1, 1, 1)
else:
    end_date = datetime.date(selected_year, selected_month + 1, 1)

filtered_expenses = pd.DataFrame()
filtered_income = pd.DataFrame()

if not expenses_df.empty:
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    filtered_expenses = expenses_df[(expenses_df['date'].dt.date >= start_date) & (expenses_df['date'].dt.date < end_date)]

if not income_df.empty:
    income_df['date'] = pd.to_datetime(income_df['date'])
    filtered_income = income_df[(income_df['date'].dt.date >= start_date) & (income_df['date'].dt.date < end_date)]

# --- Aggregates ---
total_income_eur = 0
total_expenses_eur = 0

if not filtered_expenses.empty:
    filtered_expenses['amount_eur'] = filtered_expenses.get('amount_eur', filtered_expenses['amount']).fillna(filtered_expenses['amount'])
    total_expenses_eur = filtered_expenses['amount_eur'].sum()

if not filtered_income.empty:
    filtered_income['amount_eur'] = filtered_income.get('amount_eur', filtered_income['amount']).fillna(filtered_income['amount'])
    total_income_eur = filtered_income['amount_eur'].sum()

net_savings_eur = total_income_eur - total_expenses_eur

# Convert to display currency
total_income = total_income_eur / conversion_rate
total_expenses = total_expenses_eur / conversion_rate
net_savings = net_savings_eur / conversion_rate

# --- Display Overview ---
st.header(f"Overview for {datetime.date(selected_year, selected_month, 1).strftime('%B %Y')}")

c1, c2, c3 = st.columns(3)
c1.metric("Income", f"{display_currency} {total_income:,.2f}")
c2.metric("Expenses", f"{display_currency} {total_expenses:,.2f}")
c3.metric("Net Savings", f"{display_currency} {net_savings:,.2f}", delta=f"{((net_savings/total_income)*100) if total_income > 0 else 0:.1f}% Rate")

st.divider()

# --- Visuals ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Expenses by Category")
    if not filtered_expenses.empty:
        filtered_expenses['amount_display'] = filtered_expenses['amount_eur'] / conversion_rate
        fig_cat = px.pie(filtered_expenses, values='amount_display', names='category', hole=0.4)
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No expenses this month.")

with col_right:
    st.subheader("Top Expenses")
    if not filtered_expenses.empty:
        top_expenses = filtered_expenses.nlargest(5, 'amount_eur')
        top_expenses['amount_display'] = top_expenses['amount_eur'] / conversion_rate
        
        for index, row in top_expenses.iterrows():
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{row['description']}**")
                    st.caption(f"{row['category']} • {row['date'].strftime('%Y-%m-%d')}")
                with c2:
                    st.markdown(f"**{display_currency} {row['amount_display']:,.2f}**")
                st.divider()
    else:
        st.info("No expenses this month.")
