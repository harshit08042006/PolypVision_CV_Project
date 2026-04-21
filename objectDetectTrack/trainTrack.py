import cv2
import numpy as np
import json
import os
import argparse
from datetime import datetime
from ultralytics import YOLO
import os
import sys

# ====================== CRITICAL OpenH264 DLL FIX ======================
if os.name == 'nt':  # Windows only
    # This points to the folder where app.py + openh264-1.8.0-win64.dll live
    project_root = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    
    os.add_dll_directory(project_root)
    print(f"[DLL FIX] Added OpenH264 search path → {project_root}")
    
    # Extra safety: also set working directory
    os.chdir(project_root)
    print(f"[DLL FIX] Working directory set to → {os.getcwd()}")
    
    # Add to PATH as backup
    if project_root not in os.environ.get("PATH", ""):
        os.environ["PATH"] = project_root + os.pathsep + os.environ.get("PATH", "")
# ======================================================================
# ===========================================================
# CLI argument — video path can be passed from the frontend
# ===========================================================
parser = argparse.ArgumentParser(description="Polyp detection & tracking")
parser.add_argument("--video", type=str, default="input_video.mp4",
                    help="Path to input colonoscopy video")
args = parser.parse_args()

# ===========================================================
# CONFIGURATION
# ===========================================================
VIDEO_PATH        = args.video
MODEL_PATH        = "runs/detect/train4/weights/best.pt"
OUTPUT_DIR        = "polyp_output"

CONF_THRESH       = 0.7
MIN_AREA          = 4000
MIN_AREA_FINAL    = 4000
FINAL_MIN_FRAMES  = 8

MERGE_MAX_FRAMES_GAP   = 200
MERGE_MAX_AREA_DIFF    = 100000
MERGE_MAX_CENTROID_DIST = 150

CV_STABILITY_THRESHOLD = 0.5

# === NEW: Choose tracker (BoT-SORT is recommended) ===
TRACKER_TYPE = "botsort.yaml"   # or "bytetrack.yaml"
# For even better results in colonoscopy:
#   1. Copy ultralytics/cfg/trackers/botsort.yaml to your folder as "custom_botsort.yaml"
#   2. Set:
#        track_buffer: 200
#        track_high_thresh: 0.35
#        gmc_method: sparseOptFlow
#   3. Then use TRACKER_TYPE = "custom_botsort.yaml"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------
# Load YOLO model
# ---------------------------
model = YOLO(MODEL_PATH)

# ---------------------------
# Metadata storage
# ---------------------------
polyp_data = {}

# ---------------------------
# Video I/O
# ---------------------------
cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

output_video_path = os.path.join(OUTPUT_DIR, "tracked_output.mp4")
# Use mp4v - best compatible software encoder for .mp4 containers on Linux
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

if not cap.isOpened():
    raise FileNotFoundError(f"Cannot open video file: '{VIDEO_PATH}'")

frame_idx = 0
print(f"[INFO] Processing video: {VIDEO_PATH} with {TRACKER_TYPE}")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1

    # ===================================================================
    # STEP 1 + 2: Detection + Tracking (YOLO native — this is the fix!)
    # ===================================================================
    results = model.track(
        frame,
        persist=True,           # keeps track history across frames
        conf=CONF_THRESH,
        iou=0.45,
        tracker=TRACKER_TYPE,
        verbose=False
    )[0]

    # ===================================================================
    # STEP 3: Metadata + history (your original logic, now with YOLO tracks)
    # ===================================================================
    for box in results.boxes:
        if box.id is None:
            continue

        track_id = int(box.id.item())
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        conf = float(box.conf.item())
        area = (x2 - x1) * (y2 - y1)

        if area < MIN_AREA:
            continue

        # Clamp bbox
        l, t, r, b = map(int, [x1, y1, x2, y2])
        l = max(0, l)
        t = max(0, t)
        r = min(frame.shape[1], r)
        b = min(frame.shape[0], b)
        if r <= l or b <= t:
            continue

        area = (r - l) * (b - t)
        cx = (l + r) // 2
        cy = (t + b) // 2

        crop = frame[t:b, l:r].copy()
        annotated = frame.copy()
        cv2.rectangle(annotated, (l, t), (r, b), (0, 255, 0), 2)
        cv2.putText(annotated, f"ID {track_id} conf:{conf:.2f}",
                    (l, max(t - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # NEW TRACK
        if track_id not in polyp_data:
            polyp_data[track_id] = {
                "first_frame": frame_idx,
                "last_frame": frame_idx,
                "frames": {frame_idx},
                "frames_seen": 1,
                "best_frame": frame_idx,
                "best_conf": conf,
                "best_crop": crop,
                "best_annotated": annotated,
                "largest_frame": frame_idx,
                "max_area": area,
                "largest_crop": crop,
                "largest_annotated": annotated,
                "areas": {frame_idx: area},
                "bboxes": {frame_idx: (l, t, r, b)},
                "last_centroid": (cx, cy),
                "first_centroid": (cx, cy),
            }
        # UPDATE TRACK
        else:
            data = polyp_data[track_id]
            data["last_frame"] = frame_idx
            data["frames"].add(frame_idx)
            data["frames_seen"] = len(data["frames"])
            data["areas"][frame_idx] = area
            data["bboxes"][frame_idx] = (l, t, r, b)
            data["last_centroid"] = (cx, cy)

            if conf > data["best_conf"]:
                data["best_conf"] = conf
                data["best_frame"] = frame_idx
                data["best_crop"] = crop
                data["best_annotated"] = annotated

            if area > data["max_area"]:
                data["max_area"] = area
                data["largest_frame"] = frame_idx
                data["largest_crop"] = crop
                data["largest_annotated"] = annotated

    # ---------------------------
    # Visualization on output video
    # ---------------------------
    for box in results.boxes:
        if box.id is None:
            continue
        track_id = int(box.id.item())
        l, t, r, b = map(int, box.xyxy[0].cpu().numpy())
        cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {track_id}", (l, max(t - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    out.write(frame)

cap.release()
out.release()
print(f"[INFO] Finished reading video. Total frames: {frame_idx}")

# =========================================================
# STEP 4–6: Your original merging + final filters + saving
# (unchanged — they are excellent)
# =========================================================
# ... (exactly the same as your original code from def centroid_distance ... to the end)

# (I kept the entire merge_tracks, is_same_polyp, final filters, report generation, etc.
#   Copy-paste the rest of your original script from the "def centroid_distance" line onward.
#   It works perfectly with the new track_id values.)

def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h

    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    union = areaA + areaB - inter_area
    if union == 0:
        return 0.0

    return inter_area / union

def compute_temporal_iou(polyp_data):
    results = {}

    for pid, data in polyp_data.items():
        frames = sorted(data["bboxes"].keys())

        if len(frames) < 2:
            results[pid] = 0.0
            continue

        ious = []

        for i in range(len(frames) - 1):
            f1, f2 = frames[i], frames[i + 1]

            # Only consecutive frames
            if f2 != f1 + 1:
                continue

            box1 = data["bboxes"][f1]
            box2 = data["bboxes"][f2]

            iou = compute_iou(box1, box2)
            ious.append(iou)

        results[pid] = float(np.mean(ious)) if ious else 0.0

    return results


def centroid_distance(c1, c2):
    """Euclidean distance between two (x, y) centroids."""
    return np.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)


def is_same_polyp(p1, p2):
    """
    Decide if two tracks likely represent the same physical polyp.
    All three conditions must pass:
      1. Area similarity
      2. Temporal proximity (p2 starts after p1 ends, within the gap limit)
      3. Spatial proximity (last known position of p1 is close to first of p2)
    """
    # FIX: area check
    if abs(p1["max_area"] - p2["max_area"]) > MERGE_MAX_AREA_DIFF:
        return False

    # FIX: directed temporal check — p2 must start AFTER p1 ends
    gap = p2["first_frame"] - p1["last_frame"]
    if gap < 0 or gap > MERGE_MAX_FRAMES_GAP:
        return False

    # FIX: spatial check — centroids must be close
    dist = centroid_distance(p1["last_centroid"], p2["first_centroid"])
    if dist > MERGE_MAX_CENTROID_DIST:
        return False

    return True


def merge_tracks(polyp_data):
    """
    Merge track fragments that likely belong to the same polyp.
    Sorts by first_frame so the directed temporal check works correctly.
    """
    merged = {}
    used   = set()

    # Sort by appearance time so p1 always precedes p2 chronologically
    ids = sorted(polyp_data.keys(), key=lambda k: polyp_data[k]["first_frame"])

    for i, id_i in enumerate(ids):
        if id_i in used:
            continue

        base = polyp_data[id_i]

        for id_j in ids[i + 1:]:
            if id_j in used:
                continue

            other = polyp_data[id_j]

            if is_same_polyp(base, other):
                print(f"[MERGE] Track {id_i} ← Track {id_j}")

                # FIX: merge area dicts (keyed by frame) — no duplicates possible
                base["areas"].update(other["areas"])

                # Merge frame sets
                base["frames"]      = base["frames"].union(other["frames"])
                base["frames_seen"] = len(base["frames"])

                base["first_frame"] = min(base["first_frame"], other["first_frame"])
                base["last_frame"]  = max(base["last_frame"],  other["last_frame"])

                # Update centroids
                if other["first_frame"] < base["first_frame"]:
                    base["first_centroid"] = other["first_centroid"]
                if other["last_frame"] > base["last_frame"]:
                    base["last_centroid"] = other["last_centroid"]

                # FIX: update BOTH crop AND annotated together
                if other["best_conf"] > base["best_conf"]:
                    base["best_conf"]      = other["best_conf"]
                    base["best_frame"]     = other["best_frame"]
                    base["best_crop"]      = other["best_crop"]
                    base["best_annotated"] = other["best_annotated"]

                if other["max_area"] > base["max_area"]:
                    base["max_area"]           = other["max_area"]
                    base["largest_frame"]      = other["largest_frame"]
                    base["largest_crop"]       = other["largest_crop"]
                    base["largest_annotated"]  = other["largest_annotated"]

                used.add(id_j)

        merged[id_i] = base

    return merged


polyp_data = merge_tracks(polyp_data)
print(f"[INFO] Tracks after merging: {len(polyp_data)}")

# =========================================================
# STEP 5: FINAL FILTERS
# =========================================================

# Filter 1: minimum frames seen and minimum area
polyp_data = {
    k: v for k, v in polyp_data.items()
    if v["frames_seen"] >= FINAL_MIN_FRAMES
    and v["max_area"] >= MIN_AREA_FINAL
}

# Filter 2: FIX — stability using scale-invariant coefficient of variation
def is_stable(data):
    area_values = list(data["areas"].values())
    if len(area_values) < 5:
        return True
    mean = np.mean(area_values)
    if mean == 0:
        return False
    cv = np.std(area_values) / mean  # coefficient of variation
    return cv < CV_STABILITY_THRESHOLD

polyp_data = {k: v for k, v in polyp_data.items() if is_stable(v)}

# FIX: Do NOT blindly keep only 1 track — keep all surviving polyps.
# If the clinical workflow truly requires a single polyp, log a warning
# so the operator knows others were discarded.
if len(polyp_data) > 1:
    print(
        f"[WARNING] {len(polyp_data)} polyps survived all filters. "
        "All are included in the output. Review each one."
    )

# FIX: Warn explicitly when nothing survives
if len(polyp_data) == 0:
    print(
        "[WARNING] No polyps passed all filters. "
        "The video may contain no polyps, or the detection thresholds may be too strict. "
        "Consider lowering FINAL_MIN_FRAMES, MIN_AREA_FINAL, or CONF_THRESH."
    )

temporal_iou_scores = compute_temporal_iou(polyp_data)

print("\n=== TEMPORAL IoU (Tracking Stability) ===\n")

for pid, score in temporal_iou_scores.items():
    print(f"Polyp {pid}: Temporal IoU = {score:.4f}")


if len(temporal_iou_scores) > 0:
    overall_temporal_iou = np.mean(list(temporal_iou_scores.values()))
else:
    overall_temporal_iou = 0.0

print(f"\n Overall Temporal IoU: {overall_temporal_iou:.4f}")
# =========================================================
# STEP 6: SAVE OUTPUTS
# =========================================================

report = {
    "video":       VIDEO_PATH,
    "total_frames": frame_idx,
    "processed_at": datetime.now().isoformat(),
    "polyps":      []
}

print("\n=== FINAL POLYP SUMMARY ===\n")

for pid, data in polyp_data.items():
    area_values = list(data["areas"].values())
    mean_area   = float(np.mean(area_values))   if area_values else 0.0
    median_area = float(np.median(area_values)) if area_values else 0.0

    # Save best-confidence crop and annotated frame
    crop_path      = os.path.join(OUTPUT_DIR, f"polyp_{pid}_best_crop.jpg")
    annotated_path = os.path.join(OUTPUT_DIR, f"polyp_{pid}_best_annotated.jpg")
    largest_crop_path      = os.path.join(OUTPUT_DIR, f"polyp_{pid}_largest_crop.jpg")
    largest_annotated_path = os.path.join(OUTPUT_DIR, f"polyp_{pid}_largest_annotated.jpg")

    if data["best_crop"] is not None and data["best_crop"].size > 0:
        cv2.imwrite(crop_path, data["best_crop"])
    if data["best_annotated"] is not None and data["best_annotated"].size > 0:
        cv2.imwrite(annotated_path, data["best_annotated"])
    if data["largest_crop"] is not None and data["largest_crop"].size > 0:
        cv2.imwrite(largest_crop_path, data["largest_crop"])
    if data["largest_annotated"] is not None and data["largest_annotated"].size > 0:
        cv2.imwrite(largest_annotated_path, data["largest_annotated"])

    print(f"Polyp ID      : {pid}")
    print(f"  First Frame : {data['first_frame']}")
    print(f"  Last Frame  : {data['last_frame']}")
    print(f"  Frames Seen : {data['frames_seen']}")
    print(f"  Best Frame  : {data['best_frame']}  (conf: {data['best_conf']:.2f})")
    print(f"  Largest Frame: {data['largest_frame']}  (area: {data['max_area']} px²)")
    print(f"  Mean Area   : {mean_area:.0f} px²")
    print(f"  Median Area : {median_area:.0f} px²")
    print(f"  Saved crop  : {crop_path}")
    print(f"  Saved annot : {annotated_path}")
    print("-" * 50)

    # Build JSON-serialisable record (no numpy arrays or sets)
    record = {
        "polyp_id":          int(pid),
        "first_frame":       data["first_frame"],
        "last_frame":        data["last_frame"],
        "frames_seen":       data["frames_seen"],
        "best_frame":        data["best_frame"],
        "best_conf":         round(float(data["best_conf"]), 4),
        "largest_frame":     data["largest_frame"],
        "max_area_px2":      int(data["max_area"]),
        "mean_area_px2":     round(mean_area, 1),
        "median_area_px2":   round(median_area, 1),
        "best_crop_path":    crop_path,
        "best_annotated_path": annotated_path,
        "largest_crop_path": largest_crop_path,
        "largest_annotated_path": largest_annotated_path,
        "temporal_iou": round(temporal_iou_scores.get(pid, 0.0), 4),
    }
    report["polyps"].append(record)
    report["overall_temporal_iou"] = round(float(overall_temporal_iou), 4)

# Write JSON audit report
report_path = os.path.join(OUTPUT_DIR, "polyp_report.json")
with open(report_path, "w") as f:
    json.dump(report, f, indent=2)

print(f"\n[INFO] JSON report saved: {report_path}")
print(f"[INFO] All output files saved to: {OUTPUT_DIR}/")