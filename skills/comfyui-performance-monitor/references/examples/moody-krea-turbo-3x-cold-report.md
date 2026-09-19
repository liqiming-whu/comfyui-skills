# 示例：Moody Krea Turbo Minimal Workflow API 三次测试报告

测试时间：2026-09-01（Asia/Shanghai）

## 测试对象

- UI 源文件：`Moody Krea Turbo Minimal Workflow - V1.json`
- API 文件：`Moody Krea Turbo Minimal Workflow - V1 API.json`
- API SHA-256：`916ff8e1aa866026dbce6206e80d219c7594ec09bf50ce2231993860b4013f98`
- Skill 内基准资产：`assets/benchmarks/moody-krea-turbo-minimal-api.json`
- 节点数：16
- 分辨率：640 × 960，批量 1
- 模型：`KreaMixv3MM_nvfp4.safetensors`
- 文本编码器：`qwen3vl_4b_fp8_scaled.safetensors`
- VAE：`qwen_image_vae.safetensors`

API 转换保留了 UI 中的 Seed 节点链接。保存前缀从仅适用于前端展开的日期宏改为 API/Windows 安全值 `image/Krea2-benchmark`，原 UI 文件未修改。

## 测试策略

- 正式运行 3 次。
- 每次运行前调用 `/free`，参数为 `unload_models=true`、`free_memory=true`。
- 每次清理后冷却 2 秒。
- 每次替换 Seed 节点整数种子，避免相同提示触发节点执行缓存。
- 验收要求：无 `node_errors`、历史输出非空、成功完成且 `cached_node_count = 0`。

该策略清理 ComfyUI 内存模型并避免节点结果复用，但不会清除操作系统文件缓存、CUDA 已编译内核、第三方节点私有缓存或磁盘缓存，因此不称为整机完全冷启动。

## 正式结果

| 轮次 | Seed | 执行时间 | 墙钟时间 | 队列等待估计 | 缓存节点 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 840825863936217 | 30.446 s | 30.829391 s | 0.019 s | 0 | 成功 |
| 2 | 1024318752022123 | 36.852 s | 37.232778 s | 0.015 s | 0 | 成功 |
| 3 | 341749006277457 | 35.421 s | 35.818415 s | 0.024 s | 0 | 成功 |

- 执行时间中位数：**35.421 秒**
- 最短执行时间：**30.446 秒**
- 最长执行时间：**36.852 秒**
- 三轮成功率：**100%**
- 三轮缓存节点数：**均为 0**

## 本机环境

- 机器：MECHREVO YAOSHI Series
- CPU：Intel Core Ultra 9 275HX，24 逻辑处理器
- 内存：33,778,278,400 bytes（约 31.46 GiB）
- GPU：NVIDIA GeForce RTX 5070 Ti Laptop GPU，12,227 MiB
- 驱动：616.56
- 电源计划：平衡
- ComfyUI：0.33.2
- 前端：1.49.6
- Python：3.13.11（ComfyUI 运行环境）
- PyTorch：2.13.0+cu130
- 启动参数：`--use-sage-attention --cuda-malloc`

## 排除的诊断运行

正式三轮之前发生过诊断性运行，不计入结果：

1. 监控器对 Windows 命令输出编码处理失败，任务未提交。
2. `/free` 返回空成功响应，旧监控器错误地按 JSON 解析，任务未提交。
3. 一次实际生成在 `SaveImage` 阶段因日期宏中的冒号形成非法 Windows 路径而失败。
4. 一组三轮初测中第 3 轮命中 15 个执行缓存节点，因此整组废弃。
5. 一组三轮初测使用了超出 Seed 节点范围的随机值，ComfyUI 只执行 WeiLin 输出节点，历史输出为空；监控器现会拒绝 `node_errors` 和空输出。
6. 一次完整生成期间历史轮询单次超时，未形成完整报告；监控器现会在总超时范围内容忍短暂 HTTP 超时。

本文件是一次真实机器测试的示例报告，不是跨机器性能承诺。机器可读原始报告保留在原测试环境中，未作为 Skill 运行输入。
