import streamlit as st
from core.finance_queries import get_accounts, sync_account_balance
from core.supabase_client import init_supabase

# Mock session state for auth if needed, or rely on env vars
# Assuming running via 'streamlit run' will pick up existing session if we are lucky, 
# but for a script we might need to re-auth or just assume the client works if env vars are set.
# Actually, finance_queries uses st.session_state['user']. 
# We'll try to run this as a page temporarily or just inject it.

st.title("🔄 Syncing Balances...")

try:
    accounts = get_accounts()
    if not accounts.empty:
        progress = st.progress(0)
        for i, row in accounts.iterrows():
            acc_id = row['id']
            acc_name = row['name']
            st.write(f"Syncing {acc_name}...")
            sync_account_balance(acc_id)
            progress.progress((i + 1) / len(accounts))
            
        st.success("All balances synced successfully!")
    else:
        st.warning("No accounts found.")
except Exception as e:
    st.error(f"Error: {e}")
