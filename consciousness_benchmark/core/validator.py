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

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from consciousness_benchmark.core.construct import ColumnConstruct, ConstructResult


@dataclass(frozen=True)
class ValidationReport:
    results: list[ConstructResult]
    n_bootstrap: int
    seed: int

    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        for result in self.results:
            item = asdict(result)
            item["r_95_ci"] = result.r_with_ci
            item["p_formatted"] = result.p_formatted
            rows.append(item)
        return pd.DataFrame(rows)

    def summary_markdown(self) -> str:
        df = self.to_dataframe()
        cols = ["name", "n", "r_95_ci", "p_formatted", "validated", "mechanism", "status"]
        return df[cols].to_markdown(index=False)

    def save(self, out_path: str | Path) -> Path:
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Consciousness Benchmark Reference Validation Report",
            "",
            f"Bootstrap resamples: `{self.n_bootstrap}`",
            f"Seed: `{self.seed}`",
            "",
            self.summary_markdown(),
            "",
        ]
        out.write_text("\n".join(lines), encoding="utf-8")
        self.to_dataframe().to_csv(out.with_suffix(".csv"), index=False)
        return out


class ConstructValidator:
    def __init__(self, constructs: Iterable[ColumnConstruct]):
        self.constructs = list(constructs)

    @classmethod
    def from_reference(cls) -> "ConstructValidator":
        from consciousness_benchmark.constructs.reference import reference_constructs

        return cls(reference_constructs())

    def validate_all(
        self,
        *,
        root: str | Path = ".",
        n_bootstrap: int = 10000,
        seed: int = 20260521,
    ) -> ValidationReport:
        results = [
            construct.validate(root=root, n_bootstrap=n_bootstrap, seed=seed)
            for construct in self.constructs
        ]
        return ValidationReport(results=results, n_bootstrap=n_bootstrap, seed=seed)
