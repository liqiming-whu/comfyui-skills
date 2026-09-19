#!/usr/bin/env python3
"""Probe and benchmark a local ComfyUI instance using only the standard library."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import locale
import os
import platform
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def decode_command_output(raw: bytes) -> str:
    """Decode Windows command output without relying on subprocess text mode."""
    encodings = ("utf-8-sig", locale.getpreferredencoding(False), "gb18030")
    for encoding in dict.fromkeys(encodings):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def command_output(command: list[str], timeout: float = 10) -> str:
    return decode_command_output(subprocess.check_output(command, timeout=timeout)).strip()


def request_json(base: str, path: str, payload: Any | None = None, timeout: float = 10) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base.rstrip("/") + path,
        data=body,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8")) if raw.strip() else None


def local_hardware() -> dict[str, Any]:
    result: dict[str, Any] = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "os": platform.platform(),
        "architecture": platform.machine(),
        "cpu": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "python": sys.version,
    }
    try:
        if os.name == "nt":
            command = (
                "$c=Get-CimInstance Win32_ComputerSystem;"
                "$p=Get-CimInstance Win32_Processor|Select-Object -First 1;"
                "$o=Get-CimInstance Win32_OperatingSystem;"
                "[pscustomobject]@{manufacturer=$c.Manufacturer;model=$c.Model;"
                "ram_total_bytes=[int64]$c.TotalPhysicalMemory;cpu_name=$p.Name;"
                "windows_caption=$o.Caption;windows_version=$o.Version}|ConvertTo-Json -Compress"
            )
            output = command_output(
                ["powershell", "-NoProfile", "-Command", command],
                timeout=10,
            )
            result["windows"] = json.loads(output)
            result["ram_total_bytes"] = result["windows"]["ram_total_bytes"]
            try:
                result["power_plan"] = command_output(["powercfg", "/getactivescheme"], timeout=10)
            except Exception as exc:
                result["power_plan_error"] = str(exc)
        else:
            result["ram_total_bytes"] = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except Exception as exc:
        result["ram_probe_error"] = str(exc)
    try:
        gpu = command_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,power.limit",
                "--format=csv,noheader,nounits",
            ],
            timeout=10,
        )
        result["nvidia_smi"] = [line.strip() for line in gpu.splitlines() if line.strip()]
    except Exception as exc:
        result["nvidia_smi_error"] = str(exc)
    return result


def system_snapshot(server: str) -> dict[str, Any]:
    return {"local": local_hardware(), "comfyui": request_json(server, "/system_stats")}


def history_messages(record: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
    timestamps: dict[str, int] = {}
    cached: list[str] = []
    for name, payload in record.get("status", {}).get("messages", []):
        if isinstance(payload, dict) and isinstance(payload.get("timestamp"), (int, float)):
            timestamps[name] = int(payload["timestamp"])
        if name == "execution_cached" and isinstance(payload, dict):
            cached.extend(str(node) for node in payload.get("nodes", []))
    return timestamps, sorted(set(cached))


def summarize_record(prompt_id: str, record: dict[str, Any]) -> dict[str, Any]:
    stamps, cached = history_messages(record)
    start = stamps.get("execution_start")
    success = stamps.get("execution_success")
    return {
        "prompt_id": prompt_id,
        "status": record.get("status", {}).get("status_str"),
        "completed": record.get("status", {}).get("completed"),
        "execution_seconds": round((success - start) / 1000, 6) if start is not None and success is not None else None,
        "execution_start_ms": start,
        "execution_success_ms": success,
        "cached_nodes": cached,
        "cached_node_count": len(cached),
    }


def load_prompt(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8-sig"))
    prompt = data.get("prompt", data) if isinstance(data, dict) else data
    if not isinstance(prompt, dict) or not prompt or not all(
        isinstance(node, dict) and "class_type" in node for node in prompt.values()
    ):
        raise ValueError("run requires an API-format prompt or an object containing a prompt field")
    return prompt, hashlib.sha256(raw).hexdigest()


def prompt_summary(prompt: dict[str, Any]) -> dict[str, Any]:
    model_suffixes = (".safetensors", ".ckpt", ".pt", ".pth", ".gguf", ".onnx", ".bin")
    models: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, str) and "://" not in value and value.lower().endswith(model_suffixes):
            models.add(value)
        elif isinstance(value, dict):
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(prompt)
    return {
        "node_count": len(prompt),
        "class_types": sorted({str(node.get("class_type")) for node in prompt.values()}),
        "model_references": sorted(models),
    }


def vary_seed_inputs(prompt: dict[str, Any]) -> dict[str, int]:
    changed: dict[str, int] = {}
    for node_id, node in prompt.items():
        inputs = node.get("inputs", {})
        for name in ("seed", "noise_seed"):
            if isinstance(inputs.get(name), int):
                value = uuid.uuid4().int % (2**50 + 1)
                inputs[name] = value
                changed[f"{node_id}.{name}"] = value
    return changed


def clear_memory_cache(server: str) -> None:
    request_json(server, "/free", {"unload_models": True, "free_memory": True}, timeout=60)


def apply_strict_benchmark(args: argparse.Namespace) -> None:
    if not args.strict_benchmark:
        return
    args.clear_cache = "before-each"
    args.vary_seed = True
    args.require_output = True
    args.require_uncached = True


def wait_for_history(server: str, prompt_id: str, timeout: float, poll: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            history = request_json(server, f"/history/{prompt_id}", timeout=min(30, timeout))
        except (TimeoutError, urllib.error.URLError):
            time.sleep(poll)
            continue
        if prompt_id in history:
            record = history[prompt_id]
            status = record.get("status", {})
            if status.get("completed"):
                return record
            messages = status.get("messages", [])
            failures = [payload for name, payload in messages if name in ("execution_error", "execution_interrupted")]
            if failures or status.get("status_str") == "error":
                raise RuntimeError(f"prompt {prompt_id} failed: {failures or status}")
        time.sleep(poll)
    raise TimeoutError(f"prompt {prompt_id} did not complete within {timeout} seconds")


def write_output(data: Any, output: Path | None) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    print(text)


def command_probe(args: argparse.Namespace) -> int:
    write_output(system_snapshot(args.server), args.output)
    return 0


def command_summarize(args: argparse.Namespace) -> int:
    history = request_json(args.server, f"/history?max_items={args.limit}")
    records = [summarize_record(prompt_id, record) for prompt_id, record in history.items()]
    write_output({"system": system_snapshot(args.server), "records": records}, args.output)
    return 0


def command_run(args: argparse.Namespace) -> int:
    prompt, digest = load_prompt(args.workflow)
    results: list[dict[str, Any]] = []
    snapshot = system_snapshot(args.server)
    for index in range(args.runs):
        run_prompt = copy.deepcopy(prompt)
        seed_overrides = vary_seed_inputs(run_prompt) if args.vary_seed else {}
        should_clear = args.clear_cache == "before-each" or (args.clear_cache == "before-first" and index == 0)
        if should_clear:
            clear_memory_cache(args.server)
            if args.cooldown:
                time.sleep(args.cooldown)
        client_id = uuid.uuid4().hex
        submitted_wall = time.time()
        submitted_mono = time.monotonic()
        response = request_json(args.server, "/prompt", {"prompt": run_prompt, "client_id": client_id})
        node_errors = response.get("node_errors") or {}
        if node_errors:
            raise RuntimeError(f"ComfyUI reported node validation errors: {node_errors}")
        prompt_id = response.get("prompt_id")
        if not prompt_id:
            raise RuntimeError(f"ComfyUI rejected prompt: {response}")
        record = wait_for_history(args.server, prompt_id, args.timeout, args.poll)
        if args.require_output and not record.get("outputs"):
            raise RuntimeError(f"prompt {prompt_id} completed without output artifacts")
        finished_wall = time.time()
        item = summarize_record(prompt_id, record)
        if args.require_uncached and item["cached_node_count"]:
            raise RuntimeError(
                f"prompt {prompt_id} reused {item['cached_node_count']} cached nodes: {item['cached_nodes']}"
            )
        item.update(
            {
                "run": index + 1,
                "cache_cleared": should_clear,
                "wall_seconds": round(time.monotonic() - submitted_mono, 6),
                "submitted_at_ms": round(submitted_wall * 1000),
                "finished_at_ms": round(finished_wall * 1000),
                "seed_overrides": seed_overrides,
            }
        )
        start_ms = item.get("execution_start_ms")
        item["queue_wait_estimate_seconds"] = (
            round((start_ms - item["submitted_at_ms"]) / 1000, 6) if start_ms is not None else None
        )
        results.append(item)

    durations = [item["execution_seconds"] for item in results if item["execution_seconds"] is not None]
    report = {
        "system": snapshot,
        "workflow": {
            "path": str(args.workflow.resolve()),
            "sha256": digest,
            **prompt_summary(prompt),
        },
        "settings": {
            "runs": args.runs,
            "clear_cache": args.clear_cache,
            "cooldown_seconds": args.cooldown,
            "poll_seconds": args.poll,
            "vary_seed": args.vary_seed,
            "require_output": args.require_output,
            "require_uncached": args.require_uncached,
            "strict_benchmark": args.strict_benchmark,
        },
        "summary": {
            "execution_median_seconds": round(statistics.median(durations), 6) if durations else None,
            "execution_min_seconds": min(durations) if durations else None,
            "execution_max_seconds": max(durations) if durations else None,
        },
        "runs": results,
    }
    write_output(report, args.output)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe = subparsers.add_parser("probe")
    probe.add_argument("--server", default="http://127.0.0.1:8188")
    probe.add_argument("--output", type=Path)
    probe.set_defaults(func=command_probe)

    summarize = subparsers.add_parser("summarize")
    summarize.add_argument("--server", default="http://127.0.0.1:8188")
    summarize.add_argument("--limit", type=int, default=20)
    summarize.add_argument("--output", type=Path)
    summarize.set_defaults(func=command_summarize)

    run = subparsers.add_parser("run")
    run.add_argument("workflow", type=Path)
    run.add_argument("--server", default="http://127.0.0.1:8188")
    run.add_argument("--runs", type=int, default=1)
    run.add_argument("--clear-cache", choices=("never", "before-first", "before-each"), default="never")
    run.add_argument("--cooldown", type=float, default=2)
    run.add_argument("--poll", type=float, default=0.2)
    run.add_argument("--timeout", type=float, default=3600)
    run.add_argument("--vary-seed", action="store_true", help="change integer seed inputs before each run to prevent execution-cache reuse")
    run.add_argument("--require-output", action="store_true", help="reject completed histories whose outputs object is empty")
    run.add_argument("--require-uncached", action="store_true", help="reject runs that report any cached nodes")
    run.add_argument("--strict-benchmark", action="store_true", help="enable before-each memory clearing, seed variation, non-empty output, and zero-cache requirements")
    run.add_argument("--output", type=Path)
    run.set_defaults(func=command_run)

    args = parser.parse_args()
    if getattr(args, "runs", 1) < 1:
        parser.error("--runs must be at least 1")
    if hasattr(args, "strict_benchmark"):
        apply_strict_benchmark(args)
    try:
        return args.func(args)
    except (OSError, ValueError, TimeoutError, urllib.error.URLError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
