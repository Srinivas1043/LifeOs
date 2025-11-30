import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.finance_queries import get_expenses, get_income
import datetime
from core.navigation import setup_navigation

setup_navigation()

st.title("📊 Analytics & P&L")

# --- Data Loading ---
expenses_df = get_expenses()
income_df = get_income()

# --- Currency Config ---
display_currency = st.session_state.get('currency', 'EUR')
conversion_rate = st.session_state.get('conversion_rate', 1.0)
if conversion_rate == 0: conversion_rate = 1.0

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

# --- Calculate EUR amounts for filtering/aggregation ---
if not filtered_expenses.empty:
    filtered_expenses['amount_eur'] = filtered_expenses.get('amount_eur', filtered_expenses['amount']).fillna(filtered_expenses['amount'])
    total_expenses_eur = filtered_expenses['amount_eur'].sum()
else:
    total_expenses_eur = 0

if not filtered_income.empty:
    filtered_income['amount_eur'] = filtered_income.get('amount_eur', filtered_income['amount']).fillna(filtered_income['amount'])
    total_income_eur = filtered_income['amount_eur'].sum()
else:
    total_income_eur = 0
st.header(f"Profit & Loss ({start_date} to {end_date})")

# Convert to display currency
total_income_display = (total_income_eur / conversion_rate)
total_expenses_display = (total_expenses_eur / conversion_rate)
net_profit_display = total_income_display - total_expenses_display

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"{display_currency} {total_income_display:,.2f}", delta_color="normal")
col2.metric("Total Expenses", f"{display_currency} {total_expenses_display:,.2f}", delta_color="inverse")
col3.metric("Net Profit / Loss", f"{display_currency} {net_profit_display:,.2f}", delta=f"{net_profit_display:,.2f}")

st.divider()

tab1, tab2, tab3 = st.tabs(["Spending Analysis", "Income Analysis", "Advanced Insights"])

with tab1:
    st.subheader("Spending Breakdown")
    if not filtered_expenses.empty:
        col1, col2 = st.columns(2)
        with col1:
            # Category Pie Chart
            # Convert for display
            filtered_expenses['amount_display'] = filtered_expenses['amount_eur'] / conversion_rate
            fig_cat = px.pie(filtered_expenses, values='amount_display', names='category', title=f'Expenses by Category ({display_currency})', hole=0.4)
            st.plotly_chart(fig_cat, use_container_width=True)
        
        with col2:
            # Payment Method Bar Chart
            fig_method = px.bar(filtered_expenses, x='payment_method', y='amount_display', title=f'Spending by Method ({display_currency})', color='payment_method')
            st.plotly_chart(fig_method, use_container_width=True)
        
        # Time Series
        daily_spend = filtered_expenses.groupby('date')['amount_display'].sum().reset_index()
        fig_trend = px.area(daily_spend, x='date', y='amount_display', title=f'Daily Spending Trend ({display_currency})', line_shape='spline')
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No expense data for this period.")

with tab2:
    st.subheader("Income Breakdown")
    if not filtered_income.empty:
        filtered_income['amount_display'] = filtered_income['amount_eur'] / conversion_rate
        fig_inc = px.bar(filtered_income, x='source', y='amount_display', title=f'Income by Source ({display_currency})', color='source')
        st.plotly_chart(fig_inc, use_container_width=True)
    else:
        st.info("No income data for this period.")

with tab3:
    st.subheader("Advanced Insights")
    
    # --- Sankey Diagram ---
    st.markdown("#### 🌊 Cash Flow Visualization")
    if not filtered_expenses.empty and not filtered_income.empty:
        # Nodes: Income Sources -> Budget -> Expense Categories
        
        # 1. Aggregate Income by Source
        inc_agg = filtered_income.groupby('source')['amount_eur'].sum().reset_index()
        
        # 2. Aggregate Expenses by Category
        exp_agg = filtered_expenses.groupby('category')['amount_eur'].sum().reset_index()
        
        # Create Node Labels
        income_sources = inc_agg['source'].tolist()
        expense_cats = exp_agg['category'].tolist()
        all_nodes = income_sources + ["Budget"] + expense_cats
        
        # Map labels to indices
        node_indices = {label: i for i, label in enumerate(all_nodes)}
        
        # Create Links
        sources = []
        targets = []
        values = []
        
        # Income -> Budget
        for _, row in inc_agg.iterrows():
            sources.append(node_indices[row['source']])
            targets.append(node_indices["Budget"])
            values.append(row['amount_eur'] / conversion_rate)
            
        # Budget -> Expenses
        for _, row in exp_agg.iterrows():
            sources.append(node_indices["Budget"])
            targets.append(node_indices[row['category']])
            values.append(row['amount_eur'] / conversion_rate)
            
        # Plot
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes,
                color="blue"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values
            )
        )])
        
        fig_sankey.update_layout(title_text=f"Cash Flow ({display_currency})", font_size=10)
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.info("Need both Income and Expense data for Cash Flow visualization.")
        
    st.divider()
    
    # --- Top Merchants ---
    st.markdown("#### 🏆 Top Merchants")
    if not filtered_expenses.empty:
        # Group by Vendor (fallback to description)
        # We need a 'vendor' column. If it doesn't exist in the filtered df (e.g. old data), handle it.
        if 'vendor' not in filtered_expenses.columns:
            filtered_expenses['vendor'] = None
            
        # Fill missing vendors with Description (truncated)
        filtered_expenses['merchant_display'] = filtered_expenses['vendor'].fillna(filtered_expenses['description'].str[:20])
        
        top_merchants = filtered_expenses.groupby('merchant_display')['amount_eur'].sum().nlargest(10).reset_index()
        top_merchants['amount_display'] = top_merchants['amount_eur'] / conversion_rate
        
        fig_merch = px.bar(
            top_merchants, 
            x='amount_display', 
            y='merchant_display', 
            orientation='h',
            title=f'Top Spending Destinations ({display_currency})',
            labels={'amount_display': 'Amount', 'merchant_display': 'Merchant'},
            color='amount_display',
            color_continuous_scale='Viridis'
        )
        fig_merch.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_merch, use_container_width=True)
    else:
        st.info("No expense data available.")
