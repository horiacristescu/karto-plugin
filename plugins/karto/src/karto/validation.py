"""Validation for Karto SSP modules."""

from __future__ import annotations

import argparse
import json
from types import ModuleType
from typing import Any

from .loader import LoadError, load_module


class ValidationError(ValueError):
    """Raised when an SSP module declaration is invalid."""


def _jsonable(value: Any, label: str, errors: list[str]) -> None:
    try:
        json.dumps(value)
    except (TypeError, ValueError) as exc:
        errors.append(f"{label} is not JSON-serializable: {exc}")


def validate_module(module: ModuleType) -> list[str]:
    errors: list[str] = []

    if not hasattr(module, "SSP_META"):
        errors.append("Missing SSP_META")
    if not hasattr(module, "SSP_FEATURES"):
        errors.append("Missing SSP_FEATURES")
    if not hasattr(module, "SSP_POSITIONS"):
        errors.append("Missing SSP_POSITIONS")

    if errors:
        return errors

    meta = module.SSP_META
    features = module.SSP_FEATURES
    positions = module.SSP_POSITIONS
    clusters = getattr(module, "SSP_CLUSTERS", None)

    _jsonable(meta, "SSP_META", errors)
    _jsonable(features, "SSP_FEATURES", errors)
    _jsonable(positions, "SSP_POSITIONS", errors)
    if clusters is not None:
        _jsonable(clusters, "SSP_CLUSTERS", errors)

    if not isinstance(features, dict):
        errors.append("SSP_FEATURES must be a dict of feature_name -> values")
        feature_names: list[str] = []
    else:
        feature_names = list(features)
        for feature, values in features.items():
            if not isinstance(feature, str) or not feature:
                errors.append(f"Invalid feature name: {feature!r}")
            if not isinstance(values, (list, tuple)):
                errors.append(f"Feature {feature!r} values must be a list or tuple")
                continue
            for value in values:
                if not isinstance(value, str) or not value:
                    errors.append(f"Feature {feature!r} has invalid value: {value!r}")

    if not isinstance(positions, dict):
        errors.append("SSP_POSITIONS must be a dict of position_name -> feature mapping")
        return errors

    legal_values = {
        feature: set(values)
        for feature, values in features.items()
        if isinstance(values, (list, tuple))
    } if isinstance(features, dict) else {}

    for position, assigned in positions.items():
        if not isinstance(assigned, dict):
            errors.append(f"Position {position!r} must map features to values")
            continue

        missing = sorted(set(feature_names) - set(assigned))
        extra = sorted(set(assigned) - set(feature_names))
        if missing:
            errors.append(f"Position {position!r} missing features: {', '.join(missing)}")
        if extra:
            errors.append(f"Position {position!r} has unknown features: {', '.join(extra)}")

        for feature, value in assigned.items():
            if feature in legal_values and value not in legal_values[feature]:
                errors.append(
                    f"Position {position!r} has illegal value {value!r} "
                    f"for feature {feature!r}"
                )

    return errors


def validate_path(path: str) -> None:
    module = load_module(path)
    errors = validate_module(module)
    if errors:
        raise ValidationError("\n".join(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m karto.validate")
    parser.add_argument("module", help="Path to an SSP module")
    args = parser.parse_args(argv)

    try:
        validate_path(args.module)
    except (LoadError, ValidationError) as exc:
        print(exc)
        return 1

    print(f"Valid SSP module: {args.module}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
