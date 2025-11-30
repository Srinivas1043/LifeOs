import streamlit as st
import pandas as pd
from core.finance_queries import add_saving_goal, get_saving_goals

st.title("🐷 Savings Goals")

with st.expander("➕ Add New Savings Goal", expanded=False):
    with st.form("add_goal_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Goal Name (e.g. Emergency Fund)")
            target = st.number_input("Target Amount", min_value=1.0, step=100.0)
        
        with col2:
            deadline = st.date_input("Deadline")
            notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Create Goal")
        if submitted:
            if name and target > 0:
                res = add_saving_goal(name, target, deadline, notes)
                if res:
                    st.success("Savings Goal created!")
                    st.rerun()
            else:
                st.warning("Please provide a name and target amount.")

# View Goals
st.subheader("🎯 Active Goals")
goals = get_saving_goals()

if not goals.empty:
    for index, row in goals.iterrows():
        # Calculate progress (mock logic for now as we don't have a 'savings' transactions table linked to goals yet in the simple UI)
        # In a real app, we'd sum up 'savings' transactions linked to this goal_id.
        # For now, we'll just show the goal details.
        
        st.markdown(f"### {row['goal_name']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Target", f"€{row['target_amount']:,.2f}")
        col2.metric("Deadline", row['deadline'])
        
        # Placeholder for progress bar
        st.progress(0) 
        st.caption("Link savings transactions to goals coming soon.")
        st.divider()
else:
    st.info("No savings goals set.")
