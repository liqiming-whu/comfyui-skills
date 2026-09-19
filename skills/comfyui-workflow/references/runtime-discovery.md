# Runtime discovery

Use the target ComfyUI instance as the source of truth.

- `GET /system_stats`: versions, devices, memory and launch context.
- `GET /object_info`: registered node names, inputs, outputs and widget constraints.
- `GET /history/{prompt_id}`: completed execution record.

Before adding a node, verify its exact registered name and required inputs. For custom nodes, also verify the target plugin is installed. If the server is unavailable, clearly label validation as structural-only and avoid asserting runtime compatibility.

Model filenames are local configuration, not universal constants. Report the exact referenced filename and inferred model directory; verify download URLs separately before offering them.
