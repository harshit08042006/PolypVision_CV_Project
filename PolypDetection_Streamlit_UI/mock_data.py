"""
Mock data for PolypVision demo.
All hardcoded values used across the application for demonstration purposes.
"""

# ─── Stats Cards ────────────────────────────────────────────────
STATS = {
    "unique_polyps": {
        "value": 2,
        "label": "Unique Polyps",
        "description": "Tracked across the video",
        "icon": "🔬",
    },
    "frames_processed": {
        "value": 186,
        "label": "Frames Processed",
        "description": "Video analysis complete",
        "icon": "🎞️",
    },
    "confidence": {
        "value": 0.94,
        "label": "Confidence",
        "description": "Average detection score",
        "icon": "🎯",
    },
    "largest_polyp": {
        "value": "12.4 mm",
        "label": "Largest Polyp",
        "description": "Estimated from mask area",
        "icon": "📐",
    },
}

# ─── Keyframe Data ──────────────────────────────────────────────
KEYFRAMES = [
    {
        "id": "ID 01",
        "frame_number": 42,
        "area": "1500px",
        "confidence": 0.97,
        "bbox_size": "120×75 px",
        "severity": "High",
        "border_color": "#EF4444",       # red
        "bg_color": "rgba(239,68,68,0.08)",
    },
    {
        "id": "ID 02",
        "frame_number": 87,
        "area": "900px",
        "confidence": 0.91,
        "bbox_size": "95×60 px",
        "severity": "Medium",
        "border_color": "#F59E0B",       # amber
        "bg_color": "rgba(245,158,11,0.08)",
    },
    {
        "id": "ID 03",
        "frame_number": 133,
        "area": "500px",
        "confidence": 0.88,
        "bbox_size": "70×45 px",
        "severity": "Low",
        "border_color": "#22C55E",       # green
        "bg_color": "rgba(34,197,94,0.08)",
    },
]

# ─── AI Output Items ────────────────────────────────────────────
AI_OUTPUT_ITEMS = [
    {
        "icon": "🟡",
        "title": "2 unique polyps detected",
        "description": "Tracking IDs 01 and 02 are maintained across frames.",
    },
    {
        "icon": "🟦",
        "title": "Segmented video ready",
        "description": "Mask overlays are rendered on top of detected regions.",
    },
    {
        "icon": "🟠",
        "title": "VLM assistant online",
        "description": "Ask about size, count, or what can be done now.",
    },
]

# ─── System Snapshot ────────────────────────────────────────────
SYSTEM_SNAPSHOT = [
    ("Detection model", "YOLOv8"),
    ("Segmentation model", "Polyp-PVT"),
    ("Tracking", "Unique polyp IDs"),
    ("Response style", "Medical assistant"),
]

# ─── VLM Chat – seed messages ──────────────────────────────────
INITIAL_CHAT = [
    {"role": "assistant", "content": "Upload a video to begin analysis."},
]

# ─── Mocked VLM responses ──────────────────────────────────────
MOCK_RESPONSES = {
    "default": "Based on the analysis, I can see 2 unique polyps detected across 186 frames. The largest polyp (ID 01) has an estimated size of 12.4 mm with high confidence (0.97). Would you like more details about a specific polyp?",
    "size": "The largest detected polyp is approximately 12.4 mm, estimated from the segmentation mask area. Polyp ID 01 was found at frame 42 with an area of 1500px.",
    "count": "A total of 2 unique polyps were detected and tracked across the video. They have been assigned tracking IDs 01 and 02.",
    "severity": "Polyp ID 01 is classified as High severity based on its size (12.4 mm) and morphology. Polyp ID 02 is Medium severity. Polyp ID 03 is Low severity. Please consult with a clinical expert for definitive assessment.",
}

# ─── Feature pills for landing page ────────────────────────────
FEATURES = [
    {
        "title": "Real-time analysis",
        "description": "YOLO + Polyp-PVT pipeline",
        "icon": "⚡",
    },
    {
        "title": "Unique polyp count",
        "description": "Tracking-enabled summary",
        "icon": "🔢",
    },
    {
        "title": "Medical VLM chat",
        "description": "Ask follow-up questions",
        "icon": "💬",
    },
    {
        "title": "Clinical-ready UI",
        "description": "Polished presentation mode",
        "icon": "🏥",
    },
]
