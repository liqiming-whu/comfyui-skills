# 模型推荐与模板模型基线

本文件是模板选型和模型替换的权威基线。它区分“模板已经使用的精确值”和“尚未进入模板的候选系列”，避免把热门模型、社区改版或量化文件误写成已经验证可运行的模板依赖。

最后核验：2026-09-19。

## 2026-09 主流模型格局

本节是本项目综合 B 站热度、社区口碑、Civitai、Hugging Face、魔搭下载量及近期趋势后形成的选型结论，不是模型厂商声明，也不是永久排名。后续以真实工作流测试和社区趋势变化持续修订。

- **文生图默认首选：Krea 2。** 新建通用文生图工作流时优先从官方 Turbo 或任务匹配的主流社区版开始；训练和后训练仍区分官方 RAW。
- **图像编辑优势模型：FLUX.2 [klein] 9B 与 Qwen-Image 系列。** 涉及多参考图、语义编辑、外观保持或文字编辑时优先评估这两条路线，不因 Krea 2 是文生图首选而强行替换。
- **轻量文生图选择：Z-Image。** 资源受限、少步快速生成或需要较轻本地方案时优先评估 Z-Image / Z-Image-Turbo。
- **视频生成默认首选：MiniMax H3。** 截至 2026-09，本项目将其视为社区热度与综合能力上的绝对主流；新建通用文生视频或图生视频工作流时优先评估 H3，只有硬件、节点、许可证、任务能力或已有资产不匹配时再选择 Wan 2.2、LTX-2.3 等方案。

“默认首选”决定未指定模型时的起点，不代表所有任务都必须迁移，也不代表仓库已经为该模型提供完整且实测通过的通用模板。

## 选择原则

- 新工作流优先考虑已被社区广泛使用、ComfyUI 节点支持成熟、许可证适合目标用途的模型。
- 用户提供社区量化版链接时，若来源可信、基座清楚、许可证兼容、目标节点支持该量化格式，并且硬件确实能受益，则优先评估该量化版。
- 社区版不能仅凭名称替代官方基座。应核对模型卡、基座、精度、所需编码器/VAE、推荐采样参数和文件放置目录。
- 不同社区版可能优化写实、动漫、速度、显存或提示词服从性；按任务选择。主流结论必须带核验日期，不能脱离时间范围写成永久排名。
- 模板没有采用的候选模型，在完成 UI 模板、`/object_info` 契约和真实执行验证前不得标记为“模板已支持”。

## 当前 36 份模板实际引用

以下值由 `assets/templates/` 去重整理。共享编码器、VAE 和视觉编码器只列一次。

### SD、SDXL、SD3 与 ControlNet

| 类型 | 精确模型值 |
| --- | --- |
| SD 1.5 | `v1-5-pruned-emaonly.safetensors`, `sd-v1-5-inpainting.ckpt` |
| SD 1.5 ControlNet | `control_v11p_sd15_canny.safetensors` |
| SDXL | `sd_xl_base_1.0.safetensors` |
| SDXL ControlNet | `diffusers_xl_canny_full.safetensors` |
| SD3 | `sd3_medium_incl_clips_t5xxlfp8.safetensors`, `sd3_vae.safetensors`, `clip_g.safetensors` |

### FLUX 与共享编码组件

| 类型 | 精确模型值 |
| --- | --- |
| FLUX.1 | `flux1-dev.safetensors` |
| FLUX VAE | `ae.safetensors` |
| 共享文本编码器 | `clip_l.safetensors`, `t5xxl_fp16.safetensors` |

### Wan 2.2

| 类型 | 精确模型值 |
| --- | --- |
| 官方/通用模板 | `wan2.2_t2v_14b.safetensors`, `wan2.2_i2v_480p_14b.safetensors`, `wan2.2_fun_control.safetensors` |
| 社区 Remix 模板 | `wan22RemixT2VI2V_i2vHighV30.safetensors`, `wan22RemixT2VI2V_i2vLowV30.safetensors` |
| 动作迁移模板 | `wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors`, `wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors` |
| 文本编码器 | `umt5_xxl_fp16.safetensors`, `umt5_xxl_fp8_e4m3fn_scaled.safetensors`, `nsfw_wan_umt5-xxl_fp8_scaled.safetensors`, `open_clip_vit_h.safetensors` |
| VAE 与视觉编码器 | `wan_2.1_vae.safetensors`, `clip_vision_h.safetensors` |

### 其他图像、视频、音频和 3D 模板

| 系列 | 精确模型值 |
| --- | --- |
| HunyuanVideo | `hunyuan_video_t2v_720p_bf16.safetensors`, `hunyuan_video_vae_bf16.safetensors`, `llava_llama3_fp16.safetensors` |
| LTXV 旧模板 | `ltxv_2b_0.9.7_dev_fp8.safetensors`, `ltxv_vae.safetensors` |
| Cosmos | `cosmos_cv8x8x8_1.0_text2world_7b.safetensors`, `cosmos_cv8x8x8_1.0_decoder.safetensors` |
| Mochi | `mochi_preview_bf16.safetensors`, `mochi_vae.safetensors` |
| Stable Cascade | `stable_cascade_stage_b.safetensors`, `stable_cascade_stage_c.safetensors` |
| Stable Audio | `stable_audio_open_1.0.safetensors` |
| Hunyuan3D v2 | `hunyuan3d_v2_turbo.safetensors`, `hunyuan3d_v2_vae.safetensors` |
| Upscale | `RealESRGAN_x4plus.pth` |

`example_lora.safetensors`、`your_lora.safetensors` 和 `example_flux_lora.safetensors` 是模板占位值，不是推荐下载项。使用 LoRA 模板时应替换为用户实际文件名。

## 当前图像模型推荐

### Z-Image

- 官方基座：[Tongyi-MAI/Z-Image](https://huggingface.co/Tongyi-MAI/Z-Image)
- 官方加速版：[Tongyi-MAI/Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo)
- 社区改版：可优先评估用户提供的量化、微调或合并版本，但必须追溯到上述基座。

`Z-Image` 适合作为可微调、支持 CFG 和负面提示词的完整基座；`Z-Image-Turbo` 面向少步快速生成。两者采样参数不能直接混用。

Z-Image 是当前轻量路线的优先选择。具体显存占用仍取决于精度、文本编码器、分辨率和卸载策略，不把“6B”直接换算成固定显存需求。

### FLUX.2 [klein]

- 官方 9B：[black-forest-labs/FLUX.2-klein-9B](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B)
- 官方 4B：[black-forest-labs/FLUX.2-klein-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)
- 社区改版：优先评估有明确基座、量化说明和 ComfyUI 工作流的版本。

4B 与 9B 的许可证和资源要求可能不同；社区派生版必须继承并披露对应基座许可证。加入默认模板前分别验证生成、编辑、显存和节点支持。

当前优先保留 9B 作为高质量本地图像编辑路线；4B 更适合资源受限场景。FLUX.2 [klein] 同时支持生成和编辑，但本项目在模型分工中尤其看重其图像编辑能力。

### Qwen-Image

- 官方基座：[Qwen/Qwen-Image](https://huggingface.co/Qwen/Qwen-Image)
- 社区量化与改版：用户提供明确链接时优先评估，但需确认量化格式、文本编码器、VAE 和 ComfyUI 加载节点匹配。

Qwen-Image 系列继续作为图像编辑优先路线，尤其适合语义与外观编辑以及中英文文字处理。使用时选择与任务对应的生成或编辑版本，不把整个系列当成一个可互换 checkpoint。

### Anima

- 当前候选：[Gazingstars123/Anima-2.9B](https://huggingface.co/Gazingstars123/Anima-2.9B)
- 社区改版：按基座可追溯性、风格目标和实际模板兼容性评估。

### Krea 2

- 官方 RAW：[krea/Krea-2-Raw](https://huggingface.co/krea/Krea-2-Raw)
- 官方 Turbo：[krea/Krea-2-Turbo](https://huggingface.co/krea/Krea-2-Turbo)
- 社区版：见下表的精确版本页面；模型文件、文本编码器、VAE 和加载节点仍需按对应模型页与目标 ComfyUI 实例核对。

Krea 2 是当前文生图默认首选。官方 RAW 是未蒸馏基础模型，适合训练、微调和后训练；下面的官方推荐参数专指 Turbo，不得套用到 RAW。

### Krea 2 采样参数

| 模型 | Sampler | Scheduler | Steps | CFG | 参数来源与备注 |
| --- | --- | --- | ---: | ---: | --- |
| 官方 Krea 2 Turbo | `euler` | `simple` | 8 | 1 | 本项目官方版默认参数；Turbo 为 8-step 蒸馏模型。 |
| [Moody Krea 2 Mix](https://civitai.red/models/2731187/moody-krea-2-mix-uncensored) | `euler_ancestral`（Euler a） | `beta` | 10 | 1 | 对应社区模型页推荐。 |
| [Krea2 Asian Utopian Turbo](https://civitai.red/models/2782456/1125-krea2-asian-utopian-turboint8int4nvfp4gguf?modelVersionId=3146785) | `er_sde` | `sgm_uniform` | 8 | 1 | 对应指定版本 `3146785`。 |
| [Kreativity](https://civitai.red/models/2730813/kreativity-nsfw-base-model?modelVersionId=3070037) | `euler_ancestral` | `beta` | 12 | 1 | 对应指定版本 `3070037`。 |
| [JIB Mix Krea 2](https://civitai.red/models/2799984/jib-mix-krea-2?modelVersionId=3252207) | `euler` | `simple` | 10 | 1 | 对应指定版本 `3252207`。 |
| [Muse by Stable Yogi Krea2](https://civitai.red/models/2741166/muse-by-stable-yogi-krea2?modelVersionId=3258954) | `euler` | `simple` | 8–20 | 1–2.5 | 对应指定版本 `3258954`；先从 8 steps、CFG 1 开始，再按版本说明调高。 |
| [RedCraft 2 / 3](https://civitai.red/models/958009/redcraft-or-2-or-3-int8int4fp8-scaled) | `er_sde` 或 `euler` | `simple` | 8–12 | 1 | 对应社区模型页推荐；选择 sampler 后固定它再比较。 |

通用起点：需要稳定和可复现性时使用 `euler + simple`；需要更强随机性和创造力时使用 `euler_ancestral + beta`。大多数 Turbo 或社区优化版先在 8–12 steps、CFG 1 附近测试。模型页给出专用参数时，以该版本参数为先；不要为了套用通用起点覆盖作者建议。

参数名称采用 ComfyUI 常见内部值：Euler a 记作 `euler_ancestral`，Beta 记作 `beta`。实际下拉值仍以目标实例 `/object_info` 为准。相同提示词比较不同 Krea 2 版本时，先分别使用各版本推荐参数评估完整配置，再增加统一参数对照组；两类结果不能混为同一实验。

## 当前视频模型推荐

### MiniMax-H3

- ComfyUI 重打包：[Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)
- 社区 NVFP4：[lilcheaty/MiniMax-H3-NVFP4](https://huggingface.co/lilcheaty/MiniMax-H3-NVFP4)

MiniMax H3 是截至 2026-09 的视频生成默认首选和绝对主流。它支持文本、图像、视频和音频等多模态上下文，并可生成带原生音频的视频；具体能力、时长和分辨率以所用本地权重、节点和工作流为准。

原版计算开销和生成时间较高，优先评估适合目标 GPU 的官方重打包或社区量化。Comfy-Org 当前对可选精度给出了更具体的建议，例如在兼容环境中优先 `int8_convrot`，无法使用时再考虑 `fp8_scaled`；不要仅根据“位数更低”判断速度。

另有服务侧的 MiniMax-H3 Max 提速版本值得持续追踪，但当前没有可纳入本地模板的公开权重链接。它只列为追踪项，不得写入下载指南或声称本地可用。

### Wan 2.2

- 官方 T2V A14B：[Wan-AI/Wan2.2-T2V-A14B](https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B)
- 官方 TI2V 5B：[Wan-AI/Wan2.2-TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B)
- 社区改版：可按显存、速度、画质和现有工作流节点选择，优先使用用户提供且来源清晰的链接。

仓库已有 Wan 2.2 T2V、I2V、首尾帧、控制、相机、组合生图转视频和动作迁移模板。新增官方或社区权重时，应先映射到这些任务类型，而不是重复创建近似模板。

### LTX-2.3

- 官方基座：[Lightricks/LTX-2.3](https://huggingface.co/Lightricks/LTX-2.3)
- 社区改版：在许可证兼容、节点支持和音视频能力需求明确时评估。

现有模板仍使用 `ltxv_2b_0.9.7_dev_fp8.safetensors`。LTX-2.3 应作为升级候选，完成模板迁移和真实运行验证后再替换旧默认值；其社区许可证需要在分发或商业使用前单独核对。

## LLM / Text Generation Nodes (`comfyui_LLM_party`)

| Provider | Loader / endpoint | 推荐模型值 | 说明 |
| --- | --- | --- | --- |
| OpenAI | `LLM_api_loader`, `https://api.openai.com/v1` | `gpt-5.4` | 当前仓库调用外部 API 的 UI 模板默认值。 |
| Anthropic | `aisuite_loader`, `https://api.anthropic.com/v1` | `claude-sonnet-4-5-20250929` | Claude Sonnet 4.5 的可执行 API ID。 |
| DeepSeek | `LLM_api_loader`, `https://api.deepseek.com/v1` | `deepseek-v4-flash` | 默认文本生成路径使用非思考模式；需验证安装节点的思考控制参数。 |
| Ollama | `LLM_api_loader`, `http://127.0.0.1:11434/v1/`, `is_ollama=true` | `qwen3:8b` | 本地默认值。 |

三个调用外部 API 的 UI 模板使用 `gpt-5.4`，Ollama 模板使用 `qwen3:8b`。Claude 和 DeepSeek 在取得真实 `comfyui_LLM_party` 节点契约前仍作为提供商候选，不伪造专用模板。

## 更新与去重规则

- 一个官方仓库、社区仓库或精确模型值只保留一个主条目；其他章节使用文字引用，不重复粘贴 URL。
- 同名但大小写、连字符或文件后缀不同的值不能自动合并，先确认是否确为同一文件或 API ID。
- 每次更新同时检查模板、模型下载指南和本文件；删除失效推荐时保留必要迁移说明，但不继续推荐旧名称。
- 新社区版只有在提供明确链接后才进入具体候选表；“社区改版”本身不是可下载模型。
