---
name: ssp_analysis
description: Run kNN and dendrogram analysis on any SSP module and interpret output using domain-expert reasoning, not mechanical distance reporting.
applies-to: ssps/<domain>/models/ssp_vN/ssp_vN.py
output: knn_analysis.md, cluster_analysis.md alongside the SSP module
---

# SSP Analysis Skill

## Purpose

Validate an induced SSP by running two structural diagnostics: kNN neighbor analysis and hierarchical clustering. The tools produce markdown files; this skill tells you how to read them with domain judgment — asking whether the geometry matches what you know about the domain, not just whether the numbers are valid.

Run these after every induction or significant SSP edit.

---

## Criteria for a correct SSP

These are the tests the analysis is measuring against. Every finding in Steps 2–6 traces to one of these.

**1. Discriminability** — Each position must have a unique feature vector, distinguishable from every other position. Violation: near-duplicates (d ≤ 1.5). Fix: add a discriminating feature, or merge if no operational distinction exists.

**2. Specification** — Each position must have enough non-wildcard features to be meaningfully placed in the space. Violation: wildcard gravity wells (>half features are wildcards). Fix: identify the features that should discriminate this position and assign real values, or split into more specific positions.

**3. Cluster coherence** — Positions in the same `SSP_CLUSTERS` group should be closer to each other than to positions in other groups. The dendrogram should form contiguous subtrees per cluster at some consistent merge distance. Violation: a cluster member appears in a foreign subtree. Fix: reassign the position, or restructure the cluster.

**4. Operational validity** — Each position must correspond to a real, recognizable operational situation — something an expert would name and navigate. It must have a describable entry condition ("you're in this regime when X") and an exit condition ("you leave when Y"). Violation: a position that is a topic, a concept, or a design choice rather than a state an expert navigates. Fix: either sharpen the position's entry/exit signals and add the features that discriminate them, or remove it.

**5. Feature economy** — Every declared feature must discriminate at least 3 positions from each other. A feature with the same value across all positions is dead weight. Violation: a feature that fires "none" or the same value everywhere. Fix: remove the feature, or find the positions that should differ on it.

**6. Coverage** — Every corpus unit should fall within distance d ≤ 2.0 of some position. A corpus unit far from all positions is a coverage gap — a real situation the SSP doesn't model. Violation: corpus units cluster in a region with no position. Fix: add a position. (This criterion requires the coverage tool — Step 7 extensibility — not yet implemented; flag gaps manually during corpus verification in Step 5.)

**7. Cluster completeness** — Every position belongs to exactly one `SSP_CLUSTERS` group. No position is in two groups (overlap bug); no position is unassigned (orphan). Violation: cluster overlap warnings in `cluster_analysis.md`. Fix: assign the overlap position to one group only.

**8. Predictive validity** — Each position must reliably predict what actions or stances are appropriate in that situation. Test: complete the sentence "if you're in this position, you should ___" with something specific and non-trivial. If the completion is the same for all positions, or if it's too vague to act on, the position isn't earning its place. Violation: a position that describes a situation without implying any different behavior from adjacent positions. Fix: sharpen the position's entry/exit conditions, or merge it with a neighbor it fails to predict differently from.

**9. Feature relevance** — Each feature must differentiate positions in a way that matters for the domain — not just produce unique vectors, but carve the space at joints an expert would recognize. A feature that fires differently across positions but for no meaningful operational reason (e.g., discriminating by which section of a talk something appeared in, not by what's actually true of the regime) is noise. Test: for each feature value, can you say what operational situation that value implies? If not, the feature is tracking a corpus artifact, not a domain property.

**10. Domain logic validity** — The analysis itself must apply domain knowledge, not just report distances. Every finding must be evaluated against what is true about the domain: does this grouping make sense for how an expert navigates this space? A mathematically coherent cluster that groups situations an expert would never treat similarly is wrong, even if the distances are small. Criterion: after stating a finding (e.g., "these two positions are near-duplicates"), ask "is this finding supported by domain reasoning, or just by a distance?" If only by distance, go to the corpus before concluding. The analysis is not done until each finding has a domain justification, not just a metric one.

---

## Step 1 — Run kNN analysis

```bash
# From the karto project root:
python -m karto.knn_report ssps/<domain>/models/ssp_vN/ssp_vN.py
# Output: ssps/<domain>/models/ssp_vN/knn_analysis.md
# Or print to stdout for quick inspection:
python -m karto.knn_report ssps/<domain>/models/ssp_vN/ssp_vN.py --stdout
```

The report produces one section per position: a table of its 5 nearest neighbors with distances and differing features, then a Summary Findings section listing near-duplicates (d ≤ 1.5), wildcard gravity wells (>half the features are wildcards), and isolated positions (nearest neighbor d ≥ 4.0).

---

## Step 2 — Interpret kNN output

For each position, ask:

**Neighborhood sanity:** Given what this position IS (its SSP name and discriminator label), are its neighbors the right ones? If position A's nearest neighbor is B, can you articulate why an expert would consider B the closest situation to A? If not, either the feature set doesn't capture the real discriminator, or one of the positions is underspecified.

**Near-duplicates (d ≤ 1.5):** Are these genuinely distinct operational situations, or has induction created two names for the same thing? To tell them apart: describe a concrete case that belongs to one but not the other. If you can't, merge them. If you can, verify the differing features are the correct discriminators — not noise.

**Gravity wells (wildcard-heavy positions):** Is this position legitimately general — a real "applies everywhere" regime — or is it underspecified? A real general position should have a clear entry signal ("you're in this regime when X is true") even if many features are wildcards. An underspecified position has wildcards because the induction didn't find discriminating features, not because the situation genuinely applies everywhere. Underspecified positions pollute kNN by appearing close to everything.

**Isolated positions (nearest neighbor d ≥ 4.0):** Isolation is not automatically a problem. Ask: (a) Is the position real but rare in the corpus — a legitimate outlier? (b) Does it belong to a different discriminator than the rest of the SSP? (c) Is it an artifact of wildcard inflation in its neighbors, making it appear farther than it is? If the position is real and rare, note it. If it belongs elsewhere, park it.

---

## Step 3 — Run dendrogram analysis

```bash
python -m karto.cluster_report ssps/<domain>/models/ssp_vN/ssp_vN.py
# Output: ssps/<domain>/models/ssp_vN/cluster_analysis.md
python -m karto.cluster_report ssps/<domain>/models/ssp_vN/ssp_vN.py --stdout
```

The report renders the agglomerative dendrogram as an outline-numbered tree. Internal nodes show the merge distance `[d=X.XX]`; leaves show position names with their manual cluster annotation `[cluster-name]`. Cluster overlap warnings appear at the bottom (positions assigned to multiple manual clusters).

---

## Step 4 — Interpret dendrogram output

Read the tree top-down:

**Top-level splits (highest merge distance):** The deepest branches separate the most fundamentally different situations. Do these top-level divisions reflect real domain boundaries — operational boundaries an expert would immediately recognize? If the top split is between two positions that seem similar, and very different positions are merged early, the distance metric or feature set is not capturing the right discriminators.

**Subtree coherence:** For each internal node, name the shared property of its leaves in one sentence. If you cannot name it — if the subtree seems arbitrary — the grouping is accidental, likely caused by shared wildcards rather than shared domain structure. Shared wildcards are noise; shared feature values are signal.

**Manual cluster alignment:** For each `SSP_CLUSTERS` group, find its members in the dendrogram. Correct manual clusters form contiguous subtrees at some merge distance. A cluster member that appears in a different subtree is a misassignment candidate. Check: does that member's dendrogram siblings share its manual cluster? If not, compare the merge distance at which it joins its assigned cluster vs. the distance at which it joins its dendrogram siblings — the latter tells you where the data actually places it.

**Distance gap analysis:** Find the largest jump between consecutive merge distances in the tree. That gap marks the most natural cluster boundary. Compare it to where `SSP_CLUSTERS` draws its boundaries. If the natural gap and the manual boundary agree, the manual clusters are data-supported. If they disagree, ask why: is the manual grouping driven by semantic knowledge the features don't capture, or is it a mistake?

**Wildcard inflation artifact:** A position with many wildcard features appears at low distance from everything — it merges early and distorts the tree structure around it. Identify these positions (they appear in the Summary Findings of kNN as gravity wells). When interpreting subtrees containing them, ask: does this subtree reflect genuine similarity, or is it only because the wildcard position pulls others close? If wildcard inflation is distorting the tree, consider whether the position needs more feature specification, or whether it should be excluded from clustering.

**Cluster overlap warnings:** A position appearing in two manual clusters is a bug, not a feature. Identify which cluster it actually belongs to by its dendrogram position.

---

## Step 5 — Verify doubts against corpus

When analysis raises a doubt — a near-duplicate, a misassigned position, an unexpected neighbor, a subtree that doesn't cohere — **go back to the source before concluding**. The tools work on the feature vector abstraction; the corpus has the ground truth.

For each flagged position, find corpus units that were assigned to it during induction:

```bash
# Units are in corpus/units/ or corpus/traces/
ls ssps/<domain>/corpus/units/
ls ssps/<domain>/corpus/traces/

# Read units to check what the position was actually induced from
head -50 ssps/<domain>/corpus/units/unit_001.json
```

Ask for each doubt:

**Near-duplicate (A ↔ B, d ≤ 1.5):** Read 2–3 corpus units labeled A and 2–3 labeled B. Can you tell them apart without looking at the labels? If yes — what is the operational difference? If no — one of them should be folded in.

**Unexpected neighbor:** Read a corpus unit for the flagged position and a unit for its unexpected neighbor. Is the distance surprising after reading the actual text, or does it make more sense than expected? The feature vector is a lossy projection — the source may confirm or refute the distance.

**Misassigned position (wrong subtree):** Read corpus units for the position and for each of: (a) its dendrogram siblings, (b) its manual cluster siblings. Which group does the actual text feel like it belongs to?

**Wildcard gravity well:** Read the position's source units. Are they genuinely ambiguous across the wildcard features — or did the induction just fail to assign values because the discriminating signal was subtle? Subtle signal → add a feature. Genuine ambiguity → the wildcards are correct.

Document what the corpus confirms or overturns. If a doubt is resolved by the corpus, annotate the `SSP_CLUSTERS` or position comment in the SSP module. If it opens a bigger question, park it for a follow-up task.

---

## Step 6 — Write findings and proposed fixes

After running both tools and applying the interpretation above, write a findings section with two parts:

**Part A — Issues found.** For each issue, one sentence: what is wrong, and what evidence (distance, subtree position, corpus read) confirms it.

1. Which positions are misassigned in `SSP_CLUSTERS` — what cluster does the dendrogram actually place them in?
2. Which positions are underspecified (wildcard inflation) — which features fire as wildcards that shouldn't?
3. Which near-duplicates should be merged?
4. Which positions are missing — what operational situations appear in the corpus but have no position?
5. What does the top-level tree structure reveal about domain structure that the flat cluster list obscures?

**Part B — Proposed fixes.** For each issue, a concrete proposed fix. Fixes fall into these categories:

- **Add a feature**: name the feature, its values (3–6), and which positions it would differentiate. Use this when two positions are near-duplicates but operationally distinct — the missing feature is the discriminator.
- **Add a feature value**: the feature exists but its declared values don't cover a real case. Name the new value and which positions would use it.
- **Add a position**: a cluster of corpus units doesn't match any existing position well. Name the position, sketch its feature vector, and say which cluster it belongs in.
- **Merge positions**: two near-duplicates with no operational distinction. Name the survivor (usually the more general name) and what happens to units currently assigned to the merged one.
- **Reassign to cluster**: a position belongs in a different `SSP_CLUSTERS` group. Name the current group, the correct group, and why.
- **Remove a position**: a gravity well with no real entry signal — just wildcard noise. Check the corpus first: if real units depend on it, don't remove; add features instead.
- **Update score policy**: `score_rules()` or `score_catboost` is routing wrong because the feature vector changed. Flag which positions need updated scoring logic.

Write proposed fixes in order of impact — misassignments and underspecifications before removals, since removals are destructive. If the fix requires corpus verification you haven't done yet, mark it `[needs corpus check]`.

If findings imply SSP edits, open a new task for that work — don't edit the SSP inline during analysis. The analysis task's job is to produce a clear fix list, not to apply it.

---

## Outputs

| Path | Contents |
|------|----------|
| `models/ssp_vN/knn_analysis.md` | Per-position neighbor tables, Summary Findings |
| `models/ssp_vN/cluster_analysis.md` | Dendrogram tree with manual cluster annotations |

---

## Future analysis types (extensibility)

Additional analysis tools can be added to `src/karto/` and documented here:

- **Self-score test** (`score_report.py`): run `score()` on corpus units with known labels; measure position assignment accuracy. Tests whether the rule-based scorer agrees with the induction.
- **Coverage test**: for each corpus unit, compute distance to nearest SSP position. Units beyond a threshold distance indicate coverage gaps — the SSP needs a new position.
- **Cross-version comparison** (`diff_report.py`): two SSP modules from the same corpus; show which positions migrated, merged, or split. Tests induction stability.
- **Feature importance** (`feature_report.py`): which features drive the most between-cluster distance? Which features are uniform across all positions (dead features)?

Each tool follows the same pattern: `python -m karto.<tool> <ssp_path> [--stdout]`, writes a `*_analysis.md` file alongside the SSP module.
