import os
import json
from mock_data import STATS as MOCK_STATS
from mock_data import KEYFRAMES as MOCK_KEYFRAMES

BACKEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "objectDetectTrack")
)
REPORT_PATH = os.path.join(BACKEND_DIR, "polyp_output", "polyp_report.json")

def get_severity(area):
    # Rule for severity based on pixel area.
    # > 100,000 pixels is High
    # > 50,000 pixels is Medium
    # otherwise Low
    if area > 100000:
        return "High", "#EF4444", "rgba(239,68,68,0.08)"
    elif area > 50000:
        return "Medium", "#F59E0B", "rgba(245,158,11,0.08)"
    else:
        return "Low", "#22C55E", "rgba(34,197,94,0.08)"

def load_dynamic_data():
    if not os.path.exists(REPORT_PATH):
        return MOCK_STATS, MOCK_KEYFRAMES
        
    try:
        with open(REPORT_PATH, "r") as f:
            data = json.load(f)
    except Exception:
        return MOCK_STATS, MOCK_KEYFRAMES
        
    polyps = data.get("polyps", [])
    if not polyps:
        return MOCK_STATS, MOCK_KEYFRAMES
        
    # -------- Generate STATS --------
    total_polyps = len(polyps)
    frames_processed = data.get("total_frames", 0)
    avg_conf = sum(p.get("best_conf", 0) for p in polyps) / total_polyps if total_polyps else 0
    max_area = max(p.get("max_area_px2", 0) for p in polyps) if total_polyps else 0
    
    stats = {
        "unique_polyps": {
            "value": total_polyps,
            "label": "Unique Polyps",
            "description": "Tracked across the video",
            "icon": "🔬",
        },
        "frames_processed": {
            "value": frames_processed,
            "label": "Frames Processed",
            "description": "Video analysis complete",
            "icon": "🎞️",
        },
        "confidence": {
            "value": f"{avg_conf:.2f}",
            "label": "Confidence",
            "description": "Average detection score",
            "icon": "🎯",
        },
        "largest_polyp": {
            "value": f"{max_area} px²",
            "label": "Largest Polyp",
            "description": "Max area in pixels",
            "icon": "📐",
        },
    }
    
    # -------- Generate KEYFRAMES --------
    # Sort polyps by Area (Severity) descending
    sorted_polyps = sorted(polyps, key=lambda x: x.get("max_area_px2", 0), reverse=True)
    keyframes = []
    
    for p in sorted_polyps:
        area = p.get("max_area_px2", 0)
        severity, border, bg = get_severity(area)
        
        kf = {
            "id": f"ID {p.get('polyp_id', '?')}",
            "frame_number": p.get("largest_frame", 0),
            "area": f"{area} px²",
            "confidence": f"{p.get('best_conf', 0):.2f}",
            "bbox_size": "N/A",  # Skipping as we don't have w*h without modifying the backend
            "severity": severity,
            "border_color": border,
            "bg_color": bg,
            # Pass the largest crop path so we can show REAL images in the UI instead of drawn mockups!
            "image_path": os.path.join(BACKEND_DIR, p.get("largest_crop_path", "")) if p.get("largest_crop_path") else None
        }
        keyframes.append(kf)

    # Update stats to reflect unique keyframes detected
    stats["unique_polyps"]["value"] = len(keyframes)
    stats["unique_polyps"]["label"] = "Unique Keyframes"
    stats["unique_polyps"]["description"] = "Detected across the video"

    return stats, keyframes
