import streamlit as st
import pandas as pd
from core.finance_queries import get_expenses, get_income

st.title("🏛️ Tax Center")

tab1, tab2 = st.tabs(["Tax Tracking", "Liability Estimator"])

with tab1:
    st.header("Tax Payments & Refunds")
    st.caption("Transactions with 'Tax', 'VAT', or 'BTW' in the category name.")

    # Fetch Data
    expenses = get_expenses()
    income = get_income()

    # Filter for Tax-related items
    # We assume categories containing "Tax", "VAT", "BTW" are tax related.
    # Case insensitive search.
    tax_keywords = ['tax', 'vat', 'btw', 'belasting']
    
    tax_expenses = pd.DataFrame()
    if not expenses.empty:
        # Check if category column exists and has values
        if 'category' in expenses.columns:
            mask = expenses['category'].str.contains('|'.join(tax_keywords), case=False, na=False)
            tax_expenses = expenses[mask]

    tax_income = pd.DataFrame()
    if not income.empty:
        if 'category' in income.columns:
            mask = income['category'].str.contains('|'.join(tax_keywords), case=False, na=False)
            tax_income = income[mask]

    # Metrics
    total_tax_paid = tax_expenses['amount'].sum() if not tax_expenses.empty else 0
    total_tax_refunded = tax_income['amount'].sum() if not tax_income.empty else 0
    net_tax_position = total_tax_paid - total_tax_refunded

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tax Paid", f"€{total_tax_paid:,.2f}")
    col2.metric("Tax Refunds", f"€{total_tax_refunded:,.2f}")
    col3.metric("Net Tax Outflow", f"€{net_tax_position:,.2f}")

    # Tables
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Tax Payments (Expenses)")
        if not tax_expenses.empty:
            st.dataframe(tax_expenses[['date', 'amount', 'category', 'description']], use_container_width=True)
        else:
            st.info("No tax expenses found. (Tip: Create a category like 'Income Tax')")

    with col_right:
        st.subheader("Tax Refunds (Income)")
        if not tax_income.empty:
            st.dataframe(tax_income[['date', 'amount', 'category', 'source']], use_container_width=True)
        else:
            st.info("No tax refunds found.")

with tab2:
    st.header("Simple Income Tax Estimator")
    st.caption("Estimate your annual income tax liability.")
    
    annual_income = st.number_input("Annual Gross Income (€)", min_value=0.0, step=1000.0, value=50000.0)
    tax_year = st.selectbox("Tax Year", [2024, 2025])
    
    # Simple progressive tax logic (Example: Netherlands Box 1 2024 approx)
    # This is a simplified estimation!
    st.markdown("### Estimated Calculation (NL Box 1 Approx)")
    
    bracket_1_limit = 75518
    rate_1 = 0.3697
    rate_2 = 0.4950
    
    tax_amount = 0
    if annual_income <= bracket_1_limit:
        tax_amount = annual_income * rate_1
    else:
        tax_amount = (bracket_1_limit * rate_1) + ((annual_income - bracket_1_limit) * rate_2)
        
    # General Tax Credit (Algemene heffingskorting) - Simplified
    # Max approx 3362, reduces as income grows
    general_credit = 0
    if annual_income < 24812:
        general_credit = 3362
    elif annual_income < 75518:
        general_credit = 3362 - 0.0663 * (annual_income - 24812)
    
    # Labour Tax Credit (Arbeidskorting) - Simplified
    labour_credit = 0
    if annual_income < 11490:
        labour_credit = 0.08425 * annual_income
    elif annual_income < 24820:
        labour_credit = 968 + 0.3143 * (annual_income - 11490)
    elif annual_income < 39957:
        labour_credit = 5158 + 0.0247 * (annual_income - 24820)
    elif annual_income < 124934:
        labour_credit = 5532 - 0.0651 * (annual_income - 39957)

    # Ensure credits don't go negative
    general_credit = max(0, general_credit)
    labour_credit = max(0, labour_credit)
    
    total_credits = general_credit + labour_credit
    final_tax = max(0, tax_amount - total_credits)
    net_income = annual_income - final_tax
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Estimated Tax", f"€{final_tax:,.2f}")
    c2.metric("Effective Rate", f"{(final_tax/annual_income)*100:.1f}%")
    c3.metric("Net Income", f"€{net_income:,.2f}")
    
    st.warning("⚠️ This is a simplified estimation for the Netherlands. Consult a tax advisor for accurate results.")
