from core.supabase_client import get_authenticated_client
import pandas as pd
import streamlit as st

# --- Helper Functions ---
def add_category(name, type):
    """Add a new category."""
    try:
        supabase = get_authenticated_client()
        user = st.session_state.get('user')
        if not user:
            st.error("User not authenticated")
            return None
            
        data = {"name": name, "type": type, "user_id": user.id}
        response = supabase.table("categories").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding category: {e}")
        return None

def get_categories(type_filter=None):
    """Fetch categories, optionally filtered by type (expense, income, etc.)."""
    try:
        supabase = get_authenticated_client()
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
        supabase = get_authenticated_client()
        user = st.session_state.get('user')
        if not user:
            st.error("User not authenticated")
            return None
            
        data = {
            "name": name, 
            "type": type, 
            "balance": balance, 
            "currency": currency,
            "user_id": user.id
        }
        response = supabase.table("accounts").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding account: {e}")
        return None

def get_accounts():
    """Fetch all accounts."""
    try:
        supabase = get_authenticated_client()
        response = supabase.table("accounts").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching accounts: {e}")
        return pd.DataFrame()

def get_exchange_rates():
    """Fetch exchange rates (Base: EUR)."""
    try:
        supabase = get_authenticated_client()
        response = supabase.table("exchange_rates").select("*").execute()
        data = response.data
        # Convert to dict {currency: rate}
        return {item['currency_code']: item['rate_to_eur'] for item in data}
    except Exception as e:
        st.error(f"Error fetching rates: {e}")
        return {'EUR': 1.0}

def get_user_profile():
    """Fetch user profile from DB."""
    try:
        supabase = get_authenticated_client()
        user = st.session_state.get('user')
        if not user:
            return None
        
        response = supabase.table("profiles").select("*").eq("id", user.id).single().execute()
        return response.data
    except Exception as e:
        # Fail silently or log if needed, but don't break UI
        return None

# --- Expenses ---
def add_expense(date, amount, category_id, account_id, description, payment_method, currency="EUR", vendor=None, source="manual"):
    """Add a new expense with currency conversion."""
    try:
        supabase = get_authenticated_client()
        user = st.session_state.get('user')
        if not user:
            st.error("User not authenticated")
            return None
            
        # Calculate EUR amount
        rates = get_exchange_rates()
        rate = rates.get(currency, 1.0)
        amount_eur = amount * rate
            
        data = {
            "date": str(date),
            "amount": amount,
            "currency": currency,
            "amount_eur": amount_eur,
            "category_id": category_id,
            "account_id": account_id,
            "description": description,
            "payment_method": payment_method,
            "vendor": vendor,
            "source": source,
            "user_id": user.id
        }
        response = supabase.table("expenses").insert(data).execute()
        
        # Update Account Balance (Incremental)
        adjust_account_balance(account_id, -amount_eur)
        
        return response
    except Exception as e:
        st.error(f"Error adding expense: {e}")
        return None

def get_expenses():
    """Fetch expenses with category and account details."""
    try:
        supabase = get_authenticated_client()
        response = supabase.table("expenses").select(
            "*, categories(name), accounts(name)"
        ).order("date", desc=True).execute()
        
        data = response.data
        if data:
            df = pd.json_normalize(data)
            df.rename(columns={'categories.name': 'category', 'accounts.name': 'account'}, inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching expenses: {e}")
        return pd.DataFrame()

# --- Income ---
def add_income(date, amount, category_id, account_id, source, currency="EUR", notes=None):
    """Add a new income record."""
    try:
        supabase = get_authenticated_client()
        user = st.session_state.get('user')
        if not user:
            st.error("User not authenticated")
            return None
            
        # Calculate EUR amount
        rates = get_exchange_rates()
        rate = rates.get(currency, 1.0)
        amount_eur = amount * rate
            
        data = {
            "date": str(date),
            "amount": amount,
            "currency": currency,
            "amount_eur": amount_eur,
            "category_id": category_id,
            "account_id": account_id,
            "source": source,
            "notes": notes,
            "user_id": user.id
        }
        response = supabase.table("income").insert(data).execute()
        
        # Update Account Balance (Incremental)
        adjust_account_balance(account_id, amount_eur)
        
        return response
    except Exception as e:
        st.error(f"Error adding income: {e}")
        return None

def get_income():
    """Fetch income records."""
    try:
        supabase = get_authenticated_client()
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

def adjust_account_balance(account_id, amount_eur_delta):
    """Incrementally update account balance."""
    try:
        supabase = get_authenticated_client()
        
        # Fetch account details
        acc_res = supabase.table("accounts").select("currency, balance").eq("id", account_id).single().execute()
        if not acc_res.data: return
        
        currency = acc_res.data.get('currency', 'EUR')
        current_balance = acc_res.data.get('balance', 0.0)
        if current_balance is None: current_balance = 0.0
        
        # Convert delta to Account Currency
        rates = get_exchange_rates()
        rate = rates.get(currency, 1.0)
        if not rate: rate = 1.0
        
        amount_native_delta = amount_eur_delta / rate
        
        new_balance = current_balance + amount_native_delta
        
        # Update account
        supabase.table("accounts").update({"balance": new_balance}).eq("id", account_id).execute()
        
    except Exception as e:
        print(f"Error adjusting balance: {e}")

# --- Savings ---
def add_saving_goal(name, target_amount, deadline, notes=None):
    """Add a new savings goal."""
    try:
        supabase = get_authenticated_client()
        user = st.session_state.get('user')
        if not user:
            st.error("User not authenticated")
            return None
            
        data = {
            "goal_name": name,
            "target_amount": target_amount,
            "deadline": str(deadline),
            "notes": notes,
            "user_id": user.id
        }
        response = supabase.table("saving_goals").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding savings goal: {e}")
        return None

def get_saving_goals():
    """Fetch all savings goals."""
    try:
        supabase = get_authenticated_client()
        response = supabase.table("saving_goals").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching savings goals: {e}")
        return pd.DataFrame()

# --- Investments ---
def add_investment(date, amount, instrument_name, investment_type, action, account_id, category_id, units, price_per_unit, currency="EUR"):
    """Add a new investment transaction with currency conversion."""
    try:
        supabase = get_authenticated_client()
        user = st.session_state.get('user')
        if not user:
            st.error("User not authenticated")
            return None
            
        # Calculate EUR amount
        rates = get_exchange_rates()
        rate = rates.get(currency, 1.0)
        amount_eur = amount * rate
            
        data = {
            "date": str(date),
            "amount": amount,
            "currency": currency,
            "amount_eur": amount_eur,
            "instrument_name": instrument_name,
            "investment_type": investment_type,
            "action": action,
            "account_id": account_id,
            "category_id": category_id,
            "units": units,
            "price_per_unit": price_per_unit,
            "source": "manual",
            "user_id": user.id
        }
        response = supabase.table("investments").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Error adding investment: {e}")
        return None

def get_investments():
    """Fetch all investments."""
    try:
        supabase = get_authenticated_client()
        response = supabase.table("investments").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching investments: {e}")
        return pd.DataFrame()

# --- Budgets ---
def add_budget(category_id, amount, month):
    """Add or update a budget for a category and month."""
    try:
        supabase = get_authenticated_client()
        user = st.session_state.get('user')
        if not user:
            st.error("User not authenticated")
            return None
            
        # Check if budget exists
        existing = supabase.table("budgets").select("id").eq("category_id", category_id).eq("month", month).execute()
        
        data = {
            "category_id": category_id,
            "budget_amount": amount,
            "month": month,
            "user_id": user.id
        }
        
        if existing.data:
            # Update
            response = supabase.table("budgets").update(data).eq("id", existing.data[0]['id']).execute()
        else:
            # Insert
            response = supabase.table("budgets").insert(data).execute()
            
        return response
    except Exception as e:
        st.error(f"Error saving budget: {e}")
        return None

def get_budgets(month):
    """Fetch budgets for a specific month."""
    try:
        supabase = get_authenticated_client()
        response = supabase.table("budgets").select("*, categories(name)").eq("month", month).execute()
        
        data = response.data
        if data:
            df = pd.json_normalize(data)
            df.rename(columns={'categories.name': 'category'}, inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching budgets: {e}")
        return pd.DataFrame()
def add_transfer(date, amount, source_id, dest_id, notes, dest_amount=None, exchange_rate=1.0):
    """
    Records a transfer between two accounts and updates their balances.
    Supports cross-currency transfers if dest_amount is provided.
    """
    try:
        supabase = get_authenticated_client()
        # If dest_amount is not provided, assume same currency (1:1)
        final_dest_amount = dest_amount if dest_amount is not None else amount
        
        # 1. Record Transfer
        response = supabase.table('transfers').insert({
            "date": str(date),
            "amount": amount,
            "source_account_id": source_id,
            "destination_account_id": dest_id,
            "notes": notes,
            "destination_amount": final_dest_amount,
            "exchange_rate": exchange_rate
        }).execute()
        
        # 2. Update Source Account (Decrease Balance)
        src_res = supabase.table('accounts').select('balance').eq('id', source_id).execute()
        if src_res.data:
            curr_src = src_res.data[0]['balance']
            new_src = curr_src - amount
            supabase.table('accounts').update({'balance': new_src}).eq('id', source_id).execute()
            
        # 3. Update Destination Account (Increase Balance)
        dest_res = supabase.table('accounts').select('balance').eq('id', dest_id).execute()
        if dest_res.data:
            curr_dest = dest_res.data[0]['balance']
            new_dest = curr_dest + final_dest_amount
            supabase.table('accounts').update({'balance': new_dest}).eq('id', dest_id).execute()
            
        return response
    except Exception as e:
        st.error(f"Error adding transfer: {e}")
        return None
