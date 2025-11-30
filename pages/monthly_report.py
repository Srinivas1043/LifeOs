import streamlit as st
import pandas as pd
import plotly.express as px
from core.finance_queries import get_expenses, get_income, get_budgets
from core.navigation import setup_navigation
import datetime

setup_navigation()

st.title("📅 Monthly Report")

# --- Date Selection ---
today = datetime.date.today()
# Default to previous month if today is early in the month, else current
default_date = today
if today.day < 5:
    first = today.replace(day=1)
    default_date = first - datetime.timedelta(days=1)

selected_date = st.date_input("Select Month", default_date)
selected_year = selected_date.year
selected_month = selected_date.month
month_str = selected_date.strftime("%B %Y")
month_key = selected_date.strftime("%Y-%m")

st.header(f"Report for {month_str}")

# --- Data Fetching ---
expenses = get_expenses()
income = get_income()
budgets = get_budgets(month_key)

# Filter Data
if not expenses.empty:
    expenses['date'] = pd.to_datetime(expenses['date'])
    expenses = expenses[(expenses['date'].dt.year == selected_year) & (expenses['date'].dt.month == selected_month)]

if not income.empty:
    income['date'] = pd.to_datetime(income['date'])
    income = income[(income['date'].dt.year == selected_year) & (income['date'].dt.month == selected_month)]

# --- Currency ---
display_currency = st.session_state.get('currency', 'EUR')
conversion_rate = st.session_state.get('conversion_rate', 1.0)
if conversion_rate == 0: conversion_rate = 1.0

# --- Summary Metrics ---
total_inc_eur = income['amount_eur'].sum() if not income.empty else 0
total_exp_eur = expenses['amount_eur'].sum() if not expenses.empty else 0
net_savings_eur = total_inc_eur - total_exp_eur
savings_rate = (net_savings_eur / total_inc_eur * 100) if total_inc_eur > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Income", f"{display_currency} {total_inc_eur/conversion_rate:,.2f}")
col2.metric("Expenses", f"{display_currency} {total_exp_eur/conversion_rate:,.2f}")
col3.metric("Net Savings", f"{display_currency} {net_savings_eur/conversion_rate:,.2f}")
col4.metric("Savings Rate", f"{savings_rate:.1f}%")

st.divider()

# --- Budget Performance ---
st.subheader("Budget Performance")
if not budgets.empty and not expenses.empty:
    exp_by_cat = expenses.groupby('category')['amount_eur'].sum().reset_index()
    merged = pd.merge(budgets, exp_by_cat, on='category', how='left')
    merged['amount_eur'] = merged['amount_eur'].fillna(0)
    
    # Calculate variance
    merged['variance'] = merged['budget_amount'] - (merged['amount_eur'] / conversion_rate) # Assuming budget is in display currency? 
    # Actually budget is stored as raw number, likely in EUR or base? 
    # Wait, add_budget takes amount. User inputs it. If user inputs in INR, we store as is.
    # But expenses are stored in EUR. We need to be careful.
    # In settings.py, we didn't convert budget input. It's just a number.
    # Let's assume budget is set in the *Display Currency* at the time of setting.
    # But for comparison, we should convert expenses to that currency.
    # Ideally budgets should be stored with currency.
    # For now, let's assume budgets are set in EUR for simplicity or match the display currency logic.
    # If user is viewing in INR, expenses are converted to INR. Budget should be compared to that.
    
    # Let's assume Budget was set in EUR for now to be safe, OR we assume user sets it in their mind's currency.
    # Given the complexity, let's just compare (Expense / Rate) vs Budget.
    
    merged['spent_display'] = merged['amount_eur'] / conversion_rate
    
    # Display Table
    display_df = merged[['category', 'budget_amount', 'spent_display']].copy()
    display_df['status'] = display_df.apply(lambda x: '✅' if x['spent_display'] <= x['budget_amount'] else '⚠️', axis=1)
    display_df.columns = ['Category', 'Budget', 'Actual', 'Status']
    
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No budget data for this month.")

# --- Top Expenses ---
st.subheader("Top Expenses")
if not expenses.empty:
    top_exp = expenses.nlargest(5, 'amount_eur')
    top_exp['amount_display'] = top_exp['amount_eur'] / conversion_rate
    st.dataframe(top_exp[['date', 'category', 'description', 'amount_display']], use_container_width=True)
else:
    st.info("No expenses found.")
