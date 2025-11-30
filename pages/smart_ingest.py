import streamlit as st
import pandas as pd
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.ai_client import init_groq
from core.finance_queries import get_categories, get_accounts, add_expense
from core.navigation import setup_navigation

setup_navigation()

st.title("🤖 Smart Ingestor")
st.caption("Paste text to extract details.")

# --- Helper to get context ---
def get_context():
    cats = get_categories('expense')['name'].tolist()
    accs = get_accounts()['name'].tolist()
    return cats, accs

# --- Text Input Only ---
raw_text = st.text_area("Paste Receipt Text", height=150, placeholder="e.g. 'Uber ride on Oct 24 cost 15.50 euros'")
if st.button("✨ Parse Text"):
    if raw_text:
        with st.spinner("Reading text..."):
            try:
                llm = init_groq() # Default text model
                cats, accs = get_context()
                
                parser = JsonOutputParser()
                prompt = PromptTemplate(
                    template="""
                    Extract details:
                    - date (YYYY-MM-DD)
                    - amount (float)
                    - merchant (string)
                    - category (choose from: {categories})
                    - account (choose from: {accounts})
                    - description (short summary)
                    
                    Text: {text}
                    
                    {format_instructions}
                    """,
                    input_variables=["text", "categories", "accounts"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                chain = prompt | llm | parser
                result = chain.invoke({"text": raw_text, "categories": cats, "accounts": accs})
                
                st.session_state['parsed_data'] = result
                st.success("Text Parsed!")
            except Exception as e:
                st.error(f"Text Error: {e}")

# --- Review Section ---
if 'parsed_data' in st.session_state:
    st.divider()
    st.subheader("Review & Save")
    
    data = st.session_state['parsed_data']
    
    with st.form("review_form"):
        col1, col2 = st.columns(2)
        with col1:
            # Handle date parsing safely
            try:
                default_date = pd.to_datetime(data.get('date', 'today')).date()
            except:
                default_date = pd.to_datetime('today').date()
                
            date = st.date_input("Date", value=default_date)
            col_amt, col_curr = st.columns([2, 1])
            with col_amt:
                amount = st.number_input("Amount", value=float(data.get('amount', 0.0)))
            with col_curr:
                currency = st.selectbox("Currency", ["EUR", "USD", "INR", "GBP"], index=0) # Default EUR
            
            merchant = st.text_input("Merchant", value=data.get('merchant', ''))
        
        with col2:
            cats, accs = get_context()
            
            # Try to match category/account
            try:
                cat_idx = cats.index(data.get('category'))
            except:
                cat_idx = 0
                
            try:
                acc_idx = accs.index(data.get('account'))
            except:
                acc_idx = 0
            
            category = st.selectbox("Category", cats, index=cat_idx)
            account = st.selectbox("Account", accs, index=acc_idx)
            payment_method = st.selectbox("Payment Method", ["card", "upi", "bank", "cash", "tikkie"])
            
        description = st.text_area("Description", value=data.get('description', ''))
        
        submitted = st.form_submit_button("💾 Save Expense")
        
        if submitted:
            # Get IDs
            cat_id = int(get_categories()[get_categories()['name'] == category].iloc[0]['id'])
            acc_id = int(get_accounts()[get_accounts()['name'] == account].iloc[0]['id'])
            
            res = add_expense(str(date), amount, cat_id, acc_id, description, payment_method, currency, merchant)
            if res:
                st.success("Saved successfully!")
                del st.session_state['parsed_data']
                st.rerun()
