---
name: krea2-lora-training
description: 为 Krea 2 制作和审查人物、风格或物件 LoRA 数据集，修订自然语言 caption，核对本地训练配置，并设计固定条件的检查点评估。适用于 Krea 2 训练素材、caption、训练参数和检查点选择请求。
---

# Krea 2 LoRA 数据集与训练评估

先确定训练目标、正式数据集路径、使用的训练器及版本、希望保持的特征和希望单独控制的属性。明确这次是只读审查、caption 修订、补图、配置修改还是训练；沿用用户已经指定的路径、触发词和授权范围。

## 数据与 caption

制作或审查素材时，读取 [图像与分布审查](references/image-generation.md)；写 caption 时，读取 [caption 与触发词](references/captioning.md)。

- 人物素材保持身份，变化覆盖任务需要的角度、表情、视线、服装、配饰、场景和光照。配额是起始设计，不是保证效果的比例。
- caption 以最终图片为准。描述有意义的可见属性；不能把生成提示词、文件名或想象的相机参数当成观察事实。
- 核心概念与可控属性按用户目标区分。发型、配饰和光照不因在现有图中频繁出现就自动划为身份；需要控制时如实描述并提供视觉变化。
- 自然语言正文中的否定与推理的负向条件分支不同。准确的 `without makeup` 等描述可以保留，告警只供复核。
- 修改已有数据前保存可恢复的基线。确认图文同名配对；caption 修改前后比较图片哈希。需要生成、裁切或镜像时，分别保存原图、接受样本与制作记录。
- 镜像后按最终画面修订坐标关系。画面方向使用 `image-left/image-right`，人物解剖侧别单独判断；镜像不能降低歪头比例。

## 静态检查与看图复核

在本 skill 根目录运行（PowerShell 中为路径和触发词加引号）：

```powershell
uv run --no-project --with pillow python -X utf8 scripts/lint_captions.py "<dataset_dir>" --trigger "<trigger>" --mirror-suffix _mirror --strict --json
```

默认不写任何文件。需要保存机器报告时，增加 `--report "<dataset_dir之外的报告路径.json>"`。

- 错误：空数据集、缺失配对、同名冲突、不可解码图片、非法 UTF-8、内部换行、不符合约定的触发词次数、明确复制的镜像画面方向。
- 告警：文字启发式、否定措辞、相机参数、格式扩展名不符、覆盖率不足、镜像语义需复核。普通模式只因错误失败；`--strict` 因错误或告警失败。
- JSON 的 `blocking_passed` 表示无错误，`passed` 表示通过所选模式。静态通过不证明身份一致、视觉覆盖达标或镜像语义正确。

按 [验收协议](references/qa-checklist.md) 看图核对。只报告实际观察范围；关键词未命中不能证明图片不存在该属性。机器报告保留可复算输出，人工观察和历史说明另存。

## 本地训练与检查点评估

用户请求参数、训练或 step 选择时，读取 [本地训练与评估](references/training-evaluation.md)。先核对实际 config、当前日志与版本；不要用云端默认值替代本地设置。

RAW 训练、Turbo 推理是官方推荐；评估必须注明实际基座。固定提示词、种子、采样条件和 LoRA 强度，比较身份保持与条件服从；loss 只能帮助选择抽测范围。

更换触发词或测试别名时，遵循用户指定方案。联合字符串训练不保证其各部分可以单独触发；把完整名称、各别名、无名称及无 LoRA 对照放进同条件测试。

## 交付与验证

交付包含正式路径、图文数量、触发词约定、检查结果、人工复核范围和剩余不确定项。用户要求打包时，核对 ZIP 清单与文件哈希。

修改本 skill 的脚本后运行：

```powershell
uv run --no-project --with pillow python -X utf8 -m unittest discover -s tests -t . -q
```

官方事实、环境实现和经验建议分别标明依据。查采样参数和来源时读取 [来源与适用范围](references/quick-reference.md)。
