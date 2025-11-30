import streamlit as st
import pandas as pd
import datetime
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from core.ai_client import init_groq
from core.finance_queries import get_expenses, get_income, get_accounts
from core.navigation import setup_navigation

setup_navigation()

st.title("💬 AI Financial Assistant")
st.caption("Ask questions about your spending, income, and financial health.")

# --- Helper: Get Financial Context ---
def get_financial_context():
    """Generates a summary of recent financial data for the AI."""
    try:
        # Fetch Data
        expenses = get_expenses()
        income = get_income()
        accounts = get_accounts()
        
        # Currency Config
        conversion_rate = st.session_state.get('conversion_rate', 1.0)
        currency = st.session_state.get('currency', 'EUR')
        
        # Date Filter (Last 30 Days)
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=30)
        
        # Process Expenses
        recent_expenses = pd.DataFrame()
        total_spent = 0
        top_categories = ""
        
        if not expenses.empty:
            expenses['date'] = pd.to_datetime(expenses['date'])
            recent_expenses = expenses[expenses['date'].dt.date >= start_date].copy()
            
            # Ensure amount_eur exists
            recent_expenses['amount_eur'] = recent_expenses.get('amount_eur', recent_expenses['amount']).fillna(recent_expenses['amount'])
            
            total_spent = recent_expenses['amount_eur'].sum() / conversion_rate
            
            # Top Categories
            cat_group = recent_expenses.groupby('category')['amount_eur'].sum().sort_values(ascending=False).head(5)
            top_categories = ", ".join([f"{cat} ({val/conversion_rate:.2f} {currency})" for cat, val in cat_group.items()])

        # Process Income
        total_income = 0
        if not income.empty:
            income['date'] = pd.to_datetime(income['date'])
            recent_income = income[income['date'].dt.date >= start_date].copy()
            
            recent_income['amount_eur'] = recent_income.get('amount_eur', recent_income['amount']).fillna(recent_income['amount'])
            total_income = recent_income['amount_eur'].sum() / conversion_rate

        # Process Accounts
        account_summary = ""
        if not accounts.empty:
            # Note: Account balances are snapshots, not historical. 
            # We assume they are roughly current or we'd need a complex ledger.
            # For now, listing them is helpful.
            acc_list = []
            for _, row in accounts.iterrows():
                # Simple conversion estimate if currency differs (not perfect without live rates for every acc)
                # But let's just list them as is for context
                acc_list.append(f"{row['name']} ({row['balance']} {row['currency']})")
            account_summary = ", ".join(acc_list)

        # Construct Context String
        context = f"""
        Financial Context (Last 30 Days, displayed in {currency}):
        - Total Income: {total_income:,.2f} {currency}
        - Total Expenses: {total_spent:,.2f} {currency}
        - Net Savings: {(total_income - total_spent):,.2f} {currency}
        - Top Expense Categories: {top_categories}
        - Current Accounts: {account_summary}
        
        Recent Transactions (Sample):
        """
        
        if not recent_expenses.empty:
            for _, row in recent_expenses.head(10).iterrows():
                amt = row['amount_eur'] / conversion_rate
                context += f"- {row['date'].date()}: {row['description']} ({row['category']}) - {amt:.2f} {currency}\n"
        
        return context
        
    except Exception as e:
        return f"Error generating context: {e}"

# --- Chat Interface ---

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="Hello! I'm your financial assistant. How can I help you today?")
    ]

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
    elif isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)

# Handle Input
if prompt := st.chat_input("Ask about your finances..."):
    # Display User Message
    st.chat_message("user").write(prompt)
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    # Generate Response
    with st.spinner("Thinking..."):
        try:
            llm = init_groq() # Default versatile model
            
            # Get Context
            context = get_financial_context()
            
            # System Prompt
            system_prompt = f"""You are a smart and helpful financial assistant for LifeOs. 
            You have access to the user's recent financial data (last 30 days).
            
            {context}
            
            Rules:
            1. Answer questions based strictly on the provided context.
            2. If you don't know the answer (e.g., data older than 30 days), say so politely.
            3. Be concise and encouraging.
            4. If the user asks for advice, provide general financial tips based on their spending habits visible in the context.
            5. Format currency values clearly (e.g., €150.00).
            """
            
            # Construct Message History for LLM
            # We'll send System + Last few messages to keep context window manageable
            messages = [SystemMessage(content=system_prompt)] + st.session_state.messages[-5:]
            
            response = llm.invoke(messages)
            
            # Display Assistant Response
            st.chat_message("assistant").write(response.content)
            st.session_state.messages.append(AIMessage(content=response.content))
            
        except Exception as e:
            st.error(f"Error: {e}")
