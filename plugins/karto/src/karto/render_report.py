#!/usr/bin/env python3
"""Render a belief-state JSON map to PNG + Markdown audit.

Mirrors the belief_state web app's PCA exactly (one-hot encode, eigendecomp of
X^T X / (n-1), no centering by default). Produces:

  - PNG: PC1 x PC2 scatter, points colored by cluster, axis-aligned cluster
    bboxes drawn behind the points.
  - Markdown audit: variance explained, per-feature contributions to each PC,
    k-nearest-neighbors per point, cluster purity, bbox collisions, misplaced
    points (all kNN in different clusters).

Usage:
    python -m karto.render_report ssps/romanian_politics/models/ssp_v1/ssp_v1.json
    python -m karto.render_report ssps/automation_jobs/models/ssp_v4/ssp_v4.py
    python -m karto.render_report path/to/ssp.json --png out.png --audit out.md --k 5
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from types import ModuleType

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from karto.loader import load_module


def ssp_to_dict(mod: ModuleType) -> dict:
    """Convert SSP Python module attributes to the dict that encode() expects."""
    meta = getattr(mod, "SSP_META", {})
    features = mod.SSP_FEATURES
    positions = mod.SSP_POSITIONS
    clusters: dict[str, list[str]] = getattr(mod, "SSP_CLUSTERS", {})
    if not clusters:
        clusters = {"all": list(positions.keys())}
    return {
        "core_topic": {"domain": meta.get("state_concept") or meta.get("input_concept", "SSP")},
        "state_features": features,
        "positions": positions,
        "clusters": clusters,
        "cluster_labels": {name: {"name": name} for name in clusters},
        "axis_labels": {"xAxis": {}, "yAxis": {}},
    }


def encode(d: dict):
    """One-hot encode the positions matrix (matches fileLoader.ts:positionsToMatrix)."""
    pos_names = list(d["positions"].keys())
    feat_names = list(d["state_features"].keys())
    feat_cols: dict[str, list[int]] = {}
    col_index: dict[int, tuple[str, str]] = {}
    col = 0
    for fn in feat_names:
        feat_cols[fn] = []
        for v in d["state_features"][fn]:
            col_index[col] = (fn, v)
            feat_cols[fn].append(col)
            col += 1
    M = np.zeros((len(pos_names), col))
    for r, pname in enumerate(pos_names):
        for fn in feat_names:
            v = d["positions"][pname][fn]
            c = feat_cols[fn][d["state_features"][fn].index(v)]
            M[r, c] = 1.0
    return M, pos_names, feat_names, feat_cols, col_index


def pca(M: np.ndarray, n_components: int = 2, center: bool = False):
    """Web app's algorithm: cov = X^T X / (n-1), eigendecomp, project.

    Sign-canonicalization: flip each PC so its column-sum is non-negative,
    matching the web app's power-iteration orientation.
    """
    X = M - M.mean(0) if center else M
    cov = X.T @ X / (X.shape[0] - 1)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    components = eigvecs[:, :n_components].copy()
    for k in range(n_components):
        if components[:, k].sum() < 0:
            components[:, k] = -components[:, k]
    projected = X @ components
    return projected, components, eigvals[:n_components], float(np.trace(cov))


def feature_contribs(component: np.ndarray, feat_names, feat_cols) -> dict[str, float]:
    """Per-feature share of a PC's variance — sums to 1.0 across features."""
    return {fn: float(sum(component[c] ** 2 for c in feat_cols[fn])) for fn in feat_names}


def knn(coords: np.ndarray, pos_names, k: int = 3) -> dict[str, list[str]]:
    N = len(pos_names)
    dist = np.full((N, N), np.inf)
    for i in range(N):
        for j in range(N):
            if i != j:
                dist[i, j] = float(np.linalg.norm(coords[i] - coords[j]))
    return {pos_names[i]: [pos_names[j] for j in np.argsort(dist[i])[:k]] for i in range(N)}


def cluster_bboxes(coords: np.ndarray, clusters: dict, pos_names) -> dict[str, tuple]:
    name_to_idx = {n: i for i, n in enumerate(pos_names)}
    boxes = {}
    for cname, members in clusters.items():
        idx = [name_to_idx[m] for m in members]
        c = coords[idx]
        boxes[cname] = (float(c[:, 0].min()), float(c[:, 1].min()),
                        float(c[:, 0].max()), float(c[:, 1].max()))
    return boxes


def collisions(coords: np.ndarray, pos_names, clusters: dict, boxes: dict, pad: float = 0.0):
    """Foreign points that fall inside another cluster's bbox."""
    cluster_of = {m: c for c, ms in clusters.items() for m in ms}
    name_to_idx = {n: i for i, n in enumerate(pos_names)}
    out = []
    for cname, (x0, y0, x1, y1) in boxes.items():
        for pname in pos_names:
            if cluster_of[pname] == cname:
                continue
            x, y = coords[name_to_idx[pname]]
            if x0 - pad <= x <= x1 + pad and y0 - pad <= y <= y1 + pad:
                out.append((pname, cluster_of[pname], cname))
    return out


def render(coords, pos_names, clusters, cluster_labels, axis_labels, boxes, png_path,
           pc1_var, pc2_var, title):
    fig, ax = plt.subplots(figsize=(16, 10))
    cluster_colors = plt.get_cmap("tab10")(np.linspace(0, 1, max(10, len(clusters))))
    cluster_color = dict(zip(clusters.keys(), cluster_colors))

    for cname, (x0, y0, x1, y1) in boxes.items():
        pad_x = max(0.05, (x1 - x0) * 0.04)
        pad_y = max(0.05, (y1 - y0) * 0.04)
        rect = mpatches.FancyBboxPatch(
            (x0 - pad_x, y0 - pad_y),
            (x1 - x0) + 2 * pad_x,
            (y1 - y0) + 2 * pad_y,
            boxstyle="round,pad=0.02",
            fill=True, alpha=0.10,
            edgecolor=cluster_color[cname], facecolor=cluster_color[cname],
            linewidth=2, linestyle="--",
        )
        ax.add_patch(rect)
        label = cluster_labels.get(cname, {}).get("name", cname)
        ax.text(x0 - pad_x, y1 + pad_y + 0.03, f"[{cname}] {label}",
                color=cluster_color[cname], fontsize=9, weight="bold")

    name_to_idx = {n: i for i, n in enumerate(pos_names)}
    cluster_of = {m: c for c, ms in clusters.items() for m in ms}
    for pname in pos_names:
        x, y = coords[name_to_idx[pname]]
        c = cluster_color[cluster_of[pname]]
        ax.scatter(x, y, c=[c], s=80, alpha=0.9, edgecolors="black", linewidths=0.5, zorder=3)
        ax.annotate(pname, (x, y), fontsize=7, alpha=0.75,
                    xytext=(4, 4), textcoords="offset points", zorder=4)

    xax = axis_labels.get("xAxis", {})
    yax = axis_labels.get("yAxis", {})
    ax.set_xlabel(
        f"PC1 ({pc1_var*100:.1f}%) — {xax.get('label','')}: "
        f"{xax.get('from','')} → {xax.get('to','')}", fontsize=10)
    ax.set_ylabel(
        f"PC2 ({pc2_var*100:.1f}%) — {yax.get('label','')}: "
        f"{yax.get('from','')} → {yax.get('to','')}", fontsize=10)
    ax.set_title(f"{title} — PCA projection of belief-state JSON")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(png_path, dpi=120)
    plt.close(fig)


def write_audit(audit_path: Path, *, json_path, pos_names, feat_names, clusters,
                cluster_labels, pc1_var, pc2_var, pc1_contrib, pc2_contrib,
                nn, k, purity, bbox_collisions, misplaced):
    cluster_of = {m: c for c, ms in clusters.items() for m in ms}
    L: list[str] = []
    L.append(f"# Map audit — `{json_path.name}`")
    L.append("")
    L.append("## Variance explained")
    L.append(f"- **PC1**: {pc1_var*100:.1f}%")
    L.append(f"- **PC2**: {pc2_var*100:.1f}%")
    L.append(f"- **PC1+PC2**: {(pc1_var+pc2_var)*100:.1f}%")
    L.append("")
    L.append("## Per-feature contributions to PC1 (sum = 1.0)")
    L.append("")
    L.append("| Feature | Contribution |")
    L.append("|---|---|")
    for fn, c in sorted(pc1_contrib.items(), key=lambda kv: -kv[1]):
        L.append(f"| {fn} | {c:.3f} |")
    L.append("")
    L.append("## Per-feature contributions to PC2 (sum = 1.0)")
    L.append("")
    L.append("| Feature | Contribution |")
    L.append("|---|---|")
    for fn, c in sorted(pc2_contrib.items(), key=lambda kv: -kv[1]):
        L.append(f"| {fn} | {c:.3f} |")
    L.append("")
    L.append(f"## Cluster purity ({k}-NN, fraction of neighbors in own cluster)")
    L.append("")
    L.append("| Cluster | Name | Same / Total | % |")
    L.append("|---|---|---|---|")
    for cname in sorted(clusters):
        s, t, pct = purity[cname]
        name = cluster_labels.get(cname, {}).get("name", cname)
        L.append(f"| {cname} | {name} | {s}/{t} | {pct:.0f}% |")
    L.append("")
    L.append(f"## {k}-nearest neighbors per point (sorted by cluster)")
    for cname in sorted(clusters):
        L.append("")
        name = cluster_labels.get(cname, {}).get("name", cname)
        L.append(f"### [{cname}] {name}")
        L.append("")
        for m in sorted(clusters[cname]):
            nn_str = ", ".join(f"`{n}`[{cluster_of[n]}]" for n in nn[m])
            L.append(f"- `{m}` → {nn_str}")
    L.append("")
    L.append(f"## Cluster bbox collisions ({len(bbox_collisions)} foreign points inside other cluster bboxes)")
    L.append("")
    if not bbox_collisions:
        L.append("_(none — clusters are spatially disjoint at the bbox level)_")
    else:
        per_cluster: dict[str, list] = defaultdict(list)
        for pname, own, foreign_box in bbox_collisions:
            per_cluster[foreign_box].append((pname, own))
        for foreign_box in sorted(per_cluster):
            name = cluster_labels.get(foreign_box, {}).get("name", foreign_box)
            L.append(f"### Inside bbox of [{foreign_box}] {name}")
            L.append("")
            for pname, own in sorted(per_cluster[foreign_box]):
                L.append(f"- `{pname}` (own cluster: **{own}**)")
            L.append("")
    L.append(f"## Misplaced points (all {k} nearest neighbors in different clusters)")
    L.append("")
    if not misplaced:
        L.append("_(none)_")
    else:
        for m, own, neighbors in misplaced:
            nn_str = ", ".join(f"`{n}`[{cluster_of[n]}]" for n in neighbors)
            L.append(f"- `{m}` [own: **{own}**] → {nn_str}")
    L.append("")
    audit_path.write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ssp_path", type=Path, help=".json or .py SSP file")
    ap.add_argument("--png", type=Path, default=None,
                    help="output PNG (default: alongside input, named map.png)")
    ap.add_argument("--audit", type=Path, default=None,
                    help="output Markdown audit (default: alongside input, named map_audit.md)")
    ap.add_argument("--k", type=int, default=3, help="k for kNN (default 3)")
    ap.add_argument("--center", action="store_true",
                    help="mean-center before PCA (web app default is no centering)")
    ap.add_argument("--features", default=None,
                    help="comma-separated subset of features to use (default: all). "
                         "Useful for triangulation — render the same JSON under different "
                         "feature subsets to see which relationships are robust vs encoded.")
    args = ap.parse_args()

    png_path = args.png or args.ssp_path.parent / "map.png"
    audit_path = args.audit or args.ssp_path.parent / "map_audit.md"

    if args.ssp_path.suffix == ".py":
        d = ssp_to_dict(load_module(args.ssp_path))
    else:
        d = json.loads(args.ssp_path.read_text())
    if args.features:
        keep = [f.strip() for f in args.features.split(",")]
        missing = [f for f in keep if f not in d["state_features"]]
        if missing:
            raise SystemExit(f"unknown features: {missing}; available: {list(d['state_features'])}")
        d = {**d,
             "state_features": {f: d["state_features"][f] for f in keep},
             "positions": {p: {f: v[f] for f in keep} for p, v in d["positions"].items()}}
        print(f"Filtered to features: {keep}")

    title = d.get("core_topic", {}).get("domain", "SSP")

    M, pos_names, feat_names, feat_cols, _ = encode(d)
    coords, comps, evals, total_var = pca(M, n_components=2, center=args.center)
    pc1_var = evals[0] / total_var
    pc2_var = evals[1] / total_var
    pc1_contrib = feature_contribs(comps[:, 0], feat_names, feat_cols)
    pc2_contrib = feature_contribs(comps[:, 1], feat_names, feat_cols)

    nn = knn(coords, pos_names, k=args.k)
    boxes = cluster_bboxes(coords, d["clusters"], pos_names)
    bbox_collisions = collisions(coords, pos_names, d["clusters"], boxes)

    cluster_of = {m: c for c, ms in d["clusters"].items() for m in ms}
    purity: dict[str, tuple[int, int, float]] = {}
    for cname, members in d["clusters"].items():
        same = total = 0
        for m in members:
            for n in nn[m]:
                total += 1
                if cluster_of[n] == cname:
                    same += 1
        purity[cname] = (same, total, same / total * 100 if total else 0.0)

    misplaced = []
    for m in pos_names:
        own = cluster_of[m]
        if all(cluster_of[n] != own for n in nn[m]):
            misplaced.append((m, own, nn[m]))

    render(coords, pos_names, d["clusters"], d["cluster_labels"], d["axis_labels"],
           boxes, png_path, pc1_var, pc2_var, title)

    write_audit(audit_path, json_path=args.ssp_path,
                pos_names=pos_names, feat_names=feat_names,
                clusters=d["clusters"], cluster_labels=d["cluster_labels"],
                pc1_var=pc1_var, pc2_var=pc2_var,
                pc1_contrib=pc1_contrib, pc2_contrib=pc2_contrib,
                nn=nn, k=args.k, purity=purity,
                bbox_collisions=bbox_collisions, misplaced=misplaced)

    print(f"json:   {args.ssp_path}")
    print(f"png:    {png_path}")
    print(f"audit:  {audit_path}")
    print(f"PC1: {pc1_var*100:.1f}%   PC2: {pc2_var*100:.1f}%   PC1+PC2: {(pc1_var+pc2_var)*100:.1f}%")
    avg_purity = sum(p[2] for p in purity.values()) / len(purity)
    print(f"avg cluster purity ({args.k}-NN): {avg_purity:.0f}%")
    print(f"bbox collisions: {len(bbox_collisions)}")
    print(f"misplaced (all {args.k}-NN foreign): {len(misplaced)}")


if __name__ == "__main__":
    main()
