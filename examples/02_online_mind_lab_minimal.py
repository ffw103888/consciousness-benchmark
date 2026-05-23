from __future__ import annotations

import subprocess
import sys


def main() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "consciousness_benchmark",
            "online",
            "--condition-sets",
            "thalamus",
            "--seeds",
            "1",
            "--warmup",
            "32",
            "--quick",
            "--bootstrap",
            "500",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
