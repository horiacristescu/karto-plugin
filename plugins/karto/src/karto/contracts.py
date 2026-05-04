"""Typed contracts for runnable SSP modules.

User-authored SSP modules should stay lightweight and may return raw dicts from
``score(input)``. These dataclasses are Karto's internal normalized shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Literal, Protocol


Divergence = Literal[
    "none",
    "substrate-disagreement",
    "label-disagreement",
    "ambiguous",
]


JsonDict = dict[str, Any]


def _assert_jsonable(value: Any, field_name: str) -> None:
    try:
        json.dumps(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field_name} must be JSON-serializable") from exc


@dataclass(frozen=True)
class SSPMeta:
    input_concept: str
    feature_concept: str
    state_concept: str
    leaf_concept: str
    maintainer: str = ""
    version: str = "0.1.0"
    decomposition_kind: str = "descriptive"

    def __post_init__(self) -> None:
        _assert_jsonable(self.to_json_dict(), "SSPMeta")

    def to_json_dict(self) -> JsonDict:
        return {
            "input_concept": self.input_concept,
            "feature_concept": self.feature_concept,
            "state_concept": self.state_concept,
            "leaf_concept": self.leaf_concept,
            "maintainer": self.maintainer,
            "version": self.version,
            "decomposition_kind": self.decomposition_kind,
        }


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    values: tuple[str, ...]
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("FeatureSpec.name is required")
        if not self.values:
            raise ValueError(f"FeatureSpec {self.name!r} must declare values")
        _assert_jsonable(self.to_json_dict(), f"FeatureSpec {self.name!r}")

    def to_json_dict(self) -> JsonDict:
        return {
            "name": self.name,
            "values": list(self.values),
            "description": self.description,
        }


@dataclass(frozen=True)
class PositionSpec:
    name: str
    features: JsonDict
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("PositionSpec.name is required")
        _assert_jsonable(self.to_json_dict(), f"PositionSpec {self.name!r}")

    def to_json_dict(self) -> JsonDict:
        return {
            "name": self.name,
            "features": dict(self.features),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class FeatureTrace:
    feature: str
    value: str
    backend: str
    confidence: float = 1.0
    elapsed_ms: float = 0.0
    evidence: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.feature:
            raise ValueError("FeatureTrace.feature is required")
        if not self.value:
            raise ValueError(f"FeatureTrace {self.feature!r} requires a value")
        if not self.backend:
            raise ValueError(f"FeatureTrace {self.feature!r} requires a backend")
        _assert_jsonable(self.evidence, f"FeatureTrace {self.feature!r}.evidence")
        _assert_jsonable(self.to_json_dict(), f"FeatureTrace {self.feature!r}")

    def to_json_dict(self) -> JsonDict:
        return {
            "feature": self.feature,
            "value": self.value,
            "backend": self.backend,
            "confidence": self.confidence,
            "elapsed_ms": self.elapsed_ms,
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True)
class ScoreResult:
    result: str
    features: tuple[FeatureTrace, ...]
    divergence: Divergence = "none"
    elapsed_ms: float = 0.0

    def __post_init__(self) -> None:
        if not self.result:
            raise ValueError("ScoreResult.result is required")
        object.__setattr__(self, "features", tuple(self.features))
        if self.divergence not in {
            "none",
            "substrate-disagreement",
            "label-disagreement",
            "ambiguous",
        }:
            raise ValueError(f"Unknown divergence: {self.divergence!r}")
        _assert_jsonable(self.to_json_dict(), "ScoreResult")

    def to_json_dict(self) -> JsonDict:
        return {
            "result": self.result,
            "features": [feature.to_json_dict() for feature in self.features],
            "divergence": self.divergence,
            "elapsed_ms": self.elapsed_ms,
        }


class BackendFn(Protocol):
    def __call__(self, record: JsonDict) -> FeatureTrace:
        ...
