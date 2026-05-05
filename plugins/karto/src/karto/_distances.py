"""Shared distance utilities for SSP position analysis."""

from __future__ import annotations
from typing import Any
import numpy as np

JsonDict = dict[str, Any]

WILDCARDS = frozenset({"none", "not-applicable", "general"})


def hamming(a: JsonDict, b: JsonDict, features: list[str]) -> float:
    """Hamming distance with 0.5 penalty when either value is a wildcard."""
    d = 0.0
    for f in features:
        va, vb = a[f], b[f]
        if va == vb:
            continue
        d += 0.5 if (va in WILDCARDS or vb in WILDCARDS) else 1.0
    return d


def condensed_matrix(positions: dict[str, JsonDict], features: list[str]) -> np.ndarray:
    """Upper-triangle distance matrix in scipy condensed form (n*(n-1)/2,)."""
    names = list(positions.keys())
    n = len(names)
    out = np.zeros(n * (n - 1) // 2)
    k = 0
    for i in range(n):
        for j in range(i + 1, n):
            out[k] = hamming(positions[names[i]], positions[names[j]], features)
            k += 1
    return out


def full_matrix(positions: dict[str, JsonDict], features: list[str]) -> np.ndarray:
    """Full n×n symmetric distance matrix."""
    names = list(positions.keys())
    n = len(names)
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = hamming(positions[names[i]], positions[names[j]], features)
            mat[i, j] = mat[j, i] = d
    return mat
