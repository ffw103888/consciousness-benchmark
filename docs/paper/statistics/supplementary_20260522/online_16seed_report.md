# Online Benchmark Run Report

Run ID: `online_20260522_173251`
Rows: `320`
Condition sets: `thalamus, distributed, meta-strength, meta-noise, meta-delay`
Seeds per condition: `16`
Warmup: `128`
Quick probes: `False`

## Construct Validation

| construct                    |   n | r_95_ci              | p_formatted   | validated   | mechanism                         |
|:-----------------------------|----:|:---------------------|:--------------|:------------|:----------------------------------|
| Action agency                | 320 | 0.727 [0.662, 0.781] | <1e-9         | True        | action-outcome loop               |
| Boundary self                | 320 | 0.918 [0.894, 0.935] | <1e-9         | True        | workspace                         |
| Identity-temporal self       | 320 | 0.749 [0.656, 0.816] | <1e-9         | True        | workspace      |
| Action ownership             | 320 | 0.987 [0.981, 0.990] | <1e-9         | True        | action-outcome loop |
| Distributed body-schema self | 256 | 0.902 [0.877, 0.927] | <1e-9         | True        | meta-monitor                      |

## Mechanism Effects

| mechanism   | target_construct       |   n_off |   n_on | mean_diff_95_ci         | p_formatted   |
|:------------|:-----------------------|--------:|-------:|:------------------------|:--------------|
| workspace   | Boundary self          |      32 |     32 | 0.493 [0.482, 0.504]    | <1e-9         |
| action_loop | Boundary self          |      32 |     32 | -0.013 [-0.024, -0.002] | 0.8413        |
| workspace   | Identity-temporal self |      32 |     32 | 0.246 [0.232, 0.260]    | <1e-9         |
| action_loop | Identity-temporal self |      32 |     32 | -0.008 [-0.022, 0.006]  | 0.7997        |
| workspace   | Action agency          |      32 |     32 | -0.001 [-0.003, 0.001]  | 0.9908        |
| action_loop | Action agency          |      32 |     32 | 0.698 [0.695, 0.700]    | <1e-9         |
| workspace   | Action ownership       |      32 |     32 | 0.000 [-0.000, 0.000]   | 0.9998        |
| action_loop | Action ownership       |      32 |     32 | 0.968 [0.968, 0.968]    | <1e-9         |

## Control Correlations

| control_key           |   n | r_95_ci                 | p_formatted   |
|:----------------------|----:|:------------------------|:--------------|
| meta_monitor_strength |  96 | 0.811 [0.766, 0.857]    | <1e-9         |
| meta_monitor_noise    |  64 | -0.906 [-0.943, -0.870] | <1e-9         |
| meta_monitor_delay    |  64 | -0.420 [-0.611, -0.283] | 0.0005        |

