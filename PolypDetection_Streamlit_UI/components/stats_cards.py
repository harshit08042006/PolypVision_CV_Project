"""Stats cards row component."""
import streamlit as st
from components.data_loader import load_dynamic_data

def render():
    """Render the four metric cards."""
    # Check if any analysis has been run
    analysis_done = st.session_state.get("detection_done") or st.session_state.get("segmentation_done")
    
    STATS, _ = load_dynamic_data()
    cols = st.columns(4, gap="medium")

    for col, (_, stat) in zip(cols, STATS.items()):
        
        # Display placeholders if no analysis is done yet
        display_value = stat["value"] if analysis_done else "---"
        display_desc = stat["description"] if analysis_done else "Waiting for analysis"
        
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-icon">{stat["icon"]}</div>
                    <div class="stat-label">{stat["label"]}</div>
                    <div class="stat-value">{display_value}</div>
                    <div class="stat-desc">{display_desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
