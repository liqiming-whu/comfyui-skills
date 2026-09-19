---
name: comfyui-performance-monitor
description: Measure and compare local ComfyUI workflow execution time while recording reproducible machine, GPU, software, workflow, cache, queue, and cached-node evidence. Use for ComfyUI benchmarks, runtime monitoring, performance baselines, or repeated timing runs; do not clear cache or submit prompts without explicit user authorization.
---

# ComfyUI Performance Monitor

Use `scripts/monitor_comfyui.py` to collect evidence from the local ComfyUI API. Record configuration separately from results so comparisons remain interpretable.

## Authority boundary

- `probe` and `summarize` are read-only.
- `run` submits the supplied API prompt and can generate outputs; require user authorization.
- Cache clearing unloads models and frees memory through `POST /free`; use it only when the user explicitly selects `before-first` or `before-each`.
- Never infer permission to delete ComfyUI disk caches, outputs, or model files. This skill's cache clearing is memory-only.

## Commands

Read-only system snapshot:

```powershell
uv run python scripts/monitor_comfyui.py probe --server http://127.0.0.1:8188 --output comfyui-system.json
```

Summarize completed history without submitting work:

```powershell
uv run python scripts/monitor_comfyui.py summarize --server http://127.0.0.1:8188 --limit 20 --output comfyui-history.json
```

Run an authorized API-format workflow repeatedly:

```powershell
uv run python scripts/monitor_comfyui.py run workflow-api.json --runs 3 --clear-cache never --output benchmark.json
```

For an accepted repeated benchmark, prefer the strict preset:

```powershell
uv run python scripts/monitor_comfyui.py run workflow-api.json --runs 3 --strict-benchmark --output benchmark.json
```

`--strict-benchmark` explicitly selects `before-each` memory clearing, per-run seed variation, non-empty output validation, and rejection of every cached-node run. It therefore authorizes the same memory-only `/free` action as `--clear-cache before-each`; it never deletes disk caches or files. Read [references/measurement.md](references/measurement.md) before comparing results.
For repeated generation benchmarks, add `--vary-seed` so identical prompts do not reuse ComfyUI's execution cache. The report records every substituted seed.
For workflows expected to save or preview media, add `--require-output` so partial execution with an empty history output is rejected. Any `node_errors` returned by `/prompt` always fail the run.

## Reference benchmark

Use `assets/benchmarks/moody-krea-turbo-minimal-api.json` as a real API-workflow example. It preserves the Seed link, uses a Windows-safe `SaveImage` prefix, and requires the listed Krea custom nodes and local models. Read `references/examples/moody-krea-turbo-3x-cold-report.md` for the accepted three-run report and the diagnostic failures that shaped the strict preset. Do not assume its timings transfer to another machine.

For a three-quantization comparison with per-run RAM/VRAM sampling, read `references/examples/krea2-turbo-quantization-9x-coldish-report.md`. It distinguishes memory-only model unloading from a fully cold machine restart and records the Windows WDDM limitation on per-process VRAM measurement.

For continuous local generation, use the warm-resident protocol in `references/measurement.md`: one unscored warm-up after selecting each model, followed by repeated measured runs with changed seeds and no `/free`. Read `references/examples/krea2-turbo-cold-vs-warm-report.md` for a complete comparison of model-unload and resident-model results.

For resource attribution, use the four-state protocol in `references/measurement.md`: desktop baseline, idle ComfyUI, resident model, and inference peak. Compute temporary inference cost from a same-round resident baseline instead of from a `/free` baseline. Read `references/examples/krea2-turbo-four-state-resource-report.md` for a measured three-quantization example.

## Reporting

Distinguish:

- submission-to-success wall time;
- ComfyUI execution time from history timestamps;
- estimated queue wait;
- whether any nodes were reported as cached;
- cache policy and cooldown;
- failures and timeouts.

Do not compare runs as equivalent when workflow hash, hardware, software versions, cache policy, model state, or key generation parameters differ.
