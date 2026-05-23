from __future__ import annotations

import json
import math
import os
import platform
import random
import socket
import time
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

try:
    import psutil
except Exception:  # pragma: no cover - optional dependency guard
    psutil = None


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def set_global_seed(seed: int | None) -> np.random.Generator:
    if seed is None:
        seed = int(time.time() * 1000) % (2**32 - 1)
    random.seed(seed)
    np.random.seed(seed)
    return np.random.default_rng(seed)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def write_json(path: str | Path, payload: Any) -> None:
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(
        json.dumps(jsonable(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_jsonl(path: str | Path, payload: dict[str, Any]) -> None:
    path = Path(path)
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(jsonable(payload), ensure_ascii=False) + "\n")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def entropy(values: np.ndarray, bins: int = 32) -> float:
    arr = np.asarray(values, dtype=float).ravel()
    if arr.size == 0:
        return 0.0
    hist, _ = np.histogram(arr, bins=bins, range=(float(arr.min()), float(arr.max()) + 1e-9))
    probs = hist.astype(float)
    probs = probs[probs > 0] / max(float(probs.sum()), 1e-9)
    h = -float(np.sum(probs * np.log2(probs)))
    return h / max(math.log2(bins), 1e-9)


def binary_lz_complexity(sequence: Iterable[int] | np.ndarray) -> float:
    data = "".join("1" if int(x) else "0" for x in np.asarray(list(sequence)).ravel())
    n = len(data)
    if n == 0:
        return 0.0
    phrases: set[str] = set()
    i = 0
    while i < n:
        j = i + 1
        while j <= n and data[i:j] in phrases:
            j += 1
        phrases.add(data[i:j])
        i = j
    raw = len(phrases)
    normalizer = n / max(math.log2(n + 1), 1.0)
    return float(np.clip(raw / max(normalizer, 1.0), 0.0, 1.5))


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    x = np.asarray(a, dtype=float).ravel()
    y = np.asarray(b, dtype=float).ravel()
    if x.size == 0 or y.size == 0 or x.size != y.size:
        return 0.0
    if np.std(x) < 1e-9 or np.std(y) < 1e-9:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def clamp01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def mask_centroid(mask: np.ndarray) -> np.ndarray:
    coords = np.argwhere(mask)
    if len(coords) == 0:
        return np.array([np.nan, np.nan], dtype=float)
    return coords.mean(axis=0)


def mask_iou(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=bool)
    bb = np.asarray(b, dtype=bool)
    union = np.logical_or(aa, bb).sum()
    if union == 0:
        return 0.0
    return float(np.logical_and(aa, bb).sum() / union)


def activity_summary(states: list[np.ndarray], threshold: float = 0.1) -> dict[str, float]:
    if not states:
        return {"mass_mean": 0.0, "mass_cv": 1.0, "activity_mean": 0.0, "entropy": 0.0}
    masses = np.array([float(np.sum(s)) for s in states])
    active = np.array([float(np.mean(s > threshold)) for s in states])
    return {
        "mass_mean": float(np.mean(masses)),
        "mass_cv": float(np.std(masses) / (abs(np.mean(masses)) + 1e-9)),
        "activity_mean": float(np.mean(active)),
        "entropy": entropy(np.stack(states[-min(len(states), 8) :])),
    }


def power_law_score(activity_trace: Iterable[float]) -> dict[str, float]:
    arr = np.asarray(list(activity_trace), dtype=float)
    if arr.size < 20 or np.std(arr) < 1e-9:
        return {"score": 0.0, "r2": 0.0, "slope": 0.0, "avalanches": 0}
    threshold = float(np.mean(arr))
    sizes: list[int] = []
    current = 0
    for item in arr:
        if item > threshold:
            current += 1
        elif current:
            sizes.append(current)
            current = 0
    if current:
        sizes.append(current)
    if len(sizes) < 5:
        return {"score": 0.0, "r2": 0.0, "slope": 0.0, "avalanches": len(sizes)}
    unique, counts = np.unique(sizes, return_counts=True)
    if len(unique) < 3:
        return {"score": 0.2, "r2": 0.0, "slope": 0.0, "avalanches": len(sizes)}
    x = np.log(unique)
    y = np.log(counts)
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2)) + 1e-9
    r2 = 1.0 - ss_res / ss_tot
    slope_score = 1.0 - min(abs(float(slope) + 1.5) / 2.0, 1.0)
    return {
        "score": clamp01(max(0.0, r2) * 0.7 + slope_score * 0.3),
        "r2": clamp01(r2),
        "slope": float(slope),
        "avalanches": len(sizes),
    }


def resource_usage() -> dict[str, float]:
    if psutil is None:
        return {"cpu_percent": 0.0, "memory_percent": 0.0}
    proc = psutil.Process(os.getpid())
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": float(psutil.cpu_percent(interval=None)),
        "memory_percent": float(mem.percent),
        "process_memory_mb": float(proc.memory_info().rss / (1024 * 1024)),
    }


def hardware_profile() -> dict[str, Any]:
    profile: dict[str, Any] = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu_count_logical": os.cpu_count() or 1,
    }
    if psutil is not None:
        profile["cpu_count_physical"] = psutil.cpu_count(logical=False)
        profile["memory_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
    try:
        import torch

        profile["torch_available"] = True
        profile["cuda_available"] = bool(torch.cuda.is_available())
        if torch.cuda.is_available():
            profile["cuda_device_count"] = int(torch.cuda.device_count())
            profile["cuda_name"] = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            profile["cuda_memory_gb"] = round(props.total_memory / (1024**3), 2)
    except Exception:
        profile["torch_available"] = False
        profile["cuda_available"] = False
    return profile


def choose_worker_count(profile: dict[str, Any], requested: int | None = None) -> int:
    logical = int(profile.get("cpu_count_logical") or 1)
    memory_gb = float(profile.get("memory_gb") or 8.0)
    if requested:
        return max(1, min(int(requested), logical))
    memory_bound = max(1, int(memory_gb // 3))
    return max(1, min(logical - 2 if logical > 4 else logical, 10, memory_bound))


class JsonlLogger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        ensure_dir(self.path.parent)

    def event(self, event: str, **payload: Any) -> None:
        append_jsonl(self.path, {"time": now_iso(), "event": event, **payload})

