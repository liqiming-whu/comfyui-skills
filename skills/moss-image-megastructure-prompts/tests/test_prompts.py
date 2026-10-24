import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from compile_prompt import compile_prompt
from check_prompt import check, load_draft


class PromptTests(unittest.TestCase):
    def setUp(self):
        self.draft = load_draft(ROOT / 'assets/examples/inverted-cities-layout.draft.json')

    def test_upstream_files_are_unmodified(self):
        files = {
            'scripts/compile_prompt.py': 'ff7aaa85fa1b0ae4e97bb1ca5b698093dfdd5aee',
            'references/layout.md': 'cb0126c72f17bc8847806a6b093c53324f883079',
            'third_party/MOSS-Image-LICENSE': 'd645695673349e3947e8e5ae42332d0ac3164cd7',
        }
        for name, expected in files.items():
            with self.subTest(name=name):
                content = (ROOT / name).read_bytes()
                blob = b'blob ' + str(len(content)).encode() + b'\0' + content
                self.assertEqual(hashlib.sha1(blob).hexdigest(), expected)

    def test_all_examples_match_saved_outputs(self):
        paths = sorted((ROOT / 'assets/examples').glob('*.draft.json'))
        self.assertEqual(len(paths), 5)
        for path in paths:
            with self.subTest(path=path.name):
                draft = load_draft(path)
                output = path.with_name(path.name.replace('.draft.json', '.prompt.txt')).read_text(encoding='utf-8')
                dims = {} if 'caption' in draft else dict(width=draft['width'], height=draft['height'])
                prompt = check(draft, compiled=output, **dims)
                if 'caption' in draft:
                    self.assertEqual(set(draft), {'caption'})
                    self.assertEqual(prompt, draft['caption'])
                else:
                    compiled = json.loads(prompt)
                    self.assertEqual(set(compiled), {'summary', 'items', 'bbox_coord_space', 'bbox_format'})
                    self.assertNotIn('\n', prompt)
                    self.assertEqual(len(compiled['items']), len(draft['items']))
                    for item in compiled['items']:
                        y1, x1, y2, x2 = item['bbox']
                        self.assertTrue(-draft['height']//2 <= y1 < y2 <= draft['height']//2)
                        self.assertTrue(-draft['width']//2 <= x1 < x2 <= draft['width']//2)

    def test_known_rectangular_canvas_conversion(self):
        # Independent expected values, not a second implementation of the algorithm.
        result = json.loads(compile_prompt(self.draft))
        self.assertEqual(result['items'][0]['bbox'], [-432, -768, -96, 768])
        self.assertEqual(result['items'][1]['bbox'], [-112, -16, -24, 16])
        self.assertEqual(result['items'][3]['bbox'], [24, -16, 112, 16])
        self.assertEqual(result['items'][4]['bbox'], [-14, 56, 14, 72])

    def test_fractional_edges_enclose_before_centering(self):
        self.draft['items'] = [dict(label='object', caption='A stone', bbox=[0.2, 1.8, 15.1, 16.2])]
        result = json.loads(compile_prompt(self.draft))
        self.assertEqual(result['items'][0]['bbox'], [-431, -768, -415, -752])

    def test_invalid_dimensions(self):
        for value in (0, -16, 865, 864.0, True, '864', None):
            for field in ('width', 'height'):
                with self.subTest(field=field, value=value):
                    draft = copy.deepcopy(self.draft)
                    draft[field] = value
                    with self.assertRaises(ValueError):
                        check(draft)

    def test_invalid_boxes(self):
        for box in ([-1, 0, 30, 30], [0, 0, 1537, 864], [0, 0, 20, 865],
                    [20, 0, 0, 30], [0, 2, 20, 2], [0, 0, 10],
                    [0, 0, float('nan'), 10], [0, 0, float('inf'), 10],
                    [False, 0, 10, 10], ['0', 0, 10, 10]):
            with self.subTest(box=box):
                draft = copy.deepcopy(self.draft)
                draft['items'][0]['bbox'] = box
                with self.assertRaises(ValueError):
                    check(draft)

    def test_schema_errors(self):
        mutations = [
            lambda d: d.update(elements=[]),
            lambda d: d.pop('summary'),
            lambda d: d.update(items=[]),
            lambda d: d.update(bbox_format='yxyx'),
            lambda d: d.update(bbox_coord_space='normalized'),
            lambda d: d['items'][0].update(children=[]),
            lambda d: d['items'][0].update(label='cloud'),
            lambda d: d['items'][0].update(caption='  '),
            lambda d: d['items'][0].update(label='text'),
            lambda d: d['summary'].update(canvas='poster'),
        ]
        for i, mutate in enumerate(mutations):
            with self.subTest(case=i):
                draft = copy.deepcopy(self.draft)
                mutate(draft)
                with self.assertRaises(ValueError):
                    check(draft)
        for draft in ([], None, {'caption': ''}, {'caption': 'sea', 'width': 1536}):
            with self.subTest(draft=draft):
                with self.assertRaises(ValueError):
                    check(draft)

    def test_json_duplicate_keys_nonfinite_and_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            for raw in ('{"caption":"sea","caption":"sky"}', '{"width":NaN}',
                        '{"width":Infinity}', '{', '{"caption":"sea",}'):
                with self.subTest(raw=raw):
                    path.write_text(raw, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        load_draft(path)

    def test_external_canvas_mismatch_and_stale_output(self):
        for width, height in ((1024, 1024), (1536, None), (None, 864), (1537, 864)):
            with self.subTest(width=width, height=height):
                with self.assertRaises(ValueError):
                    check(self.draft, width, height)
        check(self.draft, 1536, 864)
        old = compile_prompt(self.draft) + '\n'
        self.draft['items'][-1]['bbox'][0] += 1
        with self.assertRaises(ValueError):
            check(self.draft, compiled=old)
        with self.assertRaises(ValueError):
            check({'caption': 'A sea'}, 1536, 864)

    def test_caption_and_literal_text_survive_unicode_and_newlines(self):
        caption = 'A gate beside the sea.\n石门和小舟。'
        self.assertEqual(compile_prompt({'caption': caption}), caption)
        self.draft['items'] = [dict(label='text', caption='Carved inscription',
                                    text='归去来\nHOME', bbox=[10, 20, 200, 200])]
        result = compile_prompt(self.draft)
        self.assertNotIn('\n', result)
        self.assertEqual(json.loads(result)['items'][0]['text'], '归去来\nHOME')

    def test_cities_geometry_and_light_contract(self):
        top, down, bottom, up, balloon = self.draft['items']
        t, b, h = down['bbox'], up['bbox'], balloon['bbox']
        self.assertEqual((t[0] + t[2]) / 2, 768)
        self.assertEqual((b[0] + b[2]) / 2, 768)
        self.assertEqual(b[1] - t[3], 48)
        self.assertEqual(h[3] - h[1], 28)
        self.assertEqual((h[1] + h[3]) / 2, 432)
        self.assertGreater(h[0], t[2])
        self.assertGreater(h[1], t[3])
        self.assertLess(h[3], b[1])
        self.assertEqual(top['bbox'][3] - t[1], 16)
        self.assertEqual(b[3] - bottom['bbox'][1], 16)
        text = self.draft['summary']['caption']
        for phrase in ('sunlight comes from the left', 'shadows extend right',
                       'not a reflection', 'Exactly one tiny hot-air balloon'):
            self.assertIn(phrase, text)
        caption = load_draft(ROOT / 'assets/examples/inverted-cities-caption.draft.json')['caption']
        for phrase in ('from the left', 'shadows to the right', 'single tiny', 'almost touch'):
            self.assertIn(phrase, caption)

    def test_other_scene_geometry(self):
        bridge = load_draft(ROOT / 'assets/examples/chasm-bridge-layout.draft.json')
        left, right, span, person = [i['bbox'] for i in bridge['items']]
        self.assertLess(span[0], left[2])
        self.assertGreater(span[2], right[0])
        self.assertEqual(person[3], span[1])
        self.assertTrue(span[0] < person[0] < person[2] < span[2])
        ring = load_draft(ROOT / 'assets/examples/ring-transit-layout.draft.json')
        rim, ship, skiff = [i['bbox'] for i in ring['items']]
        self.assertTrue(rim[0] < ship[0] < rim[2] < ship[2])
        self.assertGreater(skiff[0], rim[2])
        self.assertLess(skiff[2]-skiff[0], (rim[2]-rim[0])/20)
        self.assertIn('occluded', ring['summary']['caption'])
        self.assertEqual(len(ring['items']), 3)

    def test_cli_checks_and_compile_are_cwd_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = ROOT / 'assets/examples/inverted-cities-layout.draft.json'
            target = Path(tmp) / 'prompt.txt'
            result = subprocess.run([sys.executable, str(ROOT/'scripts/compile_prompt.py'),
                                     str(source), '--output', str(target)], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([sys.executable, str(ROOT/'scripts/check_prompt.py'),
                                     str(source), '--compiled', str(target), '--width', '1536', '--height', '864'],
                                    cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([sys.executable, str(ROOT/'scripts/check_prompt.py'),
                                     str(source), '--width', '1024', '--height', '1024'],
                                    cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)

    def test_cli_does_not_overwrite_editable_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'caption.json'
            source.write_text('{"caption":"A sea"}', encoding='utf-8')
            before = source.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT/'scripts/compile_prompt.py'),
                                     str(source), '--output', str(source)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(source.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
