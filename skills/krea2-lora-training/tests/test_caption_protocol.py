"""Caption framing constraints and configurable trigger matching."""

from pathlib import Path

from tests.test_lint_captions import FILLER, TRIGGER, LintCase


class CaptionProtocolTests(LintCase):
    def test_frame_descriptions_fail_without_user_banned_list(self):
        for detail in (
            "采用竖幅人物摄影。", "这是一张横版照片。", "画面比例为2:3。",
            "宽银幕构图呈现人物。", "The aspect ratio is 16:9.",
            "It is a vertical composition.", "It uses landscape format.",
            "It is framed in portrait orientation.", "It is a 3:2 image.",
            "Image resolution is 1024x1536 pixels.",
        ):
            with self.subTest(detail=detail):
                root = self.dataset({"a.txt": TRIGGER + FILLER + " " + detail})
                before = {p.name: p.read_bytes() for p in Path(root).iterdir()}
                code, rep, raw = self.run_lint(root)
                self.assertEqual(code, 1, raw)
                self.assertIn("image ratio/frame", self.joined(rep["fail"]), raw)
                self.assertEqual(before, {p.name: p.read_bytes() for p in Path(root).iterdir()})

    def test_subject_framing_and_visible_objects_are_allowed(self):
        for detail in (
            "人物采用正面半身构图，站在镜头左侧。", "身后悬挂着一条横幅。",
            "The portrait shows her face in a close-up.",
            "A landscape painting hangs behind her.",
            "A wide shot shows her standing beside a vertical window.",
            "She is beside a square table at 16:30.",
            "She holds a square frame beside a widescreen monitor.",
        ):
            with self.subTest(detail=detail):
                code, rep, raw = self.run_lint(self.dataset({"a.txt": TRIGGER + FILLER + " " + detail}))
                self.assertEqual(code, 0, raw)
                self.assertEqual(rep["fail"], [], raw)

    def test_literal_trigger_accepts_unspaced_text(self):
        root = self.dataset({"a.txt": "示例角色站在窗边，头部端正，身穿浅色上衣，窗外的树木略微虚化。"})
        code, rep, raw = self.run_lint(
            root, "--trigger", "示例角色", "--trigger-match", "literal",
            "--min-words", "0", "--min-coverage", "0", "--strict",
        )
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["fail"], [], raw)

    def test_literal_trigger_still_rejects_missing_and_repeated_names(self):
        for text in ("人物站在窗边。", "示例角色站在窗边，示例角色手持书本。"):
            with self.subTest(text=text):
                code, rep, raw = self.run_lint(
                    self.dataset({"a.txt": text}), "--trigger", "示例角色", "--trigger-match", "literal",
                )
                self.assertEqual(code, 1, raw)
                self.assertIn("trigger", self.joined(rep["fail"]), raw)

    def test_literal_trigger_escapes_regex_metacharacters(self):
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": "Name(A)+ stands beside a window." + FILLER}),
            "--trigger", "Name(A)+", "--trigger-match", "literal", "--strict",
        )
        self.assertEqual(code, 0, raw)

    def test_default_word_matching_preserves_accented_names(self):
        code, rep, raw = self.run_lint(
            self.dataset({"a.txt": "Léonie est assise près de la fenêtre, avec un livre ouvert."}),
            "--trigger", "Léonie", "--min-words", "0", "--min-coverage", "0",
        )
        self.assertEqual(code, 0, raw)
        self.assertEqual(rep["fail"], [], raw)
