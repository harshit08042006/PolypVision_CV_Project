"""Dashboard header component."""
import streamlit as st


def render():
    """Render the dashboard top header bar."""
    # Use 3 cols: [Logo/Title] [Spacer] [Back Btn]
    col1, col2, col3 = st.columns([6, 2, 2])

    with col1:
        st.markdown(
            """
            <div class="dash-header">
                <div class="dash-header-left">
                    <div class="dash-logo">Pv</div>
                    <div>
                        <div class="dash-title">
                            PolypVision
                            <span class="badge badge-accent" style="margin-left:8px;font-size:0.72rem;">Clinical AI Demo</span>
                        </div>
                        <div class="dash-subtitle">Detection · Segmentation · Tracking · VLM assistant</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        # Pushing the button to the far right and aligning it vertically
        st.markdown('<div class="back-btn" style="text-align:right; margin-top:14px;">', unsafe_allow_html=True)
        if st.button("← Back", key="back_btn", width='stretch'):
            st.session_state.page = "landing"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
