import streamlit as st
from core.finance_queries import get_exchange_rates, get_user_profile

def setup_navigation():
    """
    Sets up the custom sidebar navigation and global styles.
    Should be called at the top of every page.
    """
    # --- Global Config ---
    st.set_page_config(page_title="Life OS", page_icon="🧬", layout="wide")

    # --- Custom CSS ---
    st.markdown("""
    <style>
        /* Global Font & Colors */
        html, body, [class*="css"] {
            font-family: 'Outfit', 'Inter', sans-serif;
            background-color: #0E1117;
            color: #FAFAFA;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #161B22;
            border-right: 1px solid #30363D;
        }
        
        /* Cards / Metrics */
        div[data-testid="stMetric"] {
            background-color: #21262D;
            border: 1px solid #30363D;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: #58A6FF;
        }
        
        /* Buttons */
        button[kind="secondary"] {
            background-color: #21262D;
            border: 1px solid #30363D;
            color: #C9D1D9;
        }
        button[kind="primary"] {
            background-color: #238636;
            border: none;
            color: white;
        }
        
        /* Headers */
        h1, h2, h3 {
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        h1 {
            background: -webkit-linear-gradient(45deg, #58A6FF, #8B949E);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Inputs */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #0D1117;
            border-color: #30363D;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Sidebar Navigation ---
    with st.sidebar:
        # Auth Check
        if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
            st.warning("Please Login")
            st.page_link("pages/login.py", label="Login", icon="🔐")
            st.stop() # Stop rendering the rest of the page if not logged in
            
        st.title("🧬 Life OS")
        
        # User Info
        if 'user' in st.session_state:
            user = st.session_state['user']
            # Try to fetch profile from DB
            profile = get_user_profile()
            full_name = profile.get('full_name', 'User') if profile else user.user_metadata.get('full_name', 'User')
            st.markdown(f"### 👋 Hi, {full_name}")
            st.caption(f"{user.email}")
        
        st.divider()

        # Global Currency Selector
        if 'exchange_rates' not in st.session_state:
             st.session_state['exchange_rates'] = get_exchange_rates()
        
        rates = st.session_state['exchange_rates']
        available_currencies = list(rates.keys()) if rates else ['EUR']
        if 'EUR' not in available_currencies: available_currencies.append('EUR')
        
        # Initialize global currency if not set
        if 'currency' not in st.session_state:
            st.session_state['currency'] = 'EUR'

        selected_currency = st.selectbox(
            "💱 Currency", 
            available_currencies, 
            index=available_currencies.index(st.session_state['currency']) if st.session_state['currency'] in available_currencies else 0
        )
        
        # Update session state
        st.session_state['currency'] = selected_currency
        st.session_state['conversion_rate'] = rates.get(selected_currency, 1.0)

        st.divider()

        # Module Selector
        module = st.selectbox("Module", ["Finance", "AI Tools", "System"])
        
        st.divider()
        
        if module == "Finance":
            st.caption("Finance Module")
            st.page_link("app.py", label="Overview", icon="🏠")
            st.page_link("pages/income.py", label="Income", icon="💰")
            st.page_link("pages/expenses.py", label="Expenses", icon="💸")
            st.page_link("pages/investments.py", label="Investments", icon="📈")
            st.page_link("pages/budget.py", label="Budget", icon="⚖️")
            st.page_link("pages/transfer.py", label="Transfer", icon="💸")
            st.page_link("pages/savings.py", label="Savings Goals", icon="🎯")
            st.page_link("pages/tax.py", label="Tax Center", icon="🏛️")
            st.page_link("pages/monthly_report.py", label="Monthly Report", icon="📅")
            
        elif module == "AI Tools":
            st.caption("AI Tools")
            st.page_link("pages/smart_ingest.py", label="Smart Ingestor", icon="🤖")
            st.page_link("pages/ai_assistant.py", label="AI Assistant", icon="💬")
            
        elif module == "System":
            st.caption("System")
            st.page_link("pages/settings.py", label="Settings", icon="⚙️")
            st.page_link("pages/admin.py", label="Admin", icon="🛡️")
            
        st.divider()
        
        if st.button("Logout", type="secondary"):
            st.session_state['authenticated'] = False
            st.rerun()
            
        st.caption("v1.3.0 • Life OS")
