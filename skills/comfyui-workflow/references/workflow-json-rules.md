# Workflow JSON Format Rules

These are preferred authoring conventions for new UI workflows, not a reason to rewrite valid existing workflows. Preserve the target frontend's format and unknown fields when they differ.

- Prefer LiteGraph UI format for canvas-import deliverables: a `nodes` array, a `links` array, and the frontend-supported numeric `version`.
- Where the chosen format uses them, try to include `id`, `revision`, `last_node_id`, `last_link_id`, `nodes`, `links`, `groups`, `config`, `extra`, and `version`.
- Try to retain each node's `id`, `type`, `pos`, `size`, `flags`, `order`, `mode`, `inputs`, `outputs`, `properties`, and widget data.
- Include connection inputs and widget inputs when the frontend export contains both. Keep `label` and `localized_name` when available, but do not synthesize them merely to satisfy this guide.
- For v0.4-style graphs, links normally use `[link_id, source_node_id, source_slot, target_node_id, target_slot, "TYPE"]`.
- Keep `widgets_values` in widget-input order where positional widgets are used, and try to keep `widgets_values_named` synchronized when the frontend provides it.
- Prefer at least one reachable output node such as `SaveImage`, `PreviewImage`, or `SaveVideo` for executable workflows. Component fragments may intentionally omit one.
- Try to provide required inputs and values within the ranges reported by the target instance's `/object_info`.
- Prefer real filenames for model selectors. Avoid placeholder filenames unless the workflow is explicitly a template requiring user substitution.
- Preserve an existing top-level `models` manifest. Add one when direct download URLs and directories are verified and the target frontend supports it; a manifest is useful but not mandatory for every workflow.

Example model manifest:

```json
"models": [
  {
    "name": "flux1-dev.safetensors",
    "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors",
    "directory": "diffusion_models"
  }
]
```

## Common output slots

Use these only as a starting reference and verify version-sensitive or custom nodes against `/object_info`:

```text
CheckpointLoaderSimple: 0=MODEL, 1=CLIP, 2=VAE
UNETLoader:             0=MODEL
CLIPLoader:             0=CLIP
DualCLIPLoader:         0=CLIP
VAELoader:              0=VAE
LoraLoader:             0=MODEL, 1=CLIP
CLIPTextEncode:         0=CONDITIONING
EmptyLatentImage:       0=LATENT
KSampler:               0=LATENT
VAEDecode:              0=IMAGE
LoadImage:              0=IMAGE, 1=MASK
ControlNetLoader:       0=CONTROL_NET
UpscaleModelLoader:     0=UPSCALE_MODEL
ImageUpscaleWithModel:  0=IMAGE
CLIPVisionLoader:       0=CLIP_VISION
CLIPVisionEncode:       0=CLIP_VISION_OUTPUT
```
