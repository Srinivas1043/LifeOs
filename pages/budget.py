import streamlit as st
import pandas as pd
import datetime
from core.finance_queries import get_categories, get_budgets, add_budget, get_expenses
from core.navigation import setup_navigation

setup_navigation()

st.title("⚖️ Budget Planner")

# --- Configuration ---
if 'budget_month' not in st.session_state:
    st.session_state['budget_month'] = datetime.date.today().replace(day=1)

col_sel1, col_sel2 = st.columns([1, 3])
with col_sel1:
    # Month Selector
    current_date = st.session_state['budget_month']
    selected_month_str = st.date_input("Select Month", value=current_date, format="YYYY/MM/DD")
    # Normalize to 1st of month
    selected_month = selected_month_str.replace(day=1)
    month_str = selected_month.strftime("%Y-%m")

# --- Data Loading ---
categories_df = get_categories("expense")
budgets_df = get_budgets(month_str)
expenses_df = get_expenses()

# Filter expenses for this month
if not expenses_df.empty:
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    mask = (expenses_df['date'].dt.strftime("%Y-%m") == month_str)
    monthly_expenses = expenses_df[mask]
else:
    monthly_expenses = pd.DataFrame()

# --- Budget Setting ---
with st.expander("📝 Set/Update Budget", expanded=False):
    with st.form("budget_form"):
        c1, c2 = st.columns(2)
        with c1:
            cat_list = categories_df['name'].tolist() if not categories_df.empty else []
            category = st.selectbox("Category", cat_list)
        with c2:
            amount = st.number_input("Budget Amount", min_value=0.0, step=10.0)
            
        submitted = st.form_submit_button("Save Budget")
        if submitted and category:
            cat_id = categories_df[categories_df['name'] == category].iloc[0]['id']
            res = add_budget(int(cat_id), amount, month_str)
            if res:
                st.success(f"Budget for {category} updated!")
                st.rerun()

# --- Budget Overview ---
st.divider()
st.subheader(f"Budget Status: {selected_month.strftime('%B %Y')}")

display_currency = st.session_state.get('currency', 'EUR')
conversion_rate = st.session_state.get('conversion_rate', 1.0)

if not categories_df.empty:
    # Prepare Data
    # 1. Get all expense categories
    budget_data = []
    
    # Calculate actual spend per category
    spend_map = {}
    if not monthly_expenses.empty:
        monthly_expenses['amount_eur'] = monthly_expenses.get('amount_eur', monthly_expenses['amount']).fillna(monthly_expenses['amount'])
        spend_series = monthly_expenses.groupby('category')['amount_eur'].sum()
        spend_map = spend_series.to_dict()
        
    # Map budgets
    budget_map = {}
    if not budgets_df.empty:
        for _, row in budgets_df.iterrows():
            budget_map[row['category']] = row['budget_amount']
            
    # Combine
    total_budget = 0
    total_spent = 0
    
    for _, row in categories_df.iterrows():
        cat_name = row['name']
        budget_val = budget_map.get(cat_name, 0.0)
        spent_val_eur = spend_map.get(cat_name, 0.0)
        
        # Convert to display
        spent_val = spent_val_eur / conversion_rate
        
        if budget_val > 0 or spent_val > 0:
            budget_data.append({
                "Category": cat_name,
                "Budget": budget_val,
                "Spent": spent_val,
                "Remaining": budget_val - spent_val,
                "Progress": (spent_val / budget_val * 100) if budget_val > 0 else (100 if spent_val > 0 else 0)
            })
            total_budget += budget_val
            total_spent += spent_val
            
    # Display Totals
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Total Budget ({display_currency})", f"{total_budget:,.2f}")
    m2.metric(f"Total Spent ({display_currency})", f"{total_spent:,.2f}")
    remaining = total_budget - total_spent
    m3.metric(f"Remaining ({display_currency})", f"{remaining:,.2f}", delta_color="normal" if remaining >= 0 else "inverse")
    
    st.divider()
    
    # Display Rows
    if budget_data:
        # Sort by progress desc
        budget_data.sort(key=lambda x: x['Progress'], reverse=True)
        
        for item in budget_data:
            c1, c2, c3 = st.columns([2, 4, 1])
            with c1:
                st.markdown(f"**{item['Category']}**")
                st.caption(f"{display_currency} {item['Spent']:,.0f} / {item['Budget']:,.0f}")
            with c2:
                prog = min(item['Progress'], 100)
                color = "green"
                if item['Progress'] > 100: color = "red"
                elif item['Progress'] > 85: color = "orange"
                
                st.progress(int(prog))
            with c3:
                st.markdown(f"**{item['Progress']:.0f}%**")
            st.divider()
    else:
        st.info("No budgets or expenses for this month.")

else:
    st.warning("Please configure categories first.")
