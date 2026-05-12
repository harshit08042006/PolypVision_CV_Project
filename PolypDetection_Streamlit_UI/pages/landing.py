"""Landing page – PolypVision home screen."""
import streamlit as st
from mock_data import FEATURES


def _go_to_dashboard():
    """Callback – navigate to the dashboard page."""
    st.session_state.page = "dashboard"


def render():
    """Render the landing / home page."""

    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

    col_left, col_spacer, col_right = st.columns([5, 1, 4])

    # ── Left: Hero Section ──────────────────────────────────
    with col_left:
        st.markdown(
            """
            <div class="badge badge-primary" style="margin-bottom:24px;">
                🔬 PolypVision | Colonoscopy AI Assistant
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="hero-title">
                Smart colonoscopy review with detection,
                segmentation, and a medical VLM.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="hero-subtitle">
                A clean health-tech dashboard: view bounding boxes,
                segmented output, keyframes, and ask polyp-related
                questions in natural language.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

        # Feature pills – 2×2 grid
        feat_cols = st.columns(2, gap="medium")
        for i, feat in enumerate(FEATURES):
            with feat_cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="feature-pill">
                        <div class="fp-title">{feat["icon"]} {feat["title"]}</div>
                        <div class="fp-desc">{feat["description"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if i < 2:
                    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # ── Right: Login Card ───────────────────────────────────
    with col_right:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="login-card">
                <div class="badge badge-demo" style="margin-bottom:18px;">
                    ✅ Demo access
                </div>
                <h2>Enter the dashboard</h2>
                <p>No login needed. Continue directly to the analysis workspace.</p>
            """,
            unsafe_allow_html=True,
        )

        project_name = st.text_input(
            "Project name",
            value="PolypVision",
        )

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        st.button(
            "Open Analysis Workspace →",
            key="open_workspace",
            width='stretch',
            type="primary",
            on_click=_go_to_dashboard,
        )

        st.markdown(
            """
                <div style="margin-top:16px;">
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
