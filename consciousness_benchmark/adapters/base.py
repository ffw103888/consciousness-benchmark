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

from typing import Any, Protocol


class SystemAdapter(Protocol):
    """Minimal protocol for future online benchmark adapters."""

    def get_internal_state(self) -> Any:
        ...

    def act(self, observation: Any) -> Any:
        ...

    def observe(self, result: Any) -> None:
        ...
