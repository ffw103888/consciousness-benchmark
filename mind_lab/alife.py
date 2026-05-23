from __future__ import annotations

import math
import time
import uuid
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy import ndimage
from scipy.signal import convolve2d

from .utils import (
    activity_summary,
    binary_lz_complexity,
    clamp01,
    entropy,
    mask_centroid,
    mask_iou,
    power_law_score,
    safe_corr,
)


@dataclass
class LeniaGenome:
    kernel_radius: int
    growth_mu: float
    growth_sigma: float
    dt: float
    seed_blobs: list[tuple[float, float, float, float]]
    kernel_beta: tuple[float, float, float] = (1.0, 0.35, 0.15)
    seed_noise: float = 0.03


@dataclass
class Individual:
    genome: LeniaGenome
    individual_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    parent_id: str | None = None
    generation: int = 0


@dataclass
class Trajectory:
    states: list[np.ndarray]
    resource_trace: list[float]
    perturbation_index: int
    activity_trace: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


def random_genome(rng: np.random.Generator, world_size: int) -> LeniaGenome:
    radius = int(rng.integers(max(4, world_size // 18), max(6, world_size // 8)))
    blobs: list[tuple[float, float, float, float]] = []
    for _ in range(int(rng.integers(2, 6))):
        blobs.append(
            (
                float(rng.uniform(0.35, 0.65)),
                float(rng.uniform(0.35, 0.65)),
                float(rng.uniform(0.035, 0.12)),
                float(rng.uniform(0.25, 1.0)),
            )
        )
    return LeniaGenome(
        kernel_radius=radius,
        growth_mu=float(rng.uniform(0.12, 0.35)),
        growth_sigma=float(rng.uniform(0.018, 0.075)),
        dt=float(rng.uniform(0.07, 0.18)),
        seed_blobs=blobs,
        kernel_beta=(
            float(rng.uniform(0.6, 1.2)),
            float(rng.uniform(0.1, 0.7)),
            float(rng.uniform(0.0, 0.4)),
        ),
        seed_noise=float(rng.uniform(0.0, 0.06)),
    )


class MutationOperators:
    def __init__(self, mutation_rate: float = 0.18, mutation_strength: float = 0.08):
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength

    def mutate(self, parent: Individual, rng: np.random.Generator, generation: int) -> Individual:
        g = parent.genome
        blobs = [tuple(blob) for blob in g.seed_blobs]

        def jitter(value: float, low: float, high: float, scale: float = 1.0) -> float:
            if rng.random() < self.mutation_rate:
                value += float(rng.normal(0.0, self.mutation_strength * scale))
            return float(np.clip(value, low, high))

        kernel_radius = g.kernel_radius
        if rng.random() < self.mutation_rate:
            kernel_radius = int(np.clip(kernel_radius + rng.integers(-2, 3), 3, 24))

        growth_mu = jitter(g.growth_mu, 0.04, 0.55, 1.1)
        growth_sigma = jitter(g.growth_sigma, 0.006, 0.18, 0.35)
        dt = jitter(g.dt, 0.025, 0.28, 0.7)
        beta = tuple(jitter(float(v), 0.0, 1.4, 0.8) for v in g.kernel_beta)
        seed_noise = jitter(g.seed_noise, 0.0, 0.12, 0.35)

        mutated_blobs: list[tuple[float, float, float, float]] = []
        for x, y, sigma, amp in blobs:
            mutated_blobs.append(
                (
                    jitter(x, 0.15, 0.85, 0.7),
                    jitter(y, 0.15, 0.85, 0.7),
                    jitter(sigma, 0.015, 0.18, 0.28),
                    jitter(amp, 0.05, 1.25, 1.2),
                )
            )
        if rng.random() < self.mutation_rate * 0.35 and len(mutated_blobs) < 8:
            mutated_blobs.append(
                (
                    float(rng.uniform(0.25, 0.75)),
                    float(rng.uniform(0.25, 0.75)),
                    float(rng.uniform(0.025, 0.13)),
                    float(rng.uniform(0.1, 1.0)),
                )
            )
        if rng.random() < self.mutation_rate * 0.2 and len(mutated_blobs) > 1:
            mutated_blobs.pop(int(rng.integers(0, len(mutated_blobs))))

        child = Individual(
            genome=LeniaGenome(
                kernel_radius=kernel_radius,
                growth_mu=growth_mu,
                growth_sigma=growth_sigma,
                dt=dt,
                seed_blobs=mutated_blobs,
                kernel_beta=beta,
                seed_noise=seed_noise,
            ),
            parent_id=parent.individual_id,
            generation=generation,
        )
        return child


class LeniaLiteEcology:
    def __init__(self, world_size: int = 72, eval_steps: int = 96, record_stride: int = 3):
        self.world_size = int(world_size)
        self.eval_steps = int(eval_steps)
        self.record_stride = max(1, int(record_stride))

    def kernel(self, genome: LeniaGenome) -> np.ndarray:
        r = int(genome.kernel_radius)
        y, x = np.ogrid[-r : r + 1, -r : r + 1]
        d = np.sqrt(x * x + y * y) / max(r, 1)
        shell = np.zeros_like(d, dtype=float)
        centers = (0.25, 0.55, 0.85)
        widths = (0.12, 0.14, 0.17)
        for beta, center, width in zip(genome.kernel_beta, centers, widths):
            shell += beta * np.exp(-((d - center) ** 2) / (2 * width**2))
        shell[d > 1.0] = 0.0
        total = float(shell.sum())
        if total <= 1e-9:
            shell[r, r] = 1.0
            total = 1.0
        return (shell / total).astype(np.float32)

    def initial_state(self, genome: LeniaGenome, rng: np.random.Generator) -> np.ndarray:
        n = self.world_size
        yy, xx = np.mgrid[0:n, 0:n]
        state = np.zeros((n, n), dtype=np.float32)
        for x0, y0, sigma, amp in genome.seed_blobs:
            cx = x0 * (n - 1)
            cy = y0 * (n - 1)
            scale = max(sigma * n, 1.0)
            state += amp * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * scale**2))
        if genome.seed_noise > 0:
            state += rng.normal(0.0, genome.seed_noise, size=(n, n)).astype(np.float32)
        return np.clip(state, 0.0, 1.0).astype(np.float32)

    def resource_field(self, t: int, rng: np.random.Generator) -> np.ndarray:
        n = self.world_size
        yy, xx = np.mgrid[0:n, 0:n]
        phase = t / max(self.eval_steps, 1) * 2 * np.pi
        field = 0.75 + 0.2 * np.sin((xx / n) * 2 * np.pi + phase) + 0.12 * np.cos((yy / n) * 4 * np.pi - phase)
        field += 0.03 * rng.normal(size=(n, n))
        return np.clip(field, 0.25, 1.15).astype(np.float32)

    def simulate(self, individual: Individual, seed: int, steps: int | None = None) -> Trajectory:
        rng = np.random.default_rng(seed)
        steps = int(steps or self.eval_steps)
        state = self.initial_state(individual.genome, rng)
        kernel = self.kernel(individual.genome)
        states: list[np.ndarray] = []
        resource_trace: list[float] = []
        activity_trace: list[float] = []
        perturb_at = max(5, steps // 2)
        n = self.world_size

        for t in range(steps):
            resource = self.resource_field(t, rng)
            potential = convolve2d(state, kernel, mode="same", boundary="wrap")
            growth = 2.0 * np.exp(-((potential - individual.genome.growth_mu) ** 2) / (2 * individual.genome.growth_sigma**2)) - 1.0
            state = np.clip(state + individual.genome.dt * growth * resource, 0.0, 1.0).astype(np.float32)

            if t == perturb_at:
                cx = int(rng.integers(n // 4, 3 * n // 4))
                cy = int(rng.integers(n // 4, 3 * n // 4))
                half = max(2, n // 10)
                state[max(0, cy - half) : min(n, cy + half), max(0, cx - half) : min(n, cx + half)] *= 0.15

            active_mask = state > 0.1
            if active_mask.any():
                resource_trace.append(float(np.mean(resource[active_mask])))
            else:
                resource_trace.append(0.0)
            activity_trace.append(float(np.mean(active_mask)))

            if t % self.record_stride == 0 or t == steps - 1 or t == perturb_at:
                states.append(state.copy())

        perturb_index = min(len(states) - 1, max(0, perturb_at // self.record_stride))
        return Trajectory(
            states=states,
            resource_trace=resource_trace,
            perturbation_index=perturb_index,
            activity_trace=activity_trace,
            metadata={"steps": steps, "record_stride": self.record_stride},
        )


class FitnessEvaluator:
    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or {
            "boundary_stability": 0.22,
            "perturbation_recovery": 0.22,
            "resource_homeostasis": 0.18,
            "structural_diversity": 0.2,
            "ecological_coupling": 0.18,
        }

    def evaluate(self, trajectory: Trajectory) -> tuple[float, dict[str, float]]:
        components = {
            "boundary_stability": self.boundary_stability(trajectory),
            "perturbation_recovery": self.perturbation_recovery(trajectory),
            "resource_homeostasis": self.resource_homeostasis(trajectory),
            "structural_diversity": self.structural_diversity(trajectory),
            "ecological_coupling": self.ecological_coupling(trajectory),
        }
        weight_sum = sum(self.weights.get(k, 0.0) for k in components) or 1.0
        fitness = sum(components[k] * self.weights.get(k, 0.0) for k in components) / weight_sum
        mass = float(np.mean([np.sum(s) for s in trajectory.states])) if trajectory.states else 0.0
        viability = clamp01(mass / (trajectory.states[-1].size * 0.18)) if trajectory.states else 0.0
        fitness = clamp01(0.82 * fitness + 0.18 * viability)
        return fitness, components

    def boundary_stability(self, trajectory: Trajectory) -> float:
        if len(trajectory.states) < 2:
            return 0.0
        start = trajectory.states[max(0, min(2, len(trajectory.states) - 1))] > 0.1
        end = trajectory.states[-1] > 0.1
        area_start = float(start.sum())
        area_end = float(end.sum())
        if area_start < 8 or area_end < 8:
            return 0.0
        area_ratio = min(area_start, area_end) / max(area_start, area_end)
        centroid_shift = np.linalg.norm(mask_centroid(start) - mask_centroid(end))
        shift_score = math.exp(-centroid_shift / max(start.shape))
        iou = mask_iou(ndimage.binary_dilation(start, iterations=2), ndimage.binary_dilation(end, iterations=2))
        return clamp01(0.35 * area_ratio + 0.35 * shift_score + 0.3 * iou)

    def perturbation_recovery(self, trajectory: Trajectory) -> float:
        states = trajectory.states
        if len(states) < 6:
            return 0.0
        p = int(np.clip(trajectory.perturbation_index, 1, len(states) - 2))
        pre = states[max(0, p - 2) : p]
        post = states[p + 1 :]
        if not pre or not post:
            return 0.0
        target_mass = float(np.mean([np.sum(s) for s in pre]))
        if target_mass <= 1e-9:
            return 0.0
        scores = []
        for idx, s in enumerate(post):
            mass_score = 1.0 - min(abs(float(np.sum(s)) - target_mass) / target_mass, 1.0)
            active = float(np.mean(s > 0.1))
            activity_score = clamp01(active / 0.22)
            time_bonus = 1.0 - idx / max(len(post), 1)
            scores.append(clamp01(0.62 * mass_score + 0.25 * activity_score + 0.13 * time_bonus))
        return float(max(scores))

    def resource_homeostasis(self, trajectory: Trajectory) -> float:
        summary = activity_summary(trajectory.states)
        cv_score = math.exp(-summary["mass_cv"])
        active = summary["activity_mean"]
        active_score = clamp01(1.0 - abs(active - 0.12) / 0.18)
        return clamp01(0.65 * cv_score + 0.35 * active_score)

    def structural_diversity(self, trajectory: Trajectory) -> float:
        if not trajectory.states:
            return 0.0
        final = trajectory.states[-1]
        mask = final > 0.1
        if mask.sum() < 12:
            return 0.0
        labels, count = ndimage.label(mask)
        if count == 0:
            return 0.0
        sizes = np.array(ndimage.sum(mask, labels, index=np.arange(1, count + 1)))
        sizes = sizes[sizes > 2]
        if sizes.size == 0:
            return 0.0
        size_entropy = entropy(sizes, bins=min(16, max(4, sizes.size)))
        cluster_score = clamp01(math.log1p(sizes.size) / math.log(8))
        texture_entropy = entropy(final, bins=24)
        return clamp01(0.38 * cluster_score + 0.32 * size_entropy + 0.3 * texture_entropy)

    def ecological_coupling(self, trajectory: Trajectory) -> float:
        if len(trajectory.resource_trace) < 8:
            return 0.0
        activity = np.asarray(trajectory.activity_trace, dtype=float)
        resource = np.asarray(trajectory.resource_trace, dtype=float)
        corr = abs(safe_corr(activity, resource))
        responsiveness = np.std(activity) / (np.mean(activity) + 1e-6)
        return clamp01(0.6 * corr + 0.4 * min(responsiveness, 1.0))


class QDArchive:
    def __init__(self, behavior_dimensions: int = 4, bins_per_dimension: int = 18):
        self.behavior_dimensions = int(behavior_dimensions)
        self.bins_per_dimension = int(bins_per_dimension)
        self.archive: dict[tuple[int, ...], dict[str, Any]] = {}
        self.stats: dict[str, float] = {
            "coverage": 0.0,
            "max_fitness": 0.0,
            "mean_fitness": 0.0,
            "qd_score": 0.0,
        }

    def __len__(self) -> int:
        return len(self.archive)

    def discretize(self, behavior: np.ndarray) -> tuple[int, ...]:
        values = np.asarray(behavior, dtype=float).ravel()[: self.behavior_dimensions]
        if values.size < self.behavior_dimensions:
            values = np.pad(values, (0, self.behavior_dimensions - values.size))
        values = np.clip(values, 0.0, 1.0)
        return tuple(int(v * (self.bins_per_dimension - 1)) for v in values)

    def add(
        self,
        individual: Individual,
        fitness: float,
        behavior: np.ndarray,
        components: dict[str, float],
        consciousness: dict[str, float] | None = None,
    ) -> bool:
        cell = self.discretize(behavior)
        existing = self.archive.get(cell)
        if existing is None or fitness > float(existing["fitness"]):
            self.archive[cell] = {
                "individual": individual,
                "fitness": float(fitness),
                "behavior": np.asarray(behavior, dtype=float),
                "components": components,
                "consciousness": consciousness or {},
                "updated_at": time.time(),
            }
            self.update_stats()
            return True
        return False

    def sample(self, rng: np.random.Generator) -> Individual | None:
        if not self.archive:
            return None
        cells = list(self.archive.keys())
        if rng.random() < 0.75:
            fitness = np.array([self.archive[c]["fitness"] for c in cells], dtype=float)
            probs = fitness - fitness.min() + 0.05
            probs = probs / probs.sum()
            idx = int(rng.choice(len(cells), p=probs))
        else:
            idx = int(rng.integers(0, len(cells)))
        return self.archive[cells[idx]]["individual"]

    def update_stats(self) -> None:
        if not self.archive:
            return
        fitness = np.array([entry["fitness"] for entry in self.archive.values()], dtype=float)
        self.stats = {
            "coverage": float(len(self.archive)),
            "max_fitness": float(np.max(fitness)),
            "mean_fitness": float(np.mean(fitness)),
            "qd_score": float(np.sum(fitness)),
        }

    def best_entries(self, n: int = 10) -> list[dict[str, Any]]:
        return [
            entry
            for _, entry in sorted(self.archive.items(), key=lambda item: item[1]["fitness"], reverse=True)[:n]
        ]

    def summary(self) -> dict[str, Any]:
        best = self.best_entries(5)
        return {
            "stats": self.stats,
            "best": [
                {
                    "individual_id": e["individual"].individual_id,
                    "fitness": e["fitness"],
                    "behavior": e["behavior"],
                    "components": e["components"],
                    "consciousness": e.get("consciousness", {}),
                }
                for e in best
            ],
        }


def behavior_descriptor(trajectory: Trajectory) -> np.ndarray:
    if not trajectory.states:
        return np.zeros(4, dtype=float)
    final = trajectory.states[-1]
    mask = final > 0.1
    activity = float(np.mean(mask))
    if mask.sum() > 0:
        coords = np.argwhere(mask)
        centroid = coords.mean(axis=0)
        distances = np.linalg.norm(coords - centroid, axis=1)
        concentration = 1.0 / (1.0 + float(np.std(distances)) / max(final.shape))
    else:
        concentration = 0.0
    masses = np.array([np.sum(s) for s in trajectory.states], dtype=float)
    temporal_variability = float(np.std(masses) / (np.mean(masses) + 1e-9))
    complexity = entropy(final, bins=24)
    return np.array(
        [
            clamp01(activity / 0.22),
            clamp01(concentration),
            clamp01(temporal_variability),
            clamp01(complexity),
        ],
        dtype=float,
    )


class RetrospectiveAnalyzer:
    def analyze(self, trajectory: Trajectory, components: dict[str, float]) -> dict[str, float]:
        if not trajectory.states:
            return {
                "phi_proxy": 0.0,
                "gnwt_broadcast_proxy": 0.0,
                "temporal_continuity": 0.0,
                "self_other_boundary": 0.0,
                "pci_proxy": 0.0,
            }
        states = trajectory.states
        final = states[-1]
        h_mid = final.shape[0] // 2
        w_mid = final.shape[1] // 2
        quadrants = [
            final[:h_mid, :w_mid].ravel(),
            final[:h_mid, w_mid:].ravel(),
            final[h_mid:, :w_mid].ravel(),
            final[h_mid:, w_mid:].ravel(),
        ]
        q_activity = np.array([np.mean(q) for q in quadrants])
        integration = clamp01(1.0 - float(np.std(q_activity) / (np.mean(q_activity) + 1e-6)))
        differentiation = entropy(final, bins=32)
        phi_proxy = clamp01(0.55 * integration + 0.45 * differentiation)

        global_signal = np.array([np.mean(s) for s in states], dtype=float)
        local_signal = np.array([np.mean(s > 0.1) for s in states], dtype=float)
        gnwt = clamp01(0.5 * abs(safe_corr(global_signal[:-1], local_signal[1:])) + 0.5 * entropy(global_signal, bins=12))

        masks = [s > 0.1 for s in states]
        similarities = [mask_iou(a, b) for a, b in zip(masks[:-1], masks[1:])]
        temporal = float(np.mean(similarities)) if similarities else 0.0

        activity_binary = (np.asarray(trajectory.activity_trace) > np.mean(trajectory.activity_trace)).astype(int)
        pci = clamp01(binary_lz_complexity(activity_binary) / 1.2)

        return {
            "phi_proxy": phi_proxy,
            "gnwt_broadcast_proxy": gnwt,
            "temporal_continuity": clamp01(temporal),
            "self_other_boundary": clamp01(components.get("boundary_stability", 0.0)),
            "pci_proxy": pci,
        }


def evaluate_individual_job(job: dict[str, Any]) -> dict[str, Any]:
    individual: Individual = job["individual"]
    ecology = LeniaLiteEcology(
        world_size=job["world_size"],
        eval_steps=job["eval_steps"],
        record_stride=job.get("record_stride", 3),
    )
    trajectory = ecology.simulate(individual, seed=job["seed"])
    evaluator = FitnessEvaluator(weights=job.get("weights"))
    fitness, components = evaluator.evaluate(trajectory)
    behavior = behavior_descriptor(trajectory)
    consciousness = RetrospectiveAnalyzer().analyze(trajectory, components)
    return {
        "individual": individual,
        "fitness": fitness,
        "components": components,
        "behavior": behavior,
        "consciousness": consciousness,
        "activity_summary": activity_summary(trajectory.states),
        "power_law": power_law_score(trajectory.activity_trace),
    }


class EvolutionEngine:
    def __init__(self, config: dict[str, Any], seed: int = 1):
        self.config = config
        self.rng = np.random.default_rng(seed)
        self.generation = 0
        self.archive = QDArchive(
            behavior_dimensions=config.get("behavior_dimensions", 4),
            bins_per_dimension=config.get("bins_per_dimension", 18),
        )
        self.mutator = MutationOperators(
            mutation_rate=config.get("mutation_rate", 0.18),
            mutation_strength=config.get("mutation_strength", 0.08),
        )
        self.world_size = int(config.get("world_size", 72))
        self.eval_steps = int(config.get("eval_steps", 96))
        self.record_stride = int(config.get("record_stride", 3))
        self.batch_size = int(config.get("batch_size", 48))
        self.workers = int(config.get("workers", 1))
        self.history: list[dict[str, Any]] = []
        self._executor: ProcessPoolExecutor | None = None

    def random_individual(self) -> Individual:
        return Individual(genome=random_genome(self.rng, self.world_size), generation=self.generation)

    def propose_batch(self, n: int) -> list[Individual]:
        batch: list[Individual] = []
        for _ in range(n):
            parent = self.archive.sample(self.rng)
            if parent is None or self.rng.random() < 0.12:
                child = self.random_individual()
            else:
                child = self.mutator.mutate(parent, self.rng, self.generation)
            batch.append(child)
        return batch

    def evaluate_batch(self, individuals: list[Individual]) -> list[dict[str, Any]]:
        jobs = [
            {
                "individual": ind,
                "world_size": self.world_size,
                "eval_steps": self.eval_steps,
                "record_stride": self.record_stride,
                "seed": int(self.rng.integers(0, 2**31 - 1)),
            }
            for ind in individuals
        ]
        if self.workers <= 1 or len(jobs) <= 1:
            return [evaluate_individual_job(job) for job in jobs]
        if self._executor is None:
            self._executor = ProcessPoolExecutor(max_workers=self.workers)
        return list(self._executor.map(evaluate_individual_job, jobs, chunksize=max(1, len(jobs) // self.workers)))

    def run_chunk(self, generations: int | None = None) -> dict[str, Any]:
        target = int(generations or self.batch_size)
        remaining = target
        added = 0
        best_fitness = 0.0
        last_results: list[dict[str, Any]] = []
        started = time.time()
        while remaining > 0:
            n = min(self.batch_size, remaining)
            individuals = self.propose_batch(n)
            results = self.evaluate_batch(individuals)
            for result in results:
                if self.archive.add(
                    result["individual"],
                    result["fitness"],
                    result["behavior"],
                    result["components"],
                    result["consciousness"],
                ):
                    added += 1
                best_fitness = max(best_fitness, float(result["fitness"]))
                self.generation += 1
            last_results = results
            remaining -= n

        chunk = {
            "generation": self.generation,
            "evaluated": target,
            "added": added,
            "best_fitness_in_chunk": best_fitness,
            "archive": self.archive.stats,
            "elapsed_seconds": time.time() - started,
            "recent_mean_fitness": float(np.mean([r["fitness"] for r in last_results])) if last_results else 0.0,
            "recent_power_law_score": float(np.mean([r["power_law"]["score"] for r in last_results])) if last_results else 0.0,
        }
        self.history.append(chunk)
        return chunk

    def system_measurements(self) -> dict[str, float]:
        best = self.archive.best_entries(8)
        if not best:
            return {
                "phi_proxy": 0.0,
                "pci_proxy": 0.0,
                "self_model_stability": 0.0,
                "temporal_continuity": 0.0,
                "agency_proxy": 0.0,
                "instability": 0.0,
            }
        consciousness = [e.get("consciousness", {}) for e in best]
        comp = [e.get("components", {}) for e in best]
        return {
            "phi_proxy": float(np.mean([c.get("phi_proxy", 0.0) for c in consciousness])),
            "pci_proxy": float(np.mean([c.get("pci_proxy", 0.0) for c in consciousness])),
            "self_model_stability": float(np.mean([c.get("self_other_boundary", 0.0) for c in consciousness])),
            "temporal_continuity": float(np.mean([c.get("temporal_continuity", 0.0) for c in consciousness])),
            "agency_proxy": float(np.mean([cc.get("ecological_coupling", 0.0) for cc in comp])),
            "instability": float(1.0 - np.mean([cc.get("resource_homeostasis", 0.0) for cc in comp])),
            "archive_coverage": float(self.archive.stats["coverage"]),
            "archive_max_fitness": float(self.archive.stats["max_fitness"]),
        }

    def evaluation_profile(self) -> dict[str, Any]:
        measurements = self.system_measurements()
        return {
            "state": clamp01(0.45 * measurements["pci_proxy"] + 0.35 * measurements["phi_proxy"] + 0.2 * measurements["archive_max_fitness"]),
            "content": clamp01(0.5 * min(self.archive.stats["coverage"] / max(self.archive.bins_per_dimension, 1), 1.0) + 0.5 * measurements["phi_proxy"]),
            "self_model": clamp01(measurements["self_model_stability"]),
            "agency": clamp01(measurements["agency_proxy"]),
            "temporal_continuity": clamp01(measurements["temporal_continuity"]),
            "details": measurements,
        }

    def shutdown(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=False)
            self._executor = None

    def __getstate__(self) -> dict[str, Any]:
        state = self.__dict__.copy()
        state["_executor"] = None
        return state
