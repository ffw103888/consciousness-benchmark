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
