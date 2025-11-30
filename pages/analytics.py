import streamlit as st
import pandas as pd
import plotly.express as px
from core.finance_queries import get_expenses, get_income
import datetime

st.title("📊 Analytics & P&L")

# --- Data Loading ---
expenses_df = get_expenses()
income_df = get_income()

# Ensure date columns are datetime
if not expenses_df.empty:
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
if not income_df.empty:
    income_df['date'] = pd.to_datetime(income_df['date'])

# --- Filters ---
st.sidebar.header("Filter Analysis")

# Date Range Filter
today = datetime.date.today()
start_of_year = datetime.date(today.year, 1, 1)

filter_type = st.sidebar.radio("Time Period", ["Year to Date", "Last 30 Days", "Quarterly", "Custom Range"])

start_date = start_of_year
end_date = today

if filter_type == "Year to Date":
    start_date = start_of_year
    end_date = today
elif filter_type == "Last 30 Days":
    start_date = today - datetime.timedelta(days=30)
    end_date = today
elif filter_type == "Quarterly":
    current_quarter = (today.month - 1) // 3 + 1
    q_start_month = 3 * current_quarter - 2
    start_date = datetime.date(today.year, q_start_month, 1)
    # End of quarter logic simplified (end of current month or today)
    end_date = today 
elif filter_type == "Custom Range":
    start_date = st.sidebar.date_input("Start Date", start_of_year)
    end_date = st.sidebar.date_input("End Date", today)

# Apply Filters
filtered_expenses = pd.DataFrame()
filtered_income = pd.DataFrame()

if not expenses_df.empty:
    filtered_expenses = expenses_df[(expenses_df['date'].dt.date >= start_date) & (expenses_df['date'].dt.date <= end_date)]

if not income_df.empty:
    filtered_income = income_df[(income_df['date'].dt.date >= start_date) & (income_df['date'].dt.date <= end_date)]

# --- P&L Statement ---
st.header(f"Profit & Loss ({start_date} to {end_date})")

total_income = filtered_income['amount'].sum() if not filtered_income.empty else 0
total_expenses = filtered_expenses['amount'].sum() if not filtered_expenses.empty else 0
net_profit = total_income - total_expenses

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"€{total_income:,.2f}", delta_color="normal")
col2.metric("Total Expenses", f"€{total_expenses:,.2f}", delta_color="inverse")
col3.metric("Net Profit / Loss", f"€{net_profit:,.2f}", delta=f"{net_profit:,.2f}")

st.divider()

tab1, tab2 = st.tabs(["Spending Analysis", "Income Analysis"])

with tab1:
    st.subheader("Spending Breakdown")
    if not filtered_expenses.empty:
        col1, col2 = st.columns(2)
        with col1:
            # Category Pie Chart
            fig_cat = px.pie(filtered_expenses, values='amount', names='category', title='Expenses by Category', hole=0.4)
            st.plotly_chart(fig_cat, use_container_width=True)
        
        with col2:
            # Payment Method Bar Chart
            fig_method = px.bar(filtered_expenses, x='payment_method', y='amount', title='Spending by Method', color='payment_method')
            st.plotly_chart(fig_method, use_container_width=True)
        
        # Time Series
        daily_spend = filtered_expenses.groupby('date')['amount'].sum().reset_index()
        fig_trend = px.area(daily_spend, x='date', y='amount', title='Daily Spending Trend', line_shape='spline')
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No expense data for this period.")

with tab2:
    st.subheader("Income Breakdown")
    if not filtered_income.empty:
        fig_inc = px.bar(filtered_income, x='source', y='amount', title='Income by Source', color='source')
        st.plotly_chart(fig_inc, use_container_width=True)
    else:
        st.info("No income data for this period.")
