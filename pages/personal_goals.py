import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from core.supabase_client import get_authenticated_client
from core.navigation import setup_navigation_with_context

# Initialize Supabase
supabase = get_authenticated_client()

setup_navigation_with_context("Personal Dev")

def fetch_goals():
    try:
        response = supabase.table("life_goals").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching goals: {e}")
        return pd.DataFrame()

def fetch_activities():
    try:
        response = supabase.table("activities").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching activities: {e}")
        return pd.DataFrame()

def add_goal(title, description, category, target_date):
    try:
        user_id = st.session_state['user'].id
        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "category": category,
            "target_date": str(target_date),
            "status": "Active"
        }
        supabase.table("life_goals").insert(data).execute()
        st.success(f"Goal '{title}' added!")
    except Exception as e:
        st.error(f"Error adding goal: {e}")

def add_activity(name, goal_id, default_happiness, return_type, impact_score):
    try:
        user_id = st.session_state['user'].id
        data = {
            "user_id": user_id,
            "name": name,
            "goal_id": goal_id if goal_id else None,
            "default_happiness": default_happiness,
            "return_type": return_type,
            "impact_score": impact_score
        }
        supabase.table("activities").insert(data).execute()
        st.success(f"Activity '{name}' added!")
    except Exception as e:
        st.error(f"Error adding activity: {e}")

def show_personal_goals_page():
    st.title("🎯 Personal Goals & Activities")
    st.markdown("Define your high-level goals and the activities that contribute to them.")

    tab1, tab2 = st.tabs(["Life Goals", "Activity Library"])

    # --- TAB 1: LIFE GOALS ---
    with tab1:
        st.subheader("Add New Life Goal")
        with st.form("new_goal_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Goal Title", placeholder="e.g., Run a Marathon")
                category = st.selectbox("Category", ["Health", "Career", "Financial", "Social", "Hobby", "Personal Development", "Other"])
            with col2:
                target_date = st.date_input("Target Date", min_value=date.today())
                description = st.text_area("Description / Motivation", placeholder="Why do you want to achieve this?")
            
            submitted = st.form_submit_button("Create Goal")
            if submitted and title:
                add_goal(title, description, category, target_date)
                st.rerun()

        st.divider()
        st.subheader("My Active Goals")
        goals_df = fetch_goals()
        
        if not goals_df.empty:
            goals_df['target_date'] = pd.to_datetime(goals_df['target_date'])
            
            # Simple Status Filter
            status_filter = st.multiselect("Filter by Status", options=goals_df['status'].unique(), default=["Active"])
            filtered_goals = goals_df[goals_df['status'].isin(status_filter)]

            for index, row in filtered_goals.iterrows():
                with st.expander(f"{row['title']} ({row['category']})"):
                    st.write(f"**Target:** {row['target_date'].date()}")
                    st.write(f"**Description:** {row['description']}")
                    st.caption(f"Status: {row['status']}")
        else:
            st.info("No goals set yet. Start by adding one above!")

    # --- TAB 2: ACTIVITY LIBRARY ---
    with tab2:
        st.subheader("Define Your Activities")
        st.markdown("Create a library of activities to log. Assign them 'Return Types' (Financial, Emotional, etc.).")
        
        # Need goals for dropdown
        goals_df = fetch_goals()
        goal_options = {row['title']: row['id'] for index, row in goals_df.iterrows()} if not goals_df.empty else {}
        
        with st.form("new_activity_form"):
            col1, col2 = st.columns(2)
            with col1:
                act_name = st.text_input("Activity Name", placeholder="e.g., Gym, Coding, Gaming")
                # Goal Mapping
                sorted_goals = ["None"] + list(goal_options.keys())
                linked_goal = st.selectbox("Link to Goal (Optional)", sorted_goals)
                goal_id = goal_options.get(linked_goal) if linked_goal != "None" else None

            with col2:
                return_type = st.selectbox("Primary Return Type", ["Financial", "Emotional/Inner Peace", "Health", "Social", "Skill", "None"])
                default_happiness = st.slider("Expected Happiness (1-10)", 1, 10, 5)
                impact_score = st.slider("Life Impact Score (1-10)", 1, 10, 5, help="10 = Life changing, 1 = Waste of time")
            
            act_submitted = st.form_submit_button("Add Activity")
            if act_submitted and act_name:
                add_activity(act_name, goal_id, default_happiness, return_type, impact_score)
                st.rerun()

        st.divider()
        st.subheader("Activity Library")
        activities_df = fetch_activities()
        if not activities_df.empty:
            # Display as a dataframe for now, maybe cards later
            display_df = activities_df[['name', 'return_type', 'default_happiness', 'impact_score']].copy()
            st.dataframe(display_df, width=1000) # Streamlit dataframe width bug workaround or just remove arg if using default
        else:
            st.info("No activities defined yet.")

if __name__ == "__main__":
    show_personal_goals_page()
