"""AI Output summary component."""
import streamlit as st
from mock_data import AI_OUTPUT_ITEMS


def render():
    """Render the AI output status items."""
    st.markdown(
        '<p style="font-weight:700;font-size:1rem;margin-bottom:10px;">✨ AI Output</p>',
        unsafe_allow_html=True,
    )

    for item in AI_OUTPUT_ITEMS:
        st.markdown(
            f"""
            <div class="ai-item">
                <div class="ai-item-icon">{item["icon"]}</div>
                <div>
                    <div class="ai-item-title">{item["title"]}</div>
                    <div class="ai-item-desc">{item["description"]}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
