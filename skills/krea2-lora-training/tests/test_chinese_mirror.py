"""Explicit Chinese coordinates share the conservative English mirror check."""

from pathlib import Path

from PIL import Image, ImageOps

from tests.test_lint_captions import LintCase


class ChineseMirrorTests(LintCase):
    TRIGGER = "林知微(Ada)"
    BASE = TRIGGER + "站在画面左侧，窗户在画面右侧。"

    def check_pair(self, base, mirror, *extra):
        root = self.dataset({"a.txt": base, "a_mirror.txt": mirror})
        # Asymmetric synthetic image and a genuine horizontal flip. No real
        # training material is read; the linter still only validates text.
        image = Image.new("RGB", (8, 4), "white")
        image.paste("red", (0, 0, 2, 4))
        image.paste("blue", (5, 0, 8, 4))
        image.save(Path(root) / "a.png")
        ImageOps.mirror(image).save(Path(root) / "a_mirror.png")
        before = {p.name: p.read_bytes() for p in Path(root).iterdir()}
        code, rep, raw = self.run_lint(
            root, "--trigger", self.TRIGGER, "--trigger-match", "literal",
            "--min-words", "0", "--min-coverage", "0",
            "--mirror-suffix", "_mirror", *extra,
        )
        self.assertIsNotNone(rep, raw)
        self.assertEqual(before, {p.name: p.read_bytes() for p in Path(root).iterdir()})
        return code, rep, raw

    def test_literal_flip_multiple_objects_and_coordinate_forms(self):
        for prefix in ("画面", "画面的"):
            for suffix in ("侧", "边", "方"):
                with self.subTest(prefix=prefix, suffix=suffix):
                    base = self.TRIGGER + f"站在{prefix}左{suffix}，窗户在{prefix}右{suffix}，书架在{prefix}左{suffix}。"
                    mirror = self.TRIGGER + f"站在{prefix}右{suffix}，窗户在{prefix}左{suffix}，书架在{prefix}右{suffix}。"
                    code, rep, raw = self.check_pair(base, mirror, "--strict")
                    self.assertEqual(code, 0, raw)
                    self.assertEqual(rep["warn"], [], raw)
                    self.assertIn("literal image-coordinate substitution matches", self.joined(rep["info"]), raw)

    def test_copied_balanced_coordinates_block_in_normal_mode(self):
        for appended in ("", " 这是同一场景的镜像。"):
            with self.subTest(appended=appended):
                code, rep, raw = self.check_pair(self.BASE, self.BASE + appended)
                self.assertEqual(code, 1, raw)
                self.assertFalse(rep["blocking_passed"], raw)
                self.assertIn("must be reversed", self.joined(rep["fail"]), raw)

    def test_identical_mode_rejects_chinese_coordinates(self):
        code, rep, raw = self.check_pair(self.BASE, self.BASE, "--mirror-mode", "identical")
        self.assertEqual(code, 1, raw)
        self.assertIn("mode=identical", self.joined(rep["fail"]), raw)

    def test_reorganized_correct_and_wrong_relations_require_review(self):
        for mirror in (
            self.TRIGGER + "旁边的窗户在画面左侧，人物站在画面右侧。",
            self.TRIGGER + "旁边的窗户在画面右侧，人物站在画面左侧。",
            self.TRIGGER + "站在画面右侧，窗户在画面右侧。",  # partial swap
            self.TRIGGER + "站在画面的右边，窗户在画面的左边。",  # synonyms
        ):
            for strict in (False, True):
                with self.subTest(mirror=mirror, strict=strict):
                    code, rep, raw = self.check_pair(self.BASE, mirror, *(("--strict",) if strict else ()))
                    self.assertEqual(code, int(strict), raw)
                    self.assertTrue(rep["blocking_passed"], raw)
                    self.assertEqual(rep["fail"], [], raw)
                    self.assertIn("relations require visual review", self.joined(rep["warn"]), raw)
                    self.assertNotIn("substitution matches", self.joined(rep["info"]), raw)

    def test_anatomy_and_motion_are_not_mechanically_swapped(self):
        base = self.TRIGGER + "站在画面左侧，左手拿书，右手扶桌，身体向左转。"
        mirror = base.replace("画面左侧", "画面右侧")
        code, rep, raw = self.check_pair(base, mirror, "--strict")
        self.assertEqual(code, 0, raw)
        self.assertIn("substitution matches", self.joined(rep["info"]), raw)
        # Changing anatomical/motion wording is a semantic rewrite, not a
        # literal coordinate-only flip that the checker can certify.
        code, rep, raw = self.check_pair(base, mirror.replace("左手", "右手"))
        self.assertEqual(code, 0, raw)
        self.assertIn("relations require visual review", self.joined(rep["warn"]), raw)

    def test_ambiguous_or_absent_coordinates_warn(self):
        for detail in ("左手拿书，右手扶桌。", "身体向左转。", "窗户在左侧，书架在右侧。", "站在窗边。", "站在镜头左侧。"):
            with self.subTest(detail=detail):
                base = self.TRIGGER + detail
                code, rep, raw = self.check_pair(base, base)
                self.assertEqual(code, 0, raw)
                self.assertEqual(rep["fail"], [], raw)
                self.assertIn("cannot be verified", self.joined(rep["warn"]), raw)
                code, rep, raw = self.check_pair(base, base, "--strict")
                self.assertEqual(code, 1, raw)
                self.assertTrue(rep["blocking_passed"], raw)

    def test_mixed_english_chinese_flip_and_copy(self):
        base = self.TRIGGER + "站在画面左侧，窗户在 image-right。"
        code, rep, raw = self.check_pair(base, base.replace("画面左侧", "画面右侧").replace("image-right", "image-left"), "--strict")
        self.assertEqual(code, 0, raw)
        code, rep, raw = self.check_pair(base, base)
        self.assertEqual(code, 1, raw)
        self.assertIn("must be reversed", self.joined(rep["fail"]), raw)

    def test_coordinate_removed_or_added_requires_review(self):
        plain = self.TRIGGER + "站在窗边。"
        for base, mirror in ((self.BASE, plain), (plain, self.BASE)):
            with self.subTest(base=base):
                code, rep, raw = self.check_pair(base, mirror)
                self.assertEqual(code, 0, raw)
                self.assertIn("relations require visual review", self.joined(rep["warn"]), raw)

    def test_mirror_checks_remain_opt_in(self):
        root = self.dataset({"a.txt": self.BASE, "a_mirror.txt": self.BASE})
        code, rep, raw = self.run_lint(root, "--trigger", self.TRIGGER, "--trigger-match", "literal", "--min-words", "0", "--min-coverage", "0", "--strict")
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["fail"], [], raw)
