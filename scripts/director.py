#!/usr/bin/env python3
"""Codex Motion Director local CLI. Run with --help for supported operations."""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
import subprocess
import sys
from pathlib import Path

from core import Engine, ROOT, atomic_json, check_dependencies, digest, file_hash, lock, now, read_json

PRESETS = {"tutorial": {"width": 1920, "height": 1080, "fps": 30}, "launch": {"width": 2560, "height": 1440, "fps": 60}, "short": {"width": 1080, "height": 1920, "fps": 30}}
STAGES = ["planning", "design", "implementation", "preview", "render", "verification", "complete"]


def validate_brief(brief):
    if not isinstance(brief, dict) or not brief.get("request") or not brief.get("title"):
        raise ValueError("Brief needs title and request")
    if brief.get("kind") not in PRESETS:
        raise ValueError("kind must be tutorial/launch/short")
    duration = brief.get("duration_seconds")
    if not isinstance(duration, (float, int)) or not math.isfinite(duration) or not 0 < duration <= 86400:
        raise ValueError("Positive finite duration required")
    for key in ("inputs", "required_capabilities"):
        if key in brief and (not isinstance(brief[key], list) or not all(isinstance(x, str) for x in brief[key])):
            raise ValueError(f"{key} must be a list of strings")
    spec = {**PRESETS[brief["kind"]], **brief.get("spec", {})}
    for key in ("width", "height", "fps"):
        if not isinstance(spec[key], int) or spec[key] <= 0:
            raise ValueError(f"Positive integer {key} required")
    if spec["width"] % 2 or spec["height"] % 2:
        raise ValueError("Use even dimensions for H.264 MP4")
    return spec


def project_folder(engine, key):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", key):
        raise ValueError("Project ID must use letters, numbers, underscore or hyphen")
    return engine.home / "projects" / key


def project_new(engine, key, brief):
    spec = validate_brief(brief)
    folder = project_folder(engine, key)
    with lock(engine.home):
        if folder.exists():
            raise ValueError("Project already exists; use project-show")
        for name in ("assets", "source", "previews", "output", "learning-drafts"):
            (folder / name).mkdir(parents=True)
        brief = copy.deepcopy(brief)
        brief["spec"] = spec
        atomic_json(folder / "brief.json", brief)
        atomic_json(folder / "shot-plan.json", {"schema_version": 1, "shots": []})
        atomic_json(folder / "state.json", {"schema_version": 1, "id": key, "stage": "planning", "brief_digest": digest(brief), "selected_option": None, "direction_confirmation": None, "next_action": "Prepare two content-motivated options with separate design/development/render estimates", "artifacts": [], "history": [{"at": now(), "stage": "planning"}]})
    return {"project": str(folder), "spec": spec, "stage": "planning"}


def project_update(engine, key, patch):
    folder = project_folder(engine, key)
    allowed = {"stage", "next_action", "selected_option", "direction_confirmation", "artifacts", "verification_path"}
    if set(patch) - allowed:
        raise ValueError("Unsupported state fields: " + ", ".join(set(patch) - allowed))
    with lock(engine.home):
        state = read_json(folder / "state.json")
        state.update(patch)
        if state["stage"] not in STAGES:
            raise ValueError("Unknown stage")
        brief = read_json(folder / "brief.json")
        validate_brief(brief)
        if state["stage"] in STAGES[1:] and not (state.get("selected_option") and state.get("direction_confirmation")):
            raise ValueError("Save selected direction and actual user authorization (including explicit 'choose and make')")
        if state["stage"] == "complete":
            import media
            shots = check_shots(folder / "shot-plan.json", brief["duration_seconds"])
            if not shots["passed"]:
                raise ValueError("Shot plan fails: " + "; ".join(shots["issues"]))
            expected = {**brief["spec"], "duration_seconds": brief["duration_seconds"]}
            report = read_json(state.get("verification_path", folder / "verification.json"))
            if report.get("visual_review") != "passed" or report.get("audio_review") not in ("passed", "not-applicable"):
                raise ValueError("Visual/audio review must pass before completion")
            if not report.get("review_evidence"):
                raise ValueError("Describe visual/audio review evidence before completion")
            actual = media.verify(report["path"], expected, decode=True)
            if not actual["technical_pass"] or actual["sha256"] != report.get("sha256"):
                raise ValueError("Delivered media changed or failed the project specification")
            if not any(p.is_file() for p in (folder / "source").rglob("*")):
                raise ValueError("Editable source must be present before completion")
        state["brief_digest"] = digest(brief)
        state["history"].append({"at": now(), "stage": state["stage"], "next_action": state.get("next_action")})
        atomic_json(folder / "state.json", state)
    return state


def check_shots(path, duration=None):
    data = read_json(path)
    shots = data.get("shots", [])
    issues, ids, last = [], set(), 0.0
    if not shots:
        issues.append("No shots")
    for shot in shots:
        key = shot.get("id", "")
        if not key or key in ids:
            issues.append(f"Missing/duplicate shot ID: {key}")
        ids.add(key)
        start, end = shot.get("start"), shot.get("end")
        if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in (start, end)) or not 0 <= start < end:
            issues.append(f"Invalid time range: {key}")
            continue
        if abs(start - last) > 0.001:
            issues.append(f"Gap/overlap before {key}; encode transitions inside shots")
        last = end
        if not shot.get("message") or not shot.get("hero") or not shot.get("camera", {}).get("purpose"):
            issues.append(f"Missing information purpose/hero/camera purpose: {key}")
        if not shot.get("start_state") or not shot.get("end_state"):
            issues.append(f"Missing start/end state: {key}")
    if duration is not None and abs(last - duration) > 0.001:
        issues.append("Shot plan does not cover requested duration")
    return {"passed": not issues, "issues": issues, "shots": len(shots), "duration": last}


def estimate(brief, complexity, sample=None):
    validate_brief(brief)
    base = {"simple": ([2, 5], [3, 10], [1, 5]), "medium": ([5, 12], [10, 25], [3, 15]), "complex": ([15, 30], [35, 90], [10, 60])}[complexity]
    design, development, rendering = base
    basis = "Uncalibrated broad ranges; assumes supplied assets, roughly 20 seconds and no external generation."
    if sample:
        frames, seconds = sample["frames"], sample["seconds"]
        if frames <= 0 or seconds <= 0:
            raise ValueError("Positive representative frame count and elapsed seconds required")
        spec = {**PRESETS[brief["kind"]], **brief.get("spec", {})}
        total = brief["duration_seconds"] * spec["fps"] * seconds / frames / 60
        rendering = [round(total * 0.8, 2), round(total * 1.5, 2)]
        basis = "Render range calibrated from representative frames at matching resolution, engine, quality and hardware."
    return {"minutes": {"design": design, "development": development, "render": rendering}, "basis": basis, "excluded": ["user response", "asset preparation", "downloads", "external generation", "major direction changes"], "promise": False}


def report(engine, reviewed_only=False):
    store = engine.load()
    if reviewed_only:
        lines = ["# 首批学习确认清单", "", "以下内容已完成阅读分析，尚未写入正式记忆。确认只代表允许保存，不代表原工具已运行通过。可确认全部、指定序号，或暂不保存。", ""]
        reviewed = [d for d in engine.draft_list() if d["status"] == "analyzed"]
        for i, d in enumerate(reviewed, 1):
            a = d["analysis"]
            lines += [f"## {i}. {a['title']}", "", a["summary"], "", f"- 学习来源：{(d.get('source') or {}).get('path', '独立候选')}", "- 设计目的：" + a.get("design", {}).get("purpose", a["summary"]), "- 适用场景：" + "、".join(a.get("design", {}).get("use_when", [])), "- 接入方式：" + a.get("implementation", {}).get("strategy", "偏好"), "- 原工具：" + "、".join(a.get("implementation", {}).get("engines", [])), "- 实现方式：" + a.get("implementation", {}).get("details", ""), "- 输入：" + "、".join(a.get("inputs", [])), "- 输出：" + "、".join(a.get("outputs", [])), "- 验证状态：" + a.get("verification", {}).get("level", "不适用"), "- 依赖：" + "；".join(x["name"] + ("（" + x.get("note", "") + "）" if x.get("note") else "") for x in a.get("dependencies", [])), "- 限制：" + "；".join(a.get("implementation", {}).get("limitations", [])), "- 重叠：" + "；".join(a.get("overlaps", [])), "- 冲突：" + "；".join(a.get("conflicts", [])), "- 来源许可：" + a.get("provenance", {}).get("license", "不适用") + "；未确立代码复制许可时只接入原能力，不复制实现。", "", "<details>", "<summary>确认版本与完整分析</summary>", "", f"候选：{d['id']}", "", f"确认摘要：{d['review_digest']}", "", "```json", json.dumps(a, ensure_ascii=False, indent=2), "```", "", "</details>", ""]
        return "\n".join(lines)
    lines = ["# Motion Director 能力汇总", "", f"记忆版本：{store['revision']}", "", "## 已确认能力", ""]
    for key, record in store["records"].items():
        if record["status"] != "confirmed":
            continue
        a = record["analysis"]
        lines.extend([f"### {a['title']}", "", f"- ID：{key}", f"- 摘要：{a['summary']}", f"- 类型：{a['kind']}", f"- 验证：{a.get('verification', {}).get('level', '不适用')}"])
        if a.get("capabilities"):
            lines.append("- 能力：" + "、".join(a["capabilities"]))
        if a.get("implementation"):
            lines.append("- 接入方式：" + a["implementation"]["strategy"])
            lines.append("- 限制：" + "；".join(a["implementation"]["limitations"]))
        lines.append("")
    if not any(r["status"] == "confirmed" for r in store["records"].values()):
        lines.extend(["尚无已确认学习条目。默认个人风格来自已确认的项目需求。", ""])
    lines.extend(["## 待确认学习", ""])
    for d in engine.draft_list():
        title = (d.get("analysis") or {}).get("title") or d.get("discovery", {}).get("name", d["id"])
        lines.append(f"- {title} — {d['status']} — {d['id']}")
    lines.extend(["", "扫描仅创建候选；正式路由只使用已确认记录。read表示已理解文档，不代表运行通过。", ""])
    return "\n".join(lines)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--home", help="External data directory; overrides environment/local config")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("init"); s.add_argument("--root", action="append", default=[])
    sub.add_parser("status")
    s = sub.add_parser("scan"); s.add_argument("--root", action="append", default=[])
    s = sub.add_parser("pending"); s.add_argument("--all", action="store_true")
    for command in ("inspect", "review", "show"):
        s = sub.add_parser(command); s.add_argument("id")
    s = sub.add_parser("analyze"); s.add_argument("id"); s.add_argument("--file", required=True)
    s = sub.add_parser("propose"); s.add_argument("--file", required=True); s.add_argument("--source"); s.add_argument("--update")
    s = sub.add_parser("approve"); s.add_argument("id"); s.add_argument("--digest", required=True); s.add_argument("--quote", required=True); s.add_argument("--reference", required=True)
    for command in ("dismiss", "revoke"):
        s = sub.add_parser(command); s.add_argument("id"); s.add_argument("--reason", required=True)
    s = sub.add_parser("search"); s.add_argument("query", nargs="?", default=""); s.add_argument("--limit", type=int, default=8); s.add_argument("--kind")
    s = sub.add_parser("route"); s.add_argument("--brief", required=True)
    sub.add_parser("doctor")
    s = sub.add_parser("report"); s.add_argument("--out"); s.add_argument("--reviewed-only", action="store_true")
    sub.add_parser("rebuild-index")
    s = sub.add_parser("restore-proposal"); s.add_argument("--backup", required=True); s.add_argument("--id", required=True)
    s = sub.add_parser("project-new"); s.add_argument("id"); s.add_argument("--brief", required=True)
    s = sub.add_parser("project-show"); s.add_argument("id")
    s = sub.add_parser("project-update"); s.add_argument("id"); s.add_argument("--file", required=True)
    s = sub.add_parser("check-shots"); s.add_argument("--file", required=True); s.add_argument("--duration", type=float)
    s = sub.add_parser("estimate"); s.add_argument("--brief", required=True); s.add_argument("--complexity", choices=["simple", "medium", "complex"], default="medium"); s.add_argument("--sample")
    s = sub.add_parser("extract-video"); s.add_argument("file"); s.add_argument("--out", required=True); s.add_argument("--interval", type=float, default=0.5); s.add_argument("--start", type=float, default=0); s.add_argument("--end", type=float); s.add_argument("--max-frames", type=int, default=80)
    s = sub.add_parser("verify-media"); s.add_argument("file"); s.add_argument("--expected"); s.add_argument("--out")
    return p


def dispatch(args):
    engine = Engine(args.home)
    c = args.command
    if c == "init": return engine.init(args.root)
    if c == "status": return engine.status()
    if c == "scan": return engine.scan(args.root)
    if c == "pending":
        return [{"id": d["id"], "status": d["status"], "title": (d.get("analysis") or {}).get("title") or d.get("discovery", {}).get("name"), "suggested_capabilities": d.get("discovery", {}).get("suggested_capabilities", []), "review_digest": d.get("review_digest")} for d in engine.draft_list(args.all)]
    if c == "inspect": return engine.inspect(args.id)
    if c == "review": return engine.review(args.id)
    if c == "show":
        store = engine.load()
        if args.id not in store["records"]: raise ValueError("Record not found")
        return store["records"][args.id]
    if c == "analyze": return engine.analyze(args.id, read_json(args.file))
    if c == "propose": return engine.propose(read_json(args.file), args.source, args.update)
    if c == "approve": return engine.approve(args.id, args.digest, args.quote, args.reference)
    if c == "dismiss": return engine.dismiss(args.id, args.reason)
    if c == "revoke": return engine.revoke(args.id, args.reason)
    if c == "search": return engine.search(args.query, max(1, min(args.limit, 50)), args.kind)
    if c == "route":
        brief = read_json(args.brief); validate_brief(brief)
        return engine.route(brief)
    if c == "doctor":
        return {"dependencies": check_dependencies([{"type": "executable", "name": x} for x in ("python", "node", "ffmpeg", "ffprobe", "git")]), "skill_roots": engine.config()["skill_roots"], "status": engine.status(), "note": "Presence checks only; engine-specific modules and paid services must be checked per selected adapter."}
    if c == "report":
        content = report(engine, args.reviewed_only)
        if args.out:
            target = Path(args.out).resolve(); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(content, encoding="utf-8")
            return {"report": str(target)}
        return {"markdown": content}
    if c == "rebuild-index":
        with lock(engine.home): engine.refresh_views(engine.load())
        return {"status": "rebuilt", "source": str(engine.store_path)}
    if c == "restore-proposal":
        backup = Path(args.backup).resolve()
        if backup.parent != (engine.memory / "history").resolve(): raise ValueError("Use a backup from this store's history folder")
        old = read_json(backup)["records"][args.id]
        if old["status"] != "confirmed": raise ValueError("Backup record was not confirmed")
        current = engine.load()["records"][args.id]
        if old.get("source") != current.get("source"):
            raise ValueError("Source revisions differ; analyze current source instead of transplanting an old verification")
        return engine.propose(old["analysis"], record_id=args.id)
    if c == "project-new": return project_new(engine, args.id, read_json(args.brief))
    if c == "project-show":
        folder = project_folder(engine, args.id)
        brief = read_json(folder / "brief.json"); state = read_json(folder / "state.json")
        return {"project": str(folder), "brief": brief, "state": state, "brief_changed": digest(brief) != state["brief_digest"], "shot_plan": str(folder / "shot-plan.json"), "missing_artifacts": [x for x in state.get("artifacts", []) if not Path(x).exists()]}
    if c == "project-update": return project_update(engine, args.id, read_json(args.file))
    if c == "check-shots": return check_shots(args.file, args.duration)
    if c == "estimate": return estimate(read_json(args.brief), args.complexity, read_json(args.sample) if args.sample else None)
    if c == "extract-video":
        from media import extract
        return extract(args.file, args.out, args.interval, args.start, args.end, args.max_frames)
    if c == "verify-media":
        from media import verify
        result = verify(args.file, read_json(args.expected) if args.expected else None)
        if args.out: atomic_json(args.out, result)
        return result
    raise ValueError("Unknown command")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parser().parse_args()
    try:
        result = dispatch(args)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        if isinstance(result, dict) and (result.get("passed") is False or result.get("technical_pass") is False):
            return 2
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
