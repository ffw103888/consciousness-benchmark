# Phase B：发展式成长轨迹（设计草案）

> 状态：设计评审稿，尚未实现。Phase A-3 能力验证完成后进入实现排期。

## 目标

用**分阶段、可审计、可里程碑验收**的方式，探索 Agent 是否呈现「成长轨迹」而非一次性训练结果。

## 设计原则

1. **Review-only 默认**：阶段晋升需显式里程碑证据，不自动写 registry。
2. **与构念 runtime 对齐**：每阶段产出 `construct_state_ledger` + `agent_state.json`。
3. **能力递进**：感知运动 → 符号表征 → 社会互动，不跳阶。
4. **失败可解释**：未达 `success_criteria` 时生成 gate advice 风格报告。

## 阶段概览

| Stage | 名称 | 时长（设计） | 环境 | 核心里程碑 |
|-------|------|--------------|------|------------|
| 0 | sensorimotor | 24h | `simple_2d_grid` | 物体恒常、自他运动区分、边界 |
| 1 | symbolic | 48h | filesystem + symbols | 符号表征、目标保持、短计划 |
| 2 | social | 72h | multi_agent_world | 意图推断、承诺履行、规范 |

## Stage 0：感知运动（Sensorimotor）

**环境**：离散 2D 网格，物体可移动/隐藏。

**能力**：`sense_position`, `move`, `grab`

**里程碑**：
- `discover_object_permanence` — 物体被遮挡后仍存在
- `discover_self_caused_motion` — 区分自身移动 vs 外部扰动
- `discover_boundary` — 识别环境边界并避免无效移动

**成功标准（草案）**：
- `explored_cells >= 0.8`
- `self_other_accuracy >= 0.9`
- `object_permanence_trials_passed >= 10`

**与 Phase A 衔接**：复用 `content_surprises` 作为「物体重现」惊讶信号原型。

## Stage 1：符号表征（Symbolic）

**环境**：文件系统 + 显式符号文件（`symbol_<object>.txt`）。

**能力**：Stage 0 + `read`, `write`, `plan`

**里程碑**：
- `use_symbols_to_represent_objects`
- `maintain_goal_across_interruptions`（跨 `agent_state.json` 恢复）
- `form_simple_plans`（2–3 步计划成功率）

**成功标准（草案）**：
- `symbol_files_created >= 5`
- `goal_persistence_rate >= 0.8`
- `plan_execution_success >= 0.7`

**与 Phase A 衔接**：直接复用 `ConstructAwareAgent` + showcase 脚本模式。

## Stage 2：社会互动（Social）

**环境**：多 Agent 沙盒（消息文件 / 共享承诺日志）。

**能力**：Stage 1 + `communicate`, `cooperate`, `commit`

**里程碑**：
- `infer_other_agent_intention`
- `make_and_keep_commitment`
- `follow_and_question_norm`

**成功标准（草案）**：
- `intention_inference_accuracy >= 0.7`
- `commitment_keeping_rate >= 0.9`
- `norms_learned >= 5`

**依赖**：需新建多 Agent 协议（Phase A-3 能力 4 未实现）。

## 实现路线图（建议）

### 第 1 周：Stage 0 骨架

- [ ] `DevelopmentalStageRunner` + 配置 JSON
- [ ] 2D grid 环境最小实现
- [ ] 里程碑检测器（纯规则 + 日志）
- [ ] 批处理 CLI：`mind-developmental-stage-run --stage sensorimotor`

### 第 2 周：Stage 1 与 filesystem 桥接

- [ ] 将 Stage 1 接到现有 `ConstructAwareAgent`
- [ ] 目标持久化指标（`agent_state.json` + goal 字段）
- [ ] 计划执行评估 harness

### 第 3 周：Stage 2 设计验证（可选）

- [ ] 多 Agent 消息协议 PoC
- [ ] 承诺履行测试（`test_commitment_keeping` 占位）

## 进入 Phase B 的前置条件（已满足 / 待满足）

| 条件 | 状态 |
|------|------|
| Phase A-3 好奇心 live | ✅ showcase_v2 |
| Phase A-3 惊讶 live | ✅ `run_showcase_surprise_live.py` + `agent_state.json` |
| 状态持久化 | ✅ |
| 反思叙事工程 fallback | ✅ B1 已加强；live Qwen 质量仍待观察 |
| 全量测试稳定 | ⚠️ 治理类文档测试与仓库大量 untracked docs 需隔离 |

## 决策建议

**推荐并行（方案 C）**：
- 主线：启动 Stage 0 环境骨架（本文件 → 实现 issue）
- 副线：用 `test_reflection_quality.py` + showcase live 观察反思改善

若 Stage 0 网格环境 3 天内无法产出可审计里程碑，则优先巩固 Phase A showcase 文档与 CI 隔离，再重启 Phase B。

## 决策记录（2026-06-03，live 后）

| 选项 | 结论 |
|------|------|
| 先补 showcase 叙事 | **否** — `run_showcase_surprise_live` 已验收惊讶；step 4 反思质量分 1.0 |
| 直接 Phase B Stage 0 | **是** — 第 1 周交付 `DevelopmentalStageRunner` + 2D grid 最小环境 |
| 反思副线 | 维持 `test_reflection_quality.py`；不阻塞 Stage 0 |

**已执行 live**：`sandbox/showcase_surprise_live_fresh`；`content_surprises` 与 weather 变化叙事均已出现。
