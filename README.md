# 🔬 PolypVision

[![Hugging Face Space](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/harshit23236/polyp-vision)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

PolypVision is an AI-powered colonoscopy analysis platform for:
- Real-time polyp detection and tracking (YOLO + tracking)
- Polyp segmentation (Polyp-PVT)
- Vision-Language Model (VLM) chat assistant
- Interactive Streamlit dashboard

---

## 🚀 Try Online (Deployed Version)

Access the latest version instantly:

👉 https://huggingface.co/spaces/harshit23236/polyp-vision

---

## 💻 Run Locally

1. **Clone the repository**
	```bash
	git clone https://github.com/harshit08042006/PolypVision_CV_Project.git
	cd CV_Project
	```
2. **Create and activate a virtual environment**
	```bash
	python3 -m venv .venv
	source .venv/bin/activate
	```
3. **Install dependencies**
	```bash
	pip install -r requirements.txt
	```
4. **Configure environment variables for VLM chat**
	- Create a `.env` file in the project root:
	  ```env
	  API_KEY=your_groq_api_key
	  ```
5. **Run the Streamlit app**
	```bash
	streamlit run PolypDetection_Streamlit_UI/app.py
	```
	Open the local URL shown in terminal (usually `http://localhost:8501`).

---

## 📁 Project Structure

```
CV_Project/
├── PolypDetection_Streamlit_UI/   # Streamlit frontend
├── objectDetectTrack/             # Detection/tracking + report + VLM query
├── segmentation/polyp-pvt/        # Segmentation pipeline
├── polypvision/                   # React/Vite frontend experiments
├── requirements.txt               # Main dependencies
└── README.md
```

---

## 🧠 Core Components

- Detection & Tracking: `objectDetectTrack/`
- Segmentation: `segmentation/polyp-pvt/`
- Dashboard UI: `PolypDetection_Streamlit_UI/app.py`
- VLM Query Engine: `objectDetectTrack/vlm_query.py`

---

## ⚠️ Disclaimer

This project is for research and educational use only. It is not a standalone diagnostic tool. Final clinical decisions must be made by qualified medical professionals.

