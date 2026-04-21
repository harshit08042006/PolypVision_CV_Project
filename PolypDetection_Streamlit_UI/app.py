"""
PolypVision – Colonoscopy AI Assistant
Entry point for the Streamlit application.
"""
import streamlit as st
import os
import sys

# Add directories to sys.path so components can import vlm_query.py
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
vlm_dir = os.path.join(root_dir, "objectDetectTrack")

for path in [root_dir, vlm_dir]:
    if path not in sys.path:
        sys.path.append(path)

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="PolypVision | Colonoscopy AI Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load global CSS ─────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Hide sidebar completely ─────────────────────────────────
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Google Fonts ────────────────────────────────────────────
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True,
)

# ── Session state defaults ──────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "detection_done" not in st.session_state:
    st.session_state.detection_done = False

if "segmentation_done" not in st.session_state:
    st.session_state.segmentation_done = False

# ── Page router ─────────────────────────────────────────────
if st.session_state.page == "landing":
    from pages.landing import render
    render()
elif st.session_state.page == "dashboard":
    from pages.dashboard import render
    render()
