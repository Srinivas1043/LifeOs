import streamlit as st
import pandas as pd
import json
import base64
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.ai_client import init_groq
from core.finance_queries import get_categories, get_accounts, add_expense
from core.navigation import setup_navigation

setup_navigation()

st.title("🤖 Smart Ingestor")
st.caption("Upload a receipt image or paste text to extract details.")

# --- Helper to get context ---
def get_context():
    cats = get_categories('expense')['name'].tolist()
    accs = get_accounts()['name'].tolist()
    return cats, accs

# --- Tabs ---
tab1, tab2 = st.tabs(["🖼️ Image Upload", "📝 Text Input"])

with tab1:
    uploaded_file = st.file_uploader("Upload Receipt", type=['png', 'jpg', 'jpeg'])
    if uploaded_file and st.button("✨ Scan Receipt"):
        with st.spinner("Analyzing image..."):
            try:
                # Encode image
                image_bytes = uploaded_file.getvalue()
                image_b64 = base64.b64encode(image_bytes).decode()
                
                # Init Vision Model
                llm_vision = init_groq(model_name="llama-3.2-11b-vision-preview")
                
                cats, accs = get_context()
                
                prompt_text = f"""
                Extract the following details from this receipt image:
                - date (YYYY-MM-DD)
                - amount (float)
                - merchant (string)
                - category (choose best match from: {cats})
                - account (choose best match from: {accs})
                - description (short summary)
                
                Return ONLY a valid JSON object. Do not include markdown formatting like ```json.
                """
                
                msg = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                        },
                    ]
                )
                
                response = llm_vision.invoke([msg])
                
                # Parse JSON
                content = response.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                result = json.loads(content)
                st.session_state['parsed_data'] = result
                st.success("Image Scanned!")
                
            except Exception as e:
                st.error(f"Vision Error: {e}")

with tab2:
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
            amount = st.number_input("Amount", value=float(data.get('amount', 0.0)))
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
            
        description = st.text_area("Description", value=data.get('description', ''))
        
        submitted = st.form_submit_button("💾 Save Expense")
        
        if submitted:
            # Get IDs
            cat_id = int(get_categories()[get_categories()['name'] == category].iloc[0]['id'])
            acc_id = int(get_accounts()[get_accounts()['name'] == account].iloc[0]['id'])
            
            res = add_expense(str(date), amount, cat_id, acc_id, description, "card", merchant)
            if res:
                st.success("Saved successfully!")
                del st.session_state['parsed_data']
                st.rerun()
