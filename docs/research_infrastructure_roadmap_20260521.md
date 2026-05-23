# 完整研究规划：从当前项目到开放研究基础设施

更新日期：2026-05-21

范围：本路线图不以论文投稿为主线，而以建立可复用、可验证、可扩展的研究基础设施为目标。

## 0. 当前基线

当前项目已经完成第一阶段的核心科学资产：

- 五个已验证操作性构念：
  - Action agency: `r = 0.874`
  - Boundary self: `r = 0.940`
  - Identity-temporal self: `r = 0.850`
  - Action ownership: `r = 0.996`
  - Distributed body-schema self: `r = 0.924`
- 三类机制分离：
  - Workspace -> boundary / identity-temporal self
  - Action-outcome loop -> action agency / action ownership
  - Meta-monitor -> distributed body-schema self
- 测量方法论资产：
  - 代理指标失败诊断
  - 构念拆分
  - 独立测试验证
  - graded controls
  - 统计冻结与数字一致性检查
- 现有代码资产：
  - `mind_lab` 实验包
  - 三条架构路径：ALife、distributed、thalamus
  - measurement validation scripts
  - paper v2 figures / frozen statistics

## 1. 总体战略

核心目标：

建立“意识相关构念的系统性拆解与验证”范式，优先做方法、测试集和平台，而不是单篇论文。

三大支柱：

1. 标准测试集：Consciousness Benchmark
2. 开源实验平台：Consciousness Lab
3. 构念库：Construct Library

辅助支柱：

4. 跨架构验证
5. 社区建设

## 2. 支柱一：Consciousness Benchmark

目标：

把当前验证过的五个构念打包成标准测试集，使外部系统也能接入验证。

### 2.1 最小可用版本

建议先从当前仓库内孵化，不急于单独开库。

目标结构：

```text
consciousness_benchmark/
  core/
    construct.py
    proxy.py
    test.py
    validator.py
    diagnostics.py
  constructs/
    agency/
    self_model/
    distributed/
  adapters/
    base.py
    mind_lab.py
    custom.py
  reporting/
    tables.py
    figures.py
    report.py
  examples/
    quickstart.py
    validate_mind_lab_systems.py
```

### 2.2 MVP 构念

第一版只纳入已冻结的五个构念：

- `ActionAgency`
- `BoundarySelf`
- `IdentityTemporalSelf`
- `ActionOwnership`
- `DistributedBodySchemaSelf`

明确排除或标记为 exploratory：

- trajectory consistency
- body ownership
- subjective consciousness / qualia

### 2.3 第一阶段交付物

- 统一 `Construct` 抽象
- 统一 `Proxy` / `IndependentTest` 抽象
- `ConstructValidator.validate_all(system)`
- `ValidationReport`
- 从现有 CSV 生成 benchmark report 的脚本
- 一个自定义系统接入示例

## 3. 支柱二：Consciousness Lab

目标：

把当前实验系统打磨成可复现、可扩展的实验平台。

### 3.1 从 mind_lab 演进

当前 `mind_lab` 不必立刻重写。建议分层：

- 保留 `mind_lab` 作为研究原型层
- 新增 `consciousness_benchmark` 作为测量接口层
- 新增 `consciousness_lab` 作为实验编排层

### 3.2 平台 MVP

优先实现：

- factorial design runner
- lesion / recovery runner
- graded control runner
- long-run monitor
- reproducibility metadata
- checkpoint / resume
- report export

暂缓：

- Web UI
- Jupyter 完整教程
- PyPI 发布
- 多框架适配器

### 3.3 可复现性要求

每个实验目录必须包含：

- `config.json`
- raw CSV
- summary JSON
- figure manifest
- frozen statistics
- environment metadata
- command log

## 4. 支柱三：Construct Library

目标：

建立“构念元素周期表”，每个构念都必须经过代理指标、独立测试、诊断和机制验证。

### 4.1 已完成构念

| Construct | Status | Mechanism |
|---|---|---|
| Action agency | validated | action-outcome loop |
| Boundary self | validated | workspace |
| Identity-temporal self | validated | workspace |
| Action ownership | validated | action attribution / action loop |
| Distributed body-schema self | validated | meta-monitor |

### 4.2 下一批构念

建议优先顺序：

1. Attention
   - selective attention
   - sustained attention
   - divided attention
2. Valence / arousal
   - approach-avoidance
   - reward prediction vs valence distinction
3. Working memory / episodic memory
4. Metacognition
   - monitoring
   - confidence
   - control

### 4.3 每个新构念的标准流程

1. 文献和概念边界
2. 初始 proxy
3. 独立 behavioral tests
4. 初始验证
5. 失败诊断
6. 构念拆分
7. 再验证
8. 机制干预
9. graded controls
10. 纳入或标记 exploratory

## 5. 跨架构验证

目标：

判断当前机制是否是通用计算原则，而不是 thalamus / distributed 的特殊结果。

### 5.1 第一优先级：Transformer

状态（2026-05-22 更新）：

- 已完成 lightweight Transformer-inspired follow-up。
- action loop 对 agency / ownership 相关处理呈现强选择性机制效应。
- clean 2x2 条件下的 `r>0.99` 被后续 stress tests 诊断为偏虚高。
- workspace 强烈影响 boundary proxy，但 generic 与 attention-specific boundary probes 均未验证。
- 结论：Transformer 是“机制泛化 + 测量/构念架构依赖性”的案例，不是完美复现案例。

已保存记录：

- `docs/paper/transformer_followup_20260522.md`
- `docs/consciousness_construct_variation_paths_20260522.md`

已回答的问题：

- action-outcome head 是否支持 agency / ownership？是，机制效应强，但验证相关需 stress-test 后保守解释。
- workspace-like broadcast 是否支持 boundary / temporal self？支持 boundary proxy，但 boundary construct 未通过独立测试；identity-temporal 初步通过。
- token-level self representation 是否需要新的独立测试？需要，现有 boundary 测量不够。

新的问题：

- Transformer 是否存在 attention-focus self？
- Transformer 的“边界”是否更像 context-window self，而不是空间/行为边界？
- 是否存在稳定的 high agency / low boundary Transformer 条件？

已完成 MVP：

- 小型 Transformer
- 2x2：workspace module x action loop
- 使用已验证五构念中的四个：distributed body-schema self 暂不适用

后续 mini-study：

- attention-focus self
- context-window self
- predictive agency without boundary

### 5.2 第二优先级：RNN / LSTM

重点：

- temporal self
- identity persistence
- memory confounds

### 5.3 第三优先级：SNN

重点：

- temporal binding
- synchronization / integration
- spike timing as construct substrate

## 6. 社区建设

当前阶段不急于扩大社区。建议在以下资产稳定后再公开推广：

- benchmark MVP
- quickstart
- reproducible example
- frozen validation tables
- clear claim boundaries

早期社区动作：

- GitHub 组织名预留
- README 叙事
- contributing 草案
- issue templates
- example notebooks

## 7. 近期执行计划

### Week 0：收尾当前实验

- 继续 ALife 长跑到 10% 覆盖或人工停止
- 保存最终 ALife summary
- 生成 final run report
- 将 ALife 标记为 open-ended search context

### Week 1：Benchmark 抽象层

- 新建 `consciousness_benchmark` 包目录
- 抽象 `Construct`, `Proxy`, `IndependentTest`, `Validator`
- 用现有五构念 raw CSV 跑一次离线 validation report
- 输出 HTML/Markdown 报告

### Week 2：系统适配层

- 实现 `MindLabAdapter`
- 将 thalamus / distributed 系统接入 benchmark API
- 跑在线验证 smoke test
- 对比离线 CSV 结果，确保数值一致

### Week 3：实验平台化

- 抽象 factorial runner
- 抽象 graded control runner
- 统一输出目录结构
- 将 `finalize_statistics.py` 纳入 reporting pipeline

### Week 4：文档与示例

- 写 quickstart
- 写 custom architecture example
- 写 diagnostic failure example
- 整理 README

## 8. 当前风险

### 8.1 概念风险

风险：构念名称过度接近主观意识术语。

控制：持续使用 operational / proxy-test / construct validation 表述。

### 8.2 工程风险

风险：过早重构导致现有可运行实验破坏。

控制：先新增包和适配层，不移动 `mind_lab` 核心文件。

### 8.3 社区风险

风险：过早公开导致别人误解为“意识检测器”。

控制：README 第一屏写清楚：not a consciousness detector; a construct-validation toolkit.

### 8.4 统计风险

风险：高相关来自二值条件。

控制：保留 graded controls；未来新增更多中间强度和跨架构连续操纵。

## 9. 成功标准

### 1 个月

- benchmark MVP 可运行
- 五构念离线验证报告可复现
- mind_lab 在线适配通过 smoke test
- ALife 10% run 完成并归档

### 3 个月

- 至少一个外部风格 custom system example
- Attention 初始 proxy/test 设计完成
- Transformer MVP 开始验证

### 6 个月

- Consciousness Benchmark 可公开预览
- Consciousness Lab 可一键复现实验
- 构念库增加 1-2 个新 validated / exploratory entries

## 10. 下一步

立即执行顺序：

1. 让 ALife 长跑完成 10%。
2. 新建 benchmark MVP，而不是继续扩写论文。
3. 把五构念的 frozen statistics 作为 benchmark 的 reference data。
4. 实现 `ValidationReport`，使任何后续构念都能走同一条验证管线。

