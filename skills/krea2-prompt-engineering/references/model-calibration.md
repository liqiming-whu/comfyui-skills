# 模型画像与强度校准

## 来源与证据

核对日期：2026-09-19；2026-09-22 增补本机官方 Turbo 四档梯度实验与配置变量消融（量化 / VAE / 光照句）。

- [官方提示指南](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md)：推荐自然语言，详细描述通常有利，同时简短提示也可用；画中文字用引号标明。这里不推出“禁止所有短语”或“越长越好”。
- [官方仓库](https://github.com/krea-ai/krea-2)：RAW 为未蒸馏基础模型，Turbo 为 8-step 蒸馏模型；推荐 RAW 训练 LoRA、Turbo 推理。具体 ComfyUI 节点参数须按实际工作流核实，不能把官方 CLI 的数值无条件移植。
- [HD V1 作者模型卡](https://huggingface.co/wikeeyang/Krea2-Turbo-HD-V1)：自述 HD 优化、同步微调 VAE、改善细节与质感。这支持“经过调制/优化”，不足以确认具体训练配方或专门增强指令遵循。
- 用户报告的官方 Turbo 局部形态实验：有时较强文字只得到温和效果。HD V1 的人物局部形态单例中，正向形态扩大，但局部范围及衣物细节边界未同步遵守。2026-09-19 又取得一组官方 Turbo 与 HD V1 的同提示词、同 seed 配对图及 PNG 工作流元数据，见下文“倒置双城配对实测”。这些仍是单种子、单题材观察，不能外推到所有 RAW、Turbo、量化、题材或种子。
- 本机官方 Turbo 四档形态梯度实验（2026-09-21 / 09-22）：以“成年女性站立全身像的下腹凸出分级”为单一概念，在 `krea2_turbo_int8_convrot` + 原生 UNETLoader、8 步、CFG 1 下做 8 臂 × 3 seed × 4 档的成对实验，用于重写“以下规则适用于Krea2 官方版”并填写本章附录画像。主结论（语序是首要杠杆）在三个 seed 上重复。范围仍限于该概念、该配置与该题材。
- 本机配置变量消融（2026-09-22）：在冻结提示词与 seed 的前提下，逐项隔离 **checkpoint 量化**、**VAE** 与**光照从句**三个非文本变量。结论是：量化决定几何读数的量尺，VAE 只改色调，光照句里的一截平光短语压制形状。三项展开见下文「配置变量：量化、VAE 与光照句」。

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

另有一个不属于提示词响应、而属于**版本能力**的维度：官方版（RAW / Turbo、官方量化与官方微调）在**模型层面**限制裸露与过度 NSFW，社区 NSFW 强化版移除了该限制。它不随提示词文本改变，因此不计入 Semantic Gain 或 Boundary Adherence，也不需要配对实验去测；写提示词时按 `SKILL.md` **2.3** 区分暴露处理即可。

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
| 未知响应 | 单一、温和、字面准确的目标句；核心形态前置、边界收尾，保留明确边界 |
| 当前官方配置已有欠执行证据 | 先排语序（核心前置＋边界收尾），再核对服装承载词；两者都摆好仍欠执行才小幅加强一个几何描述 |
| 需要多档梯度或训练集 caption | 逐字节冻结其余部分，只替换形态从句；光源与背景句逐档固定，出图后先归一化色调再判断档距 |
| 仅量化官方权重 | 用已有官方 prompt 作比较基线，不假设量化强化遵循；仍重新验证 |
| 当前概念高增益 | 删除同义叠加，降低一个强度档位；避免 fullness、rounded、clearly visible 多重强调 |
| 高增益且边界弱 | 先降低核心强度，精简竞争语义并明确局部范围及面料结构；每轮看边界是否恢复 |

“目标 5、文字 7、输出 5/10”只能作非定量比喻，不写成模型参数。重复的收益及副作用取决于模型和题材。没有某一配置的观察结果，不预先把官方模型归为低增益。

## 对照实验

先做固定种子的诊断，再用多个种子核验是否重复出现。比较 prompt 时固定 checkpoint、量化、VAE、编码器、LoRA 及权重、采样器、调度器、步数、引导参数、分辨率、输入图与其他场景句；一次只改核心、边界或场景中的一个因素。

比较 checkpoint 时固定 prompt 和尽可能一致的条件。若模型要求配套 VAE 或不同采样设置，记录为“配置组合比较”，不能归因于 checkpoint 单一变量。相同 seed 在不同模型中不保证相同构图或相同噪声演化。

每次记录：模型版本/文件标识、全部生成条件、完整 prompt、seed、结果路径、目标强度、局部范围、相邻属性、面料覆盖、构图。将观测和解释分开；缺图或缺参数时不编造分数。复现后才提高置信度，并保持结论的题材范围。

读取结果时先排除整体调色：把各档按第一档做直方图匹配后再比较，否则一次全局重打光会被误读成强度分级。分档比较还要逐字节固定框架句，并单独记录取景漂移——构图一旦随档位移动，训练集里“强度”就会与“取景”相关。详见「以下规则适用于Krea2 官方版」§11。

## 配置变量：量化、VAE 与光照句

非文本变量也会改变画面。在「同一句 caption + 同一 seed + 同一张图 + 同分辨率 / 步数 / CFG」下，每次只换一个变量逐项隔离，得到下面三条互不替代的结论：**量化决定读数的量尺，VAE 决定色调，光照句决定形状能不能被读出来。**

### 1. 量化格式决定几何读数

同一 prompt、同一 seed，只换 UNet 文件：

| UNet 文件 | 与基线逐字节 | 小腹读数 |
| --- | --- | --- |
| `krea2_turbo_fp8_scaled` | **相同** | 有清楚的柔软外凸 + 明暗起伏 |
| `krea2_turbo_mxfp8` | 不同 | 与 fp8 基本并列 |
| `krea2_turbo_int8_convrot` | 不同 | **最平**（两个视角的均值都排最后） |
| `krea2_turbo_nvfp4` | 不同 | 也平，且 prompt 依从度掉一档（同一 caption 渲出不同服装） |

排序：**`fp8_scaled` ≈ `mxfp8` ≫ `int8_convrot` ≈ `nvfp4`**。

- 「全精度级」（fp8 / mxfp8）与「低位量化」（int8_convrot / nvfp4）之间是**画质与形状表达**的台阶，不是细微差别。
- `int8_convrot` 会把同一句提示词读成**更平**的画面。在它上面做提示词 A/B，很容易把量化造成的平坦误判成「这句话没用」。
- ⇒ **任何对照实验的第一步是钉死 checkpoint 文件名与量化格式，并在记录里写明。** 换一次量化等于换一把量尺，不同量化之间不共享读数尺度。

### 2. VAE 只改色调，不改几何

`Krea2-HD-vae`（484 MB / fp32，194 tensors，decoder 卷积相对差 0.2–2.8，带 `buster_*` 元数据）与 `qwen_image_vae`（242 MB / bf16，194 tensors）key set 完全一致、解码兼容，属**重调过的调音版**，不是原模型的副本。

- 同 caption 下两个 VAE 的全帧 `mean|Δ|` 只有 5–6 / 255，视觉是**暖度、饱和度、微对比**的变化，**几何基本不动**。
- 反证：用能读出形状的 caption，两个 VAE 都渲出腹凸；用被压平的措辞，两个都平 ⇒ **VAE 是色调旋钮，不是小腹旋钮**。
- ⇒ 跨 VAE 比较时先做色调归一化再判形状；不得把 VAE 记作几何差异的来源。
- **核对方法**：读工作流的 `VAELoader` 节点值，不要读模型文件内嵌的 metadata —— 文件 metadata 里出现的 VAE 名不一定被画布引用。

### 3. 光照句尾的一截平光短语是形状压制源

基线 caption 与后几代工作流的 caption 在**视角 + 光照**那一行上有实质差异。只改这一行、其余逐字节冻结后：

- 该行结尾的 **`, with a soft even falloff across the wall behind her`** 半句是压制源。**只删这半句**（保留方向 / 高度句），全帧距离相对原样差 63（seed A）/ 48（seed C），**下腹明显回凸**，两个 seed 一致。
- **位置无关**：把这半句原样搬到独立一行，全帧只差 7.5 —— 与「纯粹把一句话换到下一行」的噪声地板同量级。**搬家不解决，删除才解决。**
- **方向 / 高度句是安全的**：`A single large soft light source is positioned 45 degrees to her left and slightly above.` 保留不动，结论照样成立。它正是为解耦「曝光 × 档位」而保留的一半。

⇒ 写分档 caption 时，光照句只写**方向、高度、软硬、来源**；**不要写平光 / 均匀衰减收尾**（`soft even falloff`、`lights her whole figure evenly`、`flat, even mid-tone` 一类都会抹平塑形光与形状读数）。

这一章的三条要先于「以下规则适用于Krea2 官方版」使用：**先钉住量化，再安定 VAE，最后才谈提示词。**

---

## 以下规则适用于Krea2 官方版

> **本章实测范围**：下列规则来自「成年女性站立全身像 · 下腹凸出分级」这一单一概念的成对实验，配置见文末「实测条件」。
> 标记含义：**【实测·3 种子】** 三个 seed 上重复出现；**【实测·单例】** 单 seed，或改动未完全单变量隔离；**【假设】** 尚未验证的下一步。
> 换概念、换题材、换配置后都应重新验证，不要把本章数值当作模型常数。

### 0. 效率顺序：先改语序，再改词汇

一条 prompt 里能动的旋钮，按实测收益排序：

> 前提：配置变量（checkpoint 量化、VAE、光照句）先钉住。量化换一次等于换一把量尺，其影响大于下表所有旋钮；见「配置变量：量化、VAE 与光照句」一章。

| 优先级 | 旋钮 | 实测收益 |
| --- | --- | --- |
| 1 | **句内语序**：核心形态在前，边界语义收尾 | 档距 CV 0.54 / 0.52 → **0.10 / 0.29 / 0.27** 【实测·3 种子】 |
| 2 | **单变量**：一次只改一句 | 不产生收益；它决定上面那个数字可不可信 |
| 3 | **承载句写对**：服装与覆盖面料的写法 | 单独一句就能把整条梯度压平，也能救回 |
| 4 | 程度副词 → 几何状态 | 语序不动时 ≈ 无效（CV 0.478 / 0.476，与对照同量级）【实测·2 种子】 |
| 5 | 语义重述（换视觉关系重说同一件事） | 推幅度，不推均匀度；seed 间不稳 |
| 6 | `(word:1.3)` 一类括号权重 | 不按传统 CLIP 线性工作 |

第 1 项与第 4 项差一个数量级。§1.2、§1.3 都是有效手段，但都不是第一顺位——**语序没摆对时，换再多同义词也读不出差别。**

---

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

这是本节唯一被实测确认的大杠杆，落地写法见 §2。

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

**实测边界**：在语序未摆正的前提下，把整条档位句从程度副词换成几何名词，读数与对照同量级（CV 0.478 / 0.476 对 0.544 / 0.519）。它的作用是把幅度做出来，不是把档距做匀。【实测·2 种子】

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

**实测边界**：按 1 / 2 / 2 / 3 句重述构造四档（梯度由重述句数驱动），实测推的是**幅度**而不是**均匀度**（档距 52.3 / 23.5 / 17.4，CV 0.489），且在第二个 seed 上档距结构改变（15.5 / 25.1 / 26.6）。它适合当幅度助推器，不适合当档距工具。【实测·2 种子】

---

### 2. 语序怎么摆：核心形态前置，边界语义收尾

落地模板——**核心形态独占第二个句子，边界降级为从句收尾**：

```text
A young adult Chinese woman. Her lower belly <形态从句>, while her waist, arms,
hips and legs stay slim and her upper abdomen stays flat.
```

对照写法——边界的属性直接挂在主语介绍里，与核心形态并列、且位置更靠前：

```text
A young adult Chinese woman with a narrow waist, slim arms, narrow hips and long
slim legs, her upper abdomen flat, her lower belly <形态从句>.
```

两种写法的档距（相邻档位移，四档）：

| 写法 | seed A | seed B | seed C | CV |
| --- | --- | --- | --- | --- |
| 边界前置 | 13.9 / 24.2 / **52.9** | 12.3 / **3.8** / 18.3 | — | 0.544 / 0.519 |
| **形态前置＋边界收尾** | 31.2 / 29.3 / 24.7 | 20.4 / 30.4 / 15.1 | 16.2 / 28.9 / 17.8 | **0.097 / 0.290 / 0.269** |

幅度没有下降（对照的 seed B 只有 11.5 的平均档位移），变的是**均匀**。

**为什么**：本配置的 Boundary Adherence 偏强（见文末画像），边界语义可以压过核心目标。边界先行时模型先建立“典型瘦身材”这个整体状态，再把局部体积从中挤出去；边界后置时它只能以从句身份限制范围，无法重写主体。

**验证方式**：只把程度副词换成几何名词、语序不动 → 读数与对照同量级（CV 0.478 / 0.476）。词汇不是杠杆，语序是。【实测·2 种子】

---

### 3. 边界语义不能删，只能后置

边界从句是承重的。删掉 `while her waist, arms, hips and legs stay slim and her upper abdomen stays flat` 不是“把空间让给核心形态”，而是失去局部化约束，体积会向全身扩散。

正确做法始终是：

- 核心形态 = 主目标，占据句子的主句位置；
- `slim limbs / waist / hips`、`upper abdomen flat` = 限制体积不外溢的边界，收尾；
- 这条竞争是**有意保留**的，不要消除它。

---

### 4. 一次只动一句

档距要能读出信号，同一批图里只能有一个变量。实测中有一整个 fold 因为服装句与视角句同时变化而无法归因，白跑。

对**训练集**还有一条更硬的约束：**除形态从句以外的所有字节逐字节冻结**（发型、服装、背景、光源、构图、风格全部相同）。否则「局部形态大小」会和「构图 / 亮度 / 服装」在数据里相关，LoRA 会把它们一起学走。

---

### 5. 服装与覆盖句是局部形态的承载句

局部形态能不能被读出来，很多时候不取决于形态句本身，而取决于**衣物那一句怎么写**。

一次单变量替换实验（阳性对照：一条已知能分级的 caption，逐次只换回一句新文本）：

| 只换入这一句 | 首→末档像素变化 | 判定 |
| --- | --- | --- |
| —（对照原样） | 52.6% | 分级 |
| 主体形态句 | 53.8% | 分级 |
| **发型＋服装＋姿态句** | **4.5%** | **压平** |
| 背景句 | 45.1% | 分级 |
| 光源句 | 55.8% | 分级 |

承载词是这一对：

```text
form-fitting mini dress made of soft, opaque fabric       ← 体积能被读出来
fitted short-sleeved dress in soft matte fabric           ← 整个梯度消失
```

机制：`form-fitting` + `opaque` 把“布料绷在身上、并且不透”写死，下腹体积**只能以剪影变化表达**；改成 `fitted … soft matte fabric` 后模型读成“版型合身的梭织连衣裙”，让布自然垂落，体积被布吸收。

**换服装近义词时：颜色、质地、袖长、裙长、配饰、层次都可以动；把“绷紧＋不透”这一对表述固定下来。**

> **同向证据（未完全单变量隔离）**：`that follows the gentle curve of her lower body`、`the fabric drapes smoothly over the curve of her lower abdomen`、`skims`、`clings` 这类**柔化谓语**同时存在时，梯度同样被压平；拆掉后梯度恢复单调可读。可表述为一条通用律：**任何形容词级的“柔化 / 顺滑 / 自然过渡”措辞都在抹掉形体读数。**

> ⚠ **目标相反时结论相反。** 如果你的目标是**遮盖**而不是**读出**，`drapes smoothly`、宽缓轮廓、不透明内衬恰恰是要写的（见[提示方法](prompt-method.md)「局部形态与面料」）。同一批词汇服务两个相反目标，选词前先确认当前要的是哪一个。

---

### 6. 构图句不得抢在体型句之前

把 `Full-length portrait from head to toe.` 从 caption 的**第 6 位提到第 1 位**（其余字节不变）：

| 构图句位置 | 相邻档位移 | CV | 最高档 |
| --- | --- | --- | --- |
| 在体型句之后（默认） | 31.2 / 29.3 / 24.7 | 0.097 | 正常凸出 |
| **提到最前** | 11.1 / 6.4 / 6.6 | 0.272 | **连衣裙从胸口直垂到髋部，肚子归零** |

取景确实被锁住了（人物中心漂移 0.1%），但代价是整条梯度被压掉——构图先验赢了早期 token 之争，模型回落到“远景精瘦模特”那个吸引子。【实测·2 种子】

**要锁构图，用体型句内部的常量前缀，不要动句序。** 即同一批图里核心句除形态从句外的所有字节保持完全相同（主体、腰部边界、上腹状态逐字节固定），只让那一个形态从句逐档变化。这样构图与档位解耦，同时不牺牲形体读数。

---

### 7. 强度分级：用几何状态，不用程度副词

对官方 Krea 2，`subtle / noticeable / pronounced / extreme` 的视觉差距可能被压缩。

更稳定的办法是让不同档位使用**不同的几何状态**——不是在同一个形容词上换档，而是在改变：

- 曲率；
- 可见程度；
- 局部体积；
- 必要时的向前投射感。

一套实测能读出四档的写法（形态从句逐档替换，其余字节冻结）：

```text
L1  Her lower belly is slightly and softly rounded below the navel, ...
L2  Her lower belly is clearly and softly rounded below the navel, with a small, visible natural fullness, ...
L3  Her lower belly is noticeably fuller and rounded below the navel, with a clearly visible natural fullness, ...
L4  Her lower belly is distinctly rounded and visibly fuller below the navel, forming a prominent natural fullness that pushes forward, ...
```

档位职责分工：L1 只给曲率；L2 加可见度（`small, visible`）；L3 加局部体积（`fuller`）；L4 加向前投射（`pushes forward`）。上一版把四个档位都写成程度副词＋`fullness` 的堆叠，实测相邻档读不出差别。

> **注意**：换几何状态只负责把幅度做出来，**不负责把档距做匀**（见 §1.2）。均匀度靠 §2 的语序和 §4 的单变量。
> 若某个强几何词带来过强先验，可以用多个温和但一致的关系描述达到相似效果，不必依赖一个极端词。

---

### 8. 语义竞争：做边界，不做主导

Krea 2 官方版在多个强语义之间经常表现为折中，而不是严格执行所有条件：

```text
extremely slender
large rounded abdomen
completely natural body
very flat abdomen
```

这类描述内部就存在明显竞争。使用原则：

1. **主目标内部保持一致**。真正目标是局部腹部体积时，核心语义应朝同一方向：`noticeably fuller`、`softly rounded`、`visible natural fullness`、`smooth lower-abdominal volume`。避免同时加入会直接否定主目标的强语义。
2. **竞争语义适合做边界，而不是抢主导权**。`Her lower abdomen is noticeably fuller and rounded. Her waist, arms, hips, and legs remain slim.` 里 `slim` 与 `fuller lower abdomen` 的竞争是有意的：前者是主目标，后者限制体积不要扩散到全身。这样可以把模型的折中行为转化为“局部化控制”。
3. **竞争语义放后面**。边界语义放在核心语义之前，模型会先建立“典型瘦身材”，然后把局部体积压掉。默认顺序是**核心形态在前，竞争／限制语义在后**。落地模板见 §2。
4. **边界生效不等于目标生效**。边界被遵守得很好时，主目标可能反而被压掉（§5、§6 的两个实例）。两者要分别记录、分别诊断，不要因为边界干净就认为整体服从。

---

### 9. 环境与风格先验也在压形态

形体读数不只由形体句决定，环境与风格句自带体型先验。

- **环境**：同一套形体阶梯句，暖色室内环境的相邻档位移可达 40% 量级，冷色深背景影棚只有约 10% 量级。深色影棚把人物拍成“时尚大片精瘦模特”，这层风格先验本身在压体积。若形体是主目标，环境句应选与目标同向的方案。【实测·单例（环境句与光源句同时变化）】
- **风格句里的体质表述是压制指令**：`authentic body proportions` 出现在风格段（caption 第 5 位）时，档距 CV 为 0.312 / 0.158 / 0.202；删掉它，幅度完整保留。与语序修正叠加后 CV 降到 0.059 / 0.092 / 0.073（全表最均匀），但 seed A 的平均档位移被压到 11.1。判定：它是**幅度钳制器**，不是档距工具——想要拉开幅度就删，想要稳定收敛就留。

---

### 10. “自然”和“强度”在官方版中的关系

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

### 11. 观察渠道与读数纪律

**渠道：侧视 ≫ 正面。** 正面视角下下腹凸出是轮廓**内部**的深度线索，只能靠明暗与边缘曲率间接读出；同一套已修好的四档，正面自动读数在躯干宽度轮廓上差异 < 1%。侧视（侧向主光）能把体积写成剪影变化，是四档阶梯的首选渠道。若成品最终主要是正面，需要单独为正面分支配更侧向的主光再验证。

**读数：肉眼看到的“有分级”可能是曝光漂移。** 修正前的一版在原始像素读数上是 34 → 63 → 81%，看似完美单调，但那批图里**墙面亮度中位数从 95 掉到 69，而身体反而变亮**——模型在把肚子画大的同时把整个场景重打了一遍灯。去掉整体色调后，真实档距是 13.9 / 24.2 / 52.9，并不均匀。

因此判定一条梯度是否成立，至少要做两件事：

1. **先把整体色调归一化**（按档 1 做直方图匹配），剩下的差异才只能是空间结构；
2. **同时看档距的幅度和均匀度**——用 `平均档位移 ×（最小档位移 / 最大档位移）` 这类判分，`均匀但都极小` 拿不到高分（那本来就是条没在分级的梯度）。

另外：**冻结光源句与背景句**。修好语序后 ROI 均值仍随档位漂移（127 → 138），训练集里“肚子大”和“画面更亮”仍可能被一起学走。

**读数纪律补充（2026-09-22）**

- **裁切宽度必须由身高定，不能由躯干最宽行定。** 按“躯干最宽行”取宽度会被手臂 / 姿势带跑（可达 40%）；改成固定身高分数（如 `0.30 × Hbody`）后各图的解剖带才等价（`Hb/H` 稳定在 ±2.5%）。同尺度对照是判几何的前提。
- **整帧距离是“家族探测器”，不是形状探测器。** 它主要跟踪服装 / 背景 / 姿势这类全局内容（长袖暗廊 vs 短袖亮墙）。判局部几何**只用同一家族内的对照**（同服装同光）；跨家族差值会被照明与服装混淆。
- **单图读数在阈值附近不可重复。** 同一张图换一次裁切，我在两份材料里给出过相反判词。接近阈值的对比只认人眼，且必须做成同一张图、同一尺度。
- **侧视凸出指数分不开档位，也防不住姿势。** 侧姿轮廓弦线法（chest→pubis 弦，取 navel 处外凸量 / 胸深处）在同一批 5 档侧视图上给出 `+0.19…+0.23` —— 档间差小于重跑噪声，**没有一个单调信号**；其中一张同臂图因为手臂搭在腹前 / 转身，外凸量从 ~50px 跳到 89px，指数当场翻倍（+0.20 → +0.39）。⇒ 侧视档距**不能自动判定**，只能同尺度成对肉眼读；自动指数只配当“有没有明显异常”的哨兵。
- **解剖带要盖住被测部位。** 默认 `0.20–0.52H` 会把下腹切到画外（立姿 navel≈0.40H，0.52H 已到髋）；测下腹用 `0.32–0.62H`。
- **做单变量前先 diff 整条 prompt。** 用 `difflib` 逐行对齐，确认“只差你打算差的那一处”再开跑。曾有一整轮“肚子句 A/B”跑在一条悄悄不同的光照行上，测的全是二阶效应。
- **读 caption 读落盘的 sidecar `.txt`。** API dict 里 `CLIPTextEncode.inputs.text` 是 link（`["48", 0]`）而非字面量字符串；只有 override 过才有字符串。

---

### 附：实测条件

- checkpoint：`krea2_turbo_int8_convrot.safetensors`，走原生 `UNETLoader`（低位量化；相对结论成立，绝对幅度见上文「量化注记」）
- 文本编码器：`qwen3vl_4b_fp8_scaled.safetensors`；VAE：`qwen_image_vae.safetensors`
- 采样：8 步，CFG 1，euler / simple；分辨率 1152 × 1728（同一 seed 连续出四档）
- seed：`135704819493437` / `246813579135` / `887394612057`
- 被测概念：成年女性站立全身像的下腹凸出，四档
- 读数：按列投影定位躯干 ROI → 直方图匹配到第 1 档（消掉整体调色）→ 相邻档 `mean|Δ|`
- 判分：`SPACING SCORE = 平均档位移 ×（最小档位移 / 最大档位移）`
- 实测日期：2026-09-21 / 2026-09-22

**caption 骨架**（各段字节固定，只有 ① 的形态从句逐档变化）：

```text
① 核心句   A young adult Chinese woman. Her lower belly <形态从句>, while her waist,
            arms, hips and legs stay slim and her upper abdomen stays flat.
② 视角光线 Side profile view. <光源方向与光质>
③ 发型服装 She has <发型>. She is wearing <服装，含 form-fitting / opaque>
④ 姿态     She stands <姿态>
⑤ 环境背景 <环境>. <色调氛围>
⑥ 构图     Full-length portrait from head to toe.        ← 保持在这一位，不要前移
⑦ 风格     <风格模板>
```

本配置的画像：

```yaml
model_profile:
  family: krea2
  checkpoint: krea2_turbo_int8_convrot.safetensors
  variant: turbo
  source: official
  modification: quant_only
  quantization: int8_convrot    # 低位量化：几何读数偏平，见「配置变量」
  vae: qwen_image_vae.safetensors
  text_encoder: qwen3vl_4b_fp8_scaled.safetensors
  loras: []
  semantic_gain: balanced      # 文字改动能产生可见变化；但程度副词不线性，档距不均匀
  boundary_adherence: strong   # 边界/覆盖语义可以压过核心目标：边界先行即抹平核心
  evidence: observed_test
  confidence: replicated       # 主结论在 3 个 seed 上重复
  scope: 成年女性站立全身像的下腹凸出分级；1152x1728，8 步，CFG 1，官方 turbo（本表档距实测在 int8_convrot 上取得）
```

`boundary_adherence: strong` 是本配置最值得记住的一条：**它既解释了为什么局部化控制好写（边界一写就生效），也解释了为什么语序这么重要（边界一旦靠前，核心就被压掉）。**

> **量化注记（2026-09-22）**：上表档距数字取自 `int8_convrot`。同一提示词与 seed 下，`fp8_scaled` / `mxfp8` 的形状读数明显更饱满，`int8_convrot` / `nvfp4` 偏平；本仓库的比较基线（“04”）经字节级证明是用 `krea2_turbo_fp8_scaled` 渲的。因此本表的**相对结论**（语序是首要杠杆、承载句承重等）在 int8 上成立且可复现，但**“形状是否被读出”与绝对幅度**应换到全精度级量化上重核。见「配置变量：量化、VAE 与光照句」一章。

---
