#!/usr/bin/env python3
"""Read-only image/caption integrity checker with optional strict warnings.

Requires Pillow. Mirror checking compares explicit image-coordinate wording;
it cannot establish visual or semantic correctness of a rewritten caption.
Exit: 0 accepted by selected mode, 1 dataset issues, 2 usage/report-write error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

# Match explicit image geometry, not a portrait subject, landscape object,
# wide shot, vertical window, or an actual banner. Other wording/languages
# still require semantic review; this is not an exhaustive language detector.
FRAME_DETAILS = re.compile(
    r"画幅|宽高比|长宽比|横版|竖版|(?:画面|图片|图像|照片)(?:的)?(?:比例|分辨率|尺寸)|"
    r"(?:横幅|竖幅|宽银幕)(?:的)?(?:构图|人物|人像|摄影|照片|图像|画面|肖像|比例)|"
    r"\b(?:aspect[- ]ratio|widescreen[- ](?:format|composition|image|photo(?:graph)?))\b|"
    r"\b(?:portrait|landscape|vertical|horizontal|square)[- ](?:format|orientation|composition)\b|"
    r"\b(?:image|picture|photo(?:graph)?|frame)[- ](?:ratio|dimensions?|resolution)\b|"
    r"(?<!\d)(?:1\s*[:：]\s*[12]|2\s*[:：]\s*[13]|3\s*[:：]\s*[24]|"
    r"4\s*[:：]\s*[35]|5\s*[:：]\s*4|9\s*[:：]\s*(?:16|21)|"
    r"16\s*[:：]\s*(?:9|10)|21\s*[:：]\s*9)(?!\d)|"
    r"\b\d{3,5}\s*[x×]\s*\d{3,5}\b",
    re.I,
)

NEGATION = ["without", "no", "not", "never", "free of", "exclude"]

# Natural-language negation in a caption is distinct from a negative-prompt
# branch. Warn for review without assuming it is invalid or rewriting it.
NEGATION_SUFFIX = re.compile(r"\b[a-z]+(?:-free|-less)\b", re.I)

# Camera settings that cannot be read off a picture. Deliberately does NOT match
# "filmed at eye level" (camera position) or "focal plane" (focus plane) - a
# regex of `film|focal` once classified those as focal-length claims, which was
# a false positive that distorted a whole review.
CAMERA_PARAMS = [
    (re.compile(r"\baperture\b", re.I), "'aperture'"),
    (re.compile(r"\bf\s*/\s*\d+(?:\.\d+)?\b", re.I), "f-number"),
    (re.compile(r"\bf-stop\b", re.I), "'f-stop'"),
    (re.compile(r"\bstopped down\b", re.I), "'stopped down'"),
    (re.compile(r"\bwide open\b", re.I), "'wide open'"),
    (re.compile(r"\bfocal length\b", re.I), "'focal length'"),
    (re.compile(r"\b\d+(?:\.\d+)?\s*mm\b", re.I), "metric focal length"),
    (re.compile(r"\b\d+(?:\.\d+)?\s*(?:degrees?|°)\b", re.I), "measured angle"),
]

# Grammar markers used to tell prose apart from bare tags.
FUNCTION_WORDS = re.compile(
    r"\b(a|an|the|is|are|was|were|she|he|they|it|her|his|their|its|with|without|"
    r"and|or|of|to|in|on|at|from|by|for|as|that|which|while|where|into|over|"
    r"under|between|wearing|wears|wore|holds|holding|rests|resting|sits|sitting|"
    r"stands|standing|looks|looking|turns|turning|leans|leaning|faces|facing|"
    r"falls|falling|blur|blurs|blurred|soften|softens|softened|light|lit|"
    r"framed|shot|filmed|held|set|close|eyes|hair|smile|smiling|this|these|"
    r"his|her|him|them|one|two|both|each|very|slightly|softly|warmly)\b",
    re.I,
)

# danbooru-style markers: multi-word phrases separated by commas, attention syntax
TAG_SOUP_MARKERS = [
    (re.compile(r"\([^()]*:\s*\d+(?:\.\d+)?\)"), "A1111 weight syntax '(tag:1.2)'"),
    (re.compile(r"::"), "'::' prompt-weight syntax"),
    (re.compile(r"\b\w+_\w+\b"), "underscore_joined tag"),
    (re.compile(r"\b(masterpiece|best quality|highres|absurdres|score_\d)\b", re.I), "legacy quality tag"),
]

DIMENSIONS = {
    "light": re.compile(
        r"\b(light|lighting|daylight|sunlight|sun|lit|lamp|backlit|back-light|"
        r"window light|golden[- ]hour|high[- ]key|dappled|overcast|flash|glow|"
        r"shadow\w*|rim|ambient)\b",
        re.I,
    ),
    "lens": re.compile(
        r"\b(focus|focused|depth of field|blur\w*|defocus\w*|out of focus|bokeh|"
        r"telephoto|wide[- ]angle|perspective|eye level|eye height|camera|shot|"
        r"framed|framing|crop\w*|close[- ]up|full[- ]body|waist[- ]up|chest[- ]up|"
        r"high angle|low angle|tilt)\b",
        re.I,
    ),
    "texture": re.compile(
        r"\b(texture\w*|weave|nap|fibre|fiber|grain\w*|matte|gloss\w*|satin|"
        r"smooth|sharp|soft|haze|flare|clip\w*|overexpos\w*|rendering|"
        r"knit|linen|cotton|wool|silk|lace|crochet)\b",
        re.I,
    ),
    "scene": re.compile(
        r"\b(wall|window|shelf\w*|desk|table|sofa|couch|chair|bed|floor|rug|carpet|"
        r"curtain|door|path|garden|street|pavement|sidewalk|room|studio|outdoor\w*|"
        r"indoor\w*|background|foreground|building\w*|tree\w*|plant\w*|flower\w*|"
        r"book\w*|glass\w*|plant\w*)\b",
        re.I,
    ),
}


class Report:
    def __init__(self) -> None:
        self.fail: list[str] = []
        self.warn: list[str] = []
        self.info: list[str] = []

    def f(self, msg: str) -> None:
        self.fail.append(msg)

    def w(self, msg: str) -> None:
        self.warn.append(msg)

    def i(self, msg: str) -> None:
        self.info.append(msg)


def read_text(path: str) -> str:
    with open(path, "rb") as fh:
        raw = fh.read()
    # utf-8-sig strips a BOM so it never leaks into a caption or a report line
    return raw.decode("utf-8-sig")


def collect(dataset_dir: str):
    names = sorted(n for n in os.listdir(dataset_dir) if os.path.isfile(os.path.join(dataset_dir, n)))
    images = [n for n in names if os.path.splitext(n)[1].lower() in IMAGE_EXTS]
    captions = [n for n in names if n.lower().endswith(".txt")]
    return images, captions


def main() -> int:
    ap = argparse.ArgumentParser(description="Krea 2 LoRA dataset caption linter")
    ap.add_argument("dataset_dir")
    ap.add_argument("--trigger", required=True, help="trigger word/phrase, must appear exactly once per caption")
    ap.add_argument(
        "--trigger-match", choices=["word", "literal"], default="word",
        help="word: require Unicode word boundaries; literal: count the exact string in unspaced text",
    )
    ap.add_argument("--mirror-suffix", default="", help="e.g. _mirror ; '' disables mirror checks")
    ap.add_argument(
        "--mirror-mode",
        choices=["flip", "identical"],
        default="flip",
        help="flip: check literal image-left/right substitution or flag visual review; "
        "identical: identical caption text with no image-coordinate wording",
    )
    ap.add_argument("--banned", default="", help="explicit user-defined comma-separated forbidden substrings; no identity defaults")
    ap.add_argument("--extra-negation", default="", help="comma-separated extra negation words to flag")
    ap.add_argument("--min-words", type=int, default=25)
    ap.add_argument("--max-words", type=int, default=200)
    ap.add_argument("--min-coverage", type=float, default=0.80, help="warning threshold for keyword coverage; not a visual-quality score")
    ap.add_argument("--strict", action="store_true", help="exit 1 for warnings as well as errors")
    ap.add_argument("--report", help="optional JSON file outside the dataset directory; no file written by default")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()
    args.trigger = args.trigger.strip()
    if not args.trigger:
        ap.error("--trigger must not be empty")
    if args.min_words < 0 or args.max_words < args.min_words or not 0 <= args.min_coverage <= 1:
        ap.error("invalid word-count or coverage thresholds")
    if args.report:
        dataset_path = Path(args.dataset_dir).resolve()
        report_path = Path(args.report).resolve()
        if report_path == dataset_path or dataset_path in report_path.parents:
            ap.error("--report must be outside the dataset directory")

    # console-safe output: Windows terminals often default to a legacy code page
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    d = args.dataset_dir
    if not os.path.isdir(d):
        print(f"error: not a directory: {d}", file=sys.stderr)
        return 2

    images, caption_files = collect(d)
    banned = [s.strip().lower() for s in args.banned.split(",") if s.strip()]
    negation = NEGATION + [s.strip().lower() for s in args.extra_negation.split(",") if s.strip()]

    rep = Report()
    per_file: dict[str, dict] = {}
    if not images and not caption_files:
        rep.f("empty dataset: no image/caption files")

    # ---------- pairing ----------
    image_stems = {os.path.splitext(n)[0] for n in images}
    caption_stems = {os.path.splitext(n)[0] for n in caption_files}
    for label, files in (("image", images), ("caption", caption_files)):
        counts = Counter(os.path.splitext(n)[0].casefold() for n in files)
        for stem, count in counts.items():
            if count > 1:
                rep.f(f"duplicate {label} stem: {stem} ({count} files)")
    for stem in sorted(image_stems - caption_stems):
        rep.f(f"image without caption: {stem}")
    for stem in sorted(caption_stems - image_stems):
        rep.f(f"caption without image: {stem}.txt")

    # ---------- container format sanity ----------
    for n in images:
        p = os.path.join(d, n)
        ext = os.path.splitext(n)[1].lower()
        try:
            with Image.open(p) as img:
                fmt = img.format
                img.verify()
            with Image.open(p) as img:
                img.load()
        except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
            rep.f(f"invalid image: {n}: {exc}")
            continue
        expected = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP", ".bmp": "BMP", ".tif": "TIFF", ".tiff": "TIFF"}.get(ext)
        if expected and fmt != expected:
            rep.w(f"extension/container mismatch: {n} is {fmt} (some loaders trust the extension)")

    # ---------- per caption ----------
    texts: dict[str, str] = {}
    for n in caption_files:
        stem = os.path.splitext(n)[0]
        path = os.path.join(d, n)
        try:
            raw = read_text(path)
        except (UnicodeDecodeError, OSError) as exc:
            rep.f(f"{n}: cannot read UTF-8 caption: {exc}")
            continue
        text = raw.strip()
        texts[stem] = text
        entry = per_file.setdefault(stem, {})
        entry["words"] = len(text.split())

        # single line
        if "\n" in raw.strip() or "\r" in raw.strip():
            rep.f(f"{n}: caption contains internal line breaks (must be one line)")

        # trigger
        trigger_pattern = re.escape(args.trigger)
        if args.trigger_match == "word":
            trigger_pattern = rf"(?<!\w){trigger_pattern}(?!\w)"
        cnt = len(re.findall(trigger_pattern, text, re.I))
        entry["trigger_count"] = cnt
        if cnt == 0:
            rep.f(f"{n}: trigger '{args.trigger}' missing")
        elif cnt > 1:
            rep.f(f"{n}: trigger '{args.trigger}' appears {cnt} times (must be exactly 1)")

        # explicit user constraints
        low = text.lower()
        for b in banned:
            if b in low:
                rep.f(f"{n}: user-defined banned phrase present: '{b}'")
        frame_detail = FRAME_DETAILS.search(text)
        if frame_detail:
            rep.f(f"{n}: image ratio/frame description present: '{frame_detail[0]}'; keep geometry in metadata")

        # Negation is a review warning, not proof of an incorrect description.
        for w in negation:
            if re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", low):
                rep.w(
                    f"{n}: negation-like '{w}' - confirm this accurately describes the image; "
                    f"caption negation is not a separate negative-prompt branch. Review by hand."
                )
        for w in sorted(set(NEGATION_SUFFIX.findall(low))):
            rep.w(
                f"{n}: negation-like suffix '{w}' - keep only if it describes what is visible; "
                f"do not 'fix' it into the opposite claim"
            )

        # unfounded camera parameters describe the camera, not the picture
        for pat, why in CAMERA_PARAMS:
            if pat.search(text):
                rep.w(f"{n}: unfounded camera parameter -> {why}; write the visible effect instead")

        # tag-soup markers
        for pat, why in TAG_SOUP_MARKERS:
            if pat.search(text):
                rep.w(f"{n}: tag-soup marker -> {why}; review whether the text is appropriate prose")

        # comma-density heuristic: real tag stacks are short segments that also
        # carry no sentence grammar. A prose enumeration ("the shelf, books,
        # plush toys and mugs") must NOT be flagged, so a segment only counts
        # as tag-like when it is short AND has no function word / verb.
        segs = [s.strip() for s in text.split(",") if s.strip()]
        if segs:
            def tag_like(s: str) -> bool:
                if len(s.split()) > 3:
                    return False
                if FUNCTION_WORDS.search(s):
                    return False
                return True

            tags = [s for s in segs if tag_like(s)]
            entry["tag_like_segments"] = len(tags)
            # Only a caption that is essentially one clause can be a bare tag
            # stack. Multi-sentence prose never is, no matter how many short
            # noun phrases it enumerates.
            if text.count(".") <= 1 and len(tags) >= 5 and len(tags) / len(segs) > 0.4:
                rep.w(
                    f"{n}: {len(tags)}/{len(segs)} comma segments look like bare tags "
                    f"(short, no grammar, no sentence structure) -> e.g. {', '.join(tags[:4])}"
                )

        # punctuation hygiene
        for pat, why in [
            (r"  +", "double space"),
            (r"\s,", "space before comma"),
            (r"\.\.(?!\.)", "double period"),
            (r",,", "double comma"),
            (r"\s\.", "space before period"),
        ]:
            if re.search(pat, text):
                rep.w(f"{n}: punctuation -> {why}")

        # word count
        if entry["words"] < args.min_words:
            rep.w(f"{n}: only {entry['words']} words (< {args.min_words}); review completeness (heuristic threshold)")
        if entry["words"] > args.max_words:
            rep.w(f"{n}: {entry['words']} words (> {args.max_words}); review relevance and encoder token limits")

    # ---------- mirror captions ----------
    # Exact image-coordinate substitution is checkable; a paraphrase is not.
    # Do not use direction counts/order as a substitute for object relations.
    if args.mirror_suffix:
        directions = re.compile(r"\bimage-(left|right)\b", re.I)
        checked = 0
        blind = []
        for stem, text in sorted(texts.items()):
            if not stem.endswith(args.mirror_suffix):
                continue
            base_stem = stem[: -len(args.mirror_suffix)]
            if base_stem not in texts:
                rep.f(f"{stem}.txt: mirror without base caption '{base_stem}.txt'")
                continue
            base = texts[base_stem]
            checked += 1

            if re.search(r"horizontally mirrored|mirrored view|mirrored version", text, re.I):
                rep.w(
                    f"{stem}.txt: states that the image is mirrored. That is production history, "
                    f"not something visible in frame; keep the note in a manifest instead."
                )

            base_dirs = directions.findall(base)
            mirror_dirs = directions.findall(text)

            if args.mirror_mode == "identical":
                if text != base:
                    rep.f(f"{stem}.txt: mirror caption differs from base caption (mode=identical)")
                if base_dirs:
                    rep.f(
                        f"{stem}.txt: mode=identical but the caption refers to image-left/right; "
                        f"those references cannot be correct for both the image and its flip"
                    )
            elif not base_dirs and not mirror_dirs:
                blind.append(stem)
            else:
                expected_text = directions.sub(
                    lambda match: "image-" + ("right" if match[1].lower() == "left" else "left"), base
                )
                normalize = lambda value: " ".join(value.lower().split())
                if base_dirs and (normalize(text) == normalize(base) or normalize(text).startswith(normalize(base) + " ")):
                    rep.f(
                        f"{stem}.txt: copied image-coordinate wording must be reversed for the mirror"
                    )
                elif normalize(text) != normalize(expected_text):
                    rep.w(f"{stem}.txt: rewritten image-coordinate relations require visual review; word counts/order cannot validate meaning")
                else:
                    rep.i(f"{stem}.txt: literal image-coordinate substitution matches; visual review still required")
        if blind:
            rep.w(
                f"{len(blind)} mirror pair(s) name no explicit image-left/right, so the flip cannot be verified "
                f"from text; anatomical left/right need not change. Visual review: {', '.join(blind[:5])}"
                + (" ..." if len(blind) > 5 else "")
            )
        rep.i(
            f"mirror pairs checked: {checked} (suffix '{args.mirror_suffix}', mode {args.mirror_mode}); "
            f"mirroring swaps tilt direction but does NOT reduce the tilted share of the dataset"
        )

    # ---------- dimension coverage ----------
    coverage = {}
    for dim, pat in DIMENSIONS.items():
        hit = [s for s, t in texts.items() if pat.search(t)]
        coverage[dim] = round(len(hit) / len(texts), 3) if texts else 0.0
        if texts and coverage[dim] < args.min_coverage:
            missing = sorted(set(texts) - set(hit))[:5]
            rep.w(
                f"dimension '{dim}' covered by only {coverage[dim]:.0%} of captions "
                f"(want >= {args.min_coverage:.0%}); e.g. missing in {', '.join(missing)}"
            )

    # ---------- repetition hotspots ----------
    phrase_counter: Counter = Counter()
    trigger_words = set(re.findall(r"[a-z0-9']+", args.trigger.lower()))
    for t in texts.values():
        # the trigger itself is a deliberate constant; keep it out of the
        # repetition report so real hotspots stand out
        cleaned = t.lower().replace(args.trigger.lower(), " ")
        words = [w for w in re.findall(r"[a-z']+", cleaned) if w not in trigger_words and w != "trigger"]
        phrases = set()
        for n in (3, 4):
            for i in range(len(words) - n + 1):
                phrases.add(" ".join(words[i : i + n]))
        phrase_counter.update(sorted(phrases))
    hotspots = [
        (p, c)
        for p, c in phrase_counter.most_common(60)
        if c >= max(4, int(0.25 * len(texts)))
        and "<trigger>" not in p
        and "trigger" not in p.split()
        and not re.fullmatch(r"(?:and|the|of|a|to|with|for|is|in|on)\b.*", p)
    ][:12]

    # ---------- summary stats ----------
    wc = [v["words"] for v in per_file.values() if "words" in v]
    stats = {}
    if wc:
        stats = {
            "captions": len(wc),
            "words_min": min(wc),
            "words_mean": round(statistics.mean(wc), 1),
            "words_max": max(wc),
            "words_stdev": round(statistics.pstdev(wc), 1),
        }

    accepted = not rep.fail and (not args.strict or not rep.warn)
    report = {
        "dataset": os.path.abspath(d),
        "images": len(images),
        "captions": len(caption_files),
        "stats": stats,
        "coverage": coverage,
        "repetition_hotspots": [{"phrase": p, "count": c} for p, c in hotspots],
        "fail": rep.fail,
        "warn": rep.warn,
        "info": rep.info,
        "error_count": len(rep.fail),
        "warning_count": len(rep.warn),
        "strict": args.strict,
        "blocking_passed": not rep.fail,
        "passed": accepted,
        "trigger_match": args.trigger_match,
        "frame_check_scope": "explicit Chinese/English phrases and common numeric forms; semantic review required for other wording",
        "mirror_scope": "text consistency only; visual semantics require image review",
    }
    report_json = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        try:
            Path(args.report).write_text(report_json + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot write report: {exc}", file=sys.stderr)
            return 2
    if args.json:
        print(report_json)
        return 0 if accepted else 1

    print(f"dataset : {os.path.abspath(d)}")
    print(f"images  : {len(images)}   captions: {len(caption_files)}   trigger: '{args.trigger}'")
    if stats:
        print(
            f"words   : min {stats['words_min']} / mean {stats['words_mean']} / max {stats['words_max']} "
            f"(stdev {stats['words_stdev']})"
        )
    print(f"coverage: " + "  ".join(f"{k}={v:.0%}" for k, v in coverage.items()))
    if hotspots:
        print("hotspots: " + "; ".join(f"'{p}' x{c}" for p, c in hotspots[:6]))
        print("          ^ counts are captions containing the phrase; review repetition against the images")
    print()
    for label, items in (("FAIL", rep.fail), ("WARN", rep.warn), ("INFO", rep.info)):
        if items:
            print(f"--- {label} ({len(items)}) ---")
            for it in items:
                print(f"  {it}")
            print()
    print("RESULT:", "PASS" if accepted else f"FAIL ({len(rep.fail)} error(s), {len(rep.warn)} warning(s), strict={args.strict})")
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
