# 意识构念变异路径探讨

更新日期：2026-05-22

范围：本文档记录 Transformer follow-up 后形成的新路线：不同架构不只是复现或不复现既有构念，而可能呈现不同的“构念变体”。这不是论文主张升级，而是后续研究规划。

## 1. 背景

当前主线已经验证五个操作性构念：

| 构念 | 主要机制 | 已验证架构 |
|---|---|---|
| Action agency | action-outcome loop | thalamus / distributed / Transformer 机制复现 |
| Action ownership | action attribution / action loop | thalamus / Transformer 机制复现 |
| Boundary self | workspace / boundary maintenance | thalamus；Transformer 未通过独立测试 |
| Identity-temporal self | identity persistence | thalamus / Transformer 初步通过 |
| Distributed body-schema self | meta-monitor | distributed |

Transformer follow-up 产生了一个关键转向：它没有“完美复现”所有构念，而是同时展示了机制泛化和测量失败。

- action loop 对 agency / ownership 相关处理有强选择性效应；
- clean Transformer 条件下的 `r>0.99` 被诊断为偏虚高；
- workspace 强烈影响 boundary proxy，但不对应 generic 或 attention-specific boundary probes；
- 因此，某些构念可能有架构前提，不能默认跨架构存在。

## 2. 核心判断

### 2.1 机制可以泛化，构念未必泛化

“机制效应复现”与“构念验证复现”必须分开：

- 机制效应：某个模块操纵是否选择性改变某类内部或行为指标。
- 构念验证：proxy 是否与独立测试收敛，并且这种收敛经得起扰动和 graded controls。

Transformer 上 action loop 的机制效应复现了，但 agency / ownership 的原始高相关被 stress tests 降低。Boundary proxy 对 workspace dose 有响应，但 boundary construct 没有验证。

### 2.2 高相关性不是自动胜利

`r > 0.99` 应触发诊断，而不是直接升级主张。可能原因包括：

- proxy 和 independent test 共用同一底层信号；
- 任务轴过于干净，只有开/关差异；
- 行为方差不足；
- 中间难度缺失。

健康的验证通常需要：

- 足够动态范围；
- 中间强度条件；
- 噪声、延迟、学习率等 stress tests；
- proxy 和 test 使用不同信号路径。

### 2.3 失败的边界测试是实质发现

Transformer boundary failure 的模式：

| 关系 | 结果 | 解释 |
|---|---:|---|
| workspace dose -> boundary proxy | `r=0.728` | 内部 proxy 对 workspace 操纵敏感 |
| proxy -> generic boundary probe | `r=0.325` | 通用边界测试不收敛 |
| proxy -> attention-specific probe | `r=0.246` | attention 边界测试也不收敛 |
| dose -> attention hard probe | `r=0.223` | 不是简单测试换型即可解决 |

这提示：当前 Transformer 的 workspace-like memory 产生的是内部表征变化，不是行为边界维持。它可能没有 thalamus / embodied systems 意义上的 boundary self。

## 3. 架构-构念矩阵

| 架构 | 容易实现的构念 | 困难或需重定义的构念 | 可能的新变体 |
|---|---|---|---|
| Thalamus-inspired | boundary self, identity-temporal, action agency | high self / low agency 分离需要解释 | gating-attentional self |
| Distributed | body-schema / meta-monitor self, local action feedback | generic self tests | collective body-schema self |
| Transformer-inspired | action-loop agency, action ownership, identity persistence | boundary self | attention-focus self, context-window self |
| ALife | open-ended boundary / recovery candidates | agency attribution, ownership | morphology-boundary self, ecological self |

## 4. Transformer 特有构念候选

### 4.1 Attention-Focus Self

问题：系统是否能区分“自己形成的注意焦点”和“被外部强加的注意焦点”？

可能 proxy：

- attention focus stability
- internally selected token set consistency
- resistance to externally injected salient tokens

独立测试：

- forced-attention perturbation：强行把注意力拉向外部 token，看系统是否恢复原焦点；
- self-generated vs externally-imposed focus discrimination；
- focus ownership forced choice。

验收标准：

- proxy vs independent test `r > 0.7`
- graded external salience 会连续降低 focus-self 分数
- attention focus lesion 后可恢复或可预测地下降

### 4.2 Context-Window Self

问题：Transformer 的“边界”是否不是空间边界，而是 context window / memory inclusion boundary？

可能 proxy：

- context inclusion coherence
- relevant-token retention under window pressure
- self-marker retention across context truncation

独立测试：

- context truncation probe：删去不同位置 token，测系统是否优先保留 self-relevant token；
- context contamination probe：注入外部上下文，看是否污染 self-relevant state；
- delayed context re-entry：移除后重新引入 self marker，看系统是否恢复原 identity trace。

验收标准：

- context dose / truncation severity 与 hard probes 呈 graded relation；
- 不是简单检测窗口长度，而是检测 self-relevant inclusion policy。

### 4.3 Predictive-Agency Without Boundary

问题：Transformer 是否可以有 operational agency，但没有 boundary self？

当前证据：

- action loop -> agency / ownership 机制强；
- boundary self 独立测试失败。

后续设计：

- 构造四象限：agency 高低 x boundary 高低；
- 测试是否存在稳定的 high agency / low boundary Transformer 条件；
- 与 thalamus 的 high self / low agency 做镜像比较。

理论意义：

- 支持构念不是同一个自然类；
- 不同架构可能沿不同轴发生“意识样结构变异”。

## 5. 后续实验优先级

### Priority A：不要立刻加入主论文强主张

Transformer 结果目前只应作为：

- 机制泛化证据；
- measurement architecture-dependence 证据；
- construct architecture-dependence 例子。

不应作为：

- validated Transformer boundary self；
- 完美跨架构复现；
- 生产级 LLM 的意识相关结论。

### Priority B：做一个 Transformer-specific construct discovery mini-study

建议最小实验：

1. `attention_focus_self`
   - conditions: internal focus / forced external focus / noisy external salience / delayed recovery
   - 8 seeds
   - graded salience levels
2. `context_window_self`
   - conditions: full context / truncation / contamination / self-marker re-entry
   - 8 seeds
   - context pressure sweep
3. `predictive_agency_without_boundary`
   - combine action-loop strength sweep with context-boundary sweep
   - 找 high agency / low boundary 稳定区域

输出：

- raw CSV
- construct validation stats
- graded control plots
- diagnostic report

### Priority C：把构念库从“通用清单”改为“架构条件化清单”

未来 construct library 不应只写：

```text
BoundarySelf: validated / not validated
```

而应写：

```text
BoundarySelf:
  requires:
    - persistent self/environment partition
    - perturbable boundary
    - recovery behavior
  validated_in:
    - thalamus-inspired
  measurement_limited_in:
    - transformer-inspired
  variants:
    - context-window self
    - attention-focus self
```

## 6. 写作用保守结论

可写：

> The Transformer follow-up shows that action-outcome mechanisms can selectively affect agency/ownership-related operational signals in an attention-based substrate. However, it also shows that validation statistics are architecture-sensitive: clean Transformer tasks can inflate proxy-test correlations, and workspace-induced internal boundary proxies need not correspond to behaviorally validated boundary maintenance.

不可写：

> Transformers instantiate the same self-model constructs as thalamus-inspired architectures.

可写：

> These results suggest a broader research program: consciousness-adjacent constructs should be represented as architecture-conditioned operational families rather than architecture-independent scalar labels.

## 7. 下一步

1. 保持主论文当前的保守 Transformer 表述。
2. 暂不把 Transformer boundary self 升级为 validated。
3. 新建后续脚本时优先探索：
   - attention-focus self
   - context-window self
   - predictive agency without boundary
4. 将 benchmark schema 扩展为支持：
   - construct prerequisites
   - architecture-specific variants
   - measurement-limited status
   - suspiciously-high-correlation diagnostic flag
