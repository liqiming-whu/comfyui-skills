#!/usr/bin/env python3
"""Read-only inspection and structural validation of ComfyUI workflows."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any


MODEL_SUFFIXES = (".safetensors", ".ckpt", ".pt", ".pth", ".gguf", ".onnx", ".bin")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def detect_format(data: Any) -> str:
    if isinstance(data, dict) and isinstance(data.get("nodes"), list):
        return "ui"
    if isinstance(data, dict) and len(data) == 1:
        wrapped = next(iter(data.values()))
        if isinstance(wrapped, str):
            try:
                return "api-wrapper" if detect_format(json.loads(wrapped)) == "api" else "unknown"
            except json.JSONDecodeError:
                pass
    candidate = data.get("prompt") if isinstance(data, dict) else None
    if isinstance(candidate, dict) and candidate:
        data = candidate
    if isinstance(data, dict) and data and all(
        isinstance(value, dict) and "class_type" in value for value in data.values()
    ):
        return "api"
    return "unknown"


def api_prompt(data: dict[str, Any]) -> dict[str, Any]:
    candidate = data.get("prompt", data)
    if isinstance(candidate, dict) and len(candidate) == 1:
        wrapped = next(iter(candidate.values()))
        if isinstance(wrapped, str):
            parsed = json.loads(wrapped)
            if isinstance(parsed, dict):
                return parsed
    return candidate


def model_references(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str) and "://" not in value and value.lower().endswith(MODEL_SUFFIXES):
        found.add(value)
    elif isinstance(value, dict):
        for nested in value.values():
            found.update(model_references(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(model_references(nested))
    return found


def validate_ui(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    nodes = data.get("nodes", [])
    links = data.get("links", [])
    node_map: dict[int, dict[str, Any]] = {}
    for node in nodes:
        node_id = node.get("id")
        if not isinstance(node_id, int):
            errors.append(f"node has non-integer id: {node_id!r}")
        elif node_id in node_map:
            errors.append(f"duplicate node id: {node_id}")
        else:
            node_map[node_id] = node

    seen_links: set[int] = set()
    for link in links:
        if not isinstance(link, list) or len(link) < 5:
            errors.append(f"invalid link record: {link!r}")
            continue
        link_id, source_id, source_slot, target_id, target_slot = link[:5]
        if not all(isinstance(item, int) for item in link[:5]):
            errors.append(f"link contains non-integer identifiers: {link!r}")
            continue
        if link_id in seen_links:
            errors.append(f"duplicate link id: {link_id}")
        seen_links.add(link_id)
        source = node_map.get(source_id)
        target = node_map.get(target_id)
        if source is None:
            errors.append(f"link {link_id}: missing source node {source_id}")
            continue
        if target is None:
            errors.append(f"link {link_id}: missing target node {target_id}")
            continue
        outputs = source.get("outputs") or []
        inputs = target.get("inputs") or []
        if source_slot >= len(outputs):
            errors.append(f"link {link_id}: source slot {source_id}/{source_slot} is out of range")
        elif link_id not in (outputs[source_slot].get("links") or []):
            errors.append(f"link {link_id}: missing source output back-reference")
        if target_slot >= len(inputs):
            errors.append(f"link {link_id}: target slot {target_id}/{target_slot} is out of range")
        elif inputs[target_slot].get("link") != link_id:
            errors.append(f"link {link_id}: missing target input back-reference")

    max_node = max(node_map, default=0)
    max_link = max(seen_links, default=0)
    if isinstance(data.get("last_node_id"), int) and data["last_node_id"] < max_node:
        errors.append(f"last_node_id {data['last_node_id']} is below maximum node id {max_node}")
    if isinstance(data.get("last_link_id"), int) and data["last_link_id"] < max_link:
        errors.append(f"last_link_id {data['last_link_id']} is below maximum link id {max_link}")
    return errors


def validate_api(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prompt = api_prompt(data)
    node_ids = {str(node_id) for node_id in prompt}
    for node_id, node in prompt.items():
        if not isinstance(node, dict) or not isinstance(node.get("class_type"), str):
            errors.append(f"node {node_id}: missing class_type")
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            errors.append(f"node {node_id}: inputs must be an object")
            continue
        for name, value in inputs.items():
            if (
                isinstance(value, list)
                and len(value) == 2
                and isinstance(value[0], (str, int))
                and isinstance(value[1], int)
                and str(value[0]) not in node_ids
            ):
                errors.append(f"node {node_id} input {name}: missing source node {value[0]}")
    return errors


def fetch_object_info(source: str) -> dict[str, Any]:
    if source.startswith(("http://", "https://")):
        url = source.rstrip("/") + "/object_info"
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.load(response)
    return load_json(Path(source))


def node_types(data: dict[str, Any], fmt: str) -> set[str]:
    if fmt == "ui":
        return {str(node.get("type")) for node in data.get("nodes", []) if node.get("type")}
    return {str(node.get("class_type")) for node in api_prompt(data).values() if node.get("class_type")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("inspect", "validate"))
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--object-info", help="ComfyUI base URL or saved object_info JSON")
    args = parser.parse_args()

    try:
        data = load_json(args.workflow)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 2

    fmt = detect_format(data)
    errors = validate_ui(data) if fmt == "ui" else validate_api(data) if fmt in ("api", "api-wrapper") else ["unknown workflow format"]
    types = node_types(data, "api" if fmt == "api-wrapper" else fmt) if fmt != "unknown" else set()
    missing_types: list[str] = []
    display_only_missing: list[str] = []
    if args.object_info:
        try:
            registry = fetch_object_info(args.object_info)
            unregistered = types - set(registry)
            if fmt == "ui":
                connected_ids = {
                    int(node_id)
                    for link in data.get("links", [])
                    if isinstance(link, list) and len(link) >= 4
                    for node_id in (link[1], link[3])
                    if isinstance(node_id, int)
                }
                connected_types = {
                    str(node.get("type"))
                    for node in data.get("nodes", [])
                    if node.get("id") in connected_ids and node.get("type")
                }
                missing_types = sorted(unregistered & connected_types)
                display_only_missing = sorted(unregistered - connected_types)
            else:
                missing_types = sorted(unregistered)
            errors.extend(f"node type not registered: {name}" for name in missing_types)
        except Exception as exc:
            errors.append(f"object_info lookup failed: {exc}")

    summary = {
        "path": str(args.workflow.resolve()),
        "format": fmt,
        "valid": not errors,
        "node_count": len(data.get("nodes", [])) if fmt == "ui" else len(api_prompt(data)) if fmt in ("api", "api-wrapper") else 0,
        "link_count": len(data.get("links", [])) if fmt == "ui" else None,
        "node_types": sorted(types),
        "model_references": sorted(model_references(data)),
        "missing_node_types": missing_types,
        "unregistered_display_node_types": display_only_missing,
        "errors": errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if args.command == "inspect" or not errors else 1


if __name__ == "__main__":
    sys.exit(main())
