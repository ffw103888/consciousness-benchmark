from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

from consciousness_benchmark import ConstructValidator, reference_constructs


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_reference(args: argparse.Namespace) -> None:
    validator = ConstructValidator(reference_constructs())
    report = validator.validate_all(root=args.root, n_bootstrap=args.bootstrap, seed=args.seed)
    out = report.save(args.out)
    print(f"Saved benchmark reference report to {out}")
    print(report.summary_markdown())


def run_online(args: argparse.Namespace) -> None:
    runner_path = PROJECT_ROOT / "scripts" / "benchmark_online_runner.py"
    if not runner_path.exists():
        raise FileNotFoundError(
            "Online MindLab runner is available only inside the full research workspace. "
            f"Missing: {runner_path}"
        )

    forwarded = [
        str(runner_path),
        "--condition-sets",
        *args.condition_sets,
        "--seeds",
        str(args.seeds),
        "--warmup",
        str(args.warmup),
        "--bootstrap",
        str(args.bootstrap),
        "--output-root",
        str(args.output_root),
        "--save-every",
        str(args.save_every),
    ]
    if args.quick:
        forwarded.append("--quick")

    old_argv = sys.argv[:]
    try:
        sys.argv = forwarded
        runpy.run_path(str(runner_path), run_name="__main__")
    finally:
        sys.argv = old_argv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="consciousness-benchmark",
        description="Operational construct-validation benchmark for artificial systems.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    reference = sub.add_parser("reference", help="Reproduce frozen reference construct statistics.")
    reference.add_argument("--root", type=Path, default=PROJECT_ROOT)
    reference.add_argument("--bootstrap", type=int, default=10000)
    reference.add_argument("--seed", type=int, default=20260521)
    reference.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "docs" / "benchmark_reference_report_20260521.md",
    )
    reference.set_defaults(func=run_reference)

    online = sub.add_parser("online", help="Run a live MindLab online benchmark batch.")
    online.add_argument(
        "--condition-sets",
        nargs="*",
        default=["thalamus", "distributed", "meta-strength"],
        help="Condition sets: thalamus, distributed, meta-strength, meta-noise, meta-delay, all",
    )
    online.add_argument("--seeds", type=int, default=4)
    online.add_argument("--warmup", type=int, default=128)
    online.add_argument("--quick", action="store_true")
    online.add_argument("--bootstrap", type=int, default=10000)
    online.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "runs" / "benchmark_online")
    online.add_argument("--save-every", type=int, default=1)
    online.set_defaults(func=run_online)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
