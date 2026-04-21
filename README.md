---
title: PolypVision
emoji: 🔬
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# PolypVision | Colonoscopy AI Assistant 🔬

PolypVision is an end-to-end computer vision and healthcare application designed to detect and track colonoscopy polyps in real-time. It features a polished frontend UI built with Streamlit and a powerful object detection & tracking backend powered by YOLOv8 and BoT-SORT.

## Key Features 🚀
- **Automated Polyp Detection**: Upload clinical colonoscopy videos (`.mp4`, `.avi`, etc.) and automatically run them through a custom-trained object detection pipeline.
- **Robust Polyp Tracking**: Uses BoT-SORT to maintain unique IDs for the same polyp across sequential video frames, reducing false double-counting.
- **Medical Segmentation Integration**: Designed to be compatible with Polyp-PVT (Pyramid Vision Transformer) for granular segmentation mask representations.
- **Interactive Health-Tech Dashboard**: A fully featured and beautiful Streamlit interface presenting bounded video output, extracted keyframes, and severity tracking telemetry.
- **AI Output Summaries**: Quick statistical metrics highlighting overall confidence, frames processed, and bounding representations.

## Tech Stack 🛠️
- **Frontend Environment**: Streamlit
- **Computer Vision & Backend**: OpenCV, Ultralytics (YOLOv8)
- **Object Tracking Model**: BoT-SORT (Native YOLOv8)
- **Data Toolkit**: Python, NumPy 

---

## 💻 How to Run Locally

### 1. Requirements
Ensure you have Python 3.9+ installed. You will need to install the project dependencies before running the application.  
Open your terminal and run:

```bash
cd PolypDetection_Streamlit_UI
pip3 install -r requirements.txt
```

### 2. Start the Frontend Application
Streamlit handles both the user interface and the backend processing pipelines. From the `PolypDetection_Streamlit_UI` directory, start the server:

```bash
python3 -m streamlit run app.py
```

### 3. Upload & Processing
1. Navigate to the local URL (typically `http://localhost:8501`) inside your web browser.
2. In the "Case Upload & Detection" module, drop a local video (e.g., `input_video.mp4`).
3. Click the **🚀 Process Video** button.
4. The system will handle processing locally and produce a `tracked_output.mp4` video with bounded detection visualization directly inside your web page!

---

## 📁 Directory Structure
- `/PolypDetection_Streamlit_UI/` - Contains the Streamlit visual layouts, components, css assets, and routing structures (`app.py`).
- `/objectDetectTrack/` - Houses the heavily lifted model code (`trainTrack.py`), trained YOLO weight snapshots (`.pt`), and the processed diagnostic output videos inside `polyp_output/`.

## ⚙️ How It Works (Behind the Scenes)
When a video is uploaded on the frontend, it saves the file payload directly to `objectDetectTrack`.  The application then kicks off `trainTrack.py --video <file>` in a headless background process using the system's python executable. The backend chunks up the frames, scores them via YOLO, threads predictions via DeepSort, and saves the final result locally utilizing `avc1` (H.264), ensuring video playback remains universally compatible with all modern browsers!

## 🎓 Academic Credit 
Built for a college project focusing on augmenting visual clinical environments through Artificial Intelligence.
