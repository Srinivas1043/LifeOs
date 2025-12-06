import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.finance_queries import get_expenses, get_income, get_investments, get_accounts, get_exchange_rates, get_budgets
from core.navigation import setup_navigation_with_context
import datetime
# --- Setup ---
setup_navigation_with_context("Finance")
st.title("💰 Financial Overview")

# --- Data Loading ---
with st.spinner("Loading financial data..."):
    expenses_df = get_expenses()
    income_df = get_income()
    investments_df = get_investments()
    accounts_df = get_accounts()
    rates = get_exchange_rates()

# --- Currency Config ---
display_currency = st.session_state.get('currency', 'EUR')
conversion_rate = st.session_state.get('conversion_rate', 1.0)
if conversion_rate == 0: conversion_rate = 1.0

# --- Helper: Convert to Display Currency ---
def to_display(amount_eur):
    return amount_eur / conversion_rate

# --- Sidebar Filters ---
st.sidebar.header("Filter Analysis")
today = datetime.date.today()
start_of_year = datetime.date(today.year, 1, 1)

filter_type = st.sidebar.radio("Time Period", ["This Month", "Last 30 Days", "Year to Date", "Custom Range"])

start_date = start_of_year
end_date = today

if filter_type == "This Month":
    start_date = datetime.date(today.year, today.month, 1)
    end_date = today
elif filter_type == "Last 30 Days":
    start_date = today - datetime.timedelta(days=30)
    end_date = today
elif filter_type == "Year to Date":
    start_date = start_of_year
    end_date = today
elif filter_type == "Custom Range":
    start_date = st.sidebar.date_input("Start Date", start_of_year)
    end_date = st.sidebar.date_input("End Date", today)

# Apply Filters
filtered_expenses = pd.DataFrame()
filtered_income = pd.DataFrame()

if not expenses_df.empty:
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    expenses_df['amount_eur'] = expenses_df.get('amount_eur', expenses_df['amount']).fillna(expenses_df['amount'])
    filtered_expenses = expenses_df[(expenses_df['date'].dt.date >= start_date) & (expenses_df['date'].dt.date <= end_date)].copy()

if not income_df.empty:
    income_df['date'] = pd.to_datetime(income_df['date'])
    income_df['amount_eur'] = income_df.get('amount_eur', income_df['amount']).fillna(income_df['amount'])
    filtered_income = income_df[(income_df['date'].dt.date >= start_date) & (income_df['date'].dt.date <= end_date)].copy()

# --- High-Level KPIs (Global / Current State) ---
# 1. Net Worth (Accounts + Investments)
total_accounts_eur = 0
if not accounts_df.empty:
    for index, row in accounts_df.iterrows():
        currency = row.get('currency', 'EUR')
        balance = row['balance']
        rate = rates.get(currency, 1.0)
        total_accounts_eur += balance * rate

total_invested_eur = 0
if not investments_df.empty:
    investments_df['amount_eur'] = investments_df.get('amount_eur', investments_df['amount']).fillna(investments_df['amount'])
    total_invested_eur = investments_df['amount_eur'].sum()

net_worth_eur = total_accounts_eur + total_invested_eur

# 2. Period Metrics (Based on Filter)
period_income_eur = filtered_income['amount_eur'].sum() if not filtered_income.empty else 0
period_expenses_eur = filtered_expenses['amount_eur'].sum() if not filtered_expenses.empty else 0
period_savings_eur = period_income_eur - period_expenses_eur
period_savings_rate = (period_savings_eur / period_income_eur * 100) if period_income_eur > 0 else 0

# Display KPIs
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(f"Net Worth ({display_currency})", f"{to_display(net_worth_eur):,.0f}", help="Total Accounts + Investments")
with col2:
    st.metric(f"Income", f"{to_display(period_income_eur):,.0f}")
with col3:
    st.metric(f"Expenses", f"{to_display(period_expenses_eur):,.0f}")
with col4:
    st.metric(f"Net Savings", f"{to_display(period_savings_eur):,.0f}", delta_color="normal")
with col5:
    st.metric(f"Savings Rate", f"{period_savings_rate:.1f}%")

st.divider()

# --- Tabs ---
tab_overview, tab_analysis, tab_insights, tab_budget = st.tabs(["Overview", "Analysis", "Insights", "Budget Status"])

# --- Tab 1: Overview ---
with tab_overview:
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("🌊 Cash Flow (Last 6 Months)")
        # Aggregate by month (Global View, ignoring filter for this chart to show trend)
        cf_data = []
        today_date = datetime.date.today()
        for i in range(5, -1, -1):
            d = today_date - pd.DateOffset(months=i)
            m = d.month
            y = d.year
            label = d.strftime("%b %Y")
            
            inc = 0
            exp = 0
            
            if not income_df.empty:
                mask = (income_df['date'].dt.month == m) & (income_df['date'].dt.year == y)
                inc = income_df.loc[mask, 'amount_eur'].sum()
                
            if not expenses_df.empty:
                mask = (expenses_df['date'].dt.month == m) & (expenses_df['date'].dt.year == y)
                exp = expenses_df.loc[mask, 'amount_eur'].sum()
                
            cf_data.append({
                "Month": label,
                "Income": to_display(inc),
                "Expenses": to_display(exp),
                "Net": to_display(inc - exp)
            })
        
        cf_df = pd.DataFrame(cf_data)
        if not cf_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=cf_df['Month'], y=cf_df['Income'], name='Income', marker_color='#238636'))
            fig.add_trace(go.Bar(x=cf_df['Month'], y=cf_df['Expenses'], name='Expenses', marker_color='#DA3633'))
            fig.add_trace(go.Scatter(x=cf_df['Month'], y=cf_df['Net'], name='Net Savings', line=dict(color='#58A6FF', width=3)))
            fig.update_layout(barmode='group', margin=dict(t=0, b=0, l=0, r=0), height=350, legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for chart.")

    with c2:
        st.subheader("Recent Activity")
        if not expenses_df.empty:
            recent = expenses_df.sort_values('date', ascending=False).head(5)
            for _, row in recent.iterrows():
                with st.container():
                    rc1, rc2, rc3 = st.columns([3, 2, 1])
                    with rc1:
                        st.markdown(f"**{row['description'] or row['category']}**")
                        st.caption(f"{row['date'].strftime('%Y-%m-%d')} • {row['category']}")
                    with rc2:
                        st.text(row['account'])
                    with rc3:
                        amt = to_display(row['amount_eur'])
                        st.markdown(f"**{display_currency} {amt:,.2f}**")
                    st.divider()
        else:
            st.text("No recent transactions.")

# --- Tab 2: Analysis ---
with tab_analysis:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Spending Breakdown")
        if not filtered_expenses.empty:
            # Category Pie Chart
            filtered_expenses['amount_display'] = to_display(filtered_expenses['amount_eur'])
            fig_cat = px.pie(filtered_expenses, values='amount_display', names='category', title=f'Expenses by Category ({display_currency})', hole=0.4)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No expense data for this period.")
            
    with col2:
        st.subheader("Income Breakdown")
        if not filtered_income.empty:
            filtered_income['amount_display'] = to_display(filtered_income['amount_eur'])
            fig_inc = px.bar(filtered_income, x='source', y='amount_display', title=f'Income by Source ({display_currency})', color='source')
            st.plotly_chart(fig_inc, use_container_width=True)
        else:
            st.info("No income data for this period.")

    st.subheader("Daily Spending Trend")
    if not filtered_expenses.empty:
        daily_spend = filtered_expenses.groupby('date')['amount_display'].sum().reset_index()
        fig_trend = px.area(daily_spend, x='date', y='amount_display', title=f'Daily Spending Trend ({display_currency})', line_shape='spline')
        st.plotly_chart(fig_trend, use_container_width=True)

# --- Tab 3: Insights ---
with tab_insights:
    st.subheader("🌊 Cash Flow Visualization")
    if not filtered_expenses.empty and not filtered_income.empty:
        # Sankey Logic
        inc_agg = filtered_income.groupby('source')['amount_eur'].sum().reset_index()
        exp_agg = filtered_expenses.groupby('category')['amount_eur'].sum().reset_index()
        
        income_sources = inc_agg['source'].tolist()
        expense_cats = exp_agg['category'].tolist()
        all_nodes = income_sources + ["Budget"] + expense_cats
        node_indices = {label: i for i, label in enumerate(all_nodes)}
        
        sources = []
        targets = []
        values = []
        
        for _, row in inc_agg.iterrows():
            sources.append(node_indices[row['source']])
            targets.append(node_indices["Budget"])
            values.append(to_display(row['amount_eur']))
            
        for _, row in exp_agg.iterrows():
            sources.append(node_indices["Budget"])
            targets.append(node_indices[row['category']])
            values.append(to_display(row['amount_eur']))
            
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=all_nodes, color="blue"),
            link=dict(source=sources, target=targets, value=values)
        )])
        fig_sankey.update_layout(title_text=f"Cash Flow ({display_currency})", font_size=10)
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.info("Need both Income and Expense data for Cash Flow visualization.")
        
    st.divider()
    
    st.subheader("🏆 Top Merchants")
    if not filtered_expenses.empty:
        if 'vendor' not in filtered_expenses.columns: filtered_expenses['vendor'] = None
        filtered_expenses['merchant_display'] = filtered_expenses['vendor'].fillna(filtered_expenses['description'].str[:20])
        top_merchants = filtered_expenses.groupby('merchant_display')['amount_eur'].sum().nlargest(10).reset_index()
        top_merchants['amount_display'] = to_display(top_merchants['amount_eur'])
        
        fig_merch = px.bar(top_merchants, x='amount_display', y='merchant_display', orientation='h', title=f'Top Spending Destinations ({display_currency})', color='amount_display', color_continuous_scale='Viridis')
        fig_merch.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_merch, use_container_width=True)

# --- Tab 4: Budget Status ---
with tab_budget:
    st.subheader("🎯 Budget vs Actual")
    # Use end_date of filter to determine budget month
    budget_month = end_date.strftime("%Y-%m")
    budgets_df = get_budgets(budget_month)
    
    if not budgets_df.empty and not filtered_expenses.empty:
        expense_by_cat = filtered_expenses.groupby('category')['amount_eur'].sum().reset_index()
        merged = pd.merge(budgets_df, expense_by_cat, on='category', how='left')
        merged['amount_eur'] = merged['amount_eur'].fillna(0)
        
        for index, row in merged.iterrows():
            cat = row['category']
            budget = row['budget_amount']
            spent = to_display(row['amount_eur'])
            
            if budget > 0:
                pct = (spent / budget) * 100
                col_b1, col_b2 = st.columns([3, 1])
                with col_b1:
                    st.write(f"**{cat}**")
                    st.progress(int(min(pct, 100)))
                with col_b2:
                    st.caption(f"{spent:.0f} / {budget:.0f} ({int(pct)}%)")
    else:
        st.info(f"No budgets set for {budget_month} or no expenses found.")
