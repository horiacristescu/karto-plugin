---
name: induct
description: Given an SSP domain workspace (ssps/<domain>/), produce a new models/ssp_vN.py by running tail-to-head induction over the corpus. Works for first induction and re-induction.
applies-to: ssps/<domain>/
output: models/ssp_vN/ssp_vN.py (validated Python SSP module)
---

# Induction Skill

## Purpose

Induce a runnable SSP from a corpus. The output is `models/ssp_vN.py` — a valid Python module that exports `SSP_META`, `SSP_FEATURES`, `SSP_POSITIONS`, `SSP_CLUSTERS`, and `score()`. Multiple inductions of the same corpus produce a family of models for cross-comparison.

---

## Step 0 — Orient

From the domain folder root (`ssps/<domain>/`):

```bash
# What corpus do we have?
ls corpus/
ls corpus/raw/ 2>/dev/null
ls corpus/units/ 2>/dev/null || echo "not segmented yet"
ls corpus/traces/ 2>/dev/null || echo "not segmented yet"

# What models already exist?
ls models/ 2>/dev/null || echo "first induction"

# How many units?
ls corpus/units/*.json 2>/dev/null | wc -l
ls corpus/traces/*.json 2>/dev/null | wc -l
```

If units/traces don't exist yet → run the segmentation skill first (`skills/karto/segmentation.md`), then return here.

**First induction** (no `models/` or no `ssp_v*.py`): that is normal — proceed directly to Step 1. There is no prior vocabulary to consult; you induce purely from the corpus.

**Re-induction** (`models/ssp_v1.py` exists): read its `SSP_FEATURES` to understand the prior vocabulary. **Do not copy it** — start fresh from the corpus, independently. Note what features were used; divergence from v1 is the signal, not a mistake.

Determine the next version number: `N = max existing version + 1` (or 1 for first induction).

---

## Step 1 — Frame the induction

Answer four questions before touching any unit:

1. **Unit of analysis**: what is one position? (one proposition, one turn, one action, one case)
2. **Discriminator**: what label or outcome differentiates units most sharply? This will drive feature selection.
3. **Decomposition kind**: descriptive (classifying what something IS) or predictive (forecasting what will happen / what should be done)?
4. **Feature side**: are features describing the state, the action, or both?

Write answers as comments at the top of the new `ssp_vN.py` before writing any code.

---

## Step 2 — Sample units for leaf naming (tail-to-head)

Read 10–20 units from `corpus/units/` or `corpus/traces/`. For each:

**Name the leaf first** — what is this unit an example of? Use the discriminator from Step 1. Be specific: not "this is a batch cost case" but "weight-bandwidth-dominated decode regime."

Collect leaf names. Group similar ones. You should see 5–20 natural clusters emerge. These become your positions. If you see 50+, you are naming too specifically — abstract up one level.

```bash
# Read a sample
head -30 corpus/units/unit_001.json
head -30 corpus/units/unit_010.json
head -30 corpus/units/unit_025.json
# For large unit files: cat corpus/units/unit_001.json | python -c "import sys,json; d=json.load(sys.stdin); print(d['text'][:500])"
```

---

## Step 3 — Induce features (tail-to-head)

For each leaf cluster from Step 2, ask: **what distinguishes units in this cluster from units in other clusters?**

That answer IS a feature. Name it, then find its values:
- Values should be 3–6 per feature
- Use hyphenated lowercase strings: `below-balance`, `censored-by-policy`, `action-reframe`
- Values must be mutually exclusive within a feature
- Values must be exhaustive enough to cover all units you've seen

Repeat for each cluster pair until you stop finding new discriminating dimensions.

**Stopping rules** (enforce these):
- Hard stop at 15 features — warn yourself if approaching 12
- Stop adding features when: new features fire on fewer than 3 units, or two features always co-occur (one is redundant)
- After 3 rounds of refinement, treat further additions as overfit risk [41][43]

**Sparse features are fine** — if a feature only applies to some units, add a `none` value. Every position must declare every feature; `none` is the correct fill for "not applicable."

---

## Step 4 — Assign features to all units

For each unit in the corpus, assign one value per feature. You do not need to read every unit manually — sample deeply (30–50% of units), then infer the rest from the leaf cluster membership.

Group by leaf → record the feature-value tuple for each leaf cluster → these become `SSP_POSITIONS`.

Position names: descriptive, hyphenated, unique. Use the leaf name from Step 2 as the position name.

---

## Step 5 — Write ssp_vN.py

Create `models/ssp_vN/ssp_vN.py` (one subfolder per model version). Required structure:

```python
"""SSP module: <domain> — <one-line description>.

Source: corpus/<source description>.
Induction: <date>, fresh induction / re-induction from <prior version>.
Discriminator: <what label drove feature selection>.
"""

from __future__ import annotations
from typing import Any
JsonDict = dict[str, Any]

SSP_META: JsonDict = {
    "input_concept": "<what an input is>",
    "feature_concept": "<what a feature describes>",
    "state_concept": "<what a state/cluster is>",
    "leaf_concept": "<what a position is>",
    "maintainer": "karto-dev",
    "version": "0.1.0",
    "decomposition_kind": "descriptive",  # or "predictive"
}

SSP_FEATURES: dict[str, list[str]] = {
    "feature_name": ["value-a", "value-b", "value-c", "none"],
    # ...
}

_D: JsonDict = {f: "none" for f in SSP_FEATURES}  # default all-none

def _pos(**kw: str) -> JsonDict:
    p = dict(_D)
    p.update(kw)
    return p

SSP_POSITIONS: dict[str, JsonDict] = {
    "position-name": _pos(feature_name="value-a", ...),
    # one entry per leaf cluster
}

SSP_CLUSTERS: dict[str, list[str]] = {
    "cluster-name": ["position-name", ...],
    # group positions by natural affinity
}

def score_rules(record: JsonDict) -> dict:
    best, best_n = next(iter(SSP_POSITIONS)), 0
    for name, feats in SSP_POSITIONS.items():
        n = sum(1 for f, v in feats.items() if v != "none" and record.get(f) == v)
        if n > best_n:
            best, best_n = name, n
    return {"result": best, "backend": "rules", "confidence": 0.5}

def score(record: JsonDict) -> dict:
    return score_rules(record)
```

---

## Step 6 — Validate

```bash
python -m karto.validate models/ssp_vN/ssp_vN.py
```

Fix any errors. Common issues:
- Position missing a feature → add it with `none`
- Illegal value (not in declared list) → add to `SSP_FEATURES` or correct the assignment
- SSP_META not JSON-serializable → use plain strings and dicts only

---

## Step 7 — Compare with prior model (if re-induction)

If `ssp_v1.py` exists, compare (substitute the actual filenames for `ssp_v1.py` and `ssp_vN.py`):

```bash
# Features in v1 not in v2 (dropped)
python -c "
import importlib.util, sys
def load(p):
    s = importlib.util.spec_from_file_location('m', p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
v1 = load('models/ssp_v1/ssp_v1.py'); v2 = load('models/ssp_v2/ssp_v2.py')  # adjust version numbers
print('dropped:', set(v1.SSP_FEATURES) - set(v2.SSP_FEATURES))
print('added:',   set(v2.SSP_FEATURES) - set(v1.SSP_FEATURES))
print('shared:',  set(v1.SSP_FEATURES) & set(v2.SSP_FEATURES))
"
```

- **Shared features** across independent inductions = robust domain signal
- **Features unique to one induction** = either corpus-artifact or perspective-specific; flag for vetting
- **Position count difference** = different granularity choice; neither is wrong

Record findings as a comment block at the top of `ssp_vN.py`.

---

## Outputs

| Path | Contents |
|------|----------|
| `models/ssp_vN/ssp_vN.py` | Validated SSP Python module |
| Comment block in file | Induction date, discriminator, comparison notes vs prior version |

The model is ready for use with `python -m karto.validate models/ssp_vN/ssp_vN.py` and `score()`.
