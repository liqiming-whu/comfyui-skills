# 来源、复用与验证边界

核对日期：2026-10-24。官方固定版本：`52b87fca23acedc399d062d593bec388aee9926a`。

原样复用自 [OpenMOSS/MOSS-Image](https://github.com/OpenMOSS/MOSS-Image/tree/52b87fca23acedc399d062d593bec388aee9926a)：

| 本地文件 | 官方路径 | Git blob SHA-1 |
| --- | --- | --- |
| scripts/compile_prompt.py | skills/moss-image-prompt-enhancer/scripts/compile_prompt.py | ff7aaa85fa1b0ae4e97bb1ca5b698093dfdd5aee |
| references/layout.md | skills/moss-image-prompt-enhancer/references/layout.md | cb0126c72f17bc8847806a6b093c53324f883079 |
| third_party/MOSS-Image-LICENSE | LICENSE | d645695673349e3947e8e5ae42332d0ac3164cd7 |

上述文件未修改，保留 Apache-2.0 许可证。该版本根目录没有 NOTICE 文件。更新上游时先核对许可证和 blob，再运行测试与重编译全部示例，不静默更换转换逻辑。

本 Skill 新增构图流程、示例、只读检查入口与回归测试。参考 [Krea 巨构方法](https://github.com/liqiming-whu/comfyui-skills/blob/0c28009b0aed2e860a85c5254ee4afa3503e45d6/skills/krea2-megastructure-prompts/SKILL.md)及其 scene-playbooks / layer-vocabulary，原 Skill 不变。
官方模型输入依据：[中文指南](https://github.com/OpenMOSS/MOSS-Image/blob/52b87fca23acedc399d062d593bec388aee9926a/USERGUIDE_ZH.md)。

只进行了离线静态/单元验证，未运行模型或 ComfyUI。Layout 为实验性控制，不是硬性几何约束；编译成功不等于模型可逐像素满足尖端、遮挡或尺度要求。
