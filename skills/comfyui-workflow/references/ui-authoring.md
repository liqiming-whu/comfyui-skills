# UI workflow authoring

Use a template from `assets/templates/` as a starting graph, then modify the smallest possible surface. Templates are editable ComfyUI canvas JSON, not API prompts.

## Control invariants

- Preserve `id`, `pos`, `size`, `order`, `mode`, `flags`, `properties`, groups, renderer metadata, subgraphs, and unknown fields unless the requested change requires them to change.
- Create nodes from the target instance's `/object_info` contract. A node spec must include its UI `inputs` and `outputs`; use a nearby node from an exported workflow when frontend-only geometry or widget metadata is required.
- When connecting nodes, update the global link record, source output back-reference, target input `link`, and `last_link_id` together.
- Keep both `widgets_values` and `widgets_values_named` synchronized. Custom frontend widgets may store controls that are not backend inputs.
- Never silently emulate bypass mode. Let the ComfyUI frontend export bypassed or subgraph-heavy workflows to API format.

## Deterministic primitives

Run from the skill directory:

```powershell
uv run python scripts/ui_graph.py clone-template assets/templates/sdxl-txt2img.json output.json
uv run python scripts/ui_graph.py set-widget output.json 1 ckpt_name '"model.safetensors"'
uv run python scripts/ui_graph.py add-node output.json node-spec.json
uv run python scripts/ui_graph.py connect output.json 1 0 7 0
uv run python scripts/ui_graph.py remove-node output.json 7
uv run python scripts/workflow_tool.py validate output.json
```

Commands edit in place unless `--output` is supplied. `set-widget` accepts a JSON literal; an unquoted value is treated as a string. Use `add-node` only with a node spec obtained from the target workflow/frontend contract.

## Adding LoRA or custom UI nodes

First inspect the loader and downstream model/CLIP links. Insert the exact installed LoRA node contract, reconnect both branches, set the filename and strengths in both widget representations, and preserve any dynamic custom-widget data. Validate against `/object_info`; finally open the result in ComfyUI because sidebar dialogs and extension widgets are frontend behavior that structural JSON checks cannot prove.
