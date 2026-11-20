#!/usr/bin/env python3
"""Measurable checks for a batch of videos and thumbnails.

Checks every video and image in a folder against checks/rules.json:
name, resolution, fps, duration and audio presence for videos; name and resolution for images.
It has no opinion on aesthetics: that's the judge's and the owner's job.

Usage:
    python3 checks/checks.py batches/2026-12/output
    python3 checks/checks.py batches/2026-12/output --rules checks/rules.json --json report.json

Exits 0 if everything passes and 1 if any file fails.
Requires ffprobe (ships with FFmpeg).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mov"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
EXTENSIONS = VIDEO_EXTENSIONS | IMAGE_EXTENSIONS


def load_rules(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def probe(video):
    """Return width, height, fps, duration and whether there is audio, according to ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_streams", "-show_format", str(video),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    vstream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
    duration = float(data.get("format", {}).get("duration", 0) or 0)
    width = height = None
    fps = None
    if vstream:
        width, height = vstream.get("width"), vstream.get("height")
        num, _, den = (vstream.get("avg_frame_rate") or "0/1").partition("/")
        try:
            fps = round(float(num) / float(den or 1), 3)
        except ZeroDivisionError:
            fps = None
    return {"width": width, "height": height, "fps": fps, "duration_s": round(duration, 3), "audio": audio}


def detect_format(name, formats):
    """Pick the format whose suffix matches the name; the longest suffix wins.
    Images only match formats with "type": "image", and videos only the rest."""
    stem = Path(name).stem
    is_image = Path(name).suffix.lower() in IMAGE_EXTENSIONS
    formats = {k: f for k, f in formats.items() if (f.get("type") == "image") == is_image}
    candidates = []
    for key, f in formats.items():
        suffix = f.get("suffix", "")
        if suffix and stem.endswith(suffix):
            candidates.append((len(suffix), key))
    if candidates:
        return max(candidates)[1]
    no_suffix = [k for k, f in formats.items() if not f.get("suffix")]
    return no_suffix[0] if no_suffix else None


def check(video, rules):
    errors = []
    name = video.name
    pattern = rules.get("file_name", {}).get("pattern")
    if pattern and not re.match(pattern, name):
        errors.append("name does not follow the naming rule")

    key = detect_format(name, rules["formats"])
    if key is None:
        return {"file": name, "format": None, "errors": ["matches no format"]}
    fmt = rules["formats"][key]

    try:
        info = probe(video)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return {"file": name, "format": key, "errors": ["ffprobe could not read the file"]}

    if (info["width"], info["height"]) != (fmt["width"], fmt["height"]):
        errors.append(f"resolution {info['width']}x{info['height']}, expected {fmt['width']}x{fmt['height']}")

    if fmt.get("type") == "image":
        return {"file": name, "format": key, "width": info["width"], "height": info["height"], "errors": errors}

    expected_fps = rules.get("fps")
    if expected_fps and not info["fps"]:
        errors.append("fps could not be read, so it was not checked")
    elif expected_fps and abs(info["fps"] - expected_fps) > 0.01:
        errors.append(f"fps {info['fps']}, expected {expected_fps}")

    tol = rules.get("duration_tolerance_s", 0.1)
    if fmt.get("max_duration_s") is not None and info["duration_s"] > fmt["max_duration_s"] + tol:
        errors.append(f"runs {info['duration_s']} s, the maximum is {fmt['max_duration_s']} s")
    if fmt.get("exact_duration_s") is not None and abs(info["duration_s"] - fmt["exact_duration_s"]) > tol:
        errors.append(f"runs {info['duration_s']} s, it must run {fmt['exact_duration_s']} s")

    if fmt.get("audio") and not info["audio"]:
        errors.append("has no audio")
    if fmt.get("audio") is False and info["audio"]:
        errors.append("has audio and this format is silent")

    return {"file": name, "format": key, **info, "errors": errors}


def main():
    root = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(description="Measurable checks for a batch of videos and thumbnails.")
    p.add_argument("folder", help="folder with the batch's videos and thumbnails")
    p.add_argument("--rules", default=str(root / "rules.json"), help="path to rules.json")
    p.add_argument("--json", help="save the full report to this file")
    args = p.parse_args()

    if not shutil.which("ffprobe"):
        sys.exit("ffprobe is missing. Install FFmpeg and try again.")

    folder = Path(args.folder)
    if not folder.is_dir():
        sys.exit(f"Folder {folder} does not exist")

    rules = load_rules(args.rules)
    videos = sorted(v for v in folder.rglob("*") if v.suffix.lower() in EXTENSIONS)
    if not videos:
        sys.exit(f"No videos or images in {folder}")

    results = [check(v, rules) for v in videos]
    failed = [r for r in results if r["errors"]]

    for r in results:
        status = "FAIL" if r["errors"] else "ok"
        print(f"[{status}] {r['file']} ({r['format'] or 'no format'})")
        for e in r["errors"]:
            print(f"        - {e}")
    print(f"\n{len(results) - len(failed)} of {len(results)} files pass the checks.")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Report saved to {args.json}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
