"""Keyframes gallery with metadata modal component."""
import streamlit as st
from PIL import Image, ImageDraw
import os
from components.data_loader import load_dynamic_data

def _generate_keyframe_thumbnail(kf):
    """Generate a thumbnail for a keyframe, using real cropped images if available!"""
    if kf.get("image_path") and os.path.exists(kf["image_path"]):
        # Show actual polyp crop!
        return Image.open(kf["image_path"])

    # Fallback to mock drawing
    size = 120
    img = Image.new("RGB", (size, size), color=(248, 248, 248))
    draw = ImageDraw.Draw(img, "RGBA")

    colors = {"High": (220, 80, 70), "Medium": (230, 170, 50), "Low": (60, 180, 100)}
    fill = colors.get(kf["severity"], (150, 150, 150))
    cx, cy = size // 2, size // 2
    draw.ellipse([cx - 36, cy - 32, cx + 36, cy + 32], fill=fill + (200,))
    draw.ellipse([cx - 22, cy - 18, cx + 22, cy + 18], fill=fill + (120,))
    return img

@st.dialog("Keyframe Metadata")
def _show_metadata(kf):
    """Display metadata for a selected keyframe."""
    rows = [
        ("ID", kf["id"]),
        ("Frame number", str(kf["frame_number"])),
        ("Area", kf["area"]),
        ("Confidence", str(kf["confidence"])),
        ("BBox size", kf["bbox_size"]),
        ("Severity", kf["severity"]),
    ]
    for key, val in rows:
        st.markdown(f'<div class="meta-row"><span class="meta-key">{key}</span><span class="meta-val">{val}</span></div>', unsafe_allow_html=True)

def render():
    """Render the keyframe gallery."""
    st.markdown(
        """
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <p style="font-weight:700;font-size:1rem;margin:0;">🔑 Keyframes</p>
            <span class="badge badge-demo" style="font-size:0.7rem;">Sorted by Severity</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    analysis_done = st.session_state.get("detection_done") or st.session_state.get("segmentation_done")
    if not analysis_done:
        st.info("Waiting for analysis to extract keyframes.")
        return

    _, KEYFRAMES = load_dynamic_data()

    if not KEYFRAMES:
        st.info("No keyframes extracted.")
        return

    for i, kf in enumerate(KEYFRAMES):
        thumb = _generate_keyframe_thumbnail(kf)

        col_img, col_info = st.columns([1, 2])
        with col_img:
            st.image(thumb, width='stretch')
        with col_info:
            st.markdown(
                f"""
                <div style="padding:4px 0;">
                    <div class="kf-id" style="color:{kf['border_color']};font-size:0.9rem;">{kf["id"]}</div>
                    <div class="kf-meta">Frame {kf["frame_number"]}</div>
                    <div class="kf-meta">Area {kf["area"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("View Details", key=f"kf_btn_{i}", width='stretch'):
                _show_metadata(kf)

        if i < len(KEYFRAMES) - 1:
            st.markdown(
                '<div style="border-bottom:1px solid #E2E8F0;margin:6px 0;"></div>',
                unsafe_allow_html=True,
            )
