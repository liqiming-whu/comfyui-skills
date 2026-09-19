# Krea 2 Turbo 四状态资源占用 Benchmark

## 目标

记录同一台电脑在四个运行状态下的系统内存与显存总占用，并以 State A 桌面基线计算后续状态的资源增量。

报告主值使用固定采样窗口内的中位数；同时保留最小值和最大值，避免把单次后台刷新误认为稳定占用。

## State A — Desktop baseline

定义：ComfyUI未运行，仅保留当前Windows桌面和既有后台应用。

测量前后均确认：

- 没有运行中的ComfyUI Python进程。
- TCP端口8188没有监听程序。
- 未启动、停止或修改任何其他应用。

### 结果

| 指标 | 主值（中位数） | 最小值 | 最大值 | 总容量 |
| --- | ---: | ---: | ---: | ---: |
| `RAM_total_used` | **10.353 GiB** | 10.344 GiB | 10.396 GiB | 31.458 GiB |
| `VRAM_total_used` | **0.944 GiB（966.8 MiB）** | 0.939 GiB | 0.989 GiB | 11.940 GiB（12,227 MiB） |

RAM使用率中位数为32.9%，采样区间为32.9%–33.0%。

### 采样方法

- 采样时间：2026-09-03（Asia/Shanghai）
- 样本数：21
- 采样间隔：0.5秒
- 采样窗口：10秒
- RAM：Windows全系统已用物理内存
- VRAM：NVML报告的整张GPU已用显存
- 原始值以bytes保存，报告使用GiB（1024³ bytes）和MiB（1024² bytes）换算

### 基线值

后续状态统一使用以下中位数作为增量基线：

```text
RAM baseline  = 11,116,179,456 bytes
VRAM baseline =  1,013,719,040 bytes
```

## State B — ComfyUI idle

定义：启动ComfyUI，但未打开Edge浏览器、未提交或执行工作流，测量时任务队列为空。

测量前确认：

- 仅有一个ComfyUI Python主进程，PID为29408。
- 该进程监听`0.0.0.0:8188`。
- ComfyUI运行队列和等待队列均为0。
- 普通`msedge.exe`进程为0；系统中的WebView2进程单独记录，不计作Edge浏览器。
- 未调用`/free`，未提交workflow。

### 结果

| 指标 | 主值（中位数） | 最小值 | 最大值 | 相对State A增量 |
| --- | ---: | ---: | ---: | ---: |
| `RAM_total_used` | **11.726 GiB** | 11.716 GiB | 11.753 GiB | **+1.374 GiB** |
| `VRAM_total_used` | **1.307 GiB** | 1.307 GiB | 1.318 GiB | **+0.363 GiB** |
| `ComfyUI_process_RAM`（主进程RSS） | **1.167 GiB** | 1.167 GiB | 1.167 GiB | — |
| `ComfyUI_process_tree_RAM`（主进程及子进程RSS） | **1.174 GiB** | 1.174 GiB | 1.175 GiB | — |

ComfyUI子进程RSS中位数为0.008 GiB，因此主进程与进程树口径相差很小。

### 解读

- 从State A到State B，整机RAM稳定占用增加约1.374 GiB，其中ComfyUI进程树自身RSS约1.174 GiB。
- 整机RAM增量与进程RSS不会严格相等：前者还会受到Windows文件缓存、驱动和其他后台进程波动影响，不能把差额直接归因于ComfyUI。
- 整机VRAM增加约0.363 GiB，可视为当前环境中ComfyUI、Python、CUDA上下文及相关驱动分配共同形成的空闲基础开销；NVML无法把这部分全部精确归属到单一进程。
- 本状态只证明采样时队列为空且未由测试脚本提交任务；“本次启动后从未执行过workflow”来自测试前的人工状态控制，API本身无法独立证明完整启动历史。

### 采样方法

- 采样时间：2026-09-03（Asia/Shanghai）
- 样本数：21
- 采样间隔：0.5秒
- 采样窗口：10秒
- RAM与VRAM口径和State A相同
- ComfyUI进程RAM：Windows进程RSS（工作集）；同时保留主进程和进程树两种口径

## State C — Model resident

定义：每种量化模型各执行一次完整workflow；任务成功结束后不调用`/free`，保持模型驻留，静置8秒，再连续采样10秒。

三种模型在同一个ComfyUI进程中按NVFP4 → MXFP8 → FP8 scaled顺序测试。只在前一种模型的resident采样完成后调用`/free`，用于切换到下一种模型；该清理不属于任何被测resident窗口。

### 结果

| 常驻模型 | 模型文件大小 | `RAM_total_used` | `VRAM_total_used` | ComfyUI进程树RSS | 相对State B RAM增量 | 相对State B VRAM增量 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| NVFP4 | 7.147 GiB | **26.740 GiB** | 8.523 GiB | **15.770 GiB** | **+15.014 GiB** | +7.216 GiB |
| MXFP8 | 12.603 GiB | 28.934 GiB | **7.922 GiB** | 17.633 GiB | +17.208 GiB | **+6.615 GiB** |
| FP8 scaled | 12.239 GiB | 29.335 GiB | 8.112 GiB | 18.154 GiB | +17.608 GiB | +6.805 GiB |

表中均为21次采样的中位数。三次workflow均成功完成，无节点校验错误，并产生输出；本轮单次运行墙钟时间分别为36.850秒、48.541秒和43.114秒，运行时间仅用于确认任务确实完成，不作为本状态的速度排名。

### 结论

- **综合常驻资源最省的是NVFP4**：它的整机RAM和ComfyUI进程树RSS均明显最低。与MXFP8相比，NVFP4少占约2.194 GiB整机RAM和1.863 GiB进程树RSS。
- **只看整卡显存，MXFP8最低**：比NVFP4低约0.601 GiB，比FP8 scaled低约0.190 GiB。
- FP8 scaled在本次同进程顺序测试中的整机RAM与进程RSS最高，因此没有表现出相对MXFP8的常驻内存优势。

### 解释边界

- `RAM_total_used`和`VRAM_total_used`是整机/整卡口径，会包含其他系统进程和驱动分配；资源归属应结合ComfyUI进程树RSS一起判断。
- `/free`能卸载模型和请求释放内存，但同一Python进程的分配器、文件缓存或CUDA上下文未必完全回到初始State B。因此NVFP4相对另外两者的明显优势可信度较高，而MXFP8与FP8 scaled之间约0.4–0.5 GiB的进程RAM差异可能含有测试顺序效应。
- 若要严格判定MXFP8与FP8 scaled谁更省主机内存，应为每种模型分别重启ComfyUI并重新取得对应的State B，然后再测resident；本表代表更贴近日常同一ComfyUI会话内切换模型的结果。

### 采样方法

- 每种模型运行次数：1次
- workflow结束后的静置时间：8秒
- 每种模型resident样本数：21
- 采样间隔：0.5秒
- resident采样窗口：10秒
- 采样窗口内不调用`/free`，不提交其他workflow
- RAM、VRAM和ComfyUI RSS口径与State B相同

## State D — Inference peak

定义：每种模型先运行一次以建立常驻状态，静置8秒并重新采集当轮State C基线；随后更换seed再次执行同一workflow，在整个推理期间以0.1秒间隔采样。临时推理成本按以下公式计算：

```text
Inference temporary cost = State D inference peak - 同轮 State C resident median
```

这里使用同一模型、同一轮次紧邻测得的resident基线，而不是直接减去上一节较早采集的State C，以减少后台进程波动、分配器状态和测试顺序造成的误差。

### 推理峰值

| 模型 | 推理前resident RAM | Peak RAM | 推理前resident VRAM | Peak VRAM | Peak ComfyUI进程树RSS | OOM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| NVFP4 | 27.108 GiB | **27.209 GiB** | 8.760 GiB | **11.259 GiB** | **16.100 GiB** | 否 |
| MXFP8 | 29.243 GiB | 29.529 GiB | **7.394 GiB** | 11.697 GiB | 18.499 GiB | 否 |
| FP8 scaled | 29.157 GiB | 29.564 GiB | 8.110 GiB | 11.726 GiB | 18.524 GiB | 否 |

### 推理临时成本（State D − State C）

| 模型 | 临时整机RAM | 临时整卡VRAM | 临时ComfyUI进程树RSS |
| --- | ---: | ---: | ---: |
| NVFP4 | **+0.101 GiB** | **+2.500 GiB** | **+0.018 GiB** |
| MXFP8 | +0.286 GiB | +4.303 GiB | +0.235 GiB |
| FP8 scaled | +0.407 GiB | +3.616 GiB | +0.305 GiB |

### 结论

- **NVFP4的推理临时开销最低**：三项增量均为最低，且整卡峰值显存也是三者最低。
- MXFP8虽然推理前resident显存最低，但执行时需要额外约4.303 GiB显存，临时显存成本最高；峰值达到11.697 GiB。
- FP8 scaled的临时显存成本介于两者之间，但本轮整机RAM和进程树RSS临时增量最高，峰值显存11.726 GiB也是三者最高。
- 三种模型都在这张约11.94 GiB显存的GPU上成功完成，没有OOM；MXFP8和FP8 scaled的显存余量明显小于NVFP4。

### 测量边界

- 这是离散的0.1秒轮询峰值，极短于采样间隔的瞬时尖峰可能被漏掉，因此应理解为“观测到的峰值”。
- RAM和VRAM仍是整机/整卡口径，临时增量可显著削弱固定后台占用的干扰，但采样期间其他进程的活动仍可能造成少量噪声。
- 每种模型在测量推理前都重新运行一次建立resident；三组建立轮和测量轮均成功并产生输出。测量轮墙钟时间分别为30.436秒、41.347秒和38.542秒，不作为本状态的主要评价指标。
- 切换模型的`/free`发生在下一模型开始前；任何resident或inference测量窗口内均未调用`/free`。

## 原始证据

- `state-a-desktop-baseline.json`：包含21次逐样本时间戳、RAM/VRAM总量、已用量、可用量及GPU温度。
- `state-b-comfyui-idle.json`：包含State B预检信息、21次逐样本RAM/VRAM、ComfyUI主进程与进程树RSS，以及相对State A的增量。
- `state-c-model-resident.json`：包含三种模型的文件大小、提交模型名、seed、workflow完成状态、静置时间、每组21次resident样本和汇总值。
- `state-d-inference-peak.json`：包含每种模型的resident建立轮、同轮State C基线、测量轮状态、0.1秒推理采样序列、峰值及State D减State C的临时成本。

后续复测应沿用相同单位、采样口径和状态定义，并同时保留绝对占用及对应基线增量。
