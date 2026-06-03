# Run Profile 系统指南

版本：v1.0  
日期：2026-06-03

## 概述

Run Profile 系统提供预设的运行配置模板，简化命令行参数，规范不同场景的门禁要求。

实现位置：`consciousness_benchmark/run_profiles.py`  
门禁失败建议：`consciousness_benchmark/gate_advisor.py`

## Profile 详细说明

### exploration（探索模式）

**适用场景**：

- 日常开发和调试
- 快速迭代和试错
- 新构念初步验证

**特点**：

- 宽松门禁（phase2_rows=1, temporal_ratio=0.3）
- 较少 rounds（3 轮）
- 不要求 health pass
- 跳过消融测试（快速）

**典型用法**：

```bash
python -m consciousness_benchmark mind-developmental-growth-batch \
  --profile exploration \
  --seed-csv 11,23,37
```

### validation（验证模式）

**适用场景**：

- 正式验证实验
- 候选构念晋升前检查
- 代码变更后的完整测试

**特点**：

- 标准门禁（phase2_rows=3, temporal_ratio=0.5）
- 中等 rounds（5 轮）
- 要求 health pass
- 包含消融测试

**典型用法**：

```bash
python -m consciousness_benchmark mind-developmental-growth-batch \
  --profile validation \
  --seed-csv 11,23,37,42,56
```

### production（生产模式）

**适用场景**：

- 发布前最终检查
- L2.5/L3 复现实验
- 学术论文数据生成

**特点**：

- 严格门禁（phase2_rows=5, temporal_ratio=0.6）
- 大量 rounds（10 轮）
- 必须 health pass
- 完整消融和理论测试

**典型用法**：

```bash
python -m consciousness_benchmark mind-developmental-growth-batch \
  --profile production \
  --seed-csv 11,23,37,42,56,67,78,89,91,103
```

### quick_check（快速检查）

**适用场景**：

- CI/CD 流水线
- Pull Request 检查
- 快速烟雾测试

**特点**：

- 最小门禁（phase2_rows=1, temporal_ratio=0.2）
- 最少 rounds（2 轮）
- 不要求 health pass
- 单个 theory case

**典型用法**：

```bash
python -m consciousness_benchmark mind-developmental-growth-batch \
  --profile quick_check \
  --seed-csv 11
```

## 参数 Override 机制

Profile 参数可以被命令行参数覆盖：

```bash
# 使用 validation，但只跑 7 轮
python -m consciousness_benchmark mind-developmental-growth-batch \
  --profile validation \
  --rounds 7 \
  --seed-csv 11,23,37

# 使用 exploration，但启用 health pass
python -m consciousness_benchmark mind-developmental-growth-batch \
  --profile exploration \
  --require-health-pass \
  --seed-csv 11,23,37
```

Override 规则：

- 只有**显式传递**的参数才会覆盖 profile
- 未传递的参数使用 profile 默认值
- `--list-profiles` 不受 override 影响

## 门禁失败处理流程

1. 运行 batch
2. Health gate 评估
3. 若失败：写入 `gate_failure_advice.md`，并在错误信息中包含文件路径
4. 根据建议调整 rounds、stage_ids、profile 或阈值后重试

## 最佳实践

### 开发流程

```bash
# Day 1-3: 探索
python -m consciousness_benchmark mind-developmental-growth-batch \
  --profile exploration --seed-csv 11,23,37

# Day 4: 验证
python -m consciousness_benchmark mind-developmental-growth-batch \
  --profile validation --seed-csv 11,23,37,42,56

# Day 5: 发布前
python -m consciousness_benchmark mind-developmental-growth-batch \
  --profile production --seed-csv 11,23,37,42,56,67,78,89,91,103
```

### 门禁失败诊断

```bash
cat runs/<batch_id>/gate_failure_advice.md
```

若 exploration 可通过而 validation 失败，通常是门禁强度与阶段不匹配，而非代码必然损坏。

### CI/CD 集成（示例）

```yaml
- name: Quick Check
  run: |
    python -m consciousness_benchmark mind-developmental-growth-batch \
      --profile quick_check \
      --seed-csv 11 \
      --out runs/ci_check/summary.json

- name: Upload advice on failure
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: gate-failure-advice
    path: runs/ci_check/growth_batch_*/gate_failure_advice.md
```

## 常见问题

### Q1: 为什么 exploration 也失败了？

检查：growth_cycle 是否产出有效 phase2、依赖与路径、必要时清理 `runs/` 重试。

### Q2: 如何自定义 profile？

编辑 `consciousness_benchmark/run_profiles.py` 中的 `PROFILES` 字典。

### Q3: production 太慢怎么办？

使用 `validation`，或 `--profile production --rounds 7`。

### Q4: 建议“增加 rounds”加到多少？

参考：exploration 3、validation 5、production 10；每次可加 2–3 轮。

## 附录

完整字段定义见 `consciousness_benchmark/run_profiles.py` 中的 `GrowthBatchProfile` 与 `PROFILES`。
