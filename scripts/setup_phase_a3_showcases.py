#!/usr/bin/env python3
"""Create Phase A-3 showcase workspaces under sandbox/."""

from __future__ import annotations

import argparse
from pathlib import Path

from consciousness_benchmark.showcase_scenarios import (
    setup_autonomy_showcase,
    setup_curiosity_showcase,
    setup_surprise_showcase,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up Phase A-3 showcase sandboxes")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("sandbox"),
        help="Sandbox root directory",
    )
    args = parser.parse_args()

    root = args.root
    setup_curiosity_showcase(root / "showcase_curiosity")
    setup_surprise_showcase(root / "showcase_surprise")
    setup_autonomy_showcase(root / "showcase_autonomy")

    print(f"Created showcases under {root.resolve()}:")
    print(f"  - {root / 'showcase_curiosity'}")
    print(f"  - {root / 'showcase_surprise'}")
    print(f"  - {root / 'showcase_autonomy'}")


if __name__ == "__main__":
    main()
