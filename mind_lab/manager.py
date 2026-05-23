from __future__ import annotations

import pickle
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .alife import EvolutionEngine
from .distributed import DistributedArchitecture
from .evaluation import ConsciousnessEvaluator
from .safety import EthicsReviewSystem, SafetyMonitor, conservative_pain_proxy
from .thalamus import ThalamusInspiredArchitecture
from .utils import (
    JsonlLogger,
    choose_worker_count,
    ensure_dir,
    hardware_profile,
    jsonable,
    now_iso,
    set_global_seed,
    write_json,
)


def default_config(mode: str = "night", seed: int = 20260520) -> dict[str, Any]:
    profile = hardware_profile()
    workers = choose_worker_count(profile)
    if mode == "smoke":
        alife_batch = 8
        alife_cycle = 8
        dist_steps = 16
        thal_steps = 16
        world = 48
        eval_steps = 36
        max_cycles = 2
    elif mode == "quick":
        alife_batch = 24
        alife_cycle = 48
        dist_steps = 96
        thal_steps = 128
        world = 64
        eval_steps = 72
        max_cycles = 8
    else:
        alife_batch = 64
        alife_cycle = 256
        dist_steps = 320
        thal_steps = 384
        world = 72
        eval_steps = 96
        max_cycles = None

    return {
        "id": f"mind_lab_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "mode": mode,
        "seed": seed,
        "sandboxed": True,
        "data_protection": True,
        "termination_conditions": {
            "max_cycles": max_cycles,
            "stop_file": "stop.flag",
            "wall_clock_deadline": None,
        },
        "hardware": profile,
        "paths": ["alife", "distributed", "thalamus"],
        "cycle": {
            "alife_generations": alife_cycle,
            "distributed_steps": dist_steps,
            "thalamus_steps": thal_steps,
            "checkpoint_every_cycles": 4 if mode != "smoke" else 1,
        },
        "alife": {
            "world_size": world,
            "eval_steps": eval_steps,
            "record_stride": 3,
            "behavior_dimensions": 4,
            "bins_per_dimension": 20 if mode != "smoke" else 8,
            "mutation_rate": 0.18,
            "mutation_strength": 0.075,
            "batch_size": alife_batch,
            "workers": 1 if mode == "smoke" else workers,
        },
        "distributed": {
            "num_agents": 12 if mode != "smoke" else 5,
            "world_size": 52 if mode != "smoke" else 28,
            "sensor_range": 6 if mode != "smoke" else 4,
            "memory_capacity": 512,
        },
        "thalamus": {
            "workspace_capacity": 96 if mode != "smoke" else 32,
            "initial_threshold": 0.52,
            "inhibition_strength": 0.45,
            "threshold_adaptation_rate": 0.08,
            "dim": 32,
        },
    }


class ExperimentManager:
    def __init__(self, config: dict[str, Any], run_dir: str | Path):
        self.config = config
        self.run_dir = ensure_dir(run_dir)
        self.logger = JsonlLogger(self.run_dir / "events.jsonl")
        self.evaluator = ConsciousnessEvaluator()
        self.safety = SafetyMonitor()
        self.ethics = EthicsReviewSystem()
        self.seed = int(config.get("seed", 1))
        self.rng = set_global_seed(self.seed)
        self.systems: dict[str, Any] = {}
        self.status = "NOT_STARTED"
        self.cycle = 0
        self.evaluation_history: list[dict[str, Any]] = []

    def initialize(self) -> None:
        review = self.ethics.review_experiment_design(self.config)
        write_json(self.run_dir / "ethics_review.json", self.ethics.review_history)
        if not review["approved"]:
            self.status = "REJECTED"
            raise RuntimeError(f"Experiment rejected by ethics review: {review['concerns']}")
        paths = set(self.config.get("paths", ["alife", "distributed", "thalamus"]))
        if "alife" in paths:
            self.systems["alife"] = EvolutionEngine(self.config["alife"], seed=self.seed + 11)
        if "distributed" in paths:
            self.systems["distributed"] = DistributedArchitecture(self.config["distributed"], seed=self.seed + 22)
        if "thalamus" in paths:
            self.systems["thalamus"] = ThalamusInspiredArchitecture(self.config["thalamus"], seed=self.seed + 33)
        write_json(self.run_dir / "config.json", self.config)
        self.logger.event("initialized", systems=list(self.systems), hardware=self.config.get("hardware", {}))

    def run(self, deadline_epoch: float | None = None) -> dict[str, Any]:
        if not self.systems:
            self.initialize()
        self.status = "RUNNING"
        stop_file = self.run_dir / self.config.get("termination_conditions", {}).get("stop_file", "stop.flag")
        termination = self.config.get("termination_conditions", {})
        max_cycles = termination.get("max_cycles")
        target_alife_coverage = termination.get("target_alife_coverage")
        checkpoint_every = int(self.config.get("cycle", {}).get("checkpoint_every_cycles", 4))
        self.logger.event("run_started", deadline_epoch=deadline_epoch)

        try:
            while True:
                if stop_file.exists():
                    self.status = "STOPPED_BY_FILE"
                    self.logger.event("stop_file_seen", path=stop_file)
                    break
                if deadline_epoch is not None and time.time() >= deadline_epoch:
                    self.status = "COMPLETED_DEADLINE"
                    self.logger.event("deadline_reached")
                    break
                if max_cycles is not None and self.cycle >= int(max_cycles):
                    self.status = "COMPLETED_MAX_CYCLES"
                    self.logger.event("max_cycles_reached", max_cycles=max_cycles)
                    break
                if target_alife_coverage is not None and "alife" in self.systems:
                    coverage = float(self.systems["alife"].archive.stats.get("coverage", 0.0))
                    if coverage >= float(target_alife_coverage):
                        self.status = "COMPLETED_TARGET_COVERAGE"
                        self.logger.event(
                            "target_alife_coverage_reached",
                            coverage=coverage,
                            target_alife_coverage=float(target_alife_coverage),
                        )
                        break

                cycle_result = self.run_cycle()
                self.logger.event("cycle_completed", **cycle_result)
                self.write_live_status(cycle_result)
                if self.cycle % checkpoint_every == 0:
                    self.save_checkpoint()
                    self.generate_visualizations()

                if cycle_result["safety"]["status"] == "CRITICAL":
                    self.status = "TERMINATED_SAFETY"
                    self.logger.event("safety_terminated", safety=cycle_result["safety"])
                    break
        except KeyboardInterrupt:
            self.status = "INTERRUPTED"
            self.logger.event("interrupted")
        except Exception as exc:
            self.status = "ERROR"
            self.logger.event("error", error=repr(exc))
            raise
        finally:
            for system in self.systems.values():
                if hasattr(system, "shutdown"):
                    system.shutdown()

        report = self.final_report()
        write_json(self.run_dir / "final_report.json", report)
        write_json(
            self.run_dir / "live_status.json",
            {
                "time": now_iso(),
                "status": self.status,
                "cycle": self.cycle,
                "final_report": report,
                "latest": self.evaluation_history[-1] if self.evaluation_history else None,
                "run_dir": str(self.run_dir),
            },
        )
        write_json(self.run_dir / "safety_log.json", self.safety.alert_history)
        write_json(self.run_dir / "ethics_review.json", self.ethics.review_history)
        self.generate_visualizations()
        self.logger.event("run_finished", status=self.status)
        return report

    def run_cycle(self) -> dict[str, Any]:
        self.cycle += 1
        started = time.time()
        cycle_cfg = self.config.get("cycle", {})
        path_results: dict[str, Any] = {}

        if "alife" in self.systems:
            path_results["alife"] = self.systems["alife"].run_chunk(int(cycle_cfg.get("alife_generations", 128)))
        if "distributed" in self.systems:
            path_results["distributed"] = self.systems["distributed"].run_steps(int(cycle_cfg.get("distributed_steps", 128)))
        if "thalamus" in self.systems:
            path_results["thalamus"] = self.systems["thalamus"].run_steps(int(cycle_cfg.get("thalamus_steps", 128)))

        evaluation = self.evaluator.evaluate(self.systems)
        recommendations = self.evaluator.recommendations(evaluation)
        measurements = self.aggregate_measurements()
        measurements["pain_proxy"] = conservative_pain_proxy(measurements)
        safety = self.safety.monitor(measurements)
        record = {
            "cycle": self.cycle,
            "elapsed_seconds": time.time() - started,
            "path_results": path_results,
            "evaluation": evaluation,
            "recommendations": recommendations,
            "measurements": measurements,
            "safety": safety,
        }
        self.evaluation_history.append(record)
        return record

    def aggregate_measurements(self) -> dict[str, float]:
        system_measurements = [
            system.system_measurements()
            for system in self.systems.values()
            if hasattr(system, "system_measurements")
        ]
        keys = sorted({k for m in system_measurements for k in m.keys()})
        aggregate = {
            key: float(np.mean([float(m.get(key, 0.0)) for m in system_measurements]))
            for key in keys
            if all(np.isscalar(m.get(key, 0.0)) for m in system_measurements)
        }
        return aggregate

    def write_live_status(self, cycle_result: dict[str, Any]) -> None:
        payload = {
            "time": now_iso(),
            "status": self.status,
            "cycle": self.cycle,
            "latest": cycle_result,
            "run_dir": str(self.run_dir),
        }
        write_json(self.run_dir / "live_status.json", payload)

    def save_checkpoint(self) -> None:
        path = self.run_dir / "checkpoint.pkl"
        with path.open("wb") as f:
            pickle.dump(
                {
                    "cycle": self.cycle,
                    "status": self.status,
                    "systems": self.systems,
                    "evaluation_history": self.evaluation_history,
                    "config": self.config,
                },
                f,
            )
        if "alife" in self.systems:
            write_json(self.run_dir / "alife_archive_summary.json", self.systems["alife"].archive.summary())

    def final_report(self) -> dict[str, Any]:
        report = {
            "experiment_id": self.config.get("id"),
            "status": self.status,
            "run_dir": str(self.run_dir),
            "cycles": self.cycle,
            "started_mode": self.config.get("mode"),
            "hardware": self.config.get("hardware", {}),
            "summary": {},
            "latest_evaluation": None,
            "anomalies": [],
            "conclusions": [],
        }
        if not self.evaluation_history:
            return report

        latest = self.evaluation_history[-1]["evaluation"]
        report["latest_evaluation"] = latest
        dims = list(latest["aggregate"]["scores"].keys())
        for dim in dims:
            series = [record["evaluation"]["aggregate"]["scores"][dim] for record in self.evaluation_history]
            report["summary"][dim] = {
                "mean": float(np.mean(series)),
                "std": float(np.std(series)),
                "min": float(np.min(series)),
                "max": float(np.max(series)),
                "final": float(series[-1]),
            }
        for record in self.evaluation_history:
            report["anomalies"].extend(record["evaluation"]["aggregate"].get("anomalies", []))
        report["conclusions"] = self.generate_conclusions(report)
        return report

    def generate_conclusions(self, report: dict[str, Any]) -> list[dict[str, str]]:
        if not report["summary"]:
            return []
        scores = {dim: data["mean"] for dim, data in report["summary"].items()}
        best = max(scores, key=scores.get)
        weakest = min(scores, key=scores.get)
        conclusions = [
            {
                "type": "dimension_profile",
                "message": f"Best mean proxy dimension: {best} ({scores[best]:.3f}); weakest: {weakest} ({scores[weakest]:.3f}).",
            }
        ]
        if len(self.evaluation_history) >= 2:
            first = self.evaluation_history[0]["evaluation"]["aggregate"]["scores"]
            last = self.evaluation_history[-1]["evaluation"]["aggregate"]["scores"]
            improved = [dim for dim in first if last[dim] - first[dim] > 0.08]
            declined = [dim for dim in first if first[dim] - last[dim] > 0.08]
            if improved:
                conclusions.append({"type": "improvement", "message": "Improved dimensions: " + ", ".join(improved)})
            if declined:
                conclusions.append({"type": "decline", "message": "Declined dimensions: " + ", ".join(declined)})
        if report["anomalies"]:
            counts: dict[str, int] = {}
            for anomaly in report["anomalies"]:
                counts[anomaly["type"]] = counts.get(anomaly["type"], 0) + 1
            common = max(counts, key=counts.get)
            conclusions.append({"type": "anomaly_pattern", "message": f"Most common anomaly: {common} ({counts[common]} times)."})
        return conclusions

    def generate_visualizations(self) -> None:
        if not self.evaluation_history:
            return
        plot_dir = ensure_dir(self.run_dir / "plots")
        cycles = [r["cycle"] for r in self.evaluation_history]
        dims = list(self.evaluation_history[-1]["evaluation"]["aggregate"]["scores"].keys())

        plt.figure(figsize=(10, 5.8))
        for dim in dims:
            values = [r["evaluation"]["aggregate"]["scores"][dim] for r in self.evaluation_history]
            plt.plot(cycles, values, marker="o", markersize=3, label=dim)
        plt.xlabel("Cycle")
        plt.ylabel("Proxy score")
        plt.title("Five-dimensional aggregate profile")
        plt.ylim(0, 1)
        plt.grid(True, alpha=0.25)
        plt.legend()
        plt.tight_layout()
        plt.savefig(plot_dir / "dimensions_over_time.png", dpi=150)
        plt.close()

        if "alife" in self.systems:
            stats = [r["path_results"].get("alife", {}).get("archive", {}) for r in self.evaluation_history]
            coverage = [s.get("coverage", 0.0) for s in stats]
            max_fit = [s.get("max_fitness", 0.0) for s in stats]
            plt.figure(figsize=(10, 5.2))
            plt.plot(cycles, coverage, label="archive coverage")
            plt.twinx()
            plt.plot(cycles, max_fit, color="tab:orange", label="max fitness")
            plt.title("ALife archive progress")
            plt.tight_layout()
            plt.savefig(plot_dir / "alife_archive_progress.png", dpi=150)
            plt.close()


def run_from_config(config: dict[str, Any], output_root: str | Path, deadline_epoch: float | None = None) -> dict[str, Any]:
    run_id = str(config.get("id") or f"mind_lab_{int(time.time())}")
    run_dir = ensure_dir(Path(output_root) / run_id)
    manager = ExperimentManager(config, run_dir)
    return manager.run(deadline_epoch=deadline_epoch)
