import streamlit as st
import pandas as pd
from datetime import date
from core.supabase_client import get_authenticated_client
from core.navigation import setup_navigation_with_context

# Initialize Supabase
supabase = get_authenticated_client()

setup_navigation_with_context("Personal Dev")

def fetch_activities():
    try:
        response = supabase.table("activities").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        # st.error(f"Error fetching activities: {e}") # Suppress for now if empty
        return pd.DataFrame()

def log_activity(activity_id, activity_date, duration, happiness, impact, notes):
    try:
        user_id = st.session_state['user'].id
        data = {
            "user_id": user_id,
            "activity_id": activity_id,
            "date": str(activity_date),
            "duration_minutes": duration,
            "happiness_score": happiness,
            "impact_score": impact,
            "notes": notes
        }
        supabase.table("activity_logs").insert(data).execute()
        st.success("Activity logged successfully!")
    except Exception as e:
        st.error(f"Error logging activity: {e}")

def fetch_todays_logs(day):
    try:
        user_id = st.session_state['user'].id
        response = supabase.table("activity_logs").select("*, activities(name)").eq("date", str(day)).execute()
        
        # Flatten the response because of the join
        if response.data:
            data = []
            for item in response.data:
                flattened = item.copy()
                flattened["activity_name"] = item["activities"]["name"] if item["activities"] else "Unknown"
                del flattened["activities"]
                data.append(flattened)
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        # st.error(f"Error fetching logs: {e}")
        return pd.DataFrame()

def show_tracker_page():
    st.title("📝 Daily Activity Logger")
    st.markdown("Track what you did today and how it made you feel.")

    activities_df = fetch_activities()

    if activities_df.empty:
        st.warning("You haven't defined any activities yet. Go to **Personal Goals** to create them first.")
        return

    # --- INPUT FORM ---
    with st.container(border=True):
        st.subheader("Log New Activity")
        
        # Create a dict for the selectbox: Name -> ID
        activity_map = {row['name']: row['id'] for index, row in activities_df.iterrows()}
        
        col1, col2 = st.columns(2)
        with col1:
            selected_activity_name = st.selectbox("Activity", options=list(activity_map.keys()))
            selected_activity_id = activity_map[selected_activity_name] if selected_activity_name else None
            
            activity_date = st.date_input("Date", value=date.today())
            duration = st.number_input("Duration (minutes)", min_value=1, value=60, step=15)
        
        with col2:
            # Prefill sliders based on default values if possible (requires more complex state management, keeping simple for now)
            # Find defaults for selected activity
            defaults = activities_df[activities_df['id'] == selected_activity_id].iloc[0]
            
            st.write(f"**Return Type:** {defaults['return_type']}")
            
            happiness = st.slider("Happiness / Inner Peace (1-10)", 1, 10, int(defaults['default_happiness']), help="How did you feel doing this?")
            impact = st.slider("Perceived Impact/Value (1-10)", 1, 10, int(defaults['impact_score']), help="Did this actually move the needle?")
        
        notes = st.text_area("Notes", placeholder="Any thoughts? (Optional)")
        
        if st.button("Log Activity", type="primary"):
            log_activity(selected_activity_id, activity_date, duration, happiness, impact, notes)
            st.rerun()

    # --- TODAY'S LOGS ---
    st.divider()
    st.subheader(f"Logged for {activity_date.strftime('%B %d, %Y')}")
    
    todays_df = fetch_todays_logs(activity_date)
    
    if not todays_df.empty:
        # Simple Table
        display_cols = ["activity_name", "duration_minutes", "happiness_score", "impact_score", "notes"]
        st.dataframe(todays_df[display_cols], width=1000)
        
        # Mini Summary
        total_mins = todays_df['duration_minutes'].sum()
        avg_happy = todays_df['happiness_score'].mean()
        st.caption(f"Total Time: {total_mins//60}h {total_mins%60}m | Avg Happiness: {avg_happy:.1f}/10")
    else:
        st.info("Nothing logged for this date yet.")

if __name__ == "__main__":
    show_tracker_page()
