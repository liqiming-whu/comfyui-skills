# Krea 2 Turbo 量化模型 9 轮基准报告

## 结论

在本机 RTX 5070 Ti Laptop 12 GB 环境中，三个模型均完成 3 轮严格测试，合计 9/9 轮成功，没有发生 OOM，也没有执行缓存命中。

`krea2_turbo_nvfp4.safetensors` 的速度和文件体积均明显领先：执行时间中位数为 **35.698 秒**，比 MXFP8 快约 **19.5%**（反向表述：MXFP8 慢 24.3%），比 FP8 scaled 快约 **22.9%**（反向表述：FP8 scaled 慢 29.7%）。NVFP4 文件也比 FP8 scaled 小约 41.6%。

| 模型 | 文件大小 | 三轮执行时间（秒） | 执行中位数 | 墙钟中位数 | ComfyUI 进程 RAM 峰值 | 整机 RAM 使用峰值 | 整卡显存使用峰值 | OOM |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `krea2_turbo_nvfp4.safetensors` | 7.147 GiB | 40.580 / 35.698 / 35.613 | **35.698 s** | 36.071 s | 16.136 GiB | 29.388 GiB | 11.643 GiB | 0/3 |
| `krea2_turbo_mxfp8.safetensors` | 12.603 GiB | 45.180 / 44.368 / 44.267 | **44.368 s** | 44.790 s | 16.622 GiB | 29.624 GiB | 11.247 GiB | 0/3 |
| `krea2_turbo_fp8_scaled.safetensors` | 12.239 GiB | 46.229 / 46.300 / 46.958 | **46.300 s** | 46.671 s | 17.183 GiB | 29.579 GiB | 11.665 GiB | 0/3 |

> 显存数据是 0.1 秒采样得到的整张 GPU 使用峰值。Windows WDDM 对 `nvidia-smi` 单进程显存报告 `[N/A]`，因此不能可靠拆分 ComfyUI 与桌面、浏览器等其他 GPU 进程的占用。

## 测试环境

- 测试时间：2026-09-03（Asia/Shanghai）
- 设备：MECHREVO YAOSHI Series
- 操作系统：Windows 11 家庭中文版，版本 10.0.26200
- CPU：Intel Core Ultra 9 275HX，24 个逻辑处理器
- 内存：33,778,278,400 bytes（约 31.46 GiB）
- GPU：NVIDIA GeForce RTX 5070 Ti Laptop GPU
- 显存：12,227 MiB（12,792,037,376 bytes）
- NVIDIA 驱动：616.56
- 电源计划：平衡
- ComfyUI：0.33.2
- ComfyUI Frontend：1.49.6
- ComfyUI Python：3.13.11
- PyTorch：2.13.0+cu130
- GPU 内存分配：`cudaMallocAsync`
- 启动参数：`--listen 0.0.0.0 --auto-launch --preview-method auto --use-sage-attention --cuda-malloc`

## 测试方法

- 基准工作流：`skills/comfyui-performance-monitor/assets/benchmarks/moody-krea-turbo-minimal-api.json`
- 工作流 SHA256：`916ff8e1aa866026dbce6206e80d219c7594ec09bf50ce2231993860b4013f98`
- 仅替换节点 `761` 的 `unet_name`；其余节点、采样参数、VAE 和文本编码器不变。
- 顺序固定为 NVFP4 3 轮、MXFP8 3 轮、FP8 scaled 3 轮。
- 每轮开始前调用 ComfyUI `/free`，设置 `unload_models=true`、`free_memory=true`，随后冷却 5 秒。
- 每轮随机替换 Seed 节点的整数 seed，防止 ComfyUI 节点执行缓存复用。
- 严格接受条件：无 `/prompt` 节点错误、执行成功、输出非空、`cached_node_count=0`。
- 内存与显存采样间隔：0.1 秒。
- `execution_seconds` 来自 ComfyUI history 的 `execution_start` 到 `execution_success`。
- `wall_seconds` 是本地提交 `/prompt` 到 history 报告完成的墙钟时间。

`/free` 只卸载 ComfyUI 内存中的模型，不会清除操作系统文件缓存、CUDA 已编译内核或插件私有缓存。因此本报告属于一致的“每轮卸载模型”测试，不应描述为重启操作系统后的完全冷启动测试。

## 逐轮结果

| 轮次 | 模型 | Seed | 执行时间 | 墙钟时间 | 队列等待估计 | 进程 RAM 峰值 | 整机 RAM 峰值 | 整卡显存峰值 | 缓存节点 | 输出节点 | OOM |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | NVFP4 | 297452898597491 | 40.580 s | 40.957 s | 0.004 s | 15.969 GiB | 28.894 GiB | 11.640 GiB | 0 | 3 | 否 |
| 2 | NVFP4 | 1116230895216531 | 35.698 s | 36.071 s | 0.003 s | 16.038 GiB | 29.197 GiB | 11.625 GiB | 0 | 3 | 否 |
| 3 | NVFP4 | 55256659665934 | 35.613 s | 35.996 s | 0.003 s | 16.136 GiB | 29.388 GiB | 11.643 GiB | 0 | 3 | 否 |
| 4 | MXFP8 | 535491521607796 | 45.180 s | 45.558 s | 0.003 s | 16.313 GiB | 29.500 GiB | 11.247 GiB | 0 | 3 | 否 |
| 5 | MXFP8 | 744739048747717 | 44.368 s | 44.790 s | 0.028 s | 16.622 GiB | 29.553 GiB | 11.247 GiB | 0 | 3 | 否 |
| 6 | MXFP8 | 262629058871476 | 44.267 s | 44.646 s | 0.004 s | 16.613 GiB | 29.624 GiB | 11.168 GiB | 0 | 3 | 否 |
| 7 | FP8 scaled | 1033230119663350 | 46.229 s | 46.626 s | 0.004 s | 17.159 GiB | 29.566 GiB | 11.625 GiB | 0 | 3 | 否 |
| 8 | FP8 scaled | 959580417359454 | 46.300 s | 46.671 s | 0.003 s | 17.183 GiB | 29.579 GiB | 11.665 GiB | 0 | 3 | 否 |
| 9 | FP8 scaled | 754085740012932 | 46.958 s | 47.378 s | 0.003 s | 17.098 GiB | 29.470 GiB | 11.648 GiB | 0 | 3 | 否 |

## 内存解释

绝对峰值不仅包含当前扩散模型，还包含 ComfyUI、文本编码器、VAE、PyTorch、CUDA 上下文、Windows 桌面和其他后台程序。相对于每轮 `/free` 后基线，三组观察到的最大增量如下：

| 模型 | ComfyUI 进程 RAM 最大增量 | 整机 RAM 使用最大增量 | 整卡显存最大增量 | 峰值时最少可用系统内存 |
| --- | ---: | ---: | ---: | ---: |
| NVFP4 | 14.778 GiB | 15.261 GiB | 10.037 GiB | 2.070 GiB |
| MXFP8 | 14.155 GiB | 14.819 GiB | 9.757 GiB | 1.835 GiB |
| FP8 scaled | 14.712 GiB | 15.328 GiB | 10.247 GiB | 1.880 GiB |

三个模型均把 12 GB 显卡和 32 GB 系统内存推到较高水位。MXFP8 的整卡显存峰值略低，不代表模型本身更省显存；它的文件更大，ComfyUI 可能通过权重流式加载、CPU offload 或不同量化内核改变了显存驻留方式。

## 性能判断

1. **NVFP4 是本机最实用的版本。** 文件最小、速度最快，三轮无 OOM；除首轮 40.580 秒外，后两轮稳定在约 35.6 秒。
2. **MXFP8 居中。** 中位数 44.368 秒，明显慢于 NVFP4，但三轮极差仅 0.913 秒，稳定性较好。
3. **FP8 scaled 最慢且 RAM 峰值最高。** 中位数 46.300 秒，进程 RAM 峰值 17.183 GiB；本工作流和本硬件下没有体现速度优势。
4. **OOM 风险仍不能视为零。** 本次 9 轮未 OOM，但峰值时系统可用内存最低约 1.84 GiB，整卡显存使用最高约 11.67 GiB。若提高分辨率、批量、并行任务或同时运行更多 GPU 应用，仍可能 OOM 或进入更重的 offload。
5. **固定顺序存在顺序效应。** CUDA 内核、操作系统文件缓存和 Python 分配器状态可能跨轮保留。结果足以反映当前日常运行方式，但若要做发布级量化性能结论，应追加随机交错顺序和重启 ComfyUI 后的多组测试。

## 原始证据

- 原始 JSON：`krea2-turbo-quantization-9run.json`
- 每轮记录 prompt ID、seed、history 时间戳、缓存节点、输出节点、基线与峰值采样值。
- 9 轮均为 `success=true`、`oom=false`、`cached_node_count=0`、`output_count=3`。
