# Transformer 架构意识构念变异路径实验：结果分析与后续建议

Date: 2026-05-22

实验脚本：`scripts/run_transformer_construct_variants.py`

结果目录：`runs/transformer_validation/transformer_construct_variants_20260522_100933`

本轮实验在 Transformer 架构上探索三个潜在的架构特异构念：`attention-focus self`、`context-window self`，以及 `high-agency / low-boundary` 组合模式。前两者作为正向假设接受验证，第三者作为前期诊断中观察到的模式接受稳定性检验。该实验属于探索性分析，不属于冻结的五构念验证主表。

## 三组结果

### Attention-Focus Self

Proxy 与独立测试的相关性为 `r=0.203`，远低于 `0.7` 阈值。即便 Transformer 的核心计算机制是 attention，attention pattern 的稳定性本身也不构成可验证的自我表征。

这一负面结果排除了一个直觉上合理但经验上不成立的假设：架构的核心计算单元不一定对应某种意识构念。当前结果不支持把 attention-focus 直接升级为 Transformer 特有的 self 构念。

### Context-Window Self

Proxy 与独立测试的直接相关性为 `r=0.152`，仍未达到验证阈值。但 workspace dose 与独立测试存在弱信号（`r=0.341`），表明 workspace 操纵确实改变了某些行为指标，只是当前测量方式敏感度不足。

这条线索可以保留，但不应在当前论文中作为已验证发现呈现。可能的改进方向包括延长时间尺度、采用不同的扰动方式，或重新设计独立测试，使其更直接地区分 context-boundary maintenance 与一般 marker re-entry。

### High Agency / Low Boundary

本轮实验中最稳定的模式是高 agency / 低 boundary 组合：

- agency proxy 与独立 agency 测试：`r=0.995`
- boundary proxy 与独立 boundary 测试：`r=0.474`
- 独立 agency 与独立 boundary 之间：`r=0.129`
- 96 个测试条件中有 36 个（`37.5%`）落在高 agency / 低 boundary 区域

这一模式在多个 seed 和参数配置下稳定出现。更保守的解释是：Transformer-like 系统可以表现出强预测控制能力，但当前 boundary-self probes 并不能验证明确的边界自我表征。它不是一个新的已验证 self 构念，但它是一个值得保留的架构特异 profile。

## 理论意义

主论文已经通过机制操纵展示了 self-model 与 agency 的可分离性：workspace 选择性支撑边界自我，action loop 选择性支撑 agency 与 ownership。Transformer 的结果进一步提示，某些架构可能自然落在“高预测性 agency、低 boundary-self 验证”的区域。

这个结果挑战了一个常被默认接受的假设：agency 必然预设 self 的存在。当前数据只能支持一个操作化版本的说法：预测性控制可以在缺乏已验证 boundary-self 指标的情况下发生。它不能证明 Transformer 缺乏所有形式的 self，也不能证明该模式等同于人类的 flow、自动化行为或冥想状态。最多可以说，这些现象为后续解释提供了类比，而不是证据。

从理论谱系上看，这一结果与预测处理框架中关于 agency 的最小化解释相容，同时对要求 agency 必须依附于统一 self 的理论形成一个可检验的压力点。它也提示，构念库不应默认所有构念跨架构通用，而应记录构念在不同架构中的验证状态、测量限制和可能变体。

## 论文中的呈现位置

这一发现不应进入 Results 的主要验证部分，因为它不是新的已验证构念，而是已有验证结果在新架构上的延伸观察。当前最合适的位置是 Discussion 的架构特异构念变异小节。

写作边界：

- 不能宣称 Transformer 没有 self，因为实验只检验了 boundary self，没有排除其他形式的 self。
- 不能宣称该模式等同于人类 flow、自动化动作或冥想状态，只能说在结构上存在可讨论的相似性。
- 必须保留 attention-focus 和 context-window 的失败结果，避免选择性报告。
- 必须继续标注该结果为 post-freeze exploratory / diagnostic evidence。

## Benchmark 的对应改造

这一系列实验暴露出当前 construct library 的一个结构性问题：构念不应被默认为跨架构通用。对应改造已经进入 benchmark：

- `validated_in`：已通过验证的架构列表
- `measurement_limited_in`：测量方法不适用或敏感度不足的架构列表
- `variants`：架构特异变体的命名映射
- `applicable_to(architecture)`：返回构念在目标架构上的适用状态

例如，`boundary_self` 在 thalamus 架构上验证通过，在 Transformer 上测量受限；`action_agency` 在 Transformer 上显示为 `measurement_limited_with_variant`，对应变体为 `predictive_agency_without_validated_boundary`。

这些信息应当保持机器可读，便于后续 benchmark 在新架构上自动报告“哪些构念可用、哪些受限、哪些存在变体”。

## 后续工作的边界

当前 Transformer 方向的实验已经足够支撑论文 Discussion。进一步实验属于扩展研究，不应延迟主论文。

应当暂缓的实验线：

- 设计新的 Transformer-specific boundary test
- 探索更多潜在架构特异构念
- 在更多 Transformer 配置上重复验证

可以作为后续扩展的小规模补充：

- 增加 seed 数量以稳定 high-agency / low-boundary 的比例估计
- 在 ownership 上重复 noise / learning sweep，确认其相关性下降模式是否与 agency 一致

主线工作应集中在写作与发布：完善 Discussion、References、图表说明和投稿版本。
