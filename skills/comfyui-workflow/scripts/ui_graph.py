#!/usr/bin/env python3
"""Deterministic primitives for authoring ComfyUI canvas workflows."""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        raise ValueError(f"not a ComfyUI UI workflow: {path}")
    return data


def save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def node(data: dict[str, Any], node_id: int) -> dict[str, Any]:
    found = next((item for item in data["nodes"] if item.get("id") == node_id), None)
    if found is None:
        raise ValueError(f"node not found: {node_id}")
    return found


def set_widget(data: dict[str, Any], node_id: int, name: str, value: Any) -> None:
    target = node(data, node_id)
    named = target.setdefault("widgets_values_named", {})
    named[name] = value
    widget_inputs = [item for item in target.get("inputs", []) if isinstance(item.get("widget"), dict)]
    values = target.setdefault("widgets_values", [])
    for index, item in enumerate(widget_inputs):
        if item["widget"].get("name") == name:
            while len(values) <= index:
                values.append(None)
            values[index] = value
            return
    raise ValueError(f"node {node_id} has no widget input named {name!r}")


def add_node(data: dict[str, Any], spec: dict[str, Any]) -> int:
    created = copy.deepcopy(spec)
    existing = {int(item["id"]) for item in data["nodes"]}
    requested = created.get("id")
    node_id = int(requested) if requested is not None else max(existing, default=0) + 1
    if node_id in existing:
        raise ValueError(f"duplicate node id: {node_id}")
    created["id"] = node_id
    created.setdefault("mode", 0)
    created.setdefault("flags", {})
    created.setdefault("order", len(data["nodes"]))
    created.setdefault("inputs", [])
    created.setdefault("outputs", [])
    created.setdefault("properties", {})
    data["nodes"].append(created)
    data["last_node_id"] = max(int(data.get("last_node_id", 0)), node_id)
    return node_id


def connect(data: dict[str, Any], source_id: int, source_slot: int, target_id: int, target_slot: int, value_type: str | None) -> int:
    source = node(data, source_id)
    target = node(data, target_id)
    outputs = source.get("outputs") or []
    inputs = target.get("inputs") or []
    if source_slot < 0 or source_slot >= len(outputs):
        raise ValueError(f"source slot out of range: {source_id}/{source_slot}")
    if target_slot < 0 or target_slot >= len(inputs):
        raise ValueError(f"target slot out of range: {target_id}/{target_slot}")
    if inputs[target_slot].get("link") is not None:
        raise ValueError(f"target slot is already connected: {target_id}/{target_slot}")
    link_id = max([int(item[0]) for item in data.get("links", [])] or [0]) + 1
    link_type = value_type or str(outputs[source_slot].get("type") or inputs[target_slot].get("type") or "*")
    data.setdefault("links", []).append([link_id, source_id, source_slot, target_id, target_slot, link_type])
    if outputs[source_slot].get("links") is None:
        outputs[source_slot]["links"] = []
    outputs[source_slot]["links"].append(link_id)
    inputs[target_slot]["link"] = link_id
    data["last_link_id"] = max(int(data.get("last_link_id", 0)), link_id)
    return link_id


def remove_node(data: dict[str, Any], node_id: int) -> None:
    node(data, node_id)
    removed_links = {int(item[0]) for item in data.get("links", []) if item[1] == node_id or item[3] == node_id}
    data["links"] = [item for item in data.get("links", []) if int(item[0]) not in removed_links]
    data["nodes"] = [item for item in data["nodes"] if item.get("id") != node_id]
    for item in data["nodes"]:
        for entry in item.get("inputs", []) or []:
            if entry.get("link") in removed_links:
                entry["link"] = None
        for entry in item.get("outputs", []) or []:
            if entry.get("links") is not None:
                entry["links"] = [link for link in entry["links"] if link not in removed_links] or None


def parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    clone = sub.add_parser("clone-template")
    clone.add_argument("template", type=Path)
    clone.add_argument("output", type=Path)
    for command in ("set-widget", "add-node", "connect", "remove-node"):
        item = sub.add_parser(command)
        item.add_argument("workflow", type=Path)
        item.add_argument("--output", type=Path)
        if command == "set-widget":
            item.add_argument("node_id", type=int)
            item.add_argument("name")
            item.add_argument("value")
        elif command == "add-node":
            item.add_argument("spec", type=Path)
        elif command == "connect":
            item.add_argument("source_id", type=int)
            item.add_argument("source_slot", type=int)
            item.add_argument("target_id", type=int)
            item.add_argument("target_slot", type=int)
            item.add_argument("--type")
        else:
            item.add_argument("node_id", type=int)
    args = parser.parse_args()
    try:
        if args.command == "clone-template":
            load(args.template)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.template, args.output)
            result = {"output": str(args.output.resolve())}
        else:
            data = load(args.workflow)
            output = args.output or args.workflow
            if args.command == "set-widget":
                set_widget(data, args.node_id, args.name, parse_value(args.value))
            elif args.command == "add-node":
                spec = json.loads(args.spec.read_text(encoding="utf-8-sig"))
                result = {"node_id": add_node(data, spec)}
            elif args.command == "connect":
                result = {"link_id": connect(data, args.source_id, args.source_slot, args.target_id, args.target_slot, args.type)}
            else:
                remove_node(data, args.node_id)
            save(output, data)
            result = {**locals().get("result", {}), "output": str(output.resolve())}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
