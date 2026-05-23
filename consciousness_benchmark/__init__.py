from __future__ import annotations

from consciousness_benchmark.core.construct import ColumnConstruct, ConstructResult
from consciousness_benchmark.core.validator import ConstructValidator, ValidationReport
from consciousness_benchmark.constructs.reference import reference_constructs

__version__ = "0.1.0"

__all__ = [
    "ColumnConstruct",
    "ConstructResult",
    "ConstructValidator",
    "ValidationReport",
    "reference_constructs",
    "__version__",
]
