# 模型画像与强度校准

## 来源与证据

核对日期：2026-09-19。

- [官方提示指南](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md)：推荐自然语言，详细描述通常有利，同时简短提示也可用；画中文字用引号标明。这里不推出“禁止所有短语”或“越长越好”。
- [官方仓库](https://github.com/krea-ai/krea-2)：RAW 为未蒸馏基础模型，Turbo 为 8-step 蒸馏模型；推荐 RAW 训练 LoRA、Turbo 推理。具体 ComfyUI 节点参数须按实际工作流核实，不能把官方 CLI 的数值无条件移植。
- [HD V1 作者模型卡](https://huggingface.co/wikeeyang/Krea2-Turbo-HD-V1)：自述 HD 优化、同步微调 VAE、改善细节与质感。这支持“经过调制/优化”，不足以确认具体训练配方或专门增强指令遵循。
- 用户报告的官方 Turbo 局部形态实验：有时较强文字只得到温和效果。HD V1 的人物局部形态单例中，正向形态扩大，但局部范围及衣物细节边界未同步遵守。2026-09-19 又取得一组官方 Turbo 与 HD V1 的同提示词、同 seed 配对图及 PNG 工作流元数据，见下文“倒置双城配对实测”。这些仍是单种子、单题材观察，不能外推到所有 RAW、Turbo、量化、题材或种子。

## 独立维度

```yaml
model_profile:
  family: krea2
  checkpoint: unknown
  variant: unknown           # raw | turbo | unknown
  source: unknown            # official | community | unknown
  modification: unknown      # none | quant_only | finetuned | tuned | unknown
  quantization: unknown      # 单独记录精度/格式；微调模型也可以再量化
  vae: unknown
  text_encoder: unknown
  loras: []                   # 未知时改为 unknown；只有确认未使用时才写 []
  semantic_gain: unknown      # low | balanced | high | unknown
  boundary_adherence: unknown # weak | balanced | strong | unknown
  evidence: unknown          # author_statement | user_report | observed_test | unknown
  confidence: provisional    # provisional | replicated
  scope: unknown             # 被测概念、工作流与种子范围
```

Semantic Gain 是在当前配置与概念上，文字变化对应的可见强度变化；不是可跨模型通用的数字系数。Boundary Adherence 是对范围、相邻属性与覆盖要求的遵守程度。两者可以一高一低。没有配对实验时均保留 unknown；不从文件名、量化精度或“社区版”推断。

HD V1 的暂定记录：source=community，modification=tuned；模型卡支持调制分类。`semantic_gain=high`、`boundary_adherence=weak` 来自人物局部形态与倒置双城两类单种子案例，`confidence=provisional`，`scope` 限于对应配置和被测概念。不同语义的响应并不均匀，精确微调方式及 VAE 独立贡献未知；这不是“全局更听指令”的结论。

## 倒置双城配对实测（2026-09-19）

### 条件与证据边界

两张 PNG 的嵌入工作流元数据确认了以下共同条件：

- 完整提示词相同；
- seed：`189019515025256`；
- 文本编码器：`qwen3vl_4b_fp8_scaled.safetensors`；
- sampler / scheduler：`euler_ancestral` + `simple`；
- steps：8；CFG：1；输出分辨率：1920 × 1088。

官方配置使用 `krea2_turbo_int8_convrot.safetensors` 与 `qwen_image_vae.safetensors`；HD 配置使用 `Krea2-Turbo-HD-V1-int8_convrot.safetensors` 与配套 `Krea2-HD-vae.safetensors`。因此这是**配置组合比较**，不是只替换 UNet 的严格消融；画面差异不能全部归因于 checkpoint，VAE 的独立贡献未知。

测试提示词：

```text
A city hanging upside down from the sky, its towers pointing toward a mirrored city on the ground below, the two almost touching at their spires with a thin band of cloud between. Debris and waterfalls fall upward from the inverted streets. A single hot air balloon floats in the gap between them, dwarfed. Warm dusk light from the left, long shadows, volumetric haze. Shot on a 24mm wide-angle, symmetrical composition with the gap centered. Surreal fantasy matte painting, terracotta and dusk blue, dreamlike depth.
```

### 可观察结果

| 维度 | 官方 Turbo 配置 | Krea2-Turbo-HD-V1 配置 |
| --- | --- | --- |
| 双城结构 | 上下两座城市都以较完整的天际线出现，倒置关系一眼可读 | 上方倒城占据更大面积，地面城市被压缩为中央近景塔楼，双城的同等体量关系减弱 |
| 尖塔关系 | 两个中心尖塔在画面轴线上接近，较忠实表达“almost touching” | 中央塔楼和尖顶被显著放大，局部接近关系压过完整城市关系 |
| 尺度锚点 | 热气球较小，仍能帮助建立巨构尺度 | 热气球明显变大，`dwarfed` 的尺度反差减弱 |
| 镜头与构图 | 更像 24mm 建立镜头，横向城市范围和环境纵深更充分 | 更接近局部建筑的中近景裁切；虽保持中央间隙，但广角全景感较弱 |
| 细节与质感 | 细节较克制，体积雾和远景衰减带来梦境纵深 | 建筑、屋瓦、车辆和人物等局部纹理更清楚，锐度、对比和暖色响应更强 |
| 氛围 | 霞光、薄雾和远近层次较均衡，接近 fantasy matte painting | 质感更硬、更清晰，局部写实细节增强，但 `volumetric haze` 与 `dreamlike depth` 相对减弱 |
| 动态元素 | 瀑布与碎片分布在双城之间，服务于整体场景 | 瀑布和碎片更醒目，但也进一步集中注意力到局部结构 |

两套配置都理解了“天空中的倒置城市”、上下重力异常、中央间隙、暖色左侧暮光和大致对称构图。HD 配置没有表现为对所有句子都更忠实：它增强了建筑细节、中心尖塔、热气球、碎片与瀑布等显著对象，却弱化了完整双城、气球应被巨构压小、24mm 全景和梦境纵深等全局关系。

这与人物局部形态案例指向同一种暂定模式：HD V1 对部分显著名词和局部几何具有更高响应，但全局构图约束与尺度边界没有同步增强。当前证据可将 `semantic_gain=high` 的适用范围扩展到“人物局部形态与本次巨构场景中的显著对象”；画像字段暂记 `boundary_adherence=weak`，并在说明中保留“不同语义响应不均匀”，置信度保持 `provisional`。

### 对提示词策略的影响

在 HD V1 上处理巨构或超尺度场景时：

- 把全局拓扑提前写成一个不可拆分的主句，例如“两座完整城市以同等视觉重量上下相对”；
- 对尺度锚点使用明确相对尺寸，如 `a tiny hot air balloon occupying only a minute fraction of the central gap`，不要只依赖 `dwarfed`；
- 明确建立镜头和保留范围，如 `an extreme wide establishing view showing both complete skylines`；
- 避免同时强调多个会争夺画面的局部显著对象；建筑纹理已经足够强时，不再叠加细节词；
- 若首轮出现局部放大，先加强完整构图、相对尺寸和画面占比，再考虑增加更多风格词。

这些策略是本次单种子诊断形成的下一轮测试假设，不是已验证的修复结论。应固定当前配置，以多个 seed 对比原提示词与最小改写版本后再升级置信度。

## 策略

| 可用证据 | 第一轮策略 |
| --- | --- |
| 未知响应 | 单一、温和、字面准确的目标句；保留明确边界 |
| 当前官方配置已有欠执行证据 | 先前置目标，再小幅加强一个几何描述；必要时增加一句提供新空间关系的重述 |
| 仅量化官方权重 | 用已有官方 prompt 作比较基线，不假设量化强化遵循；仍重新验证 |
| 当前概念高增益 | 删除同义叠加，降低一个强度档位；避免 fullness、rounded、clearly visible 多重强调 |
| 高增益且边界弱 | 先降低核心强度，精简竞争语义并明确局部范围及面料结构；每轮看边界是否恢复 |

“目标 5、文字 7、输出 5/10”只能作非定量比喻，不写成模型参数。重复的收益及副作用取决于模型和题材。没有某一配置的观察结果，不预先把官方模型归为低增益。

## 对照实验

先做固定种子的诊断，再用多个种子核验是否重复出现。比较 prompt 时固定 checkpoint、量化、VAE、编码器、LoRA 及权重、采样器、调度器、步数、引导参数、分辨率、输入图与其他场景句；一次只改核心、边界或场景中的一个因素。

比较 checkpoint 时固定 prompt 和尽可能一致的条件。若模型要求配套 VAE 或不同采样设置，记录为“配置组合比较”，不能归因于 checkpoint 单一变量。相同 seed 在不同模型中不保证相同构图或相同噪声演化。

每次记录：模型版本/文件标识、全部生成条件、完整 prompt、seed、结果路径、目标强度、局部范围、相邻属性、面料覆盖、构图。将观测和解释分开；缺图或缺参数时不编造分数。复现后才提高置信度，并保持结论的题材范围。


## 以下规则适用于Krea2 官方版

### 1.不要把传统词汇权重语法当作主要控制手段

对于 Krea 2，不要默认 `(word:1.3)`、`((word))` 一类 CLIP 传统加权能线性放大某个词。

推荐的“加权”方式：

#### 1.1 顺序加权

把最重要概念提前。

弱：

```text
A slender woman ... Her lower abdomen is rounded.
```

更强：

```text
A young woman with a noticeably fuller, rounded lower abdomen. Her waist, arms, hips, and legs remain slim.
```

后者先建立核心形态，再用后续语义限制其他部位不过界。

#### 1.2 具体化加权

不要只提高程度副词：

```text
very rounded
extremely rounded
```

优先改变可视几何：

```text
softly rounded
clearly visible rounded fullness
noticeably fuller lower abdomen
a smooth forward fullness centered in the lower abdomen
```

#### 1.3 语义重述加权

机械复制：

```text
Her lower abdomen is rounded.
Her lower abdomen is rounded.
Her lower abdomen is rounded.
```

通常收益很低。

更有效的是从不同视觉关系重述同一概念：

```text
Her lower abdomen is softly rounded.
A visible natural fullness is centered in the lower abdomen.
The lower belly forms a smooth continuous curve against her otherwise slender torso.
```

三句对人来说是在描述同一现象，但每句提供了不同的语义关系：

- 形态；
- 位置；
- 与整体轮廓的对比。

这类“语义冗余”可作为 Krea 2 的自然语言强调方式。

---


### 2.核心语义前置：最重要的控制规则之一

当一个属性必须严格生效时，把它放在 prompt 早期，并尽量与主体直接绑定。

例如目标是“整体纤细，但局部下腹圆润”。

较弱：

```text
A young woman with a narrow waist, slim arms, narrow hips, and long slim legs. She has natural proportions and a slender figure. Her lower abdomen is noticeably fuller.
```

更稳定的结构：

```text
A young woman with a noticeably fuller, rounded lower abdomen. Her waist, arms, hips, and legs remain slim.
```

这个写法有两个作用：

1. 先让模型建立核心视觉状态；
2. 后续的 `slim` 被降级为边界约束，而不是与核心状态争夺主体定义。

#### 防止后续描述越界

如果核心概念已经提前建立，后续描述应尽量只补：

- 局部边界；
- 服装；
- 姿势；
- 环境；
- 光线；
- 摄影属性。

不要在后面重新定义主体体型，否则容易覆盖或稀释前面的核心语义。

---

### 3.语义竞争：既是风险，也是边界控制工具

Krea 2 官方版在多个强语义之间经常表现为折中，而不是严格执行所有条件。

例如：

```text
extremely slender
large rounded abdomen
completely natural body
very flat abdomen
```

这类描述内部就存在明显竞争。

### 4.主目标之间应保持一致

如果真正目标是局部腹部体积，核心语义应该朝同一方向：

```text
noticeably fuller
softly rounded
visible natural fullness
smooth lower-abdominal volume
```

避免同时加入会直接否定主目标的强语义。

### 5.竞争语义适合做边界，而不是抢主导权

例如：

```text
Her lower abdomen is noticeably fuller and rounded. Her waist, arms, hips, and legs remain slim.
```

这里 `slim` 与 `fuller lower abdomen` 有一定竞争，但这种竞争是有意的：

- `fuller lower abdomen` = 主目标；
- `slim limbs / waist` = 限制体积不要扩散到全身。

这种使用方式可以把模型的折中行为转化为“局部化控制”。

### 6.竞争语义放后面

如果把边界语义放在核心语义之前，模型可能先建立“典型瘦身材”，然后把局部体积压掉。

因此默认：

**核心形态在前，竞争/限制语义在后。**

---

### 7.强度分级不要只依赖程度副词

对官方 Krea 2，`subtle / noticeable / pronounced / extreme` 的视觉差距可能被压缩。

更稳定的办法是让不同档位使用不同的几何状态。

例如：

```text
Level 1: slight roundness
Level 2: clearly visible roundness
Level 3: increased local volume
Level 4: strong smooth fullness
```

这不是单纯把一个词从 `slight` 换成 `extreme`，而是在改变：

- 曲率；
- 可见程度；
- 局部体积；
- 必要时的向前投射感。

#### 示例四档

- **L1 — Curvature**
```text
Her relaxed lower abdomen is slightly and softly rounded, while the upper abdomen remains relatively flat.
```

- **L2 — Visible curvature**
```text
Her relaxed lower abdomen is clearly and softly rounded, with a gentle but clearly visible natural fullness, while the upper abdomen remains relatively flat.
```

- **L3 — Local volume**
```text
Her relaxed lower abdomen is noticeably fuller and rounded, with a clearly visible natural fullness, while the upper abdomen remains relatively flat.
```

- **L4 — Strong local shape**
```text
Her relaxed lower abdomen is distinctly rounded and visibly fuller, forming a smooth and prominent natural fullness, while the upper abdomen remains relatively flat.
```

如果某个强几何词会带来过强先验，可以通过多个温和但一致的关系描述达到相似效果，而不必依赖一个极端词。

---

### 8.“自然”和“强度”在官方版中的关系

本地实测表明，官方 Krea 2 往往倾向于把输出保持在一个视觉上较自然、合理、审美稳定的区域。

因此在官方版上：

- `extremely`
- `dramatically`
- `strongly`
- 更激进的尺寸或形态描述

有时只是为了把结果从模型的“自然吸引子”里推出来，并不一定真的得到字面意义上的极端结果。

换句话说：

> **官方版的文字强度与视觉强度不一定线性对应。**

因此写官方版 prompt 时，可以比目标画面本身稍微激进一点，但仍要保证整条 prompt 语义一致。

> 注意：这是经验性行为总结，不是官方公开的内部约束机制。
> 仅限于官方版

**官方版为了得到目标效果可能写：**

```text
extremely pronounced
dramatically rounded
very strong fullness
```

**而社区强化版可能真的把这些词按高强度执行，导致：**

- 形态过大；
- 失去自然比例；
- 局部结构被夸张到不合理；
- 画面从“提示加强”变成“灾难性过执行”。

---
