# ComfyUI workflow formats

## UI workflow

Canvas serialization normally contains `nodes`, `links`, layout data, groups, renderer metadata, and a numeric `version`. A v0.4 link is typically:

```json
[link_id, source_node_id, source_slot, target_node_id, target_slot, "TYPE"]
```

The same link ID must be present in the source output's `links` collection and the target input's `link` field. Preserve v1 workflows and subgraphs rather than downgrading them to v0.4.

## API prompt

An API prompt submitted to `/prompt` maps node IDs to node definitions:

```json
{
  "1": {
    "class_type": "KSampler",
    "inputs": {
      "model": ["2", 0],
      "seed": 1
    }
  }
}
```

An API prompt has execution semantics but no saved canvas layout. Existing exports may wrap the prompt under `prompt`; the inspection tool accepts that structure without modifying the file.

## Export an API workflow

Open the UI workflow in ComfyUI WebUI and select **导出（API） / Export (API)** from the workflow menu to save the API JSON. Use the target instance so its frontend extensions, dynamic widgets, bypass state, and subgraphs participate in serialization. Verify the workflow runs in that instance before relying on the export for execution.

For requested changes, edit the UI workflow and repeat the WebUI export. Preserve the UI file as the editable source.
