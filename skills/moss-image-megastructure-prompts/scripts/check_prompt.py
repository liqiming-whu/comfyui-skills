#!/usr/bin/env python3
"""Read-only draft/output checks; all serialization and conversion stay upstream."""
import argparse
import json
from pathlib import Path
from compile_prompt import compile_prompt, unique_object, reject_constant

def load_draft(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object, parse_constant=reject_constant)

def check(draft, width=None, height=None, compiled=None):
    # The upstream compiler owns the schema, bounds and coordinate conversion.
    prompt = compile_prompt(draft)
    if (width is None) != (height is None):
        raise ValueError("Supply both external width and height")
    if width is not None:
        if any(type(v) is not int or v <= 0 or v % 16 for v in (width, height)):
            raise ValueError("External dimensions must be positive integer multiples of 16")
        if "caption" in draft:
            raise ValueError("Caption has no canvas metadata; omit dimension checks")
        if (width, height) != (draft["width"], draft["height"]):
            raise ValueError("External generation dimensions differ from the Layout canvas")
    if compiled is not None and compiled != prompt + "\n":
        raise ValueError("Compiled file differs from current draft; recompile it")
    if "caption" not in draft:
        result = json.loads(prompt)
        if result["bbox_coord_space"] != "abs_centralized" or result["bbox_format"] != "yxyx":
            raise ValueError("Unexpected compiled coordinate convention")
        if "\n" in prompt or "width" in result or "height" in result:
            raise ValueError("Layout must be one physical line without canvas metadata")
        if any(type(v) is not int for item in result["items"] for v in item["bbox"]):
            raise ValueError("Compiled boxes must be integers")
    return prompt

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--compiled", type=Path)
    args = parser.parse_args()
    try:
        draft = load_draft(args.draft)
        compiled = args.compiled.read_text(encoding="utf-8") if args.compiled else None
        check(draft, args.width, args.height, compiled)
    except (OSError, ValueError, TypeError, OverflowError) as error:
        parser.exit(2, f"Error: {error}\n")
    print("OK: draft and requested checks passed (no image generation)")

if __name__ == "__main__":
    main()
