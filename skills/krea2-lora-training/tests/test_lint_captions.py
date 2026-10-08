#!/usr/bin/env python3
"""Regression tests for scripts/lint_captions.py.

Each test builds a throwaway dataset with decodable PNG images and runs the
linter as a subprocess. Pillow is also used by the linter to verify images.

Run:
    uv run --no-project --with pillow python -m unittest discover -s tests -t .
"""

from __future__ import annotations

import json
import io
import os
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
LINTER = os.path.join(os.path.dirname(HERE), "scripts", "lint_captions.py")
TRIGGER = "gptmira7x"

with io.BytesIO() as buffer:
    Image.new("RGB", (1, 1), "white").save(buffer, format="PNG")
    PNG_1x1 = buffer.getvalue()

# Long enough to stay clear of the word-count warning where it would be noise.
FILLER = (
    " She stands in a quiet room facing the camera with a calm expression, "
    "wearing a cream knit top, and the plain wall behind her stays softly out "
    "of focus under even light."
)


class LintCase(unittest.TestCase):
    """Helpers for building a throwaway dataset and running the linter on it."""

    def setUp(self) -> None:
        self._dirs: list[str] = []

    def tearDown(self) -> None:
        for d in self._dirs:
            for root, _dirs, files in os.walk(d, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                os.rmdir(root)

    def dataset(self, files: dict[str, str]) -> str:
        """Create a dataset dir; every *.txt gets a matching 1x1 *.png."""
        d = tempfile.mkdtemp(prefix="lintfix_")
        self._dirs.append(d)
        for name, text in files.items():
            path = os.path.join(d, name)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            if name.endswith(".txt"):
                with open(path[:-4] + ".png", "wb") as fh:
                    fh.write(PNG_1x1)
        return d

    def run_lint(self, dataset: str, *extra: str):
        """Return (exit_code, parsed_json_or_None, combined_output)."""
        cmd = [
            sys.executable, "-B", "-X", "utf8", LINTER, dataset,
            "--trigger", TRIGGER, "--json", *extra,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        try:
            report = json.loads(proc.stdout)
        except json.JSONDecodeError:
            report = None
        return proc.returncode, report, proc.stdout + proc.stderr

    @staticmethod
    def joined(items) -> str:
        return " | ".join(items or [])


class MirrorDirectionTests(LintCase):
    BASE = (
        f"{TRIGGER} is an adult woman looking at the camera with a slight head "
        "tilt toward image-left, beside a window on image-left." + FILLER
    )

    def test_flipped_mirror_text_passes(self):
        mirror = self.BASE.replace("image-left", "image-right")
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": self.BASE, "a_mirror.txt": mirror}),
            "--mirror-suffix", "_mirror",
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["fail"], [], raw)

    def test_copied_mirror_text_fails(self):
        # The classic bug: append a provenance sentence, flip nothing.
        copied = (
            self.BASE
            + " This image is a horizontally mirrored view of the same scene."
        )
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": self.BASE, "a_mirror.txt": copied}),
            "--mirror-suffix", "_mirror",
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 1, raw)
        self.assertIn("reversed", self.joined(rep["fail"]), raw)
        # The provenance sentence itself is only a warning, not a blocker.
        self.assertIn("mirrored", self.joined(rep["warn"]).lower(), raw)

    def test_bare_left_right_same_direction_warns(self):
        # Bare left/right needs review, rather than assumptions about coordinates.
        base = f"{TRIGGER} is an adult woman beside a window on the left." + FILLER
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": base, "a_mirror.txt": base}),
            "--mirror-suffix", "_mirror",
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 0, raw)
        self.assertIn("cannot be verified", self.joined(rep["warn"]), raw)

    def test_bare_left_right_flipped_passes(self):
        base = f"{TRIGGER} is an adult woman beside a window on the left." + FILLER
        mirror = base.replace("the left", "the right")
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": base, "a_mirror.txt": mirror}),
            "--mirror-suffix", "_mirror",
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 0, raw)
        self.assertIn("cannot be verified", self.joined(rep["warn"]), raw)

    def test_balanced_pair_still_fails(self):
        # left + right flips into the same multiset, so a count comparison is
        # blind to it. Identity of the wording has to be checked.
        base = (
            f"{TRIGGER} is an adult woman with a window on image-left and shelves "
            "on image-right." + FILLER
        )
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": base, "a_mirror.txt": base}),
            "--mirror-suffix", "_mirror",
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 1, raw)
        self.assertIn("reversed", self.joined(rep["fail"]), raw)

    def test_unverifiable_mirror_warns_instead_of_silent_pass(self):
        # Neither caption names a side: the flip cannot be confirmed from text.
        plain = f"{TRIGGER} is an adult woman in a close portrait." + FILLER
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": plain, "a_mirror.txt": plain}),
            "--mirror-suffix", "_mirror",
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 0, raw)  # cannot block, but must not stay silent
        self.assertIn("cannot be verified", self.joined(rep["warn"]), raw)

    def test_identical_mode_rejects_direction_words(self):
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": self.BASE, "a_mirror.txt": self.BASE}),
            "--mirror-suffix", "_mirror", "--mirror-mode", "identical",
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 1, raw)

    def test_mirror_without_base_fails(self):
        code, rep, raw = self.run_lint(
            self.dataset({"orphan_mirror.txt": self.BASE}),
            "--mirror-suffix", "_mirror",
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 1, raw)
        self.assertIn("without base caption", self.joined(rep["fail"]), raw)


class WarningVersusBlockingTests(LintCase):
    def test_negation_is_a_warning_not_a_failure(self):
        # "without" may be an accurate description; a human decides.
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": f"{TRIGGER} is an adult woman without makeup." + FILLER})
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["fail"], [], raw)
        self.assertIn("negation-like", self.joined(rep["warn"]), raw)

    def test_suffixed_negation_is_caught(self):
        # "-free" was missed by a word list of no/not/without/never.
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": f"{TRIGGER} is an adult woman in a grain-free frame." + FILLER})
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 0, raw)
        self.assertIn("grain-free", self.joined(rep["warn"]), raw)

    def test_camera_parameters_warn(self):
        caption = (
            f"{TRIGGER} is an adult woman shot with aperture f/2.8 at 50mm."
            + FILLER
        )
        code, rep, raw = self.run_lint(self.dataset({"a.txt": caption}))
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 0, raw)
        warn = self.joined(rep["warn"])
        self.assertIn("unfounded camera parameter", warn, raw)
        self.assertIn("aperture", warn, raw)
        self.assertIn("metric focal length", warn, raw)

    def test_camera_position_words_are_not_flagged(self):
        # "filmed at eye level" is camera position; "focal plane" is the focus
        # plane. Neither is a focal length, and a `film|focal` regex got it wrong.
        caption = (
            f"{TRIGGER} is an adult woman filmed at eye level with her face sharp "
            "in the focal plane." + FILLER
        )
        code, rep, raw = self.run_lint(self.dataset({"a.txt": caption}))
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 0, raw)
        self.assertNotIn("unfounded camera parameter", self.joined(rep["warn"]), raw)

    def test_missing_caption_fails(self):
        d = self.dataset({"a.txt": f"{TRIGGER} is an adult woman." + FILLER})
        with open(os.path.join(d, "lonely.png"), "wb") as fh:
            fh.write(PNG_1x1)
        code, rep, raw = self.run_lint(d)
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 1, raw)
        self.assertIn("image without caption", self.joined(rep["fail"]), raw)

    def test_trigger_must_appear_exactly_once(self):
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": f"{TRIGGER} and {TRIGGER} again." + FILLER})
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 1, raw)
        self.assertIn("must be exactly 1", self.joined(rep["fail"]), raw)

    def test_clean_dataset_passes(self):
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": f"{TRIGGER} is an adult woman." + FILLER})
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["fail"], [], raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
