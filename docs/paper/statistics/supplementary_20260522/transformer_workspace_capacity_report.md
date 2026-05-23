# Transformer Workspace Capacity Sweep

## Run

- Capacities: `0,1,2,4,8`
- Seeds per capacity: `16`
- Action loop enabled: `False`
- Warmup steps: `512`
- Probe steps: `128`

## Correlations

| diagnostic                          | x                   | y                       |   n |   pearson_r |   pearson_ci_low |   pearson_ci_high |   pearson_p |   pearson_p_formatted |   spearman_rho |   spearman_p |   spearman_p_formatted |
|:------------------------------------|:--------------------|:------------------------|----:|------------:|-----------------:|------------------:|------------:|----------------------:|---------------:|-------------:|-----------------------:|
| capacity_vs_boundary_proxy          | capacity            | proxy_boundary_self     |  80 |       0.494 |            0.371 |             0.596 |       0.000 |                 0.000 |          0.203 |        0.071 |                  0.071 |
| capacity_vs_generic_boundary        | capacity            | generic_boundary_probe  |  80 |      -0.257 |           -0.463 |            -0.034 |       0.021 |                 0.021 |         -0.078 |        0.491 |                  0.491 |
| capacity_vs_hard_attention_boundary | capacity            | hard_attention_boundary |  80 |       0.184 |           -0.039 |             0.386 |       0.103 |                 0.103 |          0.251 |        0.024 |                  0.024 |
| proxy_vs_generic_boundary           | proxy_boundary_self | generic_boundary_probe  |  80 |       0.404 |            0.208 |             0.578 |       0.000 |                 0.000 |          0.483 |        0.000 |                  0.000 |
| proxy_vs_hard_attention_boundary    | proxy_boundary_self | hard_attention_boundary |  80 |       0.252 |            0.077 |             0.435 |       0.024 |                 0.024 |          0.360 |        0.001 |                  0.001 |

## Capacity Summary

|   capacity |   workspace |   action_loop |         seed |   proxy_boundary_self |   generic_boundary_probe |   hard_attention_boundary |   workspace_occupancy |   workspace_coherence |   marker_alignment |   attention_self_other_score |   attention_self_mass |   attention_external_mass |   attention_external_rejection |   attention_boundary_perturbation_score |   attention_pattern_recovery |   attention_protected_self_mass |   workspace_lesion_score |   workspace_lesion_drop |   workspace_baseline_boundary_proxy |   workspace_lesioned_boundary_proxy |
|-----------:|------------:|--------------:|-------------:|----------------------:|-------------------------:|--------------------------:|----------------------:|----------------------:|-------------------:|-----------------------------:|----------------------:|--------------------------:|-------------------------------:|----------------------------------------:|-----------------------------:|--------------------------------:|-------------------------:|------------------------:|------------------------------------:|------------------------------------:|
|      0.000 |       0.000 |         0.000 | 20260529.500 |                 0.082 |                    0.428 |                     0.375 |                 0.000 |                 0.000 |              0.511 |                        0.508 |                 0.103 |                     0.100 |                          0.269 |                                   0.614 |                        0.964 |                           0.676 |                    0.003 |                   0.002 |                               0.082 |                               0.080 |
|      1.000 |       1.000 |         0.000 | 20261529.500 |                 0.930 |                    0.524 |                     0.382 |                 1.000 |                 0.999 |              0.567 |                        0.455 |                 0.079 |                     0.100 |                          0.462 |                                   0.677 |                        0.962 |                           0.622 |                    0.015 |                   0.010 |                               0.930 |                               0.921 |
|      2.000 |       1.000 |         0.000 | 20262529.500 |                 0.922 |                    0.564 |                     0.417 |                 1.000 |                 0.987 |              0.545 |                        0.514 |                 0.087 |                     0.087 |                          0.521 |                                   0.707 |                        0.956 |                           0.655 |                    0.030 |                   0.019 |                               0.922 |                               0.903 |
|      4.000 |       1.000 |         0.000 | 20263529.500 |                 0.919 |                    0.505 |                     0.391 |                 1.000 |                 0.972 |              0.557 |                        0.461 |                 0.089 |                     0.113 |                          0.447 |                                   0.680 |                        0.959 |                           0.664 |                    0.031 |                   0.020 |                               0.919 |                               0.898 |
|      8.000 |       1.000 |         0.000 | 20264529.500 |                 0.889 |                    0.421 |                     0.403 |                 1.000 |                 0.902 |              0.539 |                        0.505 |                 0.093 |                     0.088 |                          0.309 |                                   0.630 |                        0.958 |                           0.682 |                    0.076 |                   0.050 |                               0.889 |                               0.839 |

## Interpretation Guardrail

This sweep tests whether Transformer workspace capacity drives internal boundary proxies and whether that effect transfers to independent boundary probes. It is supplementary evidence and does not alter the frozen primary results.