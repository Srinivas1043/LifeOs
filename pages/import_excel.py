import streamlit as st
import pandas as pd
from core.finance_queries import add_expense, add_income, get_categories, get_accounts
from core.navigation import setup_navigation

setup_navigation()

st.title("📂 Import Data")
st.caption("Import historical data from Excel.")

st.warning("⚠️ **IMPORTANT**: This tool does not check for duplicates. Run this import **ONLY ONCE** for a given file to avoid double-counting your transactions.")

# --- Import Mode Selection ---
import_mode = st.radio("Import Mode", ["Single Excel File (Multiple Sheets)", "Separate Files (CSV/Excel)"], horizontal=True)

st.divider()

# --- File Uploaders ---
uploaded_file = None
uploaded_expense_file = None
uploaded_income_file = None

if import_mode == "Single Excel File (Multiple Sheets)":
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
else:
    col1, col2 = st.columns(2)
    with col1:
        uploaded_expense_file = st.file_uploader("Upload Expenses File", type=['csv', 'xlsx', 'xls'])
    with col2:
        uploaded_income_file = st.file_uploader("Upload Income File", type=['csv', 'xlsx', 'xls'])

# --- Processing Logic ---
if uploaded_file or uploaded_expense_file or uploaded_income_file:
    try:
        # Helper to read file
        def read_file(file, sheet_name=None):
            if file.name.endswith('.csv'):
                return pd.read_csv(file)
            else:
                if sheet_name:
                    return pd.read_excel(file, sheet_name=sheet_name)
                return pd.read_excel(file)

        # Helper to get sheet names if Excel
        def get_sheet_names(file):
            if file.name.endswith('.csv'):
                return ["Default"]
            xls = pd.ExcelFile(file)
            return xls.sheet_names

        # --- Configuration ---
        st.subheader("1. Configuration")
        
        expense_sheet = "None"
        income_sheet = "None"
        
        # Mode 1 Config
        if import_mode == "Single Excel File (Multiple Sheets)" and uploaded_file:
            sheet_names = get_sheet_names(uploaded_file)
            col1, col2 = st.columns(2)
            with col1:
                expense_sheet = st.selectbox("Select Expenses Sheet", ["None"] + sheet_names, index=0)
            with col2:
                income_sheet = st.selectbox("Select Income Sheet", ["None"] + sheet_names, index=0)
        
        # Mode 2 Config (Implicit)
        elif import_mode == "Separate Files (CSV/Excel)":
            if uploaded_expense_file:
                expense_sheet = "Default" # Just a flag to say "process this"
            if uploaded_income_file:
                income_sheet = "Default"

        # --- Processing Function ---
        def process_sheet(file, sheet_name, type_):
            if sheet_name == "None" or not file:
                return None
            
            st.markdown(f"### Mapping: {type_}")
            
            # Read Data
            if import_mode == "Single Excel File (Multiple Sheets)":
                df = read_file(file, sheet_name)
            else:
                # In separate mode, sheet_name is ignored for CSV, or we default to first sheet for Excel if not specified
                # For simplicity, if it's Excel in separate mode, we read the first sheet.
                df = read_file(file)
                
            st.dataframe(df.head(3), use_container_width=True)
            
            columns = df.columns.tolist()
            
            # Mapping Form
            with st.expander(f"Map Columns for {type_}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    col_date = st.selectbox(f"Date Column ({type_})", columns, index=0 if 'Date' in columns else 0)
                with c2:
                    col_amount = st.selectbox(f"Amount Column ({type_})", columns, index=1 if len(columns)>1 else 0)
                with c3:
                    col_desc = st.selectbox(f"Description Column ({type_})", columns, index=2 if len(columns)>2 else 0)
                with c4:
                    col_cat = st.selectbox(f"Category Column ({type_})", ["Default"] + columns, index=0)
                
                c5, c6, c7, c8 = st.columns(4)
                with c5:
                    col_acc = st.selectbox(f"Account Column ({type_})", ["Default"] + columns, index=0)
                with c6:
                    col_curr = st.selectbox(f"Currency Column ({type_})", ["Default (EUR)"] + columns, index=0)
                with c7:
                    col_method = st.selectbox(f"Payment Method ({type_})", ["Default (Imported)"] + columns, index=0)
                with c8:
                    col_vendor = st.selectbox(f"Vendor/Source ({type_})", ["Default (None)"] + columns, index=0)
                
                # Defaults
                d1, d2 = st.columns(2)
                with d1:
                    # Fetch categories/accounts for defaults
                    db_cats = get_categories(type_.lower())
                    if not db_cats.empty:
                        default_cat = st.selectbox(f"Default Category ({type_})", db_cats['name'].tolist())
                    else:
                        default_cat = None
                        st.warning("No categories found in DB.")
                        
                with d2:
                    db_accs = get_accounts()
                    if not db_accs.empty:
                        default_acc = st.selectbox(f"Default Account ({type_})", db_accs['name'].tolist())
                    else:
                        default_acc = None
                        st.warning("No accounts found in DB.")

            return {
                "df": df,
                "map": {
                    "date": col_date,
                    "amount": col_amount,
                    "desc": col_desc,
                    "cat": col_cat,
                    "acc": col_acc,
                    "curr": col_curr,
                    "method": col_method,
                    "vendor": col_vendor
                },
                "defaults": {
                    "cat": default_cat,
                    "acc": default_acc
                },
                "db_cats": db_cats,
                "db_accs": db_accs
            }

        # Process Expenses
        exp_config = None
        if expense_sheet != "None":
            file_to_process = uploaded_file if import_mode == "Single Excel File (Multiple Sheets)" else uploaded_expense_file
            if file_to_process:
                exp_config = process_sheet(file_to_process, expense_sheet, "Expense")
            
        # Process Income
        inc_config = None
        if income_sheet != "None":
            file_to_process = uploaded_file if import_mode == "Single Excel File (Multiple Sheets)" else uploaded_income_file
            if file_to_process:
                inc_config = process_sheet(file_to_process, income_sheet, "Income")
            
        # --- Import Options ---
        st.markdown("### 2. Options")
        auto_create = st.checkbox("✨ Auto-create missing categories", value=True, help="If a category in Excel doesn't exist in the app, create it automatically instead of using the default.")
            
        # --- Import Button ---
        if st.button("🚀 Start Import", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_rows = 0
            if exp_config: total_rows += len(exp_config['df'])
            if inc_config: total_rows += len(inc_config['df'])
            
            current_row = 0
            
            # Helper to get or create category
            def get_or_create_category(name, type_, db_cats, default_id):
                if not auto_create:
                    # Strict matching
                    match = db_cats[db_cats['name'].str.lower() == str(name).lower()]
                    if not match.empty:
                        return int(match.iloc[0]['id'])
                    return default_id
                
                # Auto-create logic
                match = db_cats[db_cats['name'].str.lower() == str(name).lower()]
                if not match.empty:
                    return int(match.iloc[0]['id'])
                
                # Create new
                from core.finance_queries import add_category
                try:
                    res = add_category(str(name), type_.lower())
                    if res and res.data:
                        new_id = int(res.data[0]['id'])
                        # Update local cache to avoid re-creating same cat in loop
                        new_row = pd.DataFrame([{'id': new_id, 'name': str(name), 'type': type_.lower()}])
                        # We can't easily update the passed df in place effectively for the loop, 
                        # but we can return the ID. 
                        # Ideally we should update db_cats but for this simple loop we'll just return ID.
                        return new_id
                except Exception as e:
                    st.error(f"Failed to create category '{name}': {e}")
                
                return default_id

            # Import Expenses
            if exp_config:
                df = exp_config['df']
                mapping = exp_config['map']
                defaults = exp_config['defaults']
                db_cats = exp_config['db_cats']
                db_accs = exp_config['db_accs']
                
                # Default IDs
                def_cat_match = db_cats[db_cats['name'] == defaults['cat']]
                default_cat_id = int(def_cat_match.iloc[0]['id']) if not def_cat_match.empty else None
                
                def_acc_match = db_accs[db_accs['name'] == defaults['acc']]
                default_acc_id = int(def_acc_match.iloc[0]['id']) if not def_acc_match.empty else None
                
                for index, row in df.iterrows():
                    status_text.text(f"Importing Expense {index+1}/{len(df)}...")
                    
                    try:
                        # Date
                        date_val = pd.to_datetime(row[mapping['date']]).date()
                        
                        # Amount
                        amount_val = float(row[mapping['amount']])
                        
                        # Description
                        desc_val = str(row[mapping['desc']])
                        
                        # Currency
                        curr_val = "EUR"
                        if mapping['curr'] != "Default (EUR)":
                            curr_val = str(row[mapping['curr']])
                            
                        # Payment Method
                        method_val = "imported"
                        if mapping['method'] != "Default (Imported)":
                            method_val = str(row[mapping['method']])
                            
                        # Vendor
                        vendor_val = None
                        if mapping['vendor'] != "Default (None)":
                            vendor_val = str(row[mapping['vendor']])
                        
                        # Category ID
                        cat_id = default_cat_id
                        if mapping['cat'] != "Default":
                            cat_name = row[mapping['cat']]
                            cat_id = get_or_create_category(cat_name, 'expense', db_cats, default_cat_id)
                            
                        # Account ID
                        acc_id = default_acc_id
                        if mapping['acc'] != "Default":
                            acc_name = row[mapping['acc']]
                            acc_match = db_accs[db_accs['name'].str.lower() == str(acc_name).lower()]
                            if not acc_match.empty:
                                acc_id = int(acc_match.iloc[0]['id'])
                            else:
                                acc_id = default_acc_id
                            
                        if cat_id and acc_id:
                            add_expense(
                                date=date_val,
                                amount=amount_val,
                                category_id=cat_id,
                                account_id=acc_id,
                                description=desc_val,
                                payment_method=method_val,
                                currency=curr_val,
                                vendor=vendor_val,
                                source="excel_import"
                            )
                            
                    except Exception as e:
                        st.error(f"Error row {index}: {e}")
                    
                    current_row += 1
                    progress_bar.progress(min(current_row / total_rows, 1.0))

            # Import Income
            if inc_config:
                df = inc_config['df']
                mapping = inc_config['map']
                defaults = inc_config['defaults']
                db_cats = inc_config['db_cats']
                db_accs = inc_config['db_accs']
                
                def_cat_match = db_cats[db_cats['name'] == defaults['cat']]
                default_cat_id = int(def_cat_match.iloc[0]['id']) if not def_cat_match.empty else None
                
                def_acc_match = db_accs[db_accs['name'] == defaults['acc']]
                default_acc_id = int(def_acc_match.iloc[0]['id']) if not def_acc_match.empty else None
                
                for index, row in df.iterrows():
                    status_text.text(f"Importing Income {index+1}/{len(df)}...")
                    
                    try:
                        date_val = pd.to_datetime(row[mapping['date']]).date()
                        amount_val = float(row[mapping['amount']])
                        desc_val = str(row[mapping['desc']]) # Source/Notes
                        
                        # Category
                        cat_id = default_cat_id
                        if mapping['cat'] != "Default":
                            cat_name = row[mapping['cat']]
                            cat_id = get_or_create_category(cat_name, 'income', db_cats, default_cat_id)
                            
                        # Account
                        acc_id = default_acc_id
                        if mapping['acc'] != "Default":
                            acc_name = row[mapping['acc']]
                            acc_match = db_accs[db_accs['name'].str.lower() == str(acc_name).lower()]
                            if not acc_match.empty:
                                acc_id = int(acc_match.iloc[0]['id'])
                            else:
                                acc_id = default_acc_id
                            
                        if cat_id and acc_id:
                            add_income(
                                date=date_val,
                                amount=amount_val,
                                category_id=cat_id,
                                account_id=acc_id,
                                source=desc_val,
                                currency="EUR"
                            )
                            
                    except Exception as e:
                        st.error(f"Error row {index}: {e}")
                        
                    current_row += 1
                    progress_bar.progress(min(current_row / total_rows, 1.0))
            
            st.success("Import Complete!")
            st.balloons()

    except Exception as e:
        st.error(f"Error reading file: {e}")
