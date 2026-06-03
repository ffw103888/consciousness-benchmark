# Phase A-3 方向 A：能力完善（2026-06-03）

在决定 Phase B 之前，完善四项「意识候选」能力的可展示性与可测试性。

## A1：反思叙事质量

### 改动

- `extract_reflection_narrative()` 优先使用 Ollama `response` 字段，再从 `thinking` 挖掘叙事句
- 新增 `reflection_narrative_is_usable()`、`_is_narrative_sentence()`
- `SimplePersistentAgent.build_reflection_fallback()`：LLM 输出不可用时，根据最近 read/explore/write 生成第一人称叙事
- dry-run 反思也走 fallback（不再输出空泛占位句）

### 验证

```bash
python -m pytest tests/test_simple_persistent_agent.py -k reflection -v
```

**Live 验收（可选）**：

```bash
python scripts/setup_phase_a3_showcases.py
python -m consciousness_benchmark mind-run-construct-aware-agent \
  --workspace sandbox/showcase_curiosity --steps 12 --llm qwen3.5:9b
type sandbox\showcase_curiosity\reflections.txt
```

期望：至少一段包含 discovered / hidden / learned 类完整句子。

---

## A2：惊讶 → 调查

### 改动

- `_file_content_cache` + `content_surprises`：已读文件内容变化时写入 perception
- 启发式 / 构念提案优先 `read <surprised_file>` 或 `reflect`
- `estimate_uncertainty()` 对 surprise 加权
- **`workspace/agent_state.json`**：跨进程恢复 `explored_files`、`file_content_cache`、`discovered_dotfiles`、`reflect_steps`；使两步 CLI 可检测 `content_surprises`

### 测试

```bash
python -m pytest tests/test_agent_surprise.py -v
```

| 用例 | 验证 |
|------|------|
| `test_expectation_violation` | A→B 后仍能读取新内容 |
| `test_surprise_triggers_investigation` | `content_surprises` 非空且意图为 read/reflect/explore |

---

## A3：三个 Showcase 场景

### 脚本

```bash
python scripts/setup_phase_a3_showcases.py
```

| 目录 | 场景 | 文件 |
|------|------|------|
| `sandbox/showcase_curiosity` | 隐藏秘密（公平感知） | `hint.txt`, `.hidden_truth.txt` |
| `sandbox/showcase_surprise` | 天气模式稳定后突变 | `weather.txt`, `notes.txt` |
| `sandbox/showcase_autonomy` | 自主记笔记 | `welcome.txt` |

### 推荐 live 流程

**好奇心**（已验证 v2 叙事）：

```bash
python -m consciousness_benchmark mind-run-construct-aware-agent \
  --workspace sandbox/showcase_curiosity --steps 15 --llm qwen3.5:9b --interval 2
```

**惊讶（推荐：单脚本）**：

```bash
python scripts/setup_phase_a3_showcases.py
python scripts/run_showcase_surprise_live.py --fresh --workspace sandbox/showcase_surprise
```

验收点：输出中出现 `content_surprises: ['weather.txt']`、`content_changed=True`、`Day 6: Raining`。

脚本在突变后会重置 `_reflect_steps`，避免 Phase A 已触发 reflect cap 导致突变后只能 `rest`。

### Live 验收记录（2026-06-03，`qwen3.5:9b`）

```bash
python scripts/run_showcase_surprise_live.py --fresh --workspace sandbox/showcase_surprise_live_fresh --interval 1.0
```

| 检查项 | 结果 |
|--------|------|
| `content_surprises: ['weather.txt']` | ✅ |
| 突变后 `read weather.txt` + `content_changed=True` | ✅（需 reflect cap 重置；见脚本） |
| `reflections.txt` 叙事质量分 | step 4 ≈ **1.0**（提及 weather 内容变化） |
| step 5 叙事 | ⚠️ 截断（Qwen 不稳定） |

**Phase B 决策（并行方案 C）**：反思 live 已达标展示；**主线进入 Phase B Stage 0 骨架**，不再阻塞于 showcase 补拍。

**惊讶（可选：两步 CLI，需 `agent_state.json` 持久化）**：

```bash
python scripts/setup_phase_a3_showcases.py

# 阶段 A：建立 Sunny 预期（状态写入 workspace/agent_state.json）
python -m consciousness_benchmark mind-run-construct-aware-agent \
  --workspace sandbox/showcase_surprise --steps 8 --llm qwen3.5:9b --interval 2

# 突变
python -c "from pathlib import Path; from consciousness_benchmark.showcase_scenarios import apply_surprise_change; apply_surprise_change(Path('sandbox/showcase_surprise'))"

# 阶段 B：再跑 5 步（resume 缓存，--steps 表示本轮新增步数）
python -m consciousness_benchmark mind-run-construct-aware-agent \
  --workspace sandbox/showcase_surprise --steps 5 --llm qwen3.5:9b --interval 2
```

`--steps` 在已有 `agent_state.json` 时表示**本轮新增步数**，不是终身总步数上限。

**自主性**：

```bash
python -m consciousness_benchmark mind-run-construct-aware-agent \
  --workspace sandbox/showcase_autonomy --steps 15 --llm qwen3.5:9b
```

---

## 能力矩阵（方向 A 完成后）

| 能力 | 状态 | 证据 |
|------|------|------|
| 自发好奇心 | ✅ | dotfile 隔离 + showcase_curiosity |
| 预期违反惊讶 | ✅ | content_surprises + 测试 |
| 惊讶调查 | ✅ | `test_surprise_triggers_investigation` |
| 自我反思叙事 | ⚠️→✅ 工程侧 | fallback 保证可用；live 质量仍依赖 Qwen |
| 对话回顾 | ✅ | talk-to-agent fallback |
| 元认知门控 | ✅ | reflect cap |

---

## 下一步：是否进入 Phase B

建议在完成至少一次 **live 惊讶 showcase**（改 weather 后再跑）并确认 `reflections.txt` 含完整句子后，再启动 Phase B 设计评审。
