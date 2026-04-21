"""System snapshot component."""
import streamlit as st
from mock_data import SYSTEM_SNAPSHOT


def render():
    """Render the system snapshot info card."""
    st.markdown(
        '<p style="font-weight:700;font-size:0.95rem;margin-bottom:10px;">⏱ System Snapshot</p>',
        unsafe_allow_html=True,
    )

    for key, val in SYSTEM_SNAPSHOT:
        st.markdown(
            f"""
            <div class="snapshot-row">
                <span class="snapshot-key">{key}</span>
                <span class="snapshot-val">{val}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
