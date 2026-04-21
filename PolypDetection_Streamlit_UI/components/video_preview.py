"""Video preview card component – real upload + processing + output."""
import streamlit as st
import subprocess
import tempfile
import shutil
import os
import sys
import re

# ── Paths for YOLO Detection ──────────────────────────────────────────
BACKEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "objectDetectTrack")
)
OUTPUT_VIDEO = os.path.join(BACKEND_DIR, "polyp_output", "tracked_output.mp4")
SCRIPT_PATH  = os.path.join(BACKEND_DIR, "trainTrack.py")

# ── Paths for PVT Segmentation ───────────────────────────────────────
PVT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "segmentation", "polyp-pvt")
)
PVT_SCRIPT = os.path.join(PVT_DIR, "video_inference.py")
PVT_VIDEOS_DIR = os.path.join(PVT_DIR, "videos")
PVT_INPUT_VIDEO = os.path.join(PVT_VIDEOS_DIR, "input_video.mp4")
PVT_OUTPUT_VIDEO = os.path.join(PVT_VIDEOS_DIR, "output_video.mp4")


def _run_inference(cmd, cwd, is_pvt=False):
    """Run an inference script as a subprocess and show progress only (no UI logs)."""
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    # ── Heartbeat UI ──────────────────────────────────────────
    status_msg = "🎭 Deep Segmentation Active" if is_pvt else "🚀 AI Neural Detection Active"
    status_icon = "🎭" if is_pvt else "🚀"
    
    heartbeat = st.empty()
    with heartbeat.container():
        st.markdown(f'''
            <div class="processing-heartbeat">
                <div style="font-size: 24px;">{status_icon}</div>
                <div style="flex: 1;">
                    <p style="margin:0; font-weight:700; color:var(--pv-primary);">{status_msg}</p>
                    <p style="margin:2px 0 0; font-size:0.8rem; color:#6B7A8D;">Scanning frames for polyp features...</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        progress_bar = st.progress(0, text="🛠️ Preparing AI Analysis...")
    
    for line in process.stdout:
        clean_line = line.rstrip()
        # Still print to terminal for debugging
        print(f"[AI Backend] {clean_line}")

        if is_pvt:
            # PVT Progress: "Processing frame 10/100"
            match = re.search(r"Processing frame (\d+)/(\d+)", clean_line)
            if match:
                current = int(match.group(1))
                total = int(match.group(2))
                percent = min(current / total, 1.0)
                progress_bar.progress(percent, text=f"Processing: {current}/{total} frames ({int(percent*100)}%)")
        else:
            # YOLO Progress: "video 1/1 (10/100) /path/..."
            match = re.search(r"\((\d+)/(\d+)\)", clean_line)
            if match:
                current = int(match.group(1))
                total = int(match.group(2))
                percent = min(current / total, 1.0)
                progress_bar.progress(percent, text=f"Detecting: {current}/{total} frames ({int(percent*100)}%)")

    process.wait()
    heartbeat.empty()
    return process.returncode


def render():
    """Render the video upload, processing, and output section."""

    st.markdown(
        '<p style="font-weight:700;font-size:1.1rem;margin-bottom:8px;">🔬 Computer Vision Analysis</p>',
        unsafe_allow_html=True,
    )

    # Ensure videos directory exists for PVT
    os.makedirs(PVT_VIDEOS_DIR, exist_ok=True)

    # ── Upload ─────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Upload colonoscopy video",
        type=["mp4", "avi", "mov", "mkv"],
        key="video_upload",
        label_visibility="collapsed",
    )

    if uploaded:
        # Reset analysis if a new video is uploaded
        if st.session_state.get("current_video_name") != uploaded.name:
            st.session_state.current_video_name = uploaded.name
            st.session_state.detection_done = False
            st.session_state.segmentation_done = False
            st.session_state.chat_messages = []

        st.success(f"✅ Video **{uploaded.name}** ready for analysis.")
        
        # Tabs for different analysis modes
        tab1, tab2 = st.tabs(["🚀 YOLO Detection", "🎭 PVT Segmentation"])

        with tab1:
            st.info("Fast object detection & tracking (YOLOv8 + DeepSORT). Takes ~2 mins.")
            if st.button("Run YOLO Detection", type="primary", use_container_width=True):
                # Save input
                tmp_input = os.path.join(BACKEND_DIR, "uploaded_input.mp4")
                with open(tmp_input, "wb") as f: f.write(uploaded.getbuffer())
                
                # Show progress bar only
                cmd = [sys.executable, SCRIPT_PATH, "--video", tmp_input]
                res = _run_inference(cmd, BACKEND_DIR)
                if res == 0:
                    st.session_state.detection_done = True
                    st.rerun()
                else:
                    st.error(f"Error {res}")

        with tab2:
            st.warning("Advanced pixel-level segmentation. **Takes ~5 mins.**")
            if st.button("Run PVT Segmentation", type="primary", width='stretch'):
                # Reset previous results
                st.session_state.segmentation_done = False
                
                # Save input to PVT dir
                with open(PVT_INPUT_VIDEO, "wb") as f: f.write(uploaded.getbuffer())
                
                # Show progress bar only
                cmd = [sys.executable, PVT_SCRIPT, "--input_video", PVT_INPUT_VIDEO, "--output_video", PVT_OUTPUT_VIDEO]
                res = _run_inference(cmd, PVT_DIR, is_pvt=True)
                if res == 0:
                    st.session_state.segmentation_done = True
                    st.rerun()
                else:
                    st.error(f"Error {res}")


    # ── Display Results ────────────────────────────────────────────────
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    
    res_tab1, res_tab2 = st.tabs(["Detection Results", "Segmentation Results"])

    with res_tab1:
        if st.session_state.get("detection_done") and os.path.exists(OUTPUT_VIDEO):
            _render_video_card("Tracked Output (YOLO)", OUTPUT_VIDEO, "tracked_output.mp4")
        else:
            st.info("Run YOLO Detection to see results here.")

    with res_tab2:
        if st.session_state.get("segmentation_done") and os.path.exists(PVT_OUTPUT_VIDEO):
            _render_video_card("Segmented Output (PVT)", PVT_OUTPUT_VIDEO, "segmented_output.mp4")
        else:
            st.info("Run PVT Segmentation to see results here.")


def _render_video_card(title, video_path, download_name):
    """Helper to render a styled video card with download button."""
    st.markdown(
        f"""
        <div class="video-card">
            <div class="video-card-header">
                <span class="video-badge">▶ {title}</span>
                <span class="patient-label">{os.path.basename(video_path)}</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    with open(video_path, "rb") as vf:
        st.video(vf.read())

    st.markdown(
        """
            <div class="video-card-footer">
                <span class="frame-label">AI Analysis Applied</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Download button
    with open(video_path, "rb") as vf:
        st.download_button(
            label=f"⬇️ Download {title}",
            data=vf,
            file_name=download_name,
            mime="video/mp4",
            use_container_width=True,
        )
