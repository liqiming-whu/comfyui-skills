# Output Model Download Guide

When delivering a workflow, try to include a download guide for every referenced local model. Derive it from actual node values and the workflow's `models` manifest; do not claim that a model is required merely because it appears in this reference.

Use `model-recommendations.md` as the deduplicated family and candidate index. Keep exact download instructions here limited to models actually referenced by the delivered workflow.

For each model, provide:

1. Exact filename used by the workflow.
2. Model role: checkpoint, diffusion model, VAE, text encoder, CLIP vision, LoRA, ControlNet, or upscale model.
3. Destination under `ComfyUI/models/`.
4. Verified publisher or repository URL. Prefer a direct file URL when redistribution and access rules allow it.
5. Any license, access approval, quantization, or minimum-memory caveat that materially affects use.

## Common locations and sources

| Family / role | Typical directory | Upstream source |
| --- | --- | --- |
| SD 1.5 checkpoints | `models/checkpoints/` | `stable-diffusion-v1-5` repositories on Hugging Face |
| SDXL base | `models/checkpoints/` | `stabilityai/stable-diffusion-xl-base-1.0` |
| FLUX diffusion model | `models/diffusion_models/` | `black-forest-labs/FLUX.1-dev` |
| FLUX CLIP/T5 encoders | `models/text_encoders/` | `comfyanonymous/flux_text_encoders` |
| FLUX AE | `models/vae/` | `black-forest-labs/FLUX.1-dev` |
| Wan diffusion models | `models/diffusion_models/` | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` |
| Wan UMT5 | `models/text_encoders/` | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` |
| Wan VAE | `models/vae/` | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` |
| Wan CLIP vision | `models/clip_vision/` | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` |
| HunyuanVideo models | `models/diffusion_models/`, `models/vae/`, `models/text_encoders/` | `Comfy-Org/HunyuanVideo_repackaged` |
| SD 1.5 ControlNet | `models/controlnet/` | `lllyasviel/ControlNet-v1-1` |
| Real-ESRGAN / UltraSharp | `models/upscale_models/` | Publisher repositories for the exact selected file |

These sources are repository-level starting points, not proof that a guessed filename exists. Prefer the exact URLs already recorded in a validated template. If a URL cannot be verified, list the filename and destination as “download manually” instead of inventing a link.

## Suggested output

```markdown
## 模型下载指南

1. **exact-model-name.safetensors**（扩散模型）
   - 放置目录：`ComfyUI/models/diffusion_models/`
   - 下载地址：<verified direct or repository URL>
   - 备注：<access, license, precision, or memory note when relevant>
```

Downloading or installing models is a separate action. Generate the guide without starting a download unless the user explicitly authorizes it.
