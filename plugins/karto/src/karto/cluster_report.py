"""Hierarchical cluster report for SSP models.

Builds an agglomerative dendrogram from position feature distances and prints
it as a numbered outline. Internal nodes show the merge distance; leaves show
the position name. Manual SSP_CLUSTERS are annotated inline.

Usage:
    python -m karto.cluster_report ssps/matx_inference/models/ssp_v3/ssp_v3.py
    python -m karto.cluster_report ssps/matx_inference/models/ssp_v3/ssp_v3.py --stdout
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from scipy.cluster.hierarchy import linkage

from karto._distances import condensed_matrix
from karto.loader import load_module

JsonDict = dict[str, Any]


# ---------------------------------------------------------------------------
# Tree construction from scipy linkage matrix
# ---------------------------------------------------------------------------

@dataclass
class Node:
    label: str           # position name for leaves, "" for internal
    dist: float          # merge distance (0 for leaves)
    children: list["Node"] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return not self.children


def _build_tree(names: list[str], Z: np.ndarray) -> Node:
    """Convert scipy linkage matrix Z into a Node tree."""
    n = len(names)
    nodes: list[Node] = [Node(label=name, dist=0.0) for name in names]
    for i, j, d, _ in Z:
        merged = Node(label="", dist=d, children=[nodes[int(i)], nodes[int(j)]])
        nodes.append(merged)
    return nodes[-1]


# ---------------------------------------------------------------------------
# Outline rendering
# ---------------------------------------------------------------------------

def _render(node: Node, prefix: str, lines: list[str],
            manual_map: dict[str, str]) -> None:
    if node.is_leaf:
        cluster_tag = f"  [{manual_map[node.label]}]" if node.label in manual_map else ""
        lines.append(f"{prefix} {node.label}{cluster_tag}")
    else:
        lines.append(f"{prefix} [d={node.dist:.2f}]")
        for i, child in enumerate(node.children, 1):
            _render(child, f"{prefix}.{i}", lines, manual_map)


def build_report(ssp_path: Path) -> str:
    mod = load_module(ssp_path)
    features: list[str] = list(mod.SSP_FEATURES.keys())
    positions: dict[str, JsonDict] = mod.SSP_POSITIONS
    clusters: dict[str, list[str]] = mod.SSP_CLUSTERS

    names = list(positions.keys())

    # Build reverse map: position → manual cluster name
    manual_map: dict[str, str] = {}
    for cname, members in clusters.items():
        for m in members:
            if m in manual_map:
                manual_map[m] += f", {cname}"   # overlap: position in 2 clusters
            else:
                manual_map[m] = cname

    # Agglomerative clustering (average linkage, precomputed distances)
    cdist = condensed_matrix(positions, features)
    Z = linkage(cdist, method="average")
    root = _build_tree(names, Z)

    lines: list[str] = []
    lines.append(f"# Cluster Dendrogram — {ssp_path.stem}")
    lines.append("")
    lines.append(f"SSP: `{ssp_path}`  |  Positions: {len(names)}  |  "
                 f"Features: {len(features)}")
    lines.append("")
    lines.append("Linkage: average. Distance: Hamming with wildcard=0.5.")
    lines.append("Leaf annotation: manual cluster from SSP_CLUSTERS.")
    lines.append("")
    lines.append("---")
    lines.append("")

    _render(root, "1", lines, manual_map)

    lines.append("")
    lines.append("---")
    lines.append("")

    # Overlap warnings
    overlaps = {p: c for p, c in manual_map.items() if "," in c}
    if overlaps:
        lines.append("### Cluster overlap (position in multiple manual clusters)")
        lines.append("")
        for p, c in overlaps.items():
            lines.append(f"- `{p}`: {c}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hierarchical cluster dendrogram for an SSP module.")
    parser.add_argument("ssp_path", help="Path to ssp_vN.py module")
    parser.add_argument("--stdout", action="store_true",
                        help="Print to stdout instead of writing cluster_analysis.md")
    args = parser.parse_args()

    path = Path(args.ssp_path)
    report = build_report(path)

    if args.stdout:
        print(report)
    else:
        out = path.parent / "cluster_analysis.md"
        out.write_text(report)
        print(f"Written: {out}")


if __name__ == "__main__":
    main()
