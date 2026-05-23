from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from consciousness_benchmark.core.stats import bootstrap_corr_ci, format_p, pearson


@dataclass(frozen=True)
class ConstructResult:
    name: str
    source_path: str
    proxy_col: str
    independent_col: str
    mechanism: str
    status: str
    n: int
    r: float
    p: float
    ci_low: float
    ci_high: float
    validated: bool
    validated_in: tuple[str, ...] = ()
    measurement_limited_in: tuple[str, ...] = ()
    variants: dict[str, str] = field(default_factory=dict)

    @property
    def p_formatted(self) -> str:
        return format_p(self.p)

    @property
    def r_with_ci(self) -> str:
        return f"{self.r:.3f} [{self.ci_low:.3f}, {self.ci_high:.3f}]"


@dataclass(frozen=True)
class ColumnConstruct:
    """Reference construct backed by a proxy column and an independent-test column.

    This is the benchmark MVP representation. Online system adapters can later
    implement the same construct interface by producing these score columns.
    """

    name: str
    source_path: str
    proxy_col: str
    independent_col: str
    mechanism: str
    status: str = "validated"
    validation_threshold: float = 0.7
    validated_in: tuple[str, ...] = ()
    measurement_limited_in: tuple[str, ...] = ()
    variants: dict[str, str] = field(default_factory=dict)

    def applicable_to(self, architecture: str) -> str:
        """Return the current evidence status for this construct on an architecture.

        The benchmark is deliberately conservative: a construct can be validated
        in one substrate, measurement-limited in another, and have a named
        architecture-specific variant elsewhere.
        """

        has_limited = architecture in self.measurement_limited_in
        has_variant = architecture in self.variants
        if architecture in self.validated_in:
            return "validated"
        if has_limited and has_variant:
            return "measurement_limited_with_variant"
        if has_limited:
            return "measurement_limited"
        if has_variant:
            return "variant_available"
        return "untested"

    def variant_for(self, architecture: str) -> str | None:
        """Return a named architecture-specific variant, if one is registered."""

        return self.variants.get(architecture)

    def validate(
        self,
        *,
        root: str | Path = ".",
        n_bootstrap: int = 10000,
        seed: int = 20260521,
    ) -> ConstructResult:
        path = Path(root) / self.source_path
        if not path.exists():
            raise FileNotFoundError(path)
        df = pd.read_csv(path)
        missing = [col for col in [self.proxy_col, self.independent_col] if col not in df.columns]
        if missing:
            raise KeyError(f"{path} missing columns: {missing}")

        r, p, n = pearson(df[self.proxy_col], df[self.independent_col])
        ci_low, ci_high = bootstrap_corr_ci(
            df[self.proxy_col],
            df[self.independent_col],
            seed=seed,
            n_bootstrap=n_bootstrap,
        )
        return ConstructResult(
            name=self.name,
            source_path=self.source_path,
            proxy_col=self.proxy_col,
            independent_col=self.independent_col,
            mechanism=self.mechanism,
            status=self.status,
            n=n,
            r=r,
            p=p,
            ci_low=ci_low,
            ci_high=ci_high,
            validated=bool(r >= self.validation_threshold),
            validated_in=self.validated_in,
            measurement_limited_in=self.measurement_limited_in,
            variants=self.variants,
        )
