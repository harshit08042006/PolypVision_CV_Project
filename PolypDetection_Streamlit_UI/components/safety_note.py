"""Safety note component."""
import streamlit as st


def render():
    """Render the safety disclaimer card."""
    st.markdown(
        '<p style="font-weight:700;font-size:0.95rem;margin-bottom:10px;">⚠️ Safety Note</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="safety-item">
            <span class="safety-item-icon">⚠️</span>
            <div>
                <div class="safety-item-title">AI can make mistakes.</div>
                <div class="safety-item-desc">Do not rely on the assistant as a final diagnosis tool.</div>
            </div>
        </div>
        <div class="safety-item" style="border-bottom:none;">
            <span class="safety-item-icon">ℹ️</span>
            <div>
                <div class="safety-item-title">Use as decision support only.</div>
                <div class="safety-item-desc">Clinical follow-up and expert review are still required.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
