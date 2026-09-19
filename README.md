<div align="center">

# ComfyUI Skills

面向 ComfyUI 工作流创作、模型迁移、结构校验、性能测量与 Krea 2 提示词工程的多 Skill 工具箱。

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Workflows-19C3FF?style=for-the-badge)](https://github.com/comfyanonymous/ComfyUI)
[![Krea 2](https://img.shields.io/badge/Krea%202-Prompting-8B5CF6?style=for-the-badge)](skills/krea2-prompt-engineering/)
[![Workflows](https://img.shields.io/badge/Workflow%20JSON-44-FF6B6B?style=for-the-badge)](skills/comfyui-workflow/assets/templates/)
[![Repository](https://img.shields.io/badge/GitHub-Public-181717?style=for-the-badge&logo=github)](https://github.com/liqiming-whu/comfyui-skills)

</div>

![ComfyUI Skills 项目介绍卡片](assets/comfyui-skills-intro-card.png)

## 项目概览

本仓库将工作流创作、节点资料、模型选型、性能测量和提示词方法整理为可独立安装的 Codex Skills。它既提供可导入 ComfyUI WebUI 的工作流资产，也保留维护这些资产所需的脚本、参考资料和测试。

| Skill | 用途 | 主要交付 |
| --- | --- | --- |
| [`comfyui-workflow`](skills/comfyui-workflow/) | 创建、修改、迁移和校验 ComfyUI UI 工作流 | UI 工作流 JSON、模型依赖和结构检查 |
| [`comfyui-performance-monitor`](skills/comfyui-performance-monitor/) | 记录 ComfyUI 运行时间与本机资源状态 | 可比较的性能测量报告 |
| [`krea2-prompt-engineering`](skills/krea2-prompt-engineering/) | 编写和调试 Krea 2 自然语言提示词 | 模型校准、摄影和造型提示词 |
| [`krea2-megastructure-prompts`](skills/krea2-megastructure-prompts/) | 生成巨构、巨兽与超尺度场景提示词 | 英文长提示词、尺度锚定和场景变体 |

每个 Skill 都是独立可分发目录。安装时复制所需的完整目录，不要只复制 `SKILL.md`。

## 当前模型方向

- **文生图**：Krea 2 是截至 2026-09 的默认首选。
- **图像编辑**：优先评估 FLUX.2 klein 9B 与 Qwen-Image 系列。
- **轻量生成**：Z-Image 是资源受限环境下的优先选择。
- **视频生成**：MiniMax H3 是当前默认首选。

上述结论来自 B 站热度、社区口碑、Civitai、Hugging Face、魔搭下载量及趋势的综合判断。详细依据、模型链接和 Krea 2 采样参数见[模型推荐与模板基线](skills/comfyui-workflow/references/model-recommendations.md)。

## 工作流资产

[`skills/comfyui-workflow/assets/templates`](skills/comfyui-workflow/assets/templates/) 当前包含：

- **36 份创作基线**：覆盖 SD、SDXL、SD3、FLUX、Wan、LTXV、Hunyuan、Cosmos、音频、3D 和 LLM Party 等任务。
- **8 份迁入示例**：覆盖 Krea2、InfiniteYou、Flux2-klein、Qwen Edit 和 Z-Image。
- **共 44 份 UI 工作流 JSON**。

> [!IMPORTANT]
> 部分传统模板可能已随模型、节点或 ComfyUI 版本演进而过时。创建新模型工作流时，优先参考 Krea2、InfiniteYou、Flux2-klein、Qwen Edit 和 Z-Image 迁入工作流的现代图结构，再根据目标实例的 `/object_info` 更新模型、节点契约和输入参数。

完整清单见[模板目录说明](skills/comfyui-workflow/references/available-templates.md)。目标 ComfyUI 实例始终是节点输入契约的运行时权威。

## 安装

克隆仓库：

```powershell
git clone https://github.com/liqiming-whu/comfyui-skills.git
cd comfyui-skills
```

将需要的完整 Skill 目录复制到 Codex Skills 目录：

```powershell
Copy-Item -Recurse skills\comfyui-workflow "$env:USERPROFILE\.codex\skills\"
Copy-Item -Recurse skills\krea2-prompt-engineering "$env:USERPROFILE\.codex\skills\"
```

性能监测和巨构提示词 Skill 可按相同方式单独安装。复制完成后开启新会话，使 Skill 目录重新载入。

## 使用边界

### UI 与 API 工作流

`comfyui-workflow` 创作和修改可在 ComfyUI WebUI 画布中继续编辑的 UI 工作流。需要生产 API 工作流时：

1. 在 ComfyUI WebUI 中打开并验证 UI 工作流。
2. 从界面选择 **“导出（API）”（Export (API)）**。
3. 使用目标实例实际执行导出的 API JSON。

Skill 不自行创作 API 工作流，也不把 UI JSON 与 API JSON 视为可直接互换。

### 模型与节点

- 使用社区模型前核对基座、许可证、精度、文本编码器、VAE 和推荐采样参数。
- 使用自定义或版本敏感节点前查询目标实例的 `/object_info`。
- 模板导入成功不代表模型文件、自定义节点和运行参数已经满足。
- 下载模型或安装自定义节点需要单独、明确的授权。

## 仓库结构

```text
comfyui-skills/
├── assets/                          # 项目介绍视觉资产
├── doc/                             # 开发计划与设计草稿
└── skills/
    ├── comfyui-workflow/            # 工作流创作、模板、节点资料与校验脚本
    ├── comfyui-performance-monitor/ # 性能测量与报告示例
    ├── krea2-prompt-engineering/    # Krea 2 通用提示词工程
    └── krea2-megastructure-prompts/ # Krea 2 巨构提示词归档
```

维护和演进要求见[开发计划](doc/DEVELOPMENT_PLAN.md)。

## 验证

```powershell
uv run --with pyyaml python -X utf8 C:\Users\<user>\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/comfyui-workflow
uv run python -m unittest discover -s skills/comfyui-workflow/tests -v
uv run python skills/comfyui-workflow/scripts/workflow_tool.py validate workflow.json
```

当前仓库的 44 份工作流均可完成 JSON 解析；`comfyui-workflow` 的结构校验和单元测试已通过。真实运行兼容性仍取决于目标 ComfyUI、节点版本和本地模型文件。

## 致谢

- [`comfyui-workflow`](skills/comfyui-workflow/) 基于 [LingyiChen-AI/comfyui-workflow-skill](https://github.com/LingyiChen-AI/comfyui-workflow-skill) 二次创作，在原项目基础上增加了 Krea2、FLUX.2 klein 9B、Qwen Edit、Z-Image 和 MiniMax H3 等当前热门模型资料。感谢原项目作者及贡献者提供的基础工作。
- [`krea2-prompt-engineering`](skills/krea2-prompt-engineering/) 中的素材库和部分模板来源于 **B站-是古手梨花sama**。感谢作者整理和分享相关素材。
- [`krea2-megastructure-prompts`](skills/krea2-megastructure-prompts/) 来自 B 站作者 **黑鹤001**：[个人空间](https://space.bilibili.com/515231056)。本项目仅作归档保存，未对该 Skill 作任何修改。衷心感谢作者的无私奉献。本项目的部分示例工作流也取自他的分享；更多高质量教程和工作流请关注作者账号自行获取，本项目不重复拷贝。

---

<div align="center">

如果这些 Skills 对你的 ComfyUI 工作有所帮助，欢迎 Star、Fork，并分享可复现的工作流测试结果。

</div>
