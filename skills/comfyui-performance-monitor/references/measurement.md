# Measurement contract

## Metrics

- `wall_seconds`: local time from successful `/prompt` submission until history reports completion. It includes queueing and polling delay.
- `execution_seconds`: `execution_success.timestamp - execution_start.timestamp` from `/history/{prompt_id}`. This is the primary backend duration.
- `queue_wait_estimate_seconds`: execution start minus local submission time. Clocks are normally the same machine, but treat this as an estimate.
- `cached_nodes`: node IDs reported through `execution_cached`.

## Cache policies

- `never`: preserve current loaded-model and execution cache state.
- `before-first`: unload models and free memory once before the first measured run.
- `before-each`: unload models and free memory before every measured run.

`POST /free` clears in-memory model state; it does not delete disk caches, outputs, or models. ComfyUI may still reuse operating-system file cache, compiled kernels, or custom-node caches. A fully cold machine benchmark requires a broader controlled procedure and should not be claimed from this option alone.

`POST /free` also does not guarantee that ComfyUI's node execution cache is invalidated. For repeated generation timing, use `--vary-seed` and require `cached_node_count: 0` in every accepted run. Runs with cached generation nodes are not valid cold-generation measurements.

Prefer `--strict-benchmark` for a final reported result. A valid strict run requires all of the following: `/prompt` returns no `node_errors`, history contains output artifacts, the run completes successfully, and `cached_node_count` is zero. A `success` status by itself is insufficient because ComfyUI can execute only the valid output branch of a partially invalid prompt.

## Warm resident protocol

Use this protocol when the question is continuous generation with one model already loaded:

1. Do not call `/free` during the protocol.
2. After selecting each model, run one unscored warm-up prompt.
3. Keep the model resident and submit the chosen number of measured prompts with a different seed each time.
4. Require successful non-empty outputs and verify that sampling, decode, and output nodes were not cached.
5. Allow static loader and conditioning nodes to remain cached; that reuse is part of the resident-model scenario.
6. Report warm-up time separately and exclude it from summary statistics.

Do not apply `--require-uncached` to this mode because static-node reuse is expected. Record exactly which nodes were cached so the report can distinguish valid static reuse from an invalid cached generation chain. Compare warm results with model-unload results in separate tables because they represent different operating conditions.

Use multiple runs. Report median and individual values; do not hide warm-up runs unless the exclusion rule was chosen before measurement.

## Four-state resource protocol

Use this protocol when the question is resource attribution rather than execution speed. Keep hardware, ComfyUI launch options, workflow, dimensions, and sampling units unchanged across states.

### State A — Desktop baseline

Measure whole-system RAM and whole-GPU VRAM with ComfyUI stopped. Verify that no ComfyUI process or server listener remains. Use a short fixed sampling window and report the median plus minimum and maximum, rather than a single snapshot.

### State B — ComfyUI idle

Start ComfyUI without submitting a workflow. Verify the queue is empty and exclude user-selected foreground applications from the baseline when requested. Measure:

- whole-system RAM;
- whole-GPU VRAM;
- ComfyUI main-process RSS and process-tree RSS.

Report absolute values and `State B - State A`. Treat the system delta as observed environment overhead, not as exact process attribution: operating-system caches, drivers, and unrelated background activity can contribute.

### State C — Model resident

For each model, run the workflow once, require successful non-empty output, do not call `/free` after completion, wait a fixed settling interval, and then sample the same RAM, VRAM, and process-RSS metrics. Report absolute resident use and the delta from State B.

When comparing multiple models in one ComfyUI process, call `/free` only after the current model's resident sampling is complete and before loading the next model. Record this as an inter-model transition, not part of the measured resident window. Because allocator and file-cache state may survive `/free`, flag possible order effects. If small differences require strict attribution, restart ComfyUI separately for each model and reacquire State B.

### State D — Inference peak

For each model, establish residency, settle, and measure a same-round State C baseline immediately before the measured inference. Change the seed, submit the workflow, and sample throughout execution at an interval appropriate for transient peaks. Require successful non-empty output and record OOM status.

Calculate temporary inference cost per metric as:

```text
Inference temporary cost = observed State D peak - same-round State C resident median
```

Prefer the same-round resident value over a baseline captured earlier in the session. This controls for background drift, allocator state, and model-switch order more effectively than `peak - /free baseline`.

State D whole-system RAM and whole-GPU VRAM are useful capacity metrics; process-tree RSS adds attribution for host memory. On Windows WDDM, do not claim precise per-process VRAM unless a verified API supplies it. Describe sampled maxima as observed peaks because spikes shorter than the sampling interval can be missed.

For every state, retain raw byte values, timestamps, sample count and interval, process identity, queue state, model filename, workflow identity, cache policy, failures, and the exact baseline used for each subtraction.
