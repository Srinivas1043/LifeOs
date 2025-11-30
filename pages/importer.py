import streamlit as st
import pandas as pd
from core.finance_queries import (
    get_categories, get_accounts, add_expense, add_income, 
    add_category, add_account
)
from core.navigation import setup_navigation

setup_navigation()

st.title("📤 Data Importer")
st.markdown("Upload your historical data (Excel/CSV) to populate your Life OS.")

# --- File Upload ---
uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # Load Data
        dfs = {}
        if uploaded_file.name.endswith('.csv'):
            dfs = {'Sheet1': pd.read_csv(uploaded_file)}
        else:
            dfs = pd.read_excel(uploaded_file, sheet_name=None)
            
        # Sheet Selection
        sheet_names = list(dfs.keys())
        selected_sheet = st.selectbox("Select Sheet to Import", sheet_names)
        
        df = dfs[selected_sheet]
        
        st.write(f"### Preview: {selected_sheet}")
        st.dataframe(df.head())
        
        st.divider()
        st.subheader("🔧 Map Columns")
        
        cols = df.columns.tolist()
        
        # Auto-detect mappings based on common names
        def get_index(options, targets):
            for t in targets:
                for i, opt in enumerate(options):
                    if t.lower() in opt.lower():
                        return i
            return 0

        col1, col2, col3 = st.columns(3)
        with col1:
            date_col = st.selectbox("Date Column", cols, index=get_index(cols, ['date']))
            amount_col = st.selectbox("Amount Column", cols, index=get_index(cols, ['amount', 'cost', 'net amount']))
            desc_col = st.selectbox("Description Column", cols, index=get_index(cols, ['description', 'desc', 'details']))
            
        with col2:
            # Conditional Category/Source based on sheet type guess
            is_income_sheet = 'income' in selected_sheet.lower()
            
            if is_income_sheet:
                cat_col = st.selectbox("Source Column (for Income)", cols, index=get_index(cols, ['source', 'from']))
                acc_col = st.selectbox("Account Column", ["(Default Account)"] + cols)
            else:
                cat_col = st.selectbox("Category Column", cols, index=get_index(cols, ['category', 'cat']))
                acc_col = st.selectbox("Account Column", ["(Default Account)"] + cols)
                
            type_option = "Income" if is_income_sheet else "Expense"
            import_type = st.radio("Import As", ["Expense", "Income"], index=1 if is_income_sheet else 0, horizontal=True)
            
        with col3:
            curr_col = st.selectbox("Currency Column", ["(Default: EUR)"] + cols)
            default_currency = "EUR"
            if curr_col == "(Default: EUR)":
                default_currency = st.selectbox("Select Default Currency", ["EUR", "USD", "GBP", "INR"])
            
            default_account_name = None
            if acc_col == "(Default Account)":
                default_account_name = st.text_input("Default Account Name", value="Main Account")

        st.divider()
        
        if st.button("🚀 Start Import"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Cache existing categories/accounts
            cats_exp = get_categories('expense')
            cats_inc = get_categories('income')
            accounts = get_accounts()
            
            # Helper to get/create ID
            def get_id(name, df_lookup, create_func, type_arg=None):
                if not name or pd.isna(name): return None
                name = str(name).strip()
                
                if df_lookup.empty:
                    res = create_func(name, type_arg) if type_arg else create_func(name, "asset", 0.0)
                    if res and res.data: return res.data[0]['id']
                    return None
                
                match = df_lookup[df_lookup['name'].str.lower() == name.lower()]
                if not match.empty:
                    return match.iloc[0]['id']
                else:
                    # Create new
                    res = create_func(name, type_arg) if type_arg else create_func(name, "asset", 0.0)
                    if res and res.data:
                        # Update cache locally to avoid re-fetching
                        # (Simplification: just return ID, next run will hit DB or we accept slight inefficiency)
                        return res.data[0]['id']
                    return None

            success_count = 0
            fail_count = 0
            
            for i, row in df.iterrows():
                try:
                    # Get Data
                    date = pd.to_datetime(row[date_col]).date()
                    amount = float(row[amount_col])
                    desc = str(row[desc_col]) if pd.notna(row[desc_col]) else ""
                    
                    # Category / Source
                    cat_name = str(row[cat_col]) if pd.notna(row[cat_col]) else "Uncategorized"
                    
                    # Account
                    if acc_col == "(Default Account)":
                        acc_name = default_account_name
                    else:
                        acc_name = str(row[acc_col]) if pd.notna(row[acc_col]) else "Cash"
                    
                    currency = default_currency
                    if curr_col != "(Default: EUR)":
                        currency = str(row[curr_col])
                    
                    # Get/Create IDs
                    acc_id = get_id(acc_name, accounts, add_account)
                    
                    if import_type == 'Expense':
                        cat_id = get_id(cat_name, cats_exp, add_category, 'expense')
                        if cat_id and acc_id:
                            add_expense(date, amount, cat_id, acc_id, desc, "card", currency)
                            success_count += 1
                            
                    elif import_type == 'Income':
                        cat_id = get_id(cat_name, cats_inc, add_category, 'income')
                        if cat_id and acc_id:
                            add_income(date, amount, cat_id, acc_id, cat_name, currency, desc) # Source = Category name for income
                            success_count += 1
                            
                except Exception as e:
                    fail_count += 1
                    # print(f"Row {i} error: {e}") # Debug
                
                # Update Progress
                if i % 5 == 0:
                    progress_bar.progress((i + 1) / len(df))
                    status_text.text(f"Processing row {i+1}/{len(df)}")
                
            progress_bar.progress(1.0)
            st.success(f"Import Complete! ✅ {success_count} imported, ❌ {fail_count} failed.")
            st.balloons()
            
    except Exception as e:
        st.error(f"Error reading file: {e}")
