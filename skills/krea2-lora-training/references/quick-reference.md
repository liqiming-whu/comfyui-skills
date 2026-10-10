# 来源与适用范围

## 官方建议

- [Krea 2 官方 README](https://github.com/krea-ai/krea-2/blob/main/README.md)：推荐 RAW 训练、Turbo 推理；也提供 RAW 推理流程。仓库命令的推荐参数为 RAW 52 步/CFG 3.5，Turbo 8 步/CFG 0/mu 1.15。其他推理实现需核对对应参数语义。
- [官方 prompting](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md)：推荐自然语言生成提示词。生成提示词长度建议不能直接当作训练 caption 的硬门槛。
- [官方 sampler](https://github.com/krea-ai/krea-2/blob/main/sampling.py)：关闭 CFG 时跳过负向条件分支，正向文本仍编码；这不证明正文否定词无效。
- [Krea 2 LoRA training](https://www.krea.ai/blog/krea-2-lora-training)：Krea 云端训练逐图 caption、最少三张、自动描述后可修改、人物应含角度/表情/光照/背景变化。云端档位、套餐和默认步数应在使用时重新确认。
- [通用 Training 文档](https://www.krea.ai/docs/user-guide/features/training)：10–30 张为其建议规模，不是本地训练上限；风格一致性与人物多样性需要按目标区分。
- [官方 expansion 模板](https://github.com/krea-ai/krea-2/blob/main/docs/expansion.txt)：生成提示词扩写模板，副本在 `assets/expansion-system-prompt.txt`；不用于自动生成事实性图片 caption。

## 环境实现与经验

AI-Toolkit 的 caption 注入、dropout、缓存、分辨率展开和 step 定义需读取实际安装版本。可定位 `toolkit/config_modules.py`、`toolkit/dataloader_mixins.py`、`toolkit/data_loader.py` 和 `jobs/process/BaseSDTrainProcess.py`，不把一个版本的行为当作所有训练器的规范。

本机 `D:/lora/AI-Toolkit/toolkit/data_loader.py` 的目录扫描使用 `os.walk`，`num_repeats` 重复整个文件列表；参考 [上游加载源码](https://github.com/ostris/ai-toolkit/blob/main/toolkit/data_loader.py)，执行时仍以安装版本为准。文件名或目录的数字前缀不设置倍率，详细方案见 [训练与评估](training-evaluation.md)。

可复用的 ComfyUI API 图、林知微/Ada 已完成的实测范围及 Xiaoling 项目提示词见 [实测案例与测试示例](checkpoint-examples.md)。它们分别属于执行资产、历史观察和测试输入，不能代替新模型的实际测试。

词数范围、维度关键词覆盖率、补图张数、头位比例和看图抽样量都是可调整的经验或操作约定。它们不能保证训练收益，也不能自动判定图像属性的存在或不存在。

正文中每条一次的完整触发词是当前检查器默认协议；独立别名训练需另定分配与验证规则。稳定身份描述并不因重复出现就必然有害。
