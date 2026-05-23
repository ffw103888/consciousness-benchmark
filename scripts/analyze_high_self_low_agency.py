from __future__ import annotations

import argparse
import json
import math
import pickle
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import convolve2d

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mind_lab.alife import Individual, LeniaLiteEcology
from mind_lab.utils import clamp01, ensure_dir, mask_iou, write_json


def latest_run(root: Path) -> Path:
    latest = root / "latest_run.txt"
    if latest.exists():
        text = latest.read_text(encoding="utf-8").strip()
        if text and Path(text).exists():
            return Path(text)
    runs = [p for p in root.iterdir() if p.is_dir()]
    if not runs:
        raise FileNotFoundError(f"No run directories found under {root}")
    return max(runs, key=lambda p: p.stat().st_mtime)


def copy_and_load_checkpoint(run_dir: Path, out_dir: Path, retries: int = 5) -> dict[str, Any]:
    source = run_dir / "checkpoint.pkl"
    if not source.exists():
        raise FileNotFoundError(source)
    target = out_dir / "checkpoint_snapshot.pkl"
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            shutil.copy2(source, target)
            with target.open("rb") as f:
                return pickle.load(f)
        except Exception as exc:
            last_error = exc
            time.sleep(1.0)
    raise RuntimeError(f"Could not load a stable checkpoint copy: {last_error}")


def extract_alife_samples(checkpoint: dict[str, Any], self_threshold: float, agency_threshold: float) -> pd.DataFrame:
    alife = checkpoint["systems"].get("alife")
    if alife is None:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for cell, entry in alife.archive.archive.items():
        consciousness = entry.get("consciousness", {})
        components = entry.get("components", {})
        self_model_proxy = float(consciousness.get("self_other_boundary", 0.0))
        agency_proxy = float(components.get("ecological_coupling", 0.0))
        row = {
            "cell": repr(cell),
            "individual_id": entry["individual"].individual_id,
            "generation": entry["individual"].generation,
            "fitness": float(entry.get("fitness", 0.0)),
            "self_model_proxy": self_model_proxy,
            "agency_proxy": agency_proxy,
            "temporal_continuity": float(consciousness.get("temporal_continuity", 0.0)),
            "phi_proxy": float(consciousness.get("phi_proxy", 0.0)),
            "pci_proxy": float(consciousness.get("pci_proxy", 0.0)),
            "boundary_stability": float(components.get("boundary_stability", 0.0)),
            "perturbation_recovery": float(components.get("perturbation_recovery", 0.0)),
            "resource_homeostasis": float(components.get("resource_homeostasis", 0.0)),
            "structural_diversity": float(components.get("structural_diversity", 0.0)),
            "ecological_coupling": float(components.get("ecological_coupling", 0.0)),
            "is_high_self_low_agency": self_model_proxy >= self_threshold and agency_proxy <= agency_threshold,
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["separation"] = df["self_model_proxy"] - df["agency_proxy"]
    df = df.sort_values(["is_high_self_low_agency", "separation", "self_model_proxy", "fitness"], ascending=False)
    return df


def selected_individuals(checkpoint: dict[str, Any], selected_ids: set[str]) -> dict[str, Individual]:
    alife = checkpoint["systems"].get("alife")
    result: dict[str, Individual] = {}
    if alife is None:
        return result
    for entry in alife.archive.archive.values():
        individual = entry["individual"]
        if individual.individual_id in selected_ids:
            result[individual.individual_id] = individual
    return result


def lenia_step(state: np.ndarray, ecology: LeniaLiteEcology, individual: Individual, kernel: np.ndarray, t: int, rng: np.random.Generator) -> np.ndarray:
    resource = ecology.resource_field(t, rng)
    potential = convolve2d(state, kernel, mode="same", boundary="wrap")
    genome = individual.genome
    growth = 2.0 * np.exp(-((potential - genome.growth_mu) ** 2) / (2 * genome.growth_sigma**2)) - 1.0
    return np.clip(state + genome.dt * growth * resource, 0.0, 1.0).astype(np.float32)


def simulate_frames(individual: Individual, world_size: int, steps: int, seed: int, perturb: bool = True) -> list[np.ndarray]:
    ecology = LeniaLiteEcology(world_size=world_size, eval_steps=steps, record_stride=1)
    rng = np.random.default_rng(seed)
    state = ecology.initial_state(individual.genome, rng)
    kernel = ecology.kernel(individual.genome)
    frames: list[np.ndarray] = []
    for t in range(steps):
        state = lenia_step(state, ecology, individual, kernel, t, rng)
        if perturb and t == steps // 2:
            n = world_size
            half = max(2, n // 10)
            cx, cy = n // 2, n // 2
            state[max(0, cy - half) : min(n, cy + half), max(0, cx - half) : min(n, cx + half)] *= 0.15
        frames.append(state.copy())
    return frames


def frames_to_gif(frames: list[np.ndarray], path: Path, fps: int = 18) -> None:
    cmap = plt.get_cmap("viridis")
    images = []
    for frame in frames:
        norm = np.clip(frame, 0.0, 1.0)
        rgba = cmap(norm)
        rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
        images.append(rgb)
    imageio.mimsave(path, images, fps=fps)


def detailed_agency_proxy(individual: Individual, world_size: int, seed: int) -> dict[str, float]:
    steps = 96
    natural = simulate_frames(individual, world_size, steps, seed, perturb=False)
    perturbed = simulate_frames(individual, world_size, steps, seed, perturb=True)

    pre = steps // 2 - 1
    post = steps // 2 + 8
    natural_delta = np.linalg.norm(natural[post] - natural[pre])
    external_delta = np.linalg.norm(perturbed[post] - natural[post])
    external_detectability = clamp01(float(external_delta / (natural_delta + external_delta + 1e-9)))

    natural_ious = [mask_iou(a > 0.1, b > 0.1) for a, b in zip(natural[:-1], natural[1:])]
    perturbed_ious = [mask_iou(a > 0.1, b > 0.1) for a, b in zip(perturbed[:-1], perturbed[1:])]
    self_predictability = float(np.mean(natural_ious)) if natural_ious else 0.0
    perturbation_drop = max(0.0, float(np.mean(natural_ious[pre : pre + 12]) - np.mean(perturbed_ious[pre : pre + 12])))

    natural_mass = np.array([np.sum(x) for x in natural], dtype=float)
    perturbed_mass = np.array([np.sum(x) for x in perturbed], dtype=float)
    recovery = 1.0 - min(float(abs(perturbed_mass[-1] - natural_mass[-1]) / (abs(natural_mass[-1]) + 1e-9)), 1.0)

    return {
        "self_predictability": clamp01(self_predictability),
        "external_detectability": external_detectability,
        "perturbation_signature": clamp01(perturbation_drop * 5.0),
        "post_perturbation_recovery": clamp01(recovery),
        "agency_detail_proxy": clamp01(0.35 * self_predictability + 0.35 * external_detectability + 0.3 * recovery),
    }


def summarize_system_anomalies(checkpoint: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record in checkpoint.get("evaluation_history", []):
        cycle = record.get("cycle")
        systems = record.get("evaluation", {}).get("systems", {})
        for name, payload in systems.items():
            scores = payload.get("scores", {})
            rows.append(
                {
                    "cycle": cycle,
                    "system": name,
                    "state": scores.get("state", 0.0),
                    "content": scores.get("content", 0.0),
                    "self_model": scores.get("self_model", 0.0),
                    "agency": scores.get("agency", 0.0),
                    "temporal_continuity": scores.get("temporal_continuity", 0.0),
                    "separation": scores.get("self_model", 0.0) - scores.get("agency", 0.0),
                    "high_self_low_agency": scores.get("self_model", 0.0) > 0.9 and scores.get("agency", 1.0) < 0.3,
                }
            )
    return pd.DataFrame(rows)


def plot_scatter(df: pd.DataFrame, out_path: Path) -> None:
    if df.empty:
        return
    plt.figure(figsize=(8, 6))
    colors = np.where(df["is_high_self_low_agency"], "tab:red", "tab:blue")
    plt.scatter(df["self_model_proxy"], df["agency_proxy"], c=colors, s=12, alpha=0.55)
    plt.axvline(0.9, color="tab:red", linestyle="--", linewidth=1)
    plt.axhline(0.5, color="tab:red", linestyle="--", linewidth=1)
    plt.xlabel("ALife self-model proxy (boundary/self-other)")
    plt.ylabel("ALife agency proxy (ecological coupling)")
    plt.title("High-self / low-agency candidates in ALife archive")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze high-self / low-agency patterns.")
    parser.add_argument("--root", default="runs")
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--self-threshold", type=float, default=0.9)
    parser.add_argument("--agency-threshold", type=float, default=0.5)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--gif-count", type=int, default=3)
    parser.add_argument("--gif-steps", type=int, default=180)
    parser.add_argument("--world-size", type=int, default=72)
    args = parser.parse_args()

    root = Path(args.root)
    run_dir = Path(args.run_dir) if args.run_dir else latest_run(root)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = ensure_dir(run_dir / "analysis" / f"high_self_low_agency_{stamp}")

    checkpoint = copy_and_load_checkpoint(run_dir, out_dir)
    cycle = checkpoint.get("cycle")
    df = extract_alife_samples(checkpoint, args.self_threshold, args.agency_threshold)
    if df.empty:
        raise RuntimeError("No ALife archive entries found in checkpoint.")

    all_csv = out_dir / "alife_archive_self_agency.csv"
    candidates_csv = out_dir / "alife_high_self_low_agency_candidates.csv"
    df.to_csv(all_csv, index=False, encoding="utf-8-sig")
    candidates = df[df["is_high_self_low_agency"]].copy()
    candidates.to_csv(candidates_csv, index=False, encoding="utf-8-sig")
    plot_scatter(df, out_dir / "alife_self_vs_agency_scatter.png")

    systems_df = summarize_system_anomalies(checkpoint)
    if not systems_df.empty:
        systems_df.to_csv(out_dir / "system_level_self_agency_timeseries.csv", index=False, encoding="utf-8-sig")

    top_candidates = candidates.head(args.top)
    ids = set(top_candidates["individual_id"].tolist())
    individuals = selected_individuals(checkpoint, ids)
    detail_rows: list[dict[str, Any]] = []
    for rank, row in enumerate(top_candidates.itertuples(index=False), start=1):
        individual = individuals.get(row.individual_id)
        if individual is None:
            continue
        detail = detailed_agency_proxy(individual, args.world_size, seed=20260520 + rank)
        detail_rows.append({"rank": rank, "individual_id": row.individual_id, **detail})
        if rank <= args.gif_count:
            frames = simulate_frames(individual, args.world_size, args.gif_steps, seed=20260520 + rank, perturb=True)
            frames_to_gif(frames, out_dir / f"candidate_{rank:02d}_{row.individual_id}.gif")

    details_df = pd.DataFrame(detail_rows)
    if not details_df.empty:
        details_df.to_csv(out_dir / "detailed_agency_proxy_tests.csv", index=False, encoding="utf-8-sig")

    system_summary = {}
    if not systems_df.empty:
        latest = systems_df[systems_df["cycle"] == systems_df["cycle"].max()]
        system_summary = {
            row["system"]: {
                "self_model": float(row["self_model"]),
                "agency": float(row["agency"]),
                "separation": float(row["separation"]),
                "high_self_low_agency": bool(row["high_self_low_agency"]),
            }
            for _, row in latest.iterrows()
        }

    summary = {
        "run_dir": str(run_dir),
        "analysis_dir": str(out_dir),
        "checkpoint_cycle": cycle,
        "archive_entries": int(len(df)),
        "alife_high_self_low_agency_count": int(len(candidates)),
        "thresholds": {
            "self_model_proxy_min": args.self_threshold,
            "agency_proxy_max": args.agency_threshold,
        },
        "top_candidates": top_candidates.head(args.top).to_dict(orient="records"),
        "system_level_latest": system_summary,
        "files": {
            "all_archive_csv": str(all_csv),
            "candidates_csv": str(candidates_csv),
            "details_csv": str(out_dir / "detailed_agency_proxy_tests.csv"),
            "scatter": str(out_dir / "alife_self_vs_agency_scatter.png"),
        },
        "interpretation_note": (
            "ALife self_model_proxy maps to self_other_boundary/boundary stability; "
            "ALife agency_proxy maps to ecological coupling. System-level thalamus "
            "high-self/low-agency is a separate evaluator-level phenomenon."
        ),
    }
    write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
