# 🔬 PolypVision: Advanced Colonoscopy AI Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://huggingface.co/spaces/harshit23236/polyp-vision)
[![Hugging Face Space](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/harshit23236/polyp-vision)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PolypVision** is a state-of-the-art clinical decision support system designed for real-time polyp detection, tracking, and segmentation during colonoscopy procedures. It combines high-speed computer vision with a **Vision-Language Model (VLM) Assistant** to provide grounded clinical insights.

---

## 🌟 Key Features

### 1. 🚀 Neural Detection & Tracking (YOLOv8 + BoT-SORT)
*   **Real-time Detection**: Leverages custom-trained YOLOv8 models for high-precision polyp identification.
*   **Temporal Consistency**: Uses the **BoT-SORT** tracker to maintain unique polyp IDs across frames, filtering out transient false positives and reducing "double-counting" in clinical reports.

### 2. 🎭 Precision Segmentation (Polyp-PVT)
*   **Pixel-Level Masks**: Integrates **Pyramid Vision Transformer (PVT)** for granular segmentation of polyp boundaries.
*   **Clinical Detail**: Provides better visualization of polyp morphology compared to standard bounding boxes.

### 3. 🧠 Integrated VLM Assistant
*   **Grounded Q&A**: A Vision-Language Assistant (powered by Llama 3.2 Vision / GPT-4o) that reads your session's metadata.
*   **Clinical Insights**: Ask questions like *"What is the largest polyp found?"* or *"Describe the morphology of polyp ID 2"* and get answers grounded in real detection data.

### 4. 📺 Web-Ready Video Pipeline
*   **Auto-Conversion**: Automated **H.264/AVC** re-encoding pipeline ensures processed videos play natively in all modern browsers without codec errors.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Video Upload] --> B[Processing Engine]
    subgraph AI Backend
        B --> C{YOLOv8 + BoT-SORT}
        B --> D{Polyp-PVT}
        C --> E[polyp_report.json]
        D --> F[Segmentation Mask]
    end
    E --> G[VLM Assistant]
    F --> G
    G --> H[Streamlit Dashboard]
    H --> I[Clinical Review]
