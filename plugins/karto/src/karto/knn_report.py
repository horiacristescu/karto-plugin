"""kNN report for SSP models.

Usage:
    python -m karto.knn_report ssps/matx_inference/models/ssp_v3/ssp_v3.py
    python -m karto.knn_report ssps/matx_inference/models/ssp_v3/ssp_v3.py --stdout
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from karto._distances import WILDCARDS, hamming as dist
from karto.loader import load_module

JsonDict = dict[str, Any]

K = 5


def _diff_str(a: JsonDict, b: JsonDict, features: list[str]) -> str:
    parts = []
    for f in features:
        va, vb = a[f], b[f]
        if va == vb:
            continue
        if va not in WILDCARDS and vb not in WILDCARDS:
            parts.append(f"`{f}`: {va} → {vb}")
        else:
            parts.append(f"`{f}`: {va} ↔ {vb} *(wc)*")
    return ", ".join(parts) if parts else "—"


def wildcard_count(pos: JsonDict, features: list[str]) -> int:
    return sum(1 for f in features if pos[f] in WILDCARDS)


def build_report(ssp_path: Path) -> str:
    mod = load_module(ssp_path)
    features: list[str] = list(mod.SSP_FEATURES.keys())
    positions: dict[str, JsonDict] = mod.SSP_POSITIONS

    names = list(positions.keys())
    n = len(names)

    # Precompute all pairwise distances
    dist_matrix: dict[tuple[str, str], float] = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = dist(positions[a], positions[b], features)
            dist_matrix[(a, b)] = d
            dist_matrix[(b, a)] = d

    def neighbors(name: str) -> list[tuple[float, str]]:
        ds = [(dist_matrix[(name, o)], o) for o in names if o != name]
        ds.sort()
        return ds[:K]

    lines: list[str] = []

    lines.append(f"# kNN Analysis — {ssp_path.stem}")
    lines.append("")
    lines.append(f"SSP: `{ssp_path}`  ")
    lines.append(f"Positions: {n}  |  Features: {len(features)}  |  k={K}")
    lines.append("")
    lines.append("Distance metric: Hamming with wildcard penalty 0.5 "
                 "(values `none`, `not-applicable`, `general` treated as wildcards).")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-position sections
    near_dupes: list[tuple[str, str, float]] = []
    isolated: list[tuple[str, float]] = []
    gravity_wells: list[tuple[str, int]] = []

    for name in names:
        wc = wildcard_count(positions[name], features)
        nbrs = neighbors(name)

        lines.append(f"## `{name}`")
        lines.append("")
        if wc > len(features) // 2:
            lines.append(f"> ⚠ {wc}/{len(features)} features are wildcards — may act as gravity well.")
            lines.append("")
            gravity_wells.append((name, wc))

        lines.append(f"| Rank | d | Neighbor | Differing features |")
        lines.append(f"|------|---|----------|--------------------|")
        for rank, (d, nbr) in enumerate(nbrs, 1):
            diff = _diff_str(positions[name], positions[nbr], features)
            lines.append(f"| {rank} | {d:.1f} | `{nbr}` | {diff} |")
            if rank == 1 and d <= 1.5:
                near_dupes.append((name, nbr, d))
        lines.append("")

        nearest_d = nbrs[0][0]
        if nearest_d >= 4.0:
            isolated.append((name, nearest_d))

    # Summary Findings
    lines.append("---")
    lines.append("")
    lines.append("## Summary Findings")
    lines.append("")

    if near_dupes:
        lines.append("### Near-duplicates (d ≤ 1.5)")
        lines.append("")
        seen: set[frozenset[str]] = set()
        for a, b, d in near_dupes:
            pair = frozenset([a, b])
            if pair not in seen:
                seen.add(pair)
                diff = _diff_str(positions[a], positions[b], features)
                lines.append(f"- `{a}` ↔ `{b}` (d={d:.1f}): {diff}")
        lines.append("")

    if gravity_wells:
        lines.append("### Wildcard gravity wells")
        lines.append("")
        for name, wc in gravity_wells:
            lines.append(f"- `{name}`: {wc}/{len(features)} features are wildcards — "
                         f"attracts neighbors that share no meaningful features.")
        lines.append("")

    if isolated:
        lines.append("### Isolated positions (nearest neighbor d ≥ 4.0)")
        lines.append("")
        for name, d in isolated:
            lines.append(f"- `{name}`: nearest neighbor at d={d:.1f}")
        lines.append("")

    if not near_dupes and not gravity_wells and not isolated:
        lines.append("No structural problems detected.")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate kNN analysis for an SSP module.")
    parser.add_argument("ssp_path", help="Path to ssp_vN.py module")
    parser.add_argument("--stdout", action="store_true",
                        help="Print to stdout instead of writing knn_analysis.md")
    args = parser.parse_args()

    path = Path(args.ssp_path)
    report = build_report(path)

    if args.stdout:
        print(report)
    else:
        out = path.parent / "knn_analysis.md"
        out.write_text(report)
        print(f"Written: {out}")


if __name__ == "__main__":
    main()
