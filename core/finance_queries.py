from core.supabase_client import init_supabase
import pandas as pd
import streamlit as st

supabase = init_supabase()

# --- Helper Functions ---
def add_category(name, type):
    """Add a new category."""
    try:
        data = {"name": name, "type": type}
        response = supabase.table("categories").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding category: {e}")
        return None

def get_categories(type_filter=None):
    """Fetch categories, optionally filtered by type (expense, income, etc.)."""
    try:
        query = supabase.table("categories").select("*")
        if type_filter:
            query = query.eq("type", type_filter)
        response = query.execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching categories: {e}")
        return pd.DataFrame()

def add_account(name, type, balance, currency="EUR"):
    """Add a new account."""
    try:
        data = {
            "name": name, 
            "type": type, 
            "balance": balance, 
            "currency": currency
        }
        response = supabase.table("accounts").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding account: {e}")
        return None

def get_accounts():
    """Fetch all accounts."""
    try:
        response = supabase.table("accounts").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching accounts: {e}")
        return pd.DataFrame()

# --- Expenses ---
def add_expense(date, amount, category_id, account_id, description, payment_method, vendor=None):
    """Add a new expense."""
    try:
        data = {
            "date": str(date),
            "amount": amount,
            "category_id": category_id,
            "account_id": account_id,
            "description": description,
            "payment_method": payment_method,
            "vendor": vendor,
            "source": "manual"
        }
        response = supabase.table("expenses").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding expense: {e}")
        return None

def get_expenses():
    """Fetch expenses with category and account details."""
    try:
        # Supabase join syntax: table(column, ...)
        response = supabase.table("expenses").select(
            "*, categories(name), accounts(name)"
        ).order("date", desc=True).execute()
        
        # Flatten the response if needed, or handle in UI
        data = response.data
        if data:
            df = pd.json_normalize(data)
            # Rename columns for cleaner display
            df.rename(columns={'categories.name': 'category', 'accounts.name': 'account'}, inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching expenses: {e}")
        return pd.DataFrame()

# --- Income ---
def add_income(date, amount, category_id, account_id, source, notes=None):
    """Add a new income record."""
    try:
        data = {
            "date": str(date),
            "amount": amount,
            "category_id": category_id,
            "account_id": account_id,
            "source": source,
            "notes": notes
        }
        response = supabase.table("income").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding income: {e}")
        return None

def get_income():
    """Fetch income records."""
    try:
        response = supabase.table("income").select(
            "*, categories(name), accounts(name)"
        ).order("date", desc=True).execute()
        
        data = response.data
        if data:
            df = pd.json_normalize(data)
            df.rename(columns={'categories.name': 'category', 'accounts.name': 'account'}, inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching income: {e}")
        return pd.DataFrame()

# --- Savings ---
def add_saving_goal(name, target_amount, deadline, notes=None):
    """Add a new savings goal."""
    try:
        data = {
            "goal_name": name,
            "target_amount": target_amount,
            "deadline": str(deadline),
            "notes": notes
        }
        response = supabase.table("saving_goals").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding savings goal: {e}")
        return None

def get_saving_goals():
    """Fetch all savings goals."""
    try:
        response = supabase.table("saving_goals").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching savings goals: {e}")
        return pd.DataFrame()

# --- Investments ---
def add_investment(date, amount, instrument_name, investment_type, action, account_id, category_id, units, price_per_unit):
    """Add a new investment transaction."""
    try:
        data = {
            "date": str(date),
            "amount": amount,
            "instrument_name": instrument_name,
            "investment_type": investment_type,
            "action": action,
            "account_id": account_id,
            "category_id": category_id,
            "units": units,
            "price_per_unit": price_per_unit,
            "source": "manual"
        }
        response = supabase.table("investments").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding investment: {e}")
        return None

def get_investments():
    """Fetch all investments."""
    try:
        response = supabase.table("investments").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching investments: {e}")
        return pd.DataFrame()
