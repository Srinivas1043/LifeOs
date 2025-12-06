import streamlit as st
from core.finance_queries import get_exchange_rates, get_user_profile
# from st_pages import show_pages_from_config, add_page_title # Not needed for manual nav

def setup_navigation():
    """
    Sets up the custom Top Navigation and global styles.
    Removes the default sidebar.
    """
    # --- Global Config ---
    try:
        st.set_page_config(page_title="Life OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")
    except:
        pass # Ignore if already set

    # --- Custom CSS (Premium UI) ---
    st.markdown("""
    <style>
        /* Import Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Inter:wght@400;600&display=swap');

        /* Global Reset & Colors */
        :root {
            --bg-color: #0E1117;
            --surface-color: #161B22;
            --border-color: #30363D;
            --primary-color: #238636;
            --text-primary: #ECEFF4;
            --text-secondary: #8B949E;
        }

        html, body, [class*="css"] {
            font-family: 'Outfit', 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
        }

        /* Hide Streamlit Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;} /* Force hide sidebar */
        
        /* Custom Top Nav */
        .top-nav {
            background-color: var(--surface-color);
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .nav-links {
            display: flex;
            gap: 20px;
        }
        
        .nav-item {
            text-decoration: none;
            color: var(--text-secondary);
            font-weight: 500;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.2s;
        }
        
        .nav-item:hover {
            background-color: #21262D;
            color: white;
        }
        
        .nav-item.active {
            background-color: #1F242C;
            color: #58A6FF;
            border-bottom: 2px solid #58A6FF;
        }

        /* Sub Nav (Tier 2) */
        .sub-nav {
            display: flex;
            gap: 10px;
            padding: 0 2rem 1rem 2rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
            overflow-x: auto;
        }

        /* Card Styling */
        div[data-testid="stMetric"], div.stContainer {
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
        }

    </style>
    """, unsafe_allow_html=True)

    # --- Auth Check ---
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # Allow login page to render without nav
    current_page = st.navigation.get_current_page_name() if hasattr(st.navigation, "get_current_page_name") else ""
    # Fallback for finding page name if newest st version isn't available, but usually ok.
    # Actually, we can just check if we are authenticated. 
    
    if not st.session_state['authenticated']:
        # Redirect to login
        try:
            st.switch_page("pages/login.py")
        except Exception:
            # Fallback if switch_page fails (e.g. if already on it, but setup_navigation isn't called there)
            st.error("Please log in.")
            st.stop()
        return

    # --- TOP NAVIGATION BAR ---
    
    # 1. Header Row (Logo + Modules + User)
    with st.container():
        c1, c2, c3 = st.columns([1, 3, 1])
        
        with c1:
            st.markdown("### 🧬 Life OS")
        
        with c2:
            # Modules
            # We determine active module by current page
            # Mapping
            finance_pages = ["app", "income", "expenses", "investments", "budget", "transfer", "savings", "tax", "monthly_report"]
            personal_pages = ["life_roi", "tracker", "personal_goals"]
            ai_pages = ["smart_ingest", "ai_assistant"]
            system_pages = ["settings", "admin"]
            
            # Simple heuristic
            active_mod = "Finance" # Default
            # We need to know current script name. 
            # Streamlit doesn't give a clean "current page" easily in all versions, 
            # but we can assume the user clicked a link.
            
            # Use columns for buttons acting as tabs
            m1, m2, m3, m4 = st.columns(4)
            m1.page_link("app.py", label="Finance", icon="💰")
            m2.page_link("pages/life_roi.py", label="Personal Dev", icon="🌱")
            m3.page_link("pages/smart_ingest.py", label="AI Tools", icon="🤖")
            m4.page_link("pages/settings.py", label="System", icon="⚙️")

        with c3:
            # User & Currency
            if 'user' in st.session_state:
                # user_email = st.session_state['user'].email
                # st.caption(f"{user_email}")
                if st.button("Logout", key="top_logout", type="primary", use_container_width=True):
                    st.session_state['authenticated'] = False
                    st.rerun()

    # 2. Sub-Navigation Row (Context Sensitive)
    # Detect module by checking file path? Hard in streamlit cloud sometimes.
    # Re-use session state for "current_module" if we set it on click? 
    # Or just show ALL links but highlight active? No, that's cluttered.
    
    # Let's try to infer from imports or just explicit lists.
    # Since this function is called FROM the page, we can inspect __main__?
    # No, let's just use st.session_state to track 'active_module' if we can, 
    # BUT st.page_link does full reload.
    
    # Alternative: Show sub-nav based on where we are.
    # We can't easily know filename without 'os' hacks or specific vars.
    # Let's try a reliable hack: The page sets a var before calling setup?
    # No, too invasive.
    
    # Let's just render the sub-nav for the module that "Overview" page belongs to.
    # Actually, simpler: The user clicked "Finance" -> app.py. 
    # In app.py, we know it's Finance.
    
    # Let's make setup_navigation accept an optional 'module_name' arg!
    # Refactoring all pages to pass their module name is cleaner and robust.
    pass

def setup_navigation_with_context(module_name="Finance"):
    """
    Call this from pages with the module name.
    """
    setup_navigation() # Base setup
    
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        return

    st.divider()
    
    # Render Sub-Nav for the active module
    if module_name == "Finance":
        cols = st.columns(9)
        cols[0].page_link("app.py", label="Overview", icon="🏠")
        cols[1].page_link("pages/income.py", label="Income", icon="💰")
        cols[2].page_link("pages/expenses.py", label="Expenses", icon="💸")
        cols[3].page_link("pages/investments.py", label="Investments", icon="📈")
        cols[4].page_link("pages/budget.py", label="Budget", icon="⚖️")
        cols[5].page_link("pages/transfer.py", label="Transfer", icon="💸")
        cols[6].page_link("pages/savings.py", label="Savings", icon="🎯")
        cols[7].page_link("pages/tax.py", label="Tax", icon="🏛️")
        cols[8].page_link("pages/monthly_report.py", label="Report", icon="📅")
        
    elif module_name == "Personal Dev":
        cols = st.columns(3)
        cols[0].page_link("pages/life_roi.py", label="Life ROI", icon="💡")
        cols[1].page_link("pages/tracker.py", label="Daily Logger", icon="📝")
        cols[2].page_link("pages/personal_goals.py", label="Goals & Activities", icon="🎯")
        
    elif module_name == "AI Tools":
        cols = st.columns(2)
        cols[0].page_link("pages/smart_ingest.py", label="Smart Ingestor", icon="🤖")
        cols[1].page_link("pages/ai_assistant.py", label="AI Assistant", icon="💬")
        
    elif module_name == "System":
        cols = st.columns(2)
        cols[0].page_link("pages/settings.py", label="Settings", icon="⚙️")
        cols[1].page_link("pages/admin.py", label="Admin", icon="🛡️")

    st.divider()
