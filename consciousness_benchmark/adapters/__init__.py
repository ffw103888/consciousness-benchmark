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

from consciousness_benchmark.adapters.base import SystemAdapter
from consciousness_benchmark.adapters.mind_lab import (
    MindLabAdapter,
    MindLabCondition,
    all_reference_condition_sets,
    distributed_meta_monitor_delay_conditions,
    distributed_meta_monitor_noise_conditions,
    distributed_meta_monitor_strength_conditions,
    distributed_reference_conditions,
    legacy_smoke_meta_monitor_strength_conditions,
    thalamus_reference_conditions,
)

__all__ = [
    "SystemAdapter",
    "MindLabAdapter",
    "MindLabCondition",
    "all_reference_condition_sets",
    "thalamus_reference_conditions",
    "distributed_reference_conditions",
    "distributed_meta_monitor_strength_conditions",
    "distributed_meta_monitor_noise_conditions",
    "distributed_meta_monitor_delay_conditions",
    "legacy_smoke_meta_monitor_strength_conditions",
]
