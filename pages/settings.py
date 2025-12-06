import streamlit as st
import pandas as pd
from core.finance_queries import add_account, add_category, get_accounts, get_categories
from core.supabase_client import init_supabase
from core.navigation import setup_navigation_with_context

setup_navigation_with_context("System")
supabase = init_supabase()

st.title("⚙️ Settings")

tab1, tab2 = st.tabs(["Accounts", "Categories"])

with tab1:
    st.header("Manage Accounts")
    
    # Add Account Form
    with st.form("add_account_form"):
        st.subheader("Add New Account")
        name = st.text_input("Account Name (e.g., ABN AMRO Current, ABN AMRO Savings)")
        type_ = st.selectbox("Type", ["bank", "credit_card", "wallet", "cash", "investment"])
        balance = st.number_input("Initial Balance", min_value=0.0, step=0.01)
        currency = st.selectbox("Currency", ["EUR", "USD", "INR", "GBP"], index=0)
        
        submitted = st.form_submit_button("Add Account")
        if submitted:
            if name:
                # Use helper function which handles user_id
                res = add_account(name, type_, balance, currency)
                if res:
                    st.success(f"Account '{name}' added!")
                    st.rerun()
            else:
                st.warning("Please enter a name.")

    # List Accounts
    st.subheader("Existing Accounts")
    df_accounts = get_accounts()
    if not df_accounts.empty:
        # Hide technical columns
        display_cols = [c for c in df_accounts.columns if c not in ['id', 'user_id', 'created_at']]
        st.dataframe(df_accounts[display_cols], use_container_width=True)
    else:
        st.info("No accounts found.")

with tab2:
    st.header("Manage Categories")
    
    # Add Category Form
    with st.form("add_category_form"):
        st.subheader("Add New Category")
        cat_name = st.text_input("Category Name (e.g., Groceries)")
        cat_type = st.selectbox("Type", ["expense", "income", "investment", "saving"])
        
        cat_submitted = st.form_submit_button("Add Category")
        if cat_submitted:
            if cat_name:
                # Use helper function
                res = add_category(cat_name, cat_type)
                if res:
                    st.success(f"Category '{cat_name}' added!")
                    st.rerun()
            else:
                st.warning("Please enter a name.")

    # List Categories
    st.subheader("Existing Categories")
    df_cats = get_categories()
    if not df_cats.empty:
        # Hide technical columns
        display_cols = [c for c in df_cats.columns if c not in ['id', 'user_id', 'created_at']]
        st.dataframe(df_cats[display_cols], use_container_width=True)
    else:
        st.info("No categories found.")

    # Budget Configuration
    st.divider()
    st.header("Budget Configuration")
    
    if not df_cats.empty:
        expense_cats = df_cats[df_cats['type'] == 'expense']
        
        if not expense_cats.empty:
            from core.finance_queries import add_budget, get_budgets
            import datetime
            
            # Month Selector
            current_month = datetime.date.today().strftime("%Y-%m")
            selected_month = st.text_input("Budget Month (YYYY-MM)", value=current_month)
            
            # Fetch existing budgets
            existing_budgets = get_budgets(selected_month)
            budget_map = {}
            if not existing_budgets.empty:
                budget_map = dict(zip(existing_budgets['category_id'], existing_budgets['budget_amount']))
            
            st.write("Set monthly limits for your expense categories:")
            
            with st.form("budget_form"):
                budget_inputs = {}
                cols = st.columns(2)
                
                for i, (index, row) in enumerate(expense_cats.iterrows()):
                    cat_id = row['id']
                    cat_name = row['name']
                    current_val = budget_map.get(cat_id, 0.0)
                    
                    with cols[i % 2]:
                        budget_inputs[cat_id] = st.number_input(
                            f"{cat_name} Limit", 
                            min_value=0.0, 
                            value=float(current_val), 
                            step=10.0,
                            key=f"budget_{cat_id}"
                        )
                
                if st.form_submit_button("Save Budgets"):
                    success_count = 0
                    for cat_id, amount in budget_inputs.items():
                        if amount > 0 or cat_id in budget_map: # Save if > 0 or if updating existing
                             add_budget(cat_id, amount, selected_month)
                             success_count += 1
                    
                    if success_count > 0:
                        st.success(f"Updated budgets for {success_count} categories!")
                        st.rerun()
        else:
            st.info("No expense categories found to budget for.")
    else:
        st.info("Add categories first to set budgets.")
