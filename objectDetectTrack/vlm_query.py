"""
vlm_query.py — Colonoscopy VLM Assistant
==========================================
Powered by GPT-4o Vision via the OpenAI API.
All polyp metadata from trainTrack.py is loaded automatically.

Requirements:
    pip install openai pillow

Usage:
    python vlm_query.py                               # default: polyp_output/polyp_report.json
    python vlm_query.py --report path/to/report.json
"""
import os
import json
import re
import base64
import argparse
from pathlib import Path
from PIL import Image
from io import BytesIO
from typing import Optional, Union, List, Dict
import openai
from dotenv import load_dotenv
load_dotenv()
# ══════════════════════════════════════════════════════════════
#  *** ONLY CHANGE THIS LINE ***
# ══════════════════════════════════════════════════════════════

API_KEY = os.getenv("API_KEY")
# ══════════════════════════════════════════════════════════════

# For Groq, we use the Llama 3.2 Vision model for MAIN_MODEL
MAIN_MODEL       = "llama-3.2-11b-vision-preview" 
GUARD_MODEL      = "llama-3.1-8b-instant"

# Robustly find the report path relative to this script's location
THIS_DIR = Path(__file__).parent
DEFAULT_REPORT   = str(THIS_DIR / "polyp_output" / "polyp_report.json")

MAX_TOKENS       = 1024
IMAGE_MAX_PX     = 1024  # resize large crops before sending to save tokens


# ──────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert colonoscopy polyp analysis assistant.
You have been provided with the complete detection report and polyp crop images from a
colonoscopy video processed by an AI detection pipeline (YOLOv8 + DeepSORT tracking).

Your role:
- Answer questions about the entire colonoscopy session — overall findings, comparisons across polyps, session-level statistics, and individual polyp details.
- Describe visual characteristics visible in polyp crop images (shape, texture, color, surface pattern, borders, size relative to frame).
- Explain detection statistics (confidence scores, bounding box area, frame counts, tracking duration) in clear clinical language. When asked for numerical data like "Area", look specifically at the 'Max area' or 'Mean area' fields in the provided report text.
- Be precise: If the report says a polyp is 45000 px², state that exact number.
- Summarize or compare polyps when asked (e.g. "which is largest?", "how many were found?", "describe all polyps").
- Stay strictly grounded in the image AND the technical metadata provided below. Do not say information is missing if it is in the report block.
- Always end with: "Final clinical decision must be made by a gastroenterologist with full video review and biopsy results."
"""

# ──────────────────────────────────────────────────────────────
# REPORT LOADER
# ──────────────────────────────────────────────────────────────
def load_report(report_path: str) -> dict:
    path = Path(report_path)
    if not path.exists():
        # Help the user debug if path is wrong on HF Spaces
        abs_path = path.absolute()
        raise FileNotFoundError(
            f"Report not found at: {report_path} (Absolute: {abs_path})\n"
            "Ensure trainTrack.py has finished and generated 'polyp_output/polyp_report.json'."
        )
    with open(path) as f:
        report = json.load(f)
    if not report.get("polyps"):
        raise ValueError("Report contains no polyps. Nothing to analyse.")

    print(f"[INFO] Report   : {report_path}")
    print(f"[INFO] Video    : {report.get('video', 'N/A')}")
    print(f"[INFO] Frames   : {report.get('total_frames', 'N/A')}")
    print(f"[INFO] Polyps   : {len(report['polyps'])}")
    return report


def format_metadata(report: dict) -> str:
    """Convert the JSON report into a readable text block injected into every prompt."""
    lines = [
        "=== COLONOSCOPY POLYP DETECTION REPORT ===",
        f"Video          : {report.get('video', 'N/A')}",
        f"Total frames   : {report.get('total_frames', 'N/A')}",
        f"Processed at   : {report.get('processed_at', 'N/A')}",
        f"Polyps detected: {len(report['polyps'])}",
        "",
    ]
    for p in report["polyps"]:
        duration = p["last_frame"] - p["first_frame"] + 1
        lines += [
            f"--- Polyp ID {p['polyp_id']} ---",
            f"  First seen      : Frame {p['first_frame']}",
            f"  Last seen       : Frame {p['last_frame']}",
            f"  Duration        : {duration} frames",
            f"  Unique frames   : {p['frames_seen']}",
            f"  Best confidence : {p['best_conf']} (frame {p['best_frame']})",
            f"  Max area        : {p['max_area_px2']} px²  (frame {p['largest_frame']})",
            f"  Mean area       : {p['mean_area_px2']} px²",
            f"  Median area     : {p['median_area_px2']} px²",
            "",
        ]
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# IMAGE HELPERS
# ──────────────────────────────────────────────────────────────
def load_all_crops(report: dict, report_path: str) -> dict[int, dict[str, str]]:
    """
    Load every polyp's crop images and encode them as base64 strings.
    Resolves image paths relative to the report file directory.
    """
    all_crops: dict[int, dict[str, str]] = {}
    report_dir = Path(report_path).parent

    for p in report["polyps"]:
        pid   = p["polyp_id"]
        crops: dict[str, str] = {}

        for path_key, slot in [("best_crop_path", "best"), ("largest_crop_path", "largest")]:
            img_path_raw = p.get(path_key)
            if not img_path_raw:
                continue

            # In the report, path is stored as 'polyp_output/filename.jpg'
            # We assume images are in the same folder as the report.
            img_filename = os.path.basename(img_path_raw)
            img_path = report_dir / img_filename

            if img_path.exists():
                crops[slot] = encode_image(str(img_path))
            else:
                # Fallback: try the raw path just in case
                if Path(img_path_raw).exists():
                    crops[slot] = encode_image(img_path_raw)

        if crops:
            all_crops[pid] = crops
        else:
            print(f"[WARN] No crop images found for Polyp {pid} at {report_dir}")

    return all_crops


def encode_image(img_path: str) -> str:
    """Resize if needed, then return a base64-encoded JPEG string."""
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    if max(w, h) > IMAGE_MAX_PX:
        scale = IMAGE_MAX_PX / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def image_content_block(b64: str) -> dict:
    """Return an OpenAI image_url content block from a base64 string."""
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"},
    }


def best_overview_crop(all_crops: dict, report: dict) -> Union[tuple[Optional[int], Optional[str]], tuple[None, None]]:
    """Return (polyp_id, base64) for the highest-confidence polyp as a default overview image."""
    if not report["polyps"]:
        return None, None
    top = max(report["polyps"], key=lambda p: p["best_conf"])
    pid = top["polyp_id"]
    b64 = all_crops.get(pid, {}).get("best")
    return pid, b64


# ──────────────────────────────────────────────────────────────
# LLM-BASED DOMAIN GUARD
# ──────────────────────────────────────────────────────────────
def is_domain_relevant(client: openai.OpenAI, query: str) -> bool:
    """
    Smart domain guard:
    - Allows ALL questions about polyps, risk, danger, removal techniques, clinical decisions, visuals, stats, etc.
    - Blocks only truly irrelevant questions (weather, general chat, coding, etc.)
    """
    resp = client.chat.completions.create(
        model=GUARD_MODEL,
        max_tokens=1,
        temperature=0.0,
        messages=[{
            "role": "user",
            "content": (
                "You are a query classifier for a clinical colonoscopy assistant.\n"
                "Reply with ONLY 'YES' or 'NO'.\n\n"
                "The assistant is allowed to answer:\n"
                "- Anything about colonoscopy sessions, polyps, detection stats, and images.\n"
                "- Risk levels, malignant potential, and the consequences of leaving polyps untreated.\n"
                "- Patient-facing concerns about their procedure, future prognosis, and lifestyle impact.\n"
                "- Treatment options, surgical techniques, and clinical implications.\n\n"
                "It is NOT allowed to answer:\n"
                "- Completely unrelated topics (e.g., weather, sports, programming, pop culture).\n"
                "- Unrelated medical conditions outside of gastroenterology.\n\n"
                f'Question: "{query}"\n\n'
                "Is this question related to the allowed medical/clinical domain? (YES/NO only):"
            ),
        }],
    )
    answer = resp.choices[0].message.content.strip().upper()
    return answer.startswith("Y")


OUT_OF_DOMAIN_REPLY = (
    "⚠️  That question doesn't appear to be related to this colonoscopy session. "
    "I can help with:\n"
    "  • Session summaries    — 'How many polyps were found?'\n"
    "  • Cross-polyp analysis — 'Which polyp is the largest?'\n"
    "  • Individual details   — 'Describe polyp 2'\n"
    "  • Visual analysis      — 'What does polyp 1 look like?'  (use: focus 1)\n"
    "  • Detection stats      — 'What was the confidence for polyp 3?'"
)


# ──────────────────────────────────────────────────────────────
# INFERENCE
# ──────────────────────────────────────────────────────────────
def chat(
    client: openai.OpenAI,
    history: list[dict],
    user_text: str,
    image_b64: Optional[str],
    metadata_text: str,
    is_first_turn: bool,
) -> str:
    """
    Send one turn to GPT-4o and return the assistant reply.
    On the first turn the metadata + image are injected into the user message.
    Follow-up turns send plain text while the full history provides context.
    """
    if is_first_turn:
        content = [{"type": "text", "text": f"{metadata_text}\n\nQuestion: {user_text}"}]
        if image_b64:
            content.insert(0, image_content_block(image_b64))
        user_msg = {"role": "user", "content": content}
    else:
        user_msg = {"role": "user", "content": user_text}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [user_msg]

    resp = client.chat.completions.create(
        model=MAIN_MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
    )
    return resp.choices[0].message.content.strip()


# ──────────────────────────────────────────────────────────────
# INTERACTIVE LOOP
# ──────────────────────────────────────────────────────────────
def print_polyp_menu(report: dict):
    print("\n" + "═" * 65)
    print("  COLONOSCOPY SESSION — POLYP SUMMARY")
    print("═" * 65)
    for p in report["polyps"]:
        dur = p["last_frame"] - p["first_frame"] + 1
        print(
            f"  Polyp {p['polyp_id']:>3}  │  "
            f"conf: {p['best_conf']:.2f}  │  "
            f"max area: {p['max_area_px2']:>7} px²  │  "
            f"duration: {dur} frames"
        )
    print("═" * 65 + "\n")


def interactive_session(client: openai.OpenAI, report: dict, report_path: str):
    metadata_text = format_metadata(report)
    available_ids = [p["polyp_id"] for p in report["polyps"]]

    print("[INFO] Loading all polyp crop images...")
    all_crops = load_all_crops(report, report_path)
    print(f"[INFO] Crops loaded for polyp IDs: {sorted(all_crops.keys())}\n")

    overview_pid, overview_b64 = best_overview_crop(all_crops, report)
    focused_pid     = None           # None = overview mode
    active_crop_key = "best"
    active_b64      = overview_b64   # base64 image currently sent to GPT-4o

    history: list[dict] = []         # OpenAI message history (no system prompt here)

    print_polyp_menu(report)
    print("═" * 65)
    print("  COLONOSCOPY VLM ASSISTANT   (type 'help' for commands)")
    print("═" * 65)
    mode = f"overview — Polyp {overview_pid} image" if overview_pid else "no image"
    print(f"  Model         : {MAIN_MODEL}")
    print(f"  Polyps loaded : {len(report['polyps'])}")
    print(f"  Image context : {mode}")
    print("═" * 65 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Session ended.")
            break

        if not user_input:
            continue

        cmd = user_input.lower().strip()

        # ── Commands ───────────────────────────────────────────
        if cmd in ("quit", "exit", "q"):
            print("[INFO] Goodbye.")
            break

        if cmd == "menu":
            print_polyp_menu(report)
            continue

        if cmd == "clear":
            history = []
            print("[INFO] Conversation history cleared.\n")
            continue

        if cmd == "help":
            print(
                "\nCommands:\n"
                "  focus overview          — overview mode (highest-confidence polyp image)\n"
                "  focus <id>              — pin Polyp <id>'s best-confidence crop\n"
                "  focus <id> largest      — pin Polyp <id>'s largest-area crop\n"
                "  menu                    — polyp summary table\n"
                "  clear                   — reset conversation history\n"
                "  quit                    — exit\n\n"
                "Example questions:\n"
                "  'Summarize the colonoscopy findings'\n"
                "  'Which polyp has the highest confidence?'\n"
                "  'How many polyps were detected and how long was each tracked?'\n"
                "  'Describe the visual appearance of polyp 2'  →  first run: focus 2\n"
            )
            continue

        focus_match = re.match(r"^focus\s+(overview|\d+)(?:\s+(best|largest))?$", cmd)
        if focus_match:
            target_str = focus_match.group(1)
            crop_pref  = focus_match.group(2) or "best"

            if target_str == "overview":
                focused_pid     = None
                active_crop_key = "best"
                active_b64      = overview_b64
                history         = []
                mode = f"overview — Polyp {overview_pid} image" if overview_pid else "no image"
                print(f"[INFO] Switched to {mode}. Conversation cleared.\n")
            else:
                new_id = int(target_str)
                if new_id not in available_ids:
                    print(f"  Polyp {new_id} not found. Available: {available_ids}\n")
                    continue
                if new_id not in all_crops:
                    print(f"  [WARN] No crops available for Polyp {new_id}.\n")
                    continue
                b64 = all_crops[new_id].get(crop_pref) or next(iter(all_crops[new_id].values()))
                focused_pid     = new_id
                active_crop_key = crop_pref
                active_b64      = b64
                history         = []
                print(f"[INFO] Focused on Polyp {new_id} ({active_crop_key} crop). Conversation cleared.\n")
            continue

        # ── Domain guard ───────────────────────────────────────
        print("[checking...]", end="\r", flush=True)
        relevant = is_domain_relevant(client, user_input)
        print("             ", end="\r", flush=True)

        if not relevant:
            print(f"\nAssistant: {OUT_OF_DOMAIN_REPLY}\n")
            continue

        # ── GPT-4o inference ───────────────────────────────────
        is_first = len(history) == 0
        print("Assistant: ", end="", flush=True)

        try:
            reply = chat(
                client=client,
                history=history,
                user_text=user_input,
                image_b64=active_b64 if is_first else None,
                metadata_text=metadata_text,
                is_first_turn=is_first,
            )
        except openai.OpenAIError as e:
            print(f"\n[ERROR] API call failed: {e}\n")
            continue

        print(reply + "\n")

        # Append to history
        if is_first:
            first_content = [{"type": "text", "text": f"{metadata_text}\n\nQuestion: {user_input}"}]
            if active_b64:
                first_content.insert(0, image_content_block(active_b64))
            history.append({"role": "user",      "content": first_content})
        else:
            history.append({"role": "user",      "content": user_input})
        history.append(    {"role": "assistant", "content": reply})


def query_vlm(user_text: str, history: list[dict] = None, report_path: str = DEFAULT_REPORT) -> str:
    """
    Standalone function for Streamlit integration.
    Handles report loading, API client initialization, and domain guarding.
    """
    if history is None:
        history = []

    if not API_KEY:
        return "VLM Error: Groq API_KEY not found. Please set it in secrets or .env"

    try:
        report = load_report(report_path)
    except (FileNotFoundError, ValueError) as e:
        return f"VLM Error: {e}"
    except Exception as e:
        return f"VLM Error: Unexpected error loading report: {e}"

    client = openai.OpenAI(
        api_key=API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    # Domain Guard
    try:
        if not is_domain_relevant(client, user_text):
            return OUT_OF_DOMAIN_REPLY
    except Exception as e:
        return f"VLM Error: Domain guard failed. Check API key/connection: {e}"

    # Load context
    all_crops = load_all_crops(report, report_path)
    _, overview_b64 = best_overview_crop(all_crops, report)
    metadata_text = format_metadata(report)

    is_first = (len(history) == 0)

    try:
        reply = chat(
            client=client,
            history=history,
            user_text=user_text,
            image_b64=overview_b64 if is_first else None,
            metadata_text=metadata_text,
            is_first_turn=is_first,
        )
        return reply
    except Exception as e:
        return f"VLM Error: AI inference failed: {e}"


# ──────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Colonoscopy VLM Assistant — powered by GPT-4o"
    )
    parser.add_argument(
        "--report",
        type=str,
        default=DEFAULT_REPORT,
        help=f"Path to polyp_report.json from trainTrack.py (default: {DEFAULT_REPORT})",
    )
    args = parser.parse_args()

    report = load_report(args.report)
    client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
    )
    interactive_session(client, report, args.report)


if __name__ == "__main__":
    main()