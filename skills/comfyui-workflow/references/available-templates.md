# Available Templates

All paths are relative to `assets/templates/`. Some traditional templates may be outdated as models, custom nodes, and ComfyUI evolve. Inspect model references and installed-node requirements before use; file presence does not mean the workflow is a current recommendation.

## Project example workflows

These are archived working examples rather than universal baselines. For a workflow targeting a new model, prefer the Krea2, InfiniteYou, FLUX.2 klein, Qwen Edit, and Z-Image examples below as structural references before consulting older templates. Preserve useful graph structure, but verify and update every model, node contract, widget value, sampler setting, and custom-node dependency against the target ComfyUI instance.

| Example | Purpose |
| --- | --- |
| `Face Swap (InfiniteYou) Workflow V1.json` | InfiniteYou face-swap example. |
| `Krea2 High-Low-Sigma Workflow v1.json` | Krea 2 high/low-sigma example. |
| `Krea2 Raw FP8 Test Workflow (no resample) .json` | Krea 2 RAW FP8 test example. |
| `Krea2 Turbo generate training data workflow.json` | Krea 2 Turbo training-data generation example. |
| `Krea2 Turbo Stranded 4k Workflow v2.json` | Krea 2 Turbo 4K example. |
| `▶▷Flux2-klein-高清生图流.json` | FLUX.2 klein high-resolution generation example. |
| `▶▷Qwen-Edit2511-GGUF千问编辑流.json` | Qwen Image Edit 2511 GGUF editing example. |
| `▶▷Z-image-高清生图流.json` | Z-Image high-resolution generation example. |

## Image generation and editing

| Category | Templates |
| --- | --- |
| Text to image | `sd15-txt2img.json`, `sdxl-txt2img.json`, `sd3-txt2img.json`, `flux-txt2img.json` |
| Image to image | `sd15-img2img.json`, `sdxl-img2img.json`, `flux-img2img.json` |
| LoRA | `sd15-lora.json`, `sdxl-lora.json`, `flux-lora.json` |
| ControlNet | `sd15-controlnet.json`, `sdxl-controlnet.json` |
| Inpainting | `sd15-inpaint.json`, `sdxl-inpaint.json` |

## Video and multi-stage pipelines

| Template | Description |
| --- | --- |
| `wan22-txt2vid.json` | Wan 2.2 text to video. |
| `wan22-img2vid.json` | Wan 2.2 image to video. |
| `wan22-first-last.json` | Wan first/last-frame interpolation. |
| `wan22-fun-control.json` | Wan control video plus reference image. |
| `wan22-camera.json` | Wan camera-motion control. |
| `hunyuan-video.json` | HunyuanVideo text to video. |
| `hunyuan-video-i2v.json` | HunyuanVideo image to video. |
| `ltxv-txt2vid.json` | LTXV text to video. |
| `ltxv-img2vid.json` | LTXV image to video. |
| `mochi-txt2vid.json` | Mochi text to video. |
| `cosmos-txt2vid.json` | Cosmos text to video. |
| `cosmos-img2vid.json` | Cosmos image to video. |
| `flux-txt2img-wan22-img2vid.json` | FLUX text-to-image followed by Wan 2.2 image-to-video; migrated from the repository example. |
| `wan22-motion-transfer.json` | Wan 2.2 motion transfer with reference image, source video, two-stage sampling, and restored audio; migrated from the repository example. |

## Other media and architectures

| Category | Templates |
| --- | --- |
| Upscale | `upscale-model.json` |
| Audio | `stable-audio.json` |
| 3D | `hunyuan3d-v2.json` |
| Stable Cascade | `stable-cascade.json` |

## LLM integration

Requires `comfyui_LLM_party`. Read `model-recommendations.md` before selecting a provider.

| Template | Description |
| --- | --- |
| `comfyui_LLM_party/llm-chat-api.json` | API-based LLM chat. |
| `comfyui_LLM_party/llm-chat-ollama.json` | Local Ollama chat. |
| `comfyui_LLM_party/llm-prompt-enhance.json` | LLM prompt enhancement feeding FLUX generation. |
| `comfyui_LLM_party/llm-script-to-video.json` | Script, character, and storyboard text pipeline. |

## Hidden seed controls

Some frontend nodes place a hidden `control_after_generate` value immediately after a positional seed widget. When editing `widgets_values`, preserve the exported ordering or use `widgets_values_named`; do not assume every seed node has the same hidden control.
