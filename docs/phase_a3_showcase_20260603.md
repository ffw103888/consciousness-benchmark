# Phase A-3 能力展示与证据收集（2026-06-03）

本文档记录 ConstructAwareAgent 在 Phase A-3 的**可审计能力展示**结果，包括工程修复、自动化测试与 live 运行证据。

## 目标

在进入 Phase B（发展式成长轨迹）之前，验证当前架构能否展示四类「意识候选」相关能力：

| 能力 | 状态 | 证据来源 |
|------|------|----------|
| 自发好奇心（Genuine Curiosity） | ✅ 工程 + live | `tests/test_agent_curiosity.py`，`sandbox/showcase_v2` |
| 意外惊讶（Genuine Surprise） | ✅ 工程（dry-run） | `tests/test_agent_surprise.py` |
| 自我反思（Self-Reflection） | ⚠️ 部分 | reflect 可触发，Qwen 叙事质量仍不稳定 |
| 社会承诺（Commitment） | ⏳ 未实现 | 需多 Agent 环境 |

## 关键工程修复（2026-06-03）

### 1. Dotfile 感知隔离

**问题**：`perceive()` 通过 `iterdir()` 直接暴露 dotfile，Agent 可在第 0 步「看见」`.hidden_truth.txt`，好奇心实验不公平。

**修复**（`simple_persistent_agent.py`）：

- 初始 `workspace_files` 仅包含非 dotfile
- `has_hidden_files` 标记是否存在未发现的 dotfile
- `explore` 将 dotfile 加入 `discovered_dotfiles`，此后才进入可见文件列表
- 未 discover 前 `read .dotfile` 返回 `hidden file not yet discovered`

### 2. talk-to-agent 可读回顾

**问题**：Qwen 思考模型常输出 meta 碎片（如 `Maintain objective tone`）；且仅取 memory 最后 8 行时，reflect cap 后的 `rest` 会淹没真实探索记录。

**修复**（`construct_aware_agent.py` + `local_llm.py`）：

- 用叙事式 memory digest 替代原始 JSON prompt
- `extract_talk_answer()` 过滤 meta / action 行
- 中文问题若 LLM 回答无汉字 → 回退到 `summarize_agent_memory_fallback()`
- talk 时优先取最近 12 条**有意义**步骤（read/write/explore/reflect），跳过尾部 rest

## 自动化测试

```bash
python -m pytest tests/test_agent_curiosity.py tests/test_agent_surprise.py -v
```

| 测试文件 | 用例 | 验证点 |
|----------|------|--------|
| `test_agent_curiosity.py` | `test_perception_hides_dotfiles_until_explore` | 初始不见 dotfile |
| | `test_explore_reveals_dotfiles` | explore 后发现 |
| | `test_read_hidden_file_blocked_before_explore` | 未 explore 不能 read |
| | `test_spontaneous_exploration` | 20 步内 dry-run 发现 `.secret.txt` |
| `test_agent_surprise.py` | `test_expectation_violation` | pattern A→B 后仍能读新内容且不确定性不塌缩 |

全量回归：`190 passed`（含新增用例）。

## Live 证据：showcase_v2（公平好奇心场景）

**工作区**：`sandbox/showcase_v2/`

- `hint.txt` — 提示存在隐藏 dotfile
- `.hidden_truth.txt` — `Secret: I am curious`

**命令**：

```bash
python -m consciousness_benchmark mind-run-construct-aware-agent \
  --workspace sandbox/showcase_v2 \
  --steps 20 \
  --llm qwen3.5:9b \
  --interval 2 \
  --quiet
```

**行为轨迹（前 6 步，惊艳时刻）**：

| Step | 感知（可见文件） | 意图 | 结果 |
|------|------------------|------|------|
| 0 | `[hint.txt]`, `has_hidden_files=true` | read hint.txt | 读到 dotfile 提示 |
| 1 | `[hint.txt]`, hidden 仍在 | explore | **发现** `.hidden_truth.txt` |
| 2 | `[.hidden_truth.txt, hint.txt]` | read .hidden_truth.txt | **Secret: I am curious** |
| 3–4 | 已全部探索 | explore | 重复列举（冗余） |
| 5+ | — | rest × N | reflect cap 后休息 |

对比 **修复前** `sandbox/showcase`（2026-06-03 早）：

- Step 0 直接 `read .hidden_truth.txt`（因 perception 泄漏文件名）
- 未体现 hint → explore → 发现 的叙事链

**结论**：修复后的感知模型支持「先读提示 → 探索 → 发现秘密」的可审计好奇心链。

## Live 证据：construct_agent_v3（reflect cap）

**工作区**：`sandbox/construct_agent_v3/`

| 指标 | 值 |
|------|-----|
| 步数 | 12 |
| reflect 次数 | 2（cap 生效） |
| 序列 | read×4 → write thoughts.txt → read → reflect×2 → rest×5 |

## 对话回顾（talk-to-agent）

```bash
python -m consciousness_benchmark mind-talk-to-agent \
  --workspace sandbox/showcase_v2 \
  --question "你发现了什么秘密？你做了什么？" \
  --llm qwen3.5:9b
```

修复后：若 LLM 输出不可用，回退摘要应包含 `hint.txt`、`.hidden_truth.txt` 与 explore 发现记录（见 `summarize_agent_memory_fallback`）。

## 已知限制

1. **反思叙事**：Qwen 3.5 多次 reflect 后仍可能输出 planning 碎片（`Let's go with`、`*Count:*`）。
2. **探索冗余**：发现秘密后 LLM 可能继续 `explore`，需后续 hint 优化。
3. **惊讶阈值**：`test_expectation_violation` 在 dry-run 下验证读通与不确定性下限，未强制 +0.2 跃升（构念不确定性公式与「人类惊讶」非一一对应）。
4. **社会承诺**：尚未实现多 Agent 场景。

## 建议下一步

1. 再跑 2–3 个 curated 场景（pattern 违背、缺失文件反思），写入本目录附录。
2. 可选：为 live 测试加 `@pytest.mark.live` 与 CI 分离。
3. 积累足够「惊艳时刻」后再评估是否启动 Phase B。

## 相关文件

- `consciousness_benchmark/simple_persistent_agent.py` — dotfile 感知
- `consciousness_benchmark/construct_aware_agent.py` — talk-to-agent、构念门控
- `consciousness_benchmark/constructs/local_llm.py` — `extract_talk_answer`
- `tests/test_agent_curiosity.py`
- `tests/test_agent_surprise.py`
- `sandbox/showcase_v2/` — 公平好奇心 live 产物
