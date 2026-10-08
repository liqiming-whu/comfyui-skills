"""File-integrity, strict-mode and mirror-boundary regression cases."""

import json
import os
from pathlib import Path

from tests.test_lint_captions import FILLER, PNG_1x1, TRIGGER, LintCase


class RegressionTests(LintCase):
    def sample(self):
        return self.dataset({"a.txt": f"{TRIGGER} is an adult woman." + FILLER})

    def test_empty_dataset_fails(self):
        code, rep, raw = self.run_lint(self.dataset({}))
        self.assertEqual(code, 1, raw)
        self.assertIn("empty dataset", self.joined(rep["fail"]))

    def test_invalid_utf8_is_reported(self):
        root = self.sample()
        with open(os.path.join(root, "a.txt"), "ab") as fh:
            fh.write(b"\xff")
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 1, raw)
        self.assertIn("UTF-8", self.joined(rep["fail"]))

    def test_png_header_is_not_an_image(self):
        root = self.sample()
        Path(root, "a.png").write_bytes(PNG_1x1[:8])
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 1, raw)
        self.assertIn("invalid image", self.joined(rep["fail"]))

    def test_truncated_image_fails(self):
        root = self.sample()
        Path(root, "a.png").write_bytes(PNG_1x1[:-15])
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 1, raw)
        self.assertIn("invalid image", self.joined(rep["fail"]))

    def test_duplicate_image_stem_fails(self):
        root = self.sample()
        Path(root, "a.jpg").write_bytes(PNG_1x1)
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 1, raw)
        self.assertIn("duplicate image stem", self.joined(rep["fail"]))

    def test_case_colliding_stems_fail(self):
        root = self.sample()
        Path(root, "A.jpg").write_bytes(PNG_1x1)
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 1, raw)
        self.assertIn("duplicate image stem", self.joined(rep["fail"]))

    def test_directory_with_image_extension_is_ignored(self):
        root = self.sample()
        Path(root, "folder.png").mkdir()
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["images"], 1)

    def test_strict_mode_fails_on_warnings_without_edits(self):
        root = self.dataset({"a.txt": f"{TRIGGER} is an adult woman without makeup." + FILLER})
        before = {p.name: p.read_bytes() for p in Path(root).iterdir()}
        normal, rep, raw = self.run_lint(root)
        self.assertEqual(normal, 0, raw)
        strict, rep, raw = self.run_lint(root, "--strict")
        self.assertEqual(strict, 1, raw)
        self.assertEqual(rep["error_count"], 0)
        self.assertGreater(rep["warning_count"], 0)
        self.assertFalse(rep["passed"])
        self.assertTrue(rep["blocking_passed"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in Path(root).iterdir()})

    def test_strict_clean_dataset_passes(self):
        code, rep, raw = self.run_lint(self.sample(), "--strict")
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["warning_count"], 0)
        self.assertTrue(rep["passed"])

    def test_missing_dimensions_are_warnings(self):
        text = f"{TRIGGER} is an adult woman. She waits quietly and looks ahead with a calm expression while both hands rest naturally beside her body as she remains standing."
        root = self.dataset({"a.txt": text})
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["coverage"], dict.fromkeys(("light", "lens", "texture", "scene"), 0.0))
        code, rep, raw = self.run_lint(root, "--strict")
        self.assertEqual(code, 1, raw)

    def test_reordered_correct_mirror_is_not_rejected(self):
        a = f"{TRIGGER} is an adult woman. The window is on image-left and the shelf is on image-right." + FILLER
        b = f"{TRIGGER} is an adult woman. The shelf is on image-left and the window is on image-right." + FILLER
        code, rep, raw = self.run_lint(self.dataset({"a.txt": a, "a_mirror.txt": b}), "--mirror-suffix", "_mirror")
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["fail"], [])
        self.assertIn("visual review", self.joined(rep["warn"]))

    def test_reordered_wrong_mirror_cannot_pass_silently(self):
        a = f"{TRIGGER} is an adult woman. The window is on image-left and the shelf is on image-right." + FILLER
        b = f"{TRIGGER} is an adult woman. The shelf is on image-right and the window is on image-left." + FILLER
        root = self.dataset({"a.txt": a, "a_mirror.txt": b})
        code, rep, raw = self.run_lint(root, "--mirror-suffix", "_mirror")
        self.assertEqual(code, 0, raw)
        self.assertIn("visual review", self.joined(rep["warn"]))
        code, rep, raw = self.run_lint(root, "--mirror-suffix", "_mirror", "--strict")
        self.assertEqual(code, 1, raw)

    def test_anatomical_right_hand_need_not_change(self):
        a = f"{TRIGGER} is an adult woman lifting her right hand." + FILLER
        code, rep, raw = self.run_lint(self.dataset({"a.txt": a, "a_mirror.txt": a}), "--mirror-suffix", "_mirror")
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["fail"], [])

    def test_utf8_bom_is_accepted(self):
        root = self.sample()
        f = Path(root, "a.txt")
        f.write_bytes(b"\xef\xbb\xbf" + f.read_bytes())
        code, rep, raw = self.run_lint(root, "--strict")
        self.assertEqual(code, 0, raw)

    def test_trigger_substring_is_not_a_trigger(self):
        root = self.dataset({"a.txt": f"{TRIGGER}extra is an adult woman." + FILLER})
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 1, raw)
        self.assertIn("missing", self.joined(rep["fail"]))

    def test_empty_trigger_is_usage_error(self):
        code, rep, raw = self.run_lint(self.sample(), "--trigger", " ")
        self.assertEqual(code, 2, raw)

    def test_chinese_compound_trigger_is_accepted(self):
        root = self.dataset({"a.txt": "林知微(Ada) is an adult woman." + FILLER})
        code, rep, raw = self.run_lint(root, "--trigger", "林知微(Ada)", "--strict")
        self.assertEqual(code, 0, raw)

    def test_json_file_matches_stdout_and_keeps_dataset_read_only(self):
        root = self.sample()
        report_file = Path(self.dataset({}), "report.json")
        before = {p.name: p.read_bytes() for p in Path(root).iterdir()}
        code, rep, raw = self.run_lint(root, "--report", str(report_file))
        self.assertEqual(code, 0, raw)
        self.assertEqual(json.loads(report_file.read_text("utf-8")), rep)
        self.assertEqual(before, {p.name: p.read_bytes() for p in Path(root).iterdir()})

    def test_report_cannot_overwrite_dataset_file(self):
        root = self.sample()
        f = Path(root, "a.txt")
        before = f.read_bytes()
        code, rep, raw = self.run_lint(root, "--report", str(f))
        self.assertEqual(code, 2, raw)
        self.assertEqual(f.read_bytes(), before)

    def test_banned_terms_are_only_explicit_user_constraints(self):
        root = self.dataset({"a.txt": f"{TRIGGER} is an adult woman with dark brown eyes." + FILLER})
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 0, raw)
        code, rep, raw = self.run_lint(root, "--banned", "dark brown eyes")
        self.assertEqual(code, 1, raw)

    def test_repetition_counts_captions_not_occurrences(self):
        repeated = " distinct velvet curtain" * 5
        root = self.dataset({"a.txt": f"{TRIGGER} is an adult woman." + FILLER + repeated})
        code, rep, raw = self.run_lint(root)
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["repetition_hotspots"], [])

    def test_repeated_runs_produce_identical_json(self):
        root = self.dataset({f"a{i}.txt": f"{TRIGGER} is an adult woman." + FILLER for i in range(5)})
        code, first, raw = self.run_lint(root)
        self.assertEqual(code, 0, raw)
        code, second, raw = self.run_lint(root)
        self.assertEqual(code, 0, raw)
        self.assertEqual(first, second)
