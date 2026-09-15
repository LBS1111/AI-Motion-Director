"""Render an original 6-second motion/MP4 pipeline example (Pillow + FFmpeg)."""
from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
from pathlib import Path

from core import ROOT, atomic_json, file_hash

spec = importlib.util.spec_from_file_location("motion_math", ROOT / "assets/implementations/motion_math.py")
motion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(motion)


def render(out, width=1280, height=720, fps=30):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise ValueError("FFmpeg required")
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise ValueError("Output already exists; choose a new version")
    font_candidates = [Path("C:/Windows/Fonts/segoeui.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
    font_path = next((p for p in font_candidates if p.exists()), None)
    def font(size):
        return ImageFont.truetype(str(font_path), round(size * width / 1280)) if font_path else ImageFont.load_default()
    title_font, label_font, small_font = font(48), font(25), font(16)
    duration = 6
    args = [ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    scale = width/1280
    try:
        for frame in range(duration * fps):
            t = frame / fps
            image = Image.new("RGB", (width, height), (16, 17, 19))
            draw = ImageDraw.Draw(image)
            opacity = motion.progress(t, 0.1, 0.8)
            y = int((99 + 16*(1-opacity)) * height/720)
            draw.text((width//2, y), "Motion, with intention.", font=title_font, fill=tuple(round(v*opacity) for v in (242, 242, 240)), anchor="mm")
            draw.text((width//2, round(151*height/720)), "UNDERSTAND   /   DESIGN   /   CREATE", font=small_font, fill=(119, 121, 126), anchor="mm")
            focus = motion.progress(t, 3.15, 1.1)
            for i, label in enumerate(("Understand", "Design", "Create")):
                p = motion.progress(t, 0.55 + i*0.16, 1.15)
                spread = 320 * scale * p
                cx = width/2 + (i-1)*spread*(1+0.22*focus)
                cy = height*0.535 + 54*scale*(1-p)
                w = (276 + (34 if i==1 else -8)*focus)*scale
                h = (222 + (26 if i==1 else -6)*focus)*scale
                shadow = Image.new("RGBA", image.size)
                sd = ImageDraw.Draw(shadow)
                sd.rounded_rectangle((cx-w/2, cy-h/2+18*scale, cx+w/2, cy+h/2+18*scale), radius=18*scale, fill=(0,0,0,145))
                shadow = shadow.filter(ImageFilter.GaussianBlur(18*scale))
                image = Image.alpha_composite(image.convert("RGBA"), shadow).convert("RGB")
                draw = ImageDraw.Draw(image)
                tone = round((37 + (19 if i==1 else -7)*focus)*p)
                draw.rounded_rectangle((cx-w/2, cy-h/2, cx+w/2, cy+h/2), radius=18*scale, fill=(tone,tone+1,tone+3), outline=(65,66,69), width=max(1,round(scale)))
                draw.text((cx-w/2+25*scale, cy-h/2+23*scale), f"0{i+1}", font=small_font, fill=(135,137,141))
                draw.text((cx, cy+12*scale), label, font=label_font, fill=(230,230,230), anchor="mm")
                for row, length in enumerate((0.58, 0.4)):
                    x = cx-w*length/2
                    yy = cy+52*scale+row*12*scale
                    draw.rounded_rectangle((x,yy,cx+w*length/2,yy+3*scale),radius=1*scale,fill=(91,92,96))
            draw.text((width//2, round(627*height/720)), "CODEX MOTION DIRECTOR", font=small_font, fill=(122,124,129), anchor="mm")
            process.stdin.write(image.tobytes())
        process.stdin.close()
        error = process.stderr.read().decode("utf-8", errors="replace")
        if process.wait(timeout=120):
            raise ValueError(error)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
    manifest = {"source": "Original project implementation", "purpose": "Motion primitives and deterministic MP4 export demonstration, not a complete product-launch template", "path": str(out), "sha256": file_hash(out), "width": width, "height": height, "fps": fps, "duration_seconds": duration, "audio": False}
    atomic_json(out.with_suffix(".manifest.json"), manifest)
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    print(render(a.out))
