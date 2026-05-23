from __future__ import annotations

from pathlib import Path

from consciousness_benchmark import ConstructValidator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    validator = ConstructValidator.from_reference()
    report = validator.validate_all(root=PROJECT_ROOT, n_bootstrap=2000)
    print(report.summary_markdown())


if __name__ == "__main__":
    main()
