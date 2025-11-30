import streamlit as st
from langchain_groq import ChatGroq

def init_groq(model_name="llama-3.3-70b-versatile"):
    """Initialize the Groq LLM client."""
    try:
        api_key = st.secrets["groq"]["api_key"]
        llm = ChatGroq(
            temperature=0, 
            groq_api_key=api_key, 
            model_name=model_name
        )
        return llm
    except Exception as e:
        st.error(f"Error initializing Groq: {e}")
        return None
