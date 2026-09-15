#!/usr/bin/env python3
"""Install the reviewed third-party preset packs for Codex without bundling them."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Install reviewed preset skill packs for Codex")
    parser.add_argument("--only", action="append", default=[], help="Preset ID; repeat to select several")
    parser.add_argument("--dry-run", action="store_true", help="Show the commands without installing")
    args = parser.parse_args()
    sources = json.loads((ROOT / "presets" / "sources.json").read_text(encoding="utf-8"))["sources"]
    known = {item["id"] for item in sources}
    if set(args.only) - known:
        parser.error("Unknown preset: " + ", ".join(sorted(set(args.only) - known)))
    chosen = [item for item in sources if not args.only or item["id"] in args.only]
    npx = shutil.which("npx") if not args.dry_run else "npx"
    if not npx:
        parser.error("Node.js/npm is required: npx was not found")
    for item in chosen:
        repo = item["repo"]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            parser.error("Invalid repository in preset registry")
        command = [npx, "--yes", "skills", "add", repo, "-g", "-a", "codex", "-y"]
        print(f"{item['id']}: {' '.join(command)}", flush=True)
        if not args.dry_run:
            result = subprocess.run(command, check=False)
            if result.returncode:
                print(f"Installation failed for {item['id']}; remaining packs were not installed")
                return result.returncode
    if not args.dry_run:
        print("Preset installation finished. Start a new Codex task to use the skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
