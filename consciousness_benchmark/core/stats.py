# Copyright 2026 Fuwang Feng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from scipy import stats


def finite_pair(x: Iterable[float], y: Iterable[float]) -> tuple[np.ndarray, np.ndarray]:
    x_arr = np.asarray(list(x), dtype=float)
    y_arr = np.asarray(list(y), dtype=float)
    mask = np.isfinite(x_arr) & np.isfinite(y_arr)
    return x_arr[mask], y_arr[mask]


def pearson(x: Iterable[float], y: Iterable[float]) -> tuple[float, float, int]:
    x_arr, y_arr = finite_pair(x, y)
    if len(x_arr) < 3 or np.std(x_arr) < 1e-12 or np.std(y_arr) < 1e-12:
        return float("nan"), float("nan"), int(len(x_arr))
    result = stats.pearsonr(x_arr, y_arr)
    return float(result.statistic), float(result.pvalue), int(len(x_arr))


def bootstrap_corr_ci(
    x: Iterable[float],
    y: Iterable[float],
    *,
    seed: int = 20260521,
    n_bootstrap: int = 10000,
    alpha: float = 0.05,
) -> tuple[float, float]:
    x_arr, y_arr = finite_pair(x, y)
    if len(x_arr) < 3:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    values: list[float] = []
    attempts = 0
    while len(values) < n_bootstrap and attempts < n_bootstrap * 4:
        attempts += 1
        idx = rng.integers(0, len(x_arr), len(x_arr))
        x_sample = x_arr[idx]
        y_sample = y_arr[idx]
        if np.std(x_sample) < 1e-12 or np.std(y_sample) < 1e-12:
            continue
        values.append(float(stats.pearsonr(x_sample, y_sample).statistic))
    if not values:
        return float("nan"), float("nan")
    return (
        float(np.percentile(values, 100 * alpha / 2)),
        float(np.percentile(values, 100 * (1 - alpha / 2))),
    )


def format_p(p_value: float) -> str:
    if not np.isfinite(p_value):
        return "NA"
    if p_value < 1e-9:
        return "<1e-9"
    if p_value < 1e-4:
        return f"{p_value:.1e}"
    return f"{p_value:.4f}"
