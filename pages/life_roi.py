import streamlit as st
import pandas as pd
import plotly.express as px
from core.supabase_client import get_authenticated_client
from core.navigation import setup_navigation_with_context

# Initialize Supabase
supabase = get_authenticated_client()

setup_navigation_with_context("Personal Dev")

def fetch_logs():
    try:
        user_id = st.session_state['user'].id
        # Join with activities to get the name and return_type
        response = supabase.table("activity_logs").select("*, activities(name, return_type)").execute()
        
        if response.data:
            data = []
            for item in response.data:
                flattened = item.copy()
                flattened["activity_name"] = item["activities"]["name"] if item["activities"] else "Unknown"
                flattened["return_type"] = item["activities"]["return_type"] if item["activities"] else "None"
                del flattened["activities"]
                data.append(flattened)
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        # st.error(f"Error fetching logs: {e}")
        return pd.DataFrame()

def show_life_roi_page():
    st.title("💡 Life ROI Dashboard")
    st.markdown("Analyze where your time goes vs. the value (Happiness & Impact) it generates.")

    df = fetch_logs()

    if df.empty:
        st.info("No activity logs found. Start logging your days to see insights!")
        return

    # --- 1. THE MATRIX (Happiness vs Impact) ---
    st.subheader("The Life Matrix: Happiness vs. Impact")
    st.caption("Are you spending time on things that bring high Value AND High Joy?")

    # Group by activity to get averages
    activity_stats = df.groupby('activity_name').agg({
        'happiness_score': 'mean',
        'impact_score': 'mean',
        'duration_minutes': 'sum',
        'return_type': 'first'
    }).reset_index()

    # Convert minutes to hours for bubble size
    activity_stats['hours_spent'] = activity_stats['duration_minutes'] / 60

    fig = px.scatter(
        activity_stats,
        x="impact_score",
        y="happiness_score",
        size="hours_spent",
        color="return_type",
        hover_name="activity_name",
        text="activity_name",
        labels={
            "impact_score": "Impact / Value (Low to High)",
            "happiness_score": "Happiness / Inner Peace (Low to High)",
            "return_type": "Return Type"
        },
        range_x=[0, 11],
        range_y=[0, 11],
        size_max=60,
        template="plotly_dark",
        height=600
    )

    # Add Quadrant Backgrounds/Lines
    fig.add_hline(y=5.5, line_dash="dash", line_color="gray", annotation_text="Happiness Baseline")
    fig.add_vline(x=5.5, line_dash="dash", line_color="gray", annotation_text="Impact Baseline")

    # Annotations for Quadrants
    fig.add_annotation(x=9, y=9, text="✨ THE SWEET SPOT", showarrow=False, font=dict(color="green", size=14))
    fig.add_annotation(x=2, y=9, text="🍦 GUILTY PLEASURES", showarrow=False, font=dict(color="orange", size=10))
    fig.add_annotation(x=9, y=2, text="💪 THE GRIND", showarrow=False, font=dict(color="blue", size=10))
    fig.add_annotation(x=2, y=2, text="🗑️ TIME WASTE", showarrow=False, font=dict(color="red", size=10))

    st.plotly_chart(fig, use_container_width=True)

    # --- 2. TIME ALLOCATION ---
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Time by Return Type")
        pie_fig = px.pie(
            activity_stats, 
            values='hours_spent', 
            names='return_type', 
            title='Where is your time going?',
            hole=0.4
        )
        st.plotly_chart(pie_fig, use_container_width=True)

    with col2:
        st.subheader("Top Activities by Volume")
        bar_fig = px.bar(
            activity_stats.sort_values('hours_spent', ascending=True).tail(10),
            x='hours_spent',
            y='activity_name',
            orientation='h',
            title='Most Time Consuming Activites (Hours)'
        )
        st.plotly_chart(bar_fig, use_container_width=True)

if __name__ == "__main__":
    show_life_roi_page()
