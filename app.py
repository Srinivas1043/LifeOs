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

# Calculate Metrics
# Use amount_eur if available, else fallback to amount (assuming EUR for legacy)
if not income_df.empty:
    income_df['amount_eur'] = income_df.get('amount_eur', income_df['amount']).fillna(income_df['amount'])
    total_income = income_df['amount_eur'].sum()
else:
    total_income = 0

if not expenses_df.empty:
    expenses_df['amount_eur'] = expenses_df.get('amount_eur', expenses_df['amount']).fillna(expenses_df['amount'])
    total_expenses = expenses_df['amount_eur'].sum()
else:
    total_expenses = 0
net_savings = total_income - total_expenses

if not investments_df.empty:
    investments_df['amount_eur'] = investments_df.get('amount_eur', investments_df['amount']).fillna(investments_df['amount'])
    total_invested = investments_df['amount_eur'].sum()
else:
    total_invested = 0
current_investment_value = 0 # Placeholder for now, would need live data or manual update
if not investments_df.empty and 'current_value' in investments_df.columns:
     current_investment_value = investments_df['current_value'].sum()

total_balance = 0
if not accounts_df.empty:
    rates = get_exchange_rates()
    for index, row in accounts_df.iterrows():
        currency = row.get('currency', 'EUR')
        balance = row['balance']
        rate = rates.get(currency, 1.0)
        total_balance += balance * rate

# Display Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Balance", value=f"€{total_balance:,.2f}")

with col2:
    st.metric(label="Net Savings (All Time)", value=f"€{net_savings:,.2f}", delta=f"{((net_savings/total_income)*100) if total_income > 0 else 0:.1f}% Rate")

with col3:
    st.metric(label="Total Invested", value=f"€{total_invested:,.2f}")

with col4:
    st.metric(label="Monthly Spend (Avg)", value=f"€{total_expenses:,.2f}") # Placeholder logic

# --- Visualizations ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Spending by Category (EUR)")
    if not expenses_df.empty:
        fig_exp = px.pie(expenses_df, values='amount_eur', names='category', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_exp, use_container_width=True)
    else:
        st.info("No expense data available.")

with col_right:
    st.subheader("Income vs Expenses")
    if not expenses_df.empty or not income_df.empty:
        # Simple bar chart logic would go here
        st.info("Chart placeholder - add more data to visualize.")
    else:
        st.info("No data available.")

# --- Recent Transactions ---
st.subheader("Recent Activity")
if not expenses_df.empty:
    st.dataframe(expenses_df.head(5), use_container_width=True)
else:
    st.text("No recent transactions.")
