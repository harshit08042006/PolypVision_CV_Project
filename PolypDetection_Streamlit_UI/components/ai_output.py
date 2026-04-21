"""AI Output summary component – connected to real report data."""
import streamlit as st
from components.data_loader import load_dynamic_data

def render():
    """Render the AI output status items based on real detection results."""
    st.markdown(
        '<p style="font-weight:700;font-size:1rem;margin-bottom:10px;">✨ AI Output</p>',
        unsafe_allow_html=True,
    )

    # Load real stats from the report
    stats, _ = load_dynamic_data()
    
    # Check if analysis is actually done
    is_done = st.session_state.get("detection_done", False)
    is_seg_done = st.session_state.get("segmentation_done", False)

    # 1. Polyp Detection Status
    polyp_count = stats["unique_polyps"]["value"] if is_done else 0
    det_desc = f"Tracking IDs found and maintained across frames." if is_done else "Waiting for YOLO detection to finish..."
    det_title = f"{polyp_count} unique polyps detected" if is_done else "No polyps detected yet"
    det_icon = "🟡" if is_done else "⚪"

    # 2. Segmentation Status
    seg_title = "Segmented video ready" if is_seg_done else "Segmentation pending"
    seg_desc = "Mask overlays are rendered on top of detected regions." if is_seg_done else "Run PVT Segmentation to get pixel-level maps."
    seg_icon = "🔵" if is_seg_done else "⚪"

    # 3. VLM Status
    vlm_title = "VLM assistant online"
    vlm_desc = "Ask about size, count, or what can be done now."
    vlm_icon = "🟠"

    items = [
        {"icon": det_icon, "title": det_title, "description": det_desc},
        {"icon": seg_icon, "title": seg_title, "description": seg_desc},
        {"icon": vlm_icon, "title": vlm_title, "description": vlm_desc},
    ]

    for item in items:
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
