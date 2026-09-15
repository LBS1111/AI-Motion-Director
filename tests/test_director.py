import copy
import json
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from core import Engine, atomic_json, digest, file_hash, read_json, skill_snapshot, check_dependencies, inferred_capabilities
from director import check_shots, project_new, project_update, estimate


def analysis(kind="skill", caps=None):
    return {"kind": kind, "title": "Purposeful camera motion", "summary": "Overview followed by controlled focus", "capabilities": caps or ["camera", "ui-motion"], "design": {"purpose": "Explain hierarchy", "phases": ["overview", "focus"]}, "implementation": {"strategy": "direct", "engines": ["canvas"], "details": "Render deterministic positions", "limitations": ["2D perspective simulation"]}, "dependencies": [], "inputs": [], "outputs": ["mp4"], "evidence": [{"source": "fixture/SKILL.md", "observation": "Describes camera focus"}], "verification": {"level": "read", "evidence": []}, "provenance": {"license": "unknown", "copy_permission": "not-established"}, "overlaps": [], "conflicts": [], "related_ids": []}


class DirectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.skills = self.root / "skills"
        self.skill = self.skills / "camera"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: camera-test\ndescription: camera UI 动效 rendering\n---\n# Camera\nRead refs.md.\n", encoding="utf-8")
        (self.skill / "refs.md").write_text("Controlled camera focus", encoding="utf-8")
        self.engine = Engine(self.root / "data")
        self.engine.init([self.skills])

    def tearDown(self):
        self.temp.cleanup()

    def draft(self, value=None):
        self.engine.scan()
        d = self.engine.draft_list()[0]
        return self.engine.analyze(d["id"], value or analysis())

    def approve(self, draft):
        return self.engine.approve(draft["id"], draft["review_digest"], "Approve this fixture", "unit-test: explicit fixture authorization")

    def test_scan_does_not_write_formal_memory(self):
        before = self.engine.store_path.read_bytes()
        result = self.engine.scan()
        self.assertEqual(len(result["new_candidates"]), 1)
        self.assertEqual(before, self.engine.store_path.read_bytes())
        self.assertEqual(self.engine.search(), [])

    def test_default_install_locations_cover_codex_and_agents(self):
        fresh = Engine(self.root / "fresh-data")
        fresh.init()
        roots = set(fresh.config()["skill_roots"])
        self.assertIn(str((Path.home() / ".codex/skills").resolve()), roots)
        self.assertIn(str((Path.home() / ".agents/skills").resolve()), roots)

    def test_incremental_scan_idempotent(self):
        self.engine.scan()
        self.assertEqual(self.engine.scan()["new_candidates"], [])

    def test_unanalyzed_draft_cannot_be_approved(self):
        key = self.engine.scan()["new_candidates"][0]
        with self.assertRaises(ValueError): self.engine.approve(key, "bad", "yes", "test")

    def test_analyze_stays_pending(self):
        self.draft()
        self.assertEqual(self.engine.status()["confirmed"], 0)
        self.assertEqual(self.engine.status()["analyzed_pending"], 1)

    def test_approve_idempotent_and_searchable(self):
        d = self.draft()
        self.approve(d)
        revision = self.engine.load()["revision"]
        self.assertEqual(self.approve(d)["status"], "already-approved")
        self.assertEqual(self.engine.load()["revision"], revision)
        self.assertEqual(len(self.engine.search("camera")), 1)

    def test_exact_candidate_digest(self):
        d = self.draft()
        revised = analysis(); revised["summary"] = "Changed conclusion"
        self.engine.analyze(d["id"], revised)
        with self.assertRaises(ValueError): self.approve(d)
        self.assertEqual(self.engine.status()["confirmed"], 0)

    def test_manual_draft_tamper_blocked(self):
        d = self.draft()
        path = self.engine.drafts / (d["id"] + ".json")
        data = read_json(path); data["analysis"]["summary"] = "tampered"
        atomic_json(path, data)
        with self.assertRaises(ValueError): self.approve(d)

    def test_reference_change_invalidates_confirmation(self):
        d = self.draft()
        (self.skill / "refs.md").write_text("Different physics", encoding="utf-8")
        with self.assertRaises(ValueError): self.approve(d)
        self.assertEqual(len(self.engine.scan()["new_candidates"]), 1)

    def test_update_keeps_formal_record_but_blocks_stale_execution(self):
        d = self.draft(); self.approve(d)
        (self.skill / "refs.md").write_text("New version", encoding="utf-8")
        self.engine.scan()
        self.assertEqual(self.engine.status()["confirmed"], 1)
        route = self.engine.route({"required_capabilities": ["camera"], "inputs": [], "output": "mp4"})
        self.assertEqual(route["recommended_ids"], [])
        self.assertEqual(route["excluded"][0]["reason"], "changed")

    def test_pending_never_routes(self):
        self.draft()
        route = self.engine.route({"required_capabilities": ["camera"]})
        self.assertEqual(route["candidates"], [])
        self.assertEqual(route["uncovered"], ["camera"])

    def test_read_level_not_execution_ready(self):
        self.approve(self.draft())
        route = self.engine.route({"required_capabilities": ["camera"]})
        self.assertFalse(route["candidates"][0]["execution_ready"])

    def test_missing_inputs_excluded(self):
        a = analysis(); a["inputs"] = ["screenshots"]
        self.approve(self.draft(a))
        route = self.engine.route({"required_capabilities": ["camera"], "inputs": []})
        self.assertEqual(route["excluded"][0]["missing_inputs"], ["screenshots"])

    def test_disabled_skill_excluded(self):
        self.approve(self.draft())
        config = self.engine.config(); config["disabled_paths"] = [str(self.skill)]
        atomic_json(self.engine.home / "config.json", config)
        self.assertEqual(len(self.engine.scan()["skipped"]), 1)
        self.assertEqual(self.engine.route({"required_capabilities": ["camera"]})["excluded"][0]["reason"], "disabled")

    def test_removed_skill_excluded(self):
        self.approve(self.draft())
        (self.skill / "SKILL.md").unlink()
        self.assertEqual(self.engine.route({"required_capabilities": ["camera"]})["excluded"][0]["reason"], "missing")

    def test_partial_approval_only_selected_candidate(self):
        first = self.engine.propose(analysis("pattern"))
        second = self.engine.propose(analysis("pattern", ["physics"]))
        self.approve(first)
        self.assertEqual(self.engine.status()["confirmed"], 1)
        self.assertEqual(self.engine.get_draft(second["id"])["status"], "analyzed")

    def test_dismiss_does_not_create_rejection_preference(self):
        d = self.draft()
        self.engine.dismiss(d["id"], "not now")
        self.assertEqual(self.engine.load()["revision"], 0)
        self.assertEqual(read_json(self.engine.memory / "rejected-patterns.json")["data"], [])

    def test_revoke_removes_from_search_and_views(self):
        key = self.approve(self.draft())["id"]
        self.engine.revoke(key, "user request")
        self.assertEqual(self.engine.search(), [])
        self.assertEqual(read_json(self.engine.memory / "skill-index.json")["data"], [])
        self.assertTrue(list((self.engine.memory / "history").glob("*.json")))

    def test_concurrent_approvals_no_lost_record(self):
        ds = [self.engine.propose(analysis("pattern")) for _ in range(4)]
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(self.approve, ds))
        self.assertEqual(self.engine.status()["confirmed"], 4)
        self.assertEqual(self.engine.load()["revision"], 4)

    def test_update_conflict_blocks_stale_draft(self):
        first = self.engine.propose(analysis("pattern")); key = self.approve(first)["id"]
        a = self.engine.propose(analysis("pattern"), record_id=key)
        b = self.engine.propose(analysis("pattern", ["physics"]), record_id=key)
        self.approve(a)
        with self.assertRaises(ValueError): self.approve(b)

    def test_verification_level_needs_real_evidence(self):
        a = analysis(); a["verification"] = {"level": "reproduced", "evidence": []}
        with self.assertRaises(ValueError): self.draft(a)

    def test_project_resume_and_style_isolation(self):
        brief = {"title": "Bright", "request": "Use a bright white stage", "kind": "tutorial", "duration_seconds": 10, "constraints": {"background": "white"}}
        before = self.engine.store_path.read_bytes()
        result = project_new(self.engine, "sample", brief)
        resumed = read_json(Path(result["project"]) / "state.json")
        self.assertEqual(resumed["stage"], "planning")
        self.assertEqual(before, self.engine.store_path.read_bytes())
        self.assertEqual(result["spec"]["fps"], 30)

    def test_cannot_complete_without_media_and_review(self):
        brief = {"title": "Test", "request": "Motion", "kind": "launch", "duration_seconds": 6}
        project_new(self.engine, "sample", brief)
        with self.assertRaises((ValueError, OSError)):
            project_update(self.engine, "sample", {"stage": "complete", "selected_option": "A", "direction_confirmation": "test explicit authorization"})

    def test_project_path_escape_rejected(self):
        with self.assertRaises(ValueError): project_new(self.engine, "../escape", {})

    def test_malformed_yaml_does_not_abort_scan(self):
        (self.skill / "SKILL.md").write_text("---\nname: camera-test\ndescription: camera motion: with focus\n---\ntext", encoding="utf-8")
        self.assertEqual(len(self.engine.scan()["new_candidates"]), 1)
        self.assertTrue(self.engine.draft_list()[0]["discovery"]["metadata_warning"])

    def test_shot_gaps_are_detected(self):
        path = self.root / "shots.json"
        atomic_json(path, {"shots": [{"id": "a", "start": 1, "end": 3, "message": "x", "hero": "y", "camera": {"purpose": "z"}, "start_state": "a", "end_state": "b"}]})
        self.assertFalse(check_shots(path, 4)["passed"])

    def test_render_estimate_can_be_calibrated(self):
        brief = {"title": "Test", "request": "Motion", "kind": "tutorial", "duration_seconds": 20}
        result = estimate(brief, "medium", {"frames": 30, "seconds": 3})
        self.assertEqual(result["minutes"]["render"], [0.8, 1.5])
        self.assertFalse(result["promise"])

    def test_rebuild_views_from_source_of_truth(self):
        self.approve(self.draft())
        atomic_json(self.engine.memory / "skill-index.json", {"bad": True})
        self.engine.refresh_views(self.engine.load())
        self.assertEqual(len(read_json(self.engine.memory / "skill-index.json")["data"]), 1)

    def test_english_alias_does_not_match_inside_build(self):
        self.assertNotIn("ui-motion", inferred_capabilities("build a plugin"))
        self.assertIn("ui-motion", inferred_capabilities("Animate UI cards"))

    def test_source_update_supersedes_old_pending_candidate(self):
        self.draft()
        (self.skill / "refs.md").write_text("new version", encoding="utf-8")
        self.engine.scan()
        self.assertEqual(len(self.engine.draft_list()), 1)
        self.assertEqual(self.engine.draft_list()[0]["status"], "discovered")

    def test_manual_dependency_evidence_expires(self):
        evidence = self.root / "dependency-check.txt"
        evidence.write_text("Synthetic successful environment check", encoding="utf-8")
        dep = {"type": "manual", "name": "account-test", "check": {"path": str(evidence), "sha256": file_hash(evidence), "checked_at": "2020-01-01T00:00:00+00:00", "expires_at": "2099-01-01T00:00:00+00:00"}}
        self.assertEqual(check_dependencies([dep])[0]["state"], "available")
        dep["check"]["expires_at"] = "2021-01-01T00:00:00+00:00"
        self.assertEqual(check_dependencies([dep])[0]["state"], "unknown")

    def test_changed_execution_evidence_not_ready(self):
        evidence = self.root / "render-log.txt"; evidence.write_text("Fixture rendered", encoding="utf-8")
        a = analysis(); a["verification"] = {"level": "runnable", "evidence": [{"path": str(evidence), "sha256": file_hash(evidence), "result": "fixture success"}]}
        self.approve(self.draft(a))
        self.assertTrue(self.engine.route({"required_capabilities": ["camera"]})["candidates"][0]["execution_ready"])
        evidence.write_text("changed", encoding="utf-8")
        self.assertFalse(self.engine.route({"required_capabilities": ["camera"]})["candidates"][0]["execution_ready"])


if __name__ == "__main__":
    unittest.main()
