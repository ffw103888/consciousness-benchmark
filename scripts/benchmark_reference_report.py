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

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from consciousness_benchmark import ConstructValidator, reference_constructs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the benchmark MVP reference validation report.")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260521)
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "docs" / "benchmark_reference_report_20260521.md",
    )
    args = parser.parse_args()

    validator = ConstructValidator(reference_constructs())
    report = validator.validate_all(root=PROJECT_ROOT, n_bootstrap=args.bootstrap, seed=args.seed)
    out = report.save(args.out)
    print(f"Saved benchmark reference report to {out}")
    print(report.summary_markdown())


if __name__ == "__main__":
    main()
