# ComfyUI Skills

面向 ComfyUI 工作流创作、迁移、校验和性能测量的单仓库多 Skill 项目。仓库既保留可直接使用的工作流资产，也保留维护这些资产所需的节点资料、案例和开发计划。

## Skills

- [`skills/comfyui-workflow`](skills/comfyui-workflow/)：创建和精确编辑 UI 工作流、验证图结构、检查模型依赖，交付可导入 ComfyUI WebUI 的工作流 JSON。
- [`skills/comfyui-performance-monitor`](skills/comfyui-performance-monitor/)：记录本机软硬件环境和 ComfyUI 任务耗时，可选择在测量前释放模型与缓存。
- [`skills/krea2-prompt-engineering`](skills/krea2-prompt-engineering/)：编写和调试 Krea 2 自然语言提示词，提供模型响应校准、摄影与造型词库。
- [`skills/krea2-megastructure-prompts`](skills/krea2-megastructure-prompts/)：为 Krea 2 生成巨构、巨型生物、超尺度自然结构及机械载具等题材的生图提示词。

每个 Skill 都是独立可分发目录。安装时复制需要的完整目录，不要只复制 `SKILL.md`。

## 权威资产

- UI 工作流资产：[`skills/comfyui-workflow/assets/templates`](skills/comfyui-workflow/assets/templates/)，当前包含 36 份创作基线和 8 份迁入的示例工作流，共 44 份 JSON；使用前参阅[模板目录说明](skills/comfyui-workflow/references/available-templates.md)
- LLM Party 模板：[`skills/comfyui-workflow/assets/templates/comfyui_LLM_party`](skills/comfyui-workflow/assets/templates/comfyui_LLM_party/)
- 当前模型推荐：[`skills/comfyui-workflow/references/model-recommendations.md`](skills/comfyui-workflow/references/model-recommendations.md)
- 节点资料：[`skills/comfyui-workflow/references/nodes`](skills/comfyui-workflow/references/nodes/)
- 维护与演进计划：[`DEVELOPMENT_PLAN.md`](doc/DEVELOPMENT_PLAN.md)

`assets/templates/` 中的部分传统模板可能已随模型、节点或 ComfyUI 版本演进而过时，不能仅因文件存在就视为当前推荐。创建新模型对应的工作流时，优先参考 Krea2、InfiniteYou、Flux2-klein、Qwen Edit 和 Z-Image 迁入工作流的现代图结构与节点用法，再结合当前模型说明和目标实例的 `/object_info` 更新依赖与输入契约。目标 ComfyUI 实例始终是节点契约的运行时权威。

## 仓库结构

- `skills/`：可独立安装的技能；各技能自带运行所需的脚本、参考资料、模板和测试。
- `doc/`：开发计划等维护文档。

示例工作流现统一保存在 `skills/comfyui-workflow/assets/templates/`，随 `comfyui-workflow` Skill 一并分发。Krea2、InfiniteYou、Flux2-klein、Qwen Edit 和 Z-Image 迁入工作流是创建新模型工作流时的优先参考，但仍需核对模型、自定义节点和目标 ComfyUI 环境；其他模板可用于理解任务结构，不保证模型与节点版本仍然适用。

## API 工作流

需要 API 工作流时，在 ComfyUI WebUI 中打开工作流，选择 **“导出（API）”（Export (API)）** 即可。技能创作和修改 UI 工作流；修改后通过 WebUI 重新导出 API 文件。

## 验证

```powershell
uv run --with pyyaml python -X utf8 C:\Users\<user>\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/comfyui-workflow
uv run python -m unittest discover -s skills/comfyui-workflow/tests -v
uv run python skills/comfyui-workflow/scripts/workflow_tool.py validate workflow.json
```

模板更新、模型替换和推荐变更必须遵循 [`DEVELOPMENT_PLAN.md`](doc/DEVELOPMENT_PLAN.md) 的证据与回归要求。

## 致谢

- [`skills/comfyui-workflow`](skills/comfyui-workflow/) 基于 [LingyiChen-AI/comfyui-workflow-skill](https://github.com/LingyiChen-AI/comfyui-workflow-skill) 二次创作，在原项目的基础上增加了Krea2, Flux Klein 9B, Qwen Edit, Z-Image和MiniMax H3等最新热门模型的支持。感谢原项目作者及贡献者提供的基础工作。
- [`skills/krea2-prompt-engineering`](skills/krea2-prompt-engineering/) 中的素材库和部分模板来源于 **B站-是古手梨花sama**。感谢作者整理和分享相关素材。
- [`skills/krea2-megastructure-prompts`](skills/krea2-megastructure-prompts/) 来自 B 站作者 **黑鹤001**：[个人空间](https://space.bilibili.com/515231056)。本项目仅作归档保存，未对该 Skill 作任何修改。衷心感谢作者的无私奉献。本项目的部分示例工作流也取自他的分享；更多高质量教程和工作流请关注作者账号自行获取，本项目不重复拷贝。
