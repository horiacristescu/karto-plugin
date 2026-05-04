"""Scoring helpers for runnable SSP modules."""

from __future__ import annotations

import argparse
import json
import re
import time
from types import ModuleType
from typing import Any, Callable

from .contracts import Divergence, FeatureTrace, JsonDict, ScoreResult
from .loader import LoadError, load_module
from .validation import ValidationError, validate_module


def code(
    feature: str,
    value: str,
    *,
    confidence: float = 1.0,
    evidence: JsonDict | None = None,
    backend: str = "code",
    elapsed_ms: float = 0.0,
) -> FeatureTrace:
    return FeatureTrace(
        feature=feature,
        value=value,
        backend=backend,
        confidence=confidence,
        evidence=evidence or {},
        elapsed_ms=elapsed_ms,
    )


def regex(
    record: JsonDict,
    feature: str,
    field: str,
    patterns: dict[str, str],
    *,
    default: str | None = None,
    confidence: float = 1.0,
) -> FeatureTrace:
    text = str(record.get(field, ""))
    start = time.perf_counter()
    for value, pattern in patterns.items():
        if re.search(pattern, text):
            elapsed_ms = (time.perf_counter() - start) * 1000
            return FeatureTrace(
                feature=feature,
                value=value,
                backend="regex",
                confidence=confidence,
                elapsed_ms=elapsed_ms,
                evidence={"field": field, "pattern": pattern},
            )
    if default is None:
        raise ValueError(f"No regex pattern matched for feature {feature!r}")
    elapsed_ms = (time.perf_counter() - start) * 1000
    return FeatureTrace(
        feature=feature,
        value=default,
        backend="regex",
        confidence=0.0,
        elapsed_ms=elapsed_ms,
        evidence={"field": field, "matched": False},
    )


def normalize_score(raw: JsonDict, *, elapsed_ms: float = 0.0) -> ScoreResult:
    result = str(raw.get("result", "unknown"))
    feature_rows = raw.get("features", [])
    if not isinstance(feature_rows, list):
        raise ValueError("score() raw dict must contain features as a list")

    traces: list[FeatureTrace] = []
    for row in feature_rows:
        if isinstance(row, FeatureTrace):
            traces.append(row)
            continue
        if not isinstance(row, dict):
            raise ValueError("score() feature rows must be dicts")
        traces.append(
            FeatureTrace(
                feature=str(row.get("feature", "")),
                value=str(row.get("value", "")),
                backend=str(row.get("backend", "unknown")),
                confidence=float(row.get("confidence", 1.0)),
                elapsed_ms=float(row.get("elapsed_ms", 0.0)),
                evidence=dict(row.get("evidence", {})),
            )
        )

    return ScoreResult(
        result=result,
        features=traces,
        divergence="none",
        elapsed_ms=elapsed_ms or float(raw.get("elapsed_ms", 0.0)),
    )


def _call_score(fn: Callable[[JsonDict], JsonDict], record: JsonDict) -> ScoreResult:
    start = time.perf_counter()
    raw = fn(record)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return normalize_score(raw, elapsed_ms=elapsed_ms)


def _feature_values(result: ScoreResult) -> dict[str, str]:
    return {trace.feature: trace.value for trace in result.features}


def _assert_complete_features(module: ModuleType, result: ScoreResult) -> None:
    declared = getattr(module, "SSP_FEATURES", {})
    expected = set(declared)
    actual = {trace.feature for trace in result.features}
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        parts = []
        if missing:
            parts.append(f"missing features: {', '.join(missing)}")
        if extra:
            parts.append(f"unknown features: {', '.join(extra)}")
        raise ValueError(f"score() returned incomplete feature trace ({'; '.join(parts)})")

    for trace in result.features:
        legal_values = set(declared.get(trace.feature, []))
        if legal_values and trace.value not in legal_values:
            raise ValueError(
                f"score() returned illegal value {trace.value!r} "
                f"for feature {trace.feature!r}"
            )


def detect_divergence(results: list[ScoreResult], label: str | None = None) -> Divergence:
    result_values = {result.result for result in results}
    feature_maps = [_feature_values(result) for result in results]
    feature_names = set().union(*(set(values) for values in feature_maps)) if feature_maps else set()
    feature_split = any(
        len({values.get(feature) for values in feature_maps}) > 1
        for feature in feature_names
    )
    substrate_split = len(result_values) > 1 or feature_split

    label_split = False
    if label is not None:
        label_split = any(result.result != label for result in results)

    if substrate_split and label_split:
        return "ambiguous"
    if substrate_split:
        return "substrate-disagreement"
    if label_split:
        return "label-disagreement"
    return "none"


def score_module(module: ModuleType, record: JsonDict) -> ScoreResult:
    score_functions: list[Callable[[JsonDict], JsonDict]] = []
    if hasattr(module, "score_rules"):
        score_functions.append(module.score_rules)
    if hasattr(module, "score_model"):
        score_functions.append(module.score_model)

    if score_functions:
        substrate_results = [_call_score(fn, record) for fn in score_functions]
        primary = substrate_results[0]
    elif hasattr(module, "score"):
        primary = _call_score(module.score, record)
        substrate_results = [primary]
    else:
        raise ValueError("SSP module must define score(record) or substrate scorers")

    for result in substrate_results:
        _assert_complete_features(module, result)

    label = record.get("label", record.get("expected_result"))
    divergence = detect_divergence(substrate_results, str(label) if label is not None else None)
    return ScoreResult(
        result=primary.result,
        features=primary.features,
        divergence=divergence,
        elapsed_ms=sum(result.elapsed_ms for result in substrate_results),
    )


def score_path(module_path: str, input_path: str) -> ScoreResult:
    module = load_module(module_path)
    validation_errors = validate_module(module)
    if validation_errors:
        raise ValidationError("\n".join(validation_errors))
    with open(input_path) as f:
        record = json.load(f)
    return score_module(module, record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m karto.score")
    parser.add_argument("module", help="Path to an SSP module")
    parser.add_argument("input", help="Path to a JSON input record")
    args = parser.parse_args(argv)

    try:
        result = score_path(args.module, args.input)
    except (LoadError, ValidationError, ValueError) as exc:
        print(exc)
        return 1

    print(json.dumps(result.to_json_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
