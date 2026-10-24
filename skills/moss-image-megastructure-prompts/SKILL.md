---
name: moss-image-megastructure-prompts
description: 为 MOSS-Image 编写幻想巨构、倒悬城市、悬浮建筑与超尺度场景的自然语言 Caption 或结构化 Layout。需要尺度锚定、留白、遮挡、相向塔尖或多主体位置控制，以及可编辑像素草稿与可复制正向提示词时使用；不执行生图。
---

# MOSS 巨构构图

以官方 MOSS 提示词增强协议为基础，结合巨构的尺度参照、结构语义、镜头语言和大气分层。保留用户的主体数量、方向、媒介、光照与排除项。默认英文描述，按用户要求切换语言；画内文字保持原文。

## 选择输出

- 默认 **Caption**：自由摄影、插画、单一巨构、只需大致空间关系时，输出自然语言，不强行加框。
- 使用 **Layout**：用户明确要求，或相向尖端、狭窄间隙、多个独立主体、穿过/遮挡等关系需要明确位置时。
- 复杂度不等于需要 Layout。没有坐标需求时保留自然构图；只在用户需要比较时提供双版本。
- 不把 Krea 的 creativity、Medium/Large、量化实测或固定语序当作 MOSS 参数。默认不提供未经核对的推理配置。

## 构图步骤

1. 提取不变量：主体数、上下/前后关系、尺度参照、留白、光源方向、画幅。缺失的普通创作细节自行补足；重要冲突才询问。
2. 选一个可辨识的尺度锚点，例如气球、船或人物。说明它相对巨构的大小，避免为显大而擅自添加人群、鸟群和多余道具。
3. 指明结构：扶壁、肋架、拱廊或台地等一两种可读重复单元。幻想悬浮可以违反重力，但要说明朝向与连接关系。
4. 写近、中、远的大气层次；保持关键轮廓和尺度锚点清楚。以一个主光方向统一各主体的亮面与阴影。
5. 选择镜头和距离，区分广角视野与近距离透视夸张。优先保护留白与轮廓，不强制巨构占画面 70–90%，不机械填满七层细节。
6. 先写主体和关系，再补材质、环境、光线、相机与媒介。控制装饰细节，只写有助于用户目标的内容。

方法与示例选择见 [composition.md](references/composition.md)。通用官方行为见 [官方 Skill](https://github.com/OpenMOSS/MOSS-Image/blob/52b87fca23acedc399d062d593bec388aee9926a/skills/moss-image-prompt-enhancer/SKILL.md)，坐标字段见 [layout.md](references/layout.md)。来源与许可证见 [provenance.md](references/provenance.md)。

## 草稿

Caption：保存 UTF-8 JSON，且只有 `{"caption":"自然语言提示词"}`。不要加入框或坐标说明。

Layout：先读 `references/layout.md`。使用 `width`、`height`、`summary`、扁平 `items`、`bbox_coord_space="abs"`、`bbox_format="xyxy"`。框为左上角原点的实际像素 `[x_min,y_min,x_max,y_max]`，范围在画布以内。宽高必须为 16 的正整数倍。明确尺寸不兼容时说明冲突，不静默取整；只有比例时自行选兼容画布。

只框必须独立定位的可见单元。城体与伸出的关键塔尖可拆开并略微重叠，使其视觉连续；不要把同一座城又完整框一次。空隙、光源方向、云雾和负空间写入 `summary.caption`，不要伪装成可见物体。框不是边框或拼贴面板，也不能保证轮廓逐像素贴合。遮挡关系必须同时写在描述里；框相交本身不表达前后。

尺寸与每个框同步修改。不要只改宽高假装缩放，不使用归一化坐标，不手算中心坐标，不把工程说明塞入图像描述字段。

## 校验、编译与交付

从本 Skill 实际位置解析脚本路径，保留草稿和输出为不同文件：

```bash
python3 /path/to/moss-image-megastructure-prompts/scripts/check_prompt.py draft.json --width 1536 --height 864
python3 /path/to/moss-image-megastructure-prompts/scripts/compile_prompt.py draft.json --output prompt.txt
python3 /path/to/moss-image-megastructure-prompts/scripts/check_prompt.py draft.json --compiled prompt.txt --width 1536 --height 864
```

`check_prompt.py` 调用原样附带的官方编译器，核验外部生成尺寸和保存的编译输出；不另写转换算法。Caption 无画布元数据：省略宽高检查，建议生成尺寸作为说明另给。校验失败时修改草稿并重编译，不手写转换后的 JSON。

逐一复核主体、塔尖间距、留白、锚点比例、遮挡和光向。静态校验只能证明结构与坐标有效，不能宣称模型已稳定执行构图。MOSS 官方将 Layout 标为实验性功能；后续实测需要用户另行授权。

交付可直接粘贴的纯文本 Caption，或一物理行的编译 Layout JSON；保留可编辑 JSON 草稿，Layout 必须在提示词外注明实际生成宽高。不要把 Markdown 围栏、草稿或说明一起贴入正向输入框。

## 示例与本地测试

在 `assets/examples/` 中读取相应 `.draft.json` 与 `.prompt.txt`：

| 示例 | 模式 | 画布 | 检查关系 |
| --- | --- | --- | --- |
| `inverted-cities-caption` | Caption | 建议 1536×864 | 同一双城场景的自然语言版 |
| `inverted-cities-layout` | Layout | 1536×864 | 两城、相向塔尖、48 px 空隙、28 px 高气球、左侧夕照 |
| `ring-transit-layout` | Layout | 1536×1024 | 船穿环、前后遮挡、小艇尺度 |
| `chasm-bridge-layout` | Layout | 1536×864 | 左右悬崖、桥梁跨越、桥上人物 |
| `sea-gate-caption` | Caption | 建议 1536×864 | 自由摄影式负空间，保持无框 |

示例构图依据见 [composition.md](references/composition.md)。运行：

```bash
python3 -m unittest discover -s /path/to/moss-image-megastructure-prompts/tests -v
```

禁止自动提交 ComfyUI 任务、下载模型、安装节点或改动现有 Krea 2 Skill。
