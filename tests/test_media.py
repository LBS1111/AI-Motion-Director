import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from core import Engine, atomic_json, read_json
from director import project_new, project_update
from media import run, verify, extract


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg integration requires local executables")
class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.video = self.root / "fixture.mp4"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=320x180:r=30:d=1", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(self.video)])

    def tearDown(self):
        self.temp.cleanup()

    def test_actual_media_specs_and_decode(self):
        result = verify(self.video, {"width": 320, "height": 180, "fps": 30, "duration_seconds": 1, "audio": False})
        self.assertTrue(result["technical_pass"])
        self.assertEqual(result["visual_review"], "pending")

    def test_spec_mismatch_fails(self):
        self.assertFalse(verify(self.video, {"width": 1920})["technical_pass"])

    def test_extraction_keeps_original_and_no_analysis_claim(self):
        before = self.video.read_bytes()
        result = extract(self.video, self.root / "frames", interval=0.25, max_frames=4)
        manifest = read_json(result["manifest"])
        self.assertEqual(len(manifest["frames"]), 4)
        self.assertEqual(manifest["analysis_status"], "awaiting_visual_analysis")
        self.assertEqual(self.video.read_bytes(), before)

    def test_variable_gif_timing_is_preserved(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow required for GIF fixture")
        gif = self.root / "variable.gif"
        images = [Image.new("RGB", (64,64), c) for c in ("red", "green", "blue")]
        images[0].save(gif, save_all=True, append_images=images[1:], duration=[100,300,50], loop=0)
        result = extract(gif, self.root / "gif-frames", interval=0.1, max_frames=3)
        timing = read_json(result["manifest"])["gif_frame_timing"]
        self.assertEqual(len(timing), 3)
        self.assertAlmostEqual(float(timing[1]["timestamp"]), 0.1, places=3)
        self.assertAlmostEqual(float(timing[2]["timestamp"]), 0.4, places=3)

    def test_completion_rechecks_media_and_source(self):
        engine = Engine(self.root / "data"); engine.init()
        brief = {"title": "Fixture", "request": "Technical test only", "kind": "tutorial", "duration_seconds": 1, "spec": {"width": 320, "height": 180, "fps": 30}}
        folder = Path(project_new(engine, "fixture", brief)["project"])
        atomic_json(folder / "shot-plan.json", {"shots": [{"id": "a", "start": 0, "end": 1, "message": "decode fixture", "hero": "solid color", "camera": {"purpose": "static technical fixture"}, "start_state": "black", "end_state": "black"}]})
        (folder / "source" / "fixture.txt").write_text("Test-only synthetic source", encoding="utf-8")
        report = verify(self.video)
        report.update({"visual_review": "passed", "audio_review": "not-applicable", "review_evidence": "Synthetic test fixture review for state-machine testing; not production approval"})
        atomic_json(folder / "verification.json", report)
        patch = {"stage": "complete", "selected_option": "fixture", "direction_confirmation": "Test fixture authorization"}
        self.assertEqual(project_update(engine, "fixture", patch)["stage"], "complete")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=white:s=320x180:r=30:d=1", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", str(self.video)])
        with self.assertRaises(ValueError): project_update(engine, "fixture", patch)


if __name__ == "__main__":
    unittest.main()
