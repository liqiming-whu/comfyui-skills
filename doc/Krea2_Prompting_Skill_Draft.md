---
name: krea2-prompt-engineering
description: >
  Krea 2 本地开源模型（RAW / Turbo）提示词编写与调试指南。
  重点处理自然语言提示、语义强调、语义竞争、顺序控制、局部形态控制、
  官方模型与社区改版之间的提示强度差异。默认面向 ComfyUI。
---

# Krea 2 Prompt Engineering Skill

## 0. 适用范围与证据等级

本 Skill 默认面向 **Krea 2 官方开源权重**，尤其是本地 ComfyUI 中的 Krea 2 RAW / Turbo。

使用规则时区分三类证据：

1. **官方明确说明**
   - Krea 2 推荐自然语言提示。
   - 长而详细的提示通常能得到更可控的结果，但模型也能从简短提示中生成高质量图像。
   - RAW 是未蒸馏基础模型，适合训练、LoRA 和后训练；Turbo 是 8-step 蒸馏模型，适合快速推理。
   - 官方推荐：在 RAW 上训练，在 Turbo 上运行。

2. **公开社区经验**
   - 旧式 CLIP/SDXL 的 `(word:1.3)` 等 token emphasis 对 Krea 2 往往不像传统 CLIP 模型那样工作。
   - 顺序、自然语言重述、具体词汇通常比单 token 数值加权更有效。

3. **本地实测经验**
   - 以下关于“核心语义前置”“语义竞争”“同义重述增强”“官方版自然/合理边界”“社区强化指令版需要更保守提示”等规则，属于针对具体工作流的经验性结论。
   - 不应把这些行为描述成已知的内部实现机制。
   - 特别不要声称模型存在“文本去重模块”；更安全的表述是：**机械重复的边际收益低，而语义重述通常比逐字复制有效。**

---

# 1. 核心心智模型

## 1.1 Krea 2 更像在理解一段画面描述，而不是解析 tag 权重表

默认把提示词写成“向另一个人描述最终画面”的自然语言，而不是：

`masterpiece, best quality, young woman, slim, belly, rounded, realistic, 8k`

更推荐：

`A young adult woman stands facing the camera in a softly lit hotel corridor. Her figure is slender overall, while her relaxed lower abdomen has a small, softly rounded fullness.`

重点：

- 使用完整句子或自然短语；
- 描述主语、空间关系、动作、材质、光线、构图；
- 不依赖大量同级关键词堆叠；
- 不把重要概念拆成十几个彼此独立的 tag。

## 1.2 Prompt 是语义结构，不只是词汇集合

Krea 2 的控制重点应理解为：

- 什么是主语；
- 什么是主语的核心属性；
- 哪些属性是局部的；
- 属性之间是什么空间关系；
- 哪些条件是主目标，哪些只是边界条件；
- 哪些语义彼此竞争。

因此写 prompt 时优先优化 **语义组织**，而不是单纯增加关键词数量。

---

# 2. 推荐的 Prompt 结构

默认顺序：

1. **主体 + 核心语义**
2. **局部几何 / 空间关系**
3. **边界约束**
4. **视角 / 构图**
5. **服装 / 姿势**
6. **场景**
7. **光线 / 摄影或风格**

示例：

```text
A young adult Chinese woman with a slender figure. Her relaxed lower abdomen is noticeably fuller and rounded, while her upper abdomen remains relatively flat.

Front view, facing the camera, wearing fitted opaque clothing that follows her body naturally without revealing fine anatomical surface details.

She wears a loose ponytail and has swept bangs. She is wearing a form-fitting mini dress made of soft, opaque fabric. She stands in a relaxed posture with one leg slightly forward.

Hotel corridor. Warm indoor lighting.

Natural realistic photography, authentic body proportions, natural skin texture, candid photography.
```

这类结构的目的不是固定模板，而是确保 **最重要的视觉语义最先建立**。

---

# 3. 自然语言优先，避免 SDXL/CLIP 式 tag 清单

## 推荐

```text
A young woman with a narrow waist and slim limbs. Her relaxed lower abdomen is softly rounded, forming a small natural fullness.
```

## 不推荐

```text
young woman, slim, narrow waist, slim arms, slim hips, rounded belly, lower belly, natural, realistic
```

原因：

- tag 清单弱化了语法和关系；
- 多个同级 tag 容易产生语义竞争；
- 位置关系、局部性和边界更难表达；
- 加更多 tag 不等于增加目标概念的有效权重。

例外：风格名、材质名、镜头术语等短语仍可作为简洁描述的一部分，但不要让整条 prompt 退化成 tag soup。

---

# 4. 不要把传统词汇权重语法当作主要控制手段

对于 Krea 2，不要默认 `(word:1.3)`、`((word))` 一类 CLIP 传统加权能线性放大某个词。

推荐的“加权”方式：

## 4.1 顺序加权

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

## 4.2 具体化加权

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

## 4.3 语义重述加权

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

# 5. 不要假设存在 literal deduplication

如果复制同一句多次没有增强效果，不要在 Skill 中解释为“Krea 2 一定有去重机制”。

更可靠的规则是：

> **逐字重复通常不会产生与重复次数成比例的增益；换一种自然语言、增加新的空间关系或视觉描述，通常更有效。**

这是外部可观察行为，不需要推测内部实现。

---

# 6. 核心语义前置：最重要的控制规则之一

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

### 防止后续描述越界

如果核心概念已经提前建立，后续描述应尽量只补：

- 局部边界；
- 服装；
- 姿势；
- 环境；
- 光线；
- 摄影属性。

不要在后面重新定义主体体型，否则容易覆盖或稀释前面的核心语义。

---

# 7. 语义竞争：既是风险，也是边界控制工具

Krea 2 官方版在多个强语义之间经常表现为折中，而不是严格执行所有条件。

例如：

```text
extremely slender
large rounded abdomen
completely natural body
very flat abdomen
```

这类描述内部就存在明显竞争。

## 7.1 主目标之间应保持一致

如果真正目标是局部腹部体积，核心语义应该朝同一方向：

```text
noticeably fuller
softly rounded
visible natural fullness
smooth lower-abdominal volume
```

避免同时加入会直接否定主目标的强语义。

## 7.2 竞争语义适合做边界，而不是抢主导权

例如：

```text
Her lower abdomen is noticeably fuller and rounded. Her waist, arms, hips, and legs remain slim.
```

这里 `slim` 与 `fuller lower abdomen` 有一定竞争，但这种竞争是有意的：

- `fuller lower abdomen` = 主目标；
- `slim limbs / waist` = 限制体积不要扩散到全身。

这种使用方式可以把模型的折中行为转化为“局部化控制”。

## 7.3 竞争语义放后面

如果把边界语义放在核心语义之前，模型可能先建立“典型瘦身材”，然后把局部体积压掉。

因此默认：

**核心形态在前，竞争/限制语义在后。**

---

# 8. 强度分级不要只依赖程度副词

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

## 示例四档

### L1 — Curvature
```text
Her relaxed lower abdomen is slightly and softly rounded, while the upper abdomen remains relatively flat.
```

### L2 — Visible curvature
```text
Her relaxed lower abdomen is clearly and softly rounded, with a gentle but clearly visible natural fullness, while the upper abdomen remains relatively flat.
```

### L3 — Local volume
```text
Her relaxed lower abdomen is noticeably fuller and rounded, with a clearly visible natural fullness, while the upper abdomen remains relatively flat.
```

### L4 — Strong local shape
```text
Her relaxed lower abdomen is distinctly rounded and visibly fuller, forming a smooth and prominent natural fullness, while the upper abdomen remains relatively flat.
```

如果某个强几何词会带来过强先验，可以通过多个温和但一致的关系描述达到相似效果，而不必依赖一个极端词。

---

# 9. “自然”和“强度”在官方版中的关系

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

注意：这是经验性行为总结，不是官方公开的内部约束机制。

---

# 10. 官方版与社区改版必须分开处理

## 10.1 默认规则只适用于官方 RAW / Turbo

本 Skill 中关于：

- 需要更激进文本才能突破自然范围；
- 竞争语义会被折中；
- `extremely` 可能只产生中等视觉增益；

都应默认视为 **官方 Krea 2 行为画像**。

## 10.2 不要把所有“社区版”视为同一种模型

必须区分：

### A. 仅量化 / 格式转换

例如：

- FP8
- MXFP8
- NVFP4
- INT8 ConvRot

这类变体可能改变数值误差、细节和随机轨迹，但**不能仅凭“社区版”三个字就假设它重新训练了指令遵循能力**。

### B. 真正经过 post-training / fine-tuning / adherence modification 的社区版

如果模型卡、作者说明或 A/B 实测明确证明它强化了指令遵循，则应使用另一套提示强度策略。

## 10.3 强指令遵循社区版：提示要更保守

对于经过强化、实测表现为“更忠实执行强度词”的改版：

官方版为了得到目标效果可能写：

```text
extremely pronounced
dramatically rounded
very strong fullness
```

而强化版可能真的把这些词按高强度执行，导致：

- 形态过大；
- 失去自然比例；
- 局部结构被夸张到不合理；
- 画面从“提示加强”变成“灾难性过执行”。

因此社区强化版的默认规则应是：

> **先从较温和、字面准确的自然语言开始，不要继承官方版为克服自然边界而使用的激进措辞。**

也就是说：

- 官方版：可能需要“稍微说重一点”；
- 强化社区版：更适合“说到什么程度，就写什么程度”。

## 10.4 Skill 中建议加入 model_profile

```yaml
model_profile:
  family: krea2
  checkpoint: official_turbo
  adherence_profile: official_balanced
```

可选：

- `official_raw`
- `official_turbo`
- `community_quant_only`
- `community_adherence_enhanced`
- `unknown`

当模型为 `unknown` 时，默认采用官方规则，不自动假设社区版加强了指令遵循。

---

# 11. 修改 Prompt 时一次只改一个层级

Krea 2 的 prompt 调试很容易因为多个变量同时变化而误判。

推荐实验流程：

1. 固定 seed；
2. 固定 sampler / scheduler / steps / CFG；
3. 固定模型与 text encoder；
4. 固定分辨率；
5. 固定服装、姿势、场景、光线；
6. 每次只修改 core；
7. 比较视觉变化是否集中在目标语义。

如果比较模型格式或社区改版，则反过来：

- prompt 固定；
- seed 固定；
- 参数固定；
- 只换模型。

不要把量化、text encoder、prompt、seed 同时变化后再判断某一项的效果。

---

# 12. 对局部身体形态的推荐写法

这一类任务尤其适合把 prompt 分成：

## Core
描述需要学习或强调的概念。

## Boundary
说明哪些相邻属性不应跟着变化。

## Scene
视角、姿势、服装、环境。

例如：

```text
CORE:
Her relaxed lower abdomen is noticeably fuller and rounded.

BOUNDARY:
Her waist, arms, hips, and legs remain slim, and her upper abdomen remains relatively flat.

SCENE:
Front view, facing the camera, wearing fitted opaque clothing that follows her body naturally.
```

重要原则：

> **Boundary 的作用是阻止语义扩散，而不是否定 Core。**

---

# 13. 服装覆盖局部形态时：描述低频轮廓，而不是高频解剖

当目标是“衣物覆盖下仍保留整体腹部体积”，应描述：

- smooth volume；
- rounded silhouette；
- opaque fabric；
- fabric follows / bridges over broad contours；
- fine anatomical surface detail is not visible。

例如：

```text
She wears fitted opaque clothing that follows the rounded lower-abdominal volume naturally without revealing fine anatomical surface details.
```

避免把“没有某个细节”反复写成主体语义，否则模型可能反而提高该解剖概念的显著性。

---

# 14. Prompt 长度：信息密度比绝对长度重要

官方说明长而详细的提示通常效果很好，但这不意味着“越长越好”。

对 Krea 2，应区分：

### 有效长度
每句话增加了新的可视信息：

- 主体；
- 空间；
- 材质；
- 光源；
- 构图；
- 局部关系。

### 无效长度
同一个意思堆大量近义词：

```text
natural, realistic, authentic, believable, lifelike, true-to-life
```

或者不断重复：

```text
rounded belly, rounded belly, rounded belly
```

Skill 应优先压缩后一类冗余。

---

# 15. Prompt 冲突检查清单

生成前扫描：

- 核心主体是否在前？
- 核心属性是否在前两句内明确？
- 是否存在直接否定核心的词？
- 边界条件是否只是限制扩散，而不是反客为主？
- 是否有两个互斥动作？
- 是否有两个互斥视角？
- 是否有两个互斥服装状态？
- 是否用大量程度副词代替实际几何描述？
- 是否机械复制同一句？
- 是否把 SDXL/CLIP 权重语法当作主要控制方法？
- 是否混用了官方版和社区强化版的提示强度策略？

---

# 16. 自动重写规则（适合 Skill 执行）

当收到用户目标时：

## Step 1：识别最高优先级视觉语义

例如：

`small rounded lower abdomen`

## Step 2：把它与主体绑定并前置

```text
A young adult woman with a softly rounded lower abdomen...
```

或：

```text
A young adult woman. Her relaxed lower abdomen is...
```

## Step 3：加入空间关系

```text
while the upper abdomen remains relatively flat
```

## Step 4：加入必要的边界竞争语义

```text
while her waist and limbs remain slim
```

只添加真正需要防止漂移的属性。

## Step 5：将视角 / 姿势 / 服装放在 Core 之后

不要让场景描述抢占核心主体。

## Step 6：需要强调时先做语义重述

不要首先使用机械复制或传统 token weighting。

## Step 7：根据 model_profile 调整强度

### official_balanced
允许稍强的语义措辞以克服自然化倾向。

### community_adherence_enhanced
降低程度副词，避免过执行。

---

# 17. 推荐的 Skill 决策逻辑

```text
IF model_profile == official:
    use natural-language sentence structure
    front-load core concept
    allow moderate semantic exaggeration
    use boundary competition after core
    prefer paraphrased redundancy over repetition

IF model_profile == community_quant_only:
    use official prompt strategy first
    do not assume stronger adherence
    validate with matched-seed A/B tests

IF model_profile == community_adherence_enhanced:
    preserve natural-language structure
    reduce extreme intensifiers
    describe desired final magnitude literally
    avoid multiple reinforcing phrases unless needed
```

---

# 18. 最重要的几条规则

1. **Natural language first.**
2. **Core meaning first.**
3. **Relationships beat tag lists.**
4. **Paraphrase to emphasize; do not copy-paste.**
5. **Use semantic competition as a boundary, not as a second main goal.**
6. **Keep the prompt semantically coherent.**
7. **Change geometry, not only adjectives, when building strength levels.**
8. **Official and community-modified Krea 2 require different intensity calibration.**
9. **Do not equate quantization with adherence fine-tuning.**
10. **Test one variable at a time with fixed seeds and parameters.**

---

# 19. 示例：从错误 Prompt 到 Krea 2 Prompt

## Tag-list style

```text
young Chinese woman, slender, narrow waist, slim arms, narrow hips, long legs,
rounded lower belly, fullness, flat upper abdomen, natural, realistic
```

## Krea 2 style

```text
A young adult Chinese woman with a narrow waist, slim arms, narrow hips, and long slim legs. Her relaxed lower abdomen is noticeably fuller and rounded, with a clearly visible natural fullness, while her upper abdomen remains relatively flat.
```

## Core-first style

```text
A young adult Chinese woman. Her relaxed lower abdomen is noticeably fuller and rounded, with a clearly visible natural fullness. Her waist, arms, hips, and legs remain slim, while her upper abdomen stays relatively flat.
```

第三种尤其适合在后续描述容易“越界”时使用，因为核心语义先完成主体定义，后面的 slender/flat 主要负责限制扩散。

---

# 20. Skill 的措辞约束

不要把经验性行为写成模型内部事实。

避免：

- “Krea 2 会自动去重提示词。”
- “Krea 2 给第一句固定 2× 权重。”
- “社区版都取消了自然限制。”
- “INT8 一定比官方版更听指令。”

改写为：

- “机械重复在实测中边际收益较低。”
- “前置核心语义通常更稳定。”
- “某些经过强化的社区改版可能表现出更强的指令遵循，需要单独校准。”
- “量化版与 post-trained adherence-enhanced 版本应区别对待。”

---

# 21. 最终工作原则

把 Krea 2 prompt 当作一个**有优先级的语义程序**：

- 第一部分定义世界；
- 第二部分定义局部关系；
- 第三部分设置边界；
- 后续只负责构图、服装、场景与摄影。

不要试图通过不停加关键词“压服模型”。

真正有效的控制通常来自：

**更早、更具体、更一致、更关系化的语言。**

---

# Sources

- Official Krea 2 prompting guide: https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md
- Official Krea 2 repository / RAW vs Turbo guidance: https://github.com/krea-ai/krea-2
- Community prompt guide used as secondary evidence: https://www.instasd.com/post/krea-2-prompt-and-style-guide-comfyui

