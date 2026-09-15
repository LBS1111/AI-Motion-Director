"""FFmpeg-backed evidence extraction and media verification; no automatic aesthetic claims."""
from __future__ import annotations

import json
import math
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

from core import atomic_json, file_hash, now


def run(args, timeout=180):
    binary = shutil.which(args[0])
    if not binary:
        raise ValueError(f"Missing executable: {args[0]}")
    result = subprocess.run([binary, *args[1:]], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, shell=False)
    if result.returncode:
        raise ValueError(result.stderr[-5000:] or f"Command failed: {args[0]}")
    return result.stdout


def probe(path, frames=False):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError("Media file not found")
    args = ["ffprobe", "-v", "error", "-of", "json", "-show_streams", "-show_format"]
    if frames:
        args.extend(["-select_streams", "v:0", "-show_frames", "-show_entries", "frame=best_effort_timestamp_time,pkt_duration_time,duration_time:stream:format"])
    return json.loads(run([*args, str(path)]))


def rate(value):
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return 0.0


def extract(path, destination, interval=0.5, start=0.0, end=None, max_frames=80):
    path, destination = Path(path).resolve(), Path(destination).resolve()
    if interval <= 0 or start < 0 or not 1 <= max_frames <= 300:
        raise ValueError("Positive interval, nonnegative start, 1..300 max_frames required")
    info = probe(path)
    duration = float(info.get("format", {}).get("duration", 0))
    if not duration:
        raise ValueError("No readable duration")
    stop = min(duration, float(end)) if end is not None else duration
    if stop <= start:
        raise ValueError("End must be after start and within the media")
    if math.ceil((stop - start) / interval) > max_frames:
        interval = (stop - start) / max_frames
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Choose an empty evidence output folder")
    destination.mkdir(parents=True, exist_ok=True)
    frames = []
    # Accurate input timestamps are retained in the manifest; each selected image is decoded.
    for index in range(max_frames):
        timestamp = start + index * interval
        if timestamp >= stop - 0.00001:
            break
        target = destination / f"frame-{index:04d}.png"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-ss", f"{timestamp:.6f}", "-frames:v", "1", "-vf", "scale=960:960:force_original_aspect_ratio=decrease", "-y", str(target)])
        if target.exists():
            frames.append({"requested_time_seconds": round(timestamp, 6), "path": str(target), "sha256": file_hash(target)})
    gif_timing = None
    if path.suffix.lower() == ".gif":
        detail = probe(path, frames=True)
        gif_timing = [{"timestamp": f.get("best_effort_timestamp_time"), "duration": f.get("duration_time", f.get("pkt_duration_time"))} for f in detail.get("frames", [])]
    manifest = {"schema_version": 1, "source": str(path), "source_sha256": file_hash(path), "created_at": now(), "duration_seconds": duration, "range": [start, stop], "sample_interval": interval, "frames": frames, "gif_frame_timing": gif_timing, "analysis_status": "awaiting_visual_analysis", "note": "Sample times are requested seek times, not exact source-frame timestamps. Use actual GIF timings and dense local sampling for curve estimates. No movement or aesthetics have been inferred by this tool."}
    atomic_json(destination / "evidence.json", manifest)
    return {"manifest": str(destination / "evidence.json"), "frames": len(frames), "range": manifest["range"], "next": "View images and source motion, then write observed/inferred pattern candidates; never auto-approve."}


def verify(path, expected=None, decode=True):
    path = Path(path).resolve()
    info = probe(path)
    videos = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    if not videos:
        raise ValueError("No video stream")
    stream = videos[0]
    actual = {"width": stream["width"], "height": stream["height"], "fps": rate(stream.get("avg_frame_rate", "0/1")), "duration_seconds": float(info.get("format", {}).get("duration", 0)), "codec": stream.get("codec_name"), "audio": any(s.get("codec_type") == "audio" for s in info["streams"])}
    checks = {"nonzero_duration": actual["duration_seconds"] > 0, "mp4_container": path.suffix.lower() == ".mp4" and "mp4" in info.get("format", {}).get("format_name", "")}
    expected = expected or {}
    for key in ("width", "height", "fps", "duration_seconds", "audio"):
        if key in expected:
            if key == "fps":
                checks[key] = abs(actual[key] - expected[key]) < 0.05
            elif key == "duration_seconds":
                checks[key] = abs(actual[key] - expected[key]) <= max(0.1, 1 / max(1, actual["fps"]))
            else:
                checks[key] = actual[key] == expected[key]
    if decode:
        run(["ffmpeg", "-hide_banner", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"], timeout=600)
        checks["full_decode"] = True
    return {"schema_version": 1, "path": str(path), "sha256": file_hash(path), "checked_at": now(), "actual": actual, "checks": checks, "technical_pass": all(checks.values()), "visual_review": "pending", "audio_review": "pending" if actual["audio"] else "not-applicable"}
