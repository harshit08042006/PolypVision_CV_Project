"""Dashboard / Analysis workspace page."""
import streamlit as st
from components import header, stats_cards, video_preview, ai_output
from components import keyframes, vlm_chat, safety_note, system_snapshot


def render():
    """Render the full analysis dashboard."""

    # ── Header ──────────────────────────────────────────────
    header.render()

    # ── ROW 1: Stats (full width) ───────────────────────────
    stats_cards.render()

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── ROW 2: Main content (3 columns) ─────────────────────
    # Left: Upload + Video | Center: AI Output + Keyframes | Right: VLM Chat
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        # ── Case Upload + Video ─────────────
        with st.container(border=True):
            video_preview.render()

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # ── AI Output + Keyframes side by side ──
        col_ai, col_kf = st.columns(2, gap="medium")
        with col_ai:
            with st.container(border=True):
                ai_output.render()
        with col_kf:
            with st.container(border=True):
                keyframes.render()

    with col_right:
        # ── VLM Chat ───────────────────────
        with st.container(border=True):
            vlm_chat.render()

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # ── Safety + System stacked ────────
        with st.container(border=True):
            safety_note.render()

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            system_snapshot.render()
