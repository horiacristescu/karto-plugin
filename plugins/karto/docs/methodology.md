# SSP Methodology Reference

Full-detail companion to `MIND_MAP.md` nodes [35]–[45]. MIND_MAP carries the routing pointer + key dev insight; this file carries the reasoning.

---

## Mirror Thesis [35]

An SSP as pure text is weak — read once, agreed with, forgotten. Rendered as a runnable model it works like a mirror, flagging inconsistencies in either the data or the SSP itself by forcing disagreement to become legible. The mirror doesn't tell you what's true; it makes the gap between your model and reality visible enough that you can't unsee it.

This is the load-bearing claim of the project, retroactively justifying several commitments: discriminations not embeddings [13] (embeddings reflect disagreement but not which axis drove it; discrete SSPs preserve legibility so the mirror can say "you're wrong about axis X"), vector-as-data not prompt-as-runtime [10] (materialization makes the SSP cheap enough to use as a continuous mirror), ensemble SSPs [11] (multiple mirrors cross-checking; disagreement is itself signal), and calibrate confidence to consequence [5] (the compass works because the mirror tells you when you've outrun your trust budget).

Without rendering it as something that can disagree with you, you cannot tell when you are wrong.

---

## Consumption Modes and Lifecycle [36]

**Two consumption modes** always coexist on the same artifact:
- **Read-mode**: human directly consumes for understanding via narrative, flashcards, slides, neighborhood walk, viewer
- **Run-mode**: agent applies SSP to inputs and emits scored positions via scoring API or classifier or policy

What varies between use-cases is which mode dominates; the other is always present. Operational SSPs need read-mode for debug/audit/drift; didactic SSPs need run-mode for self-test/drill generation.

**Three lifecycle stages:**
- **Stage A — Research**: induct, walk, narrate, ensemble cross-check, internalize. Read-mode-dominant. Tolerates incompleteness and ensemble disagreement. Many use-cases stop here.
- **Stage B — Operationalize**: assign per-feature backends, train substrate, build eval harness. Needs locked schemas. Explicit `karto promote` gesture marks the A→B boundary.
- **Stage C — Operate**: apply, monitor drift, debug failures. Read-mode returns for diagnostic walking.

**Six use-cases** all over the same artifact: domain expertise breakdown, agent policy/classifier, learning materials production for others, architectural design support, runtime cross-checker, and learning-by-construction (the human builds the SSP to learn the domain — deliverable is the user's internalized model, not the SSP itself).

**Vetting** is first-class throughout, not a bottleneck step at the end — happens at every transition (framing decision, leaf-naming, feature naming, cluster definition, axis interpretation, triage, substrate behavior). HITL as legitimacy mechanism, not as cost.

---

## Inputs and the Discrete Coordinate System [37]

**Single input pipeline**: seed (idea / domain / question / problem / expertise space) plus optional grounding (traces / documents / papers / reference data) feeds subagent sampling producing a sampled trajectory corpus that IS the dataset. Variability lives in the seed (what you're mapping) and grounding (what anchors the sampling) — pure-idea seeds have no grounding, trace-grounded sampling has rich grounding, but the same generation pipeline runs in both cases.

**Compositional state/action spaces**: both are bags over discrete features, not atoms. State space = bags over {f_i ∈ V_i}; action space = bags over {a_j ∈ U_j} (compositional) or atomic a ∈ U (degenerate). The standard (S, A) formalism is the special case where both bags collapse to single values. Compositional generalization justifies action-side feature induction (crowdstrike's `action_type`, `api_domain`, `in_question_tactic` are action-side features, not state).

**Data shapes**:
- **Sequence**: (s_0, a_0) → (s_1, a_1) → ... — trajectories enabling transition modeling (policy + dynamics). CUA, conversations, agent runs.
- **Collection**: {(s_k, a_k)} scattered points — distribution modeling only, no dynamics. Papers, cases, methods.

Most existing SSPs are atemporal collections; CUA work needs the temporal extension. The `karto apply` perception step assigns (s(x), a(x)) feature-bags to each example — this discretization step IS what makes the SSP runnable.

---

## Induction: Framing-First, Tail-to-Head, Labels-Induce-States [38]

**The key hinge**: labels DEFINE features, not the other way around. A "state" is the set of points sharing a feature-value, where the feature was named by asking "what discriminates this label?" Choosing labels = choosing the SSP's structure. Features cluster the space the way the labels carve it.

**Four-prong framing decision**:
1. Unit of analysis — what's a position?
2. State-side feature space — what describes a state?
3. Action-side feature space — what describes an action?
4. Discriminator — which label drives induction?

Different framings yield different SSPs from the same data; ensemble inductions vary the framing to find robust features.

**Tail-to-head algorithm** (within a framing):
1. For each example, name the leaf (position / stance / action / outcome)
2. For each leaf-value, find features distinguishing examples with that leaf from examples with other leaf-values
3. Discretize features into 3-6 hyphenated categorical values per feature
4. Cluster feature-value combinations into named states (or let states emerge as feature-bags)

This is the inverse problem: standard ML maps state → action; SSP induction observes leaves and reverse-engineers states. The leaf is what you can label cheaply and reliably; the state must be inferred. Every feature is named in the act of being induced — interpretability is built-in, not retrofit.

---

## Substrate Fungibility [39]

The same SSP feature space is scoreable by three substrate types:

| Substrate | Interpretability | Coverage | Audit | When to use |
|---|---|---|---|---|
| Python rules | Maximal (every decision = one rule) | Weak on soft combinators | Excellent (line-readable) | Early iteration, audit, debug |
| CatBoost | Global SHAP + per-case SHAP (inferred) | Strong (learns interactions) | Medium | Soft combinators, unanticipated interactions |
| Small-LLM | LLM reasoning trace only | Very strong (novel framings) | Weak (no fixed decision tree) | Coverage, novel inputs |

**Substrate-pairing as cross-check**: run two substrates over the same SSP, treat disagreement as signal — CatBoost-wins → rules likely missing a soft interaction; rules-wins → CatBoost likely overfit.

**The durable artifact insight**: the SSP is the durable artifact because it survives multiple substrate generations. Heavy spending on induction (Layer 1) is justified since the substrate (Layer 3) is replaceable. This is why substrate-fungibility is a first-class design property, not just a nice-to-have.

Semlabel adds Tier-1.5 between regex and small-LLM — see [Semlabel as Backend](#semlabel-backend).

---

## Closed-Loop Pipeline [40]

The full methodology loop:

```
frame [38] → sample [37] → tail-to-head induce [38]
  → VET (features, cluster definitions, axis names)
  → perceive (assign feature-values to each example)
  → VET (sanity-check perception assignments)
  → train substrate [39]
  → VET (inspect decision rules / SHAP / prompt behavior)
  → deploy on new traces
  → detect disagreement
  → triage [41]
  → refine (new features / retrain / park)
  → ↺ back to induce
```

Vetting is integrated at each transition, not appended at the end. Two flavors of new traces:
- **Same-distribution**: disagreement signals drift, coverage gap, or label noise
- **Different-corpus probe**: deliberate generalization test (p1/p5/p6/p7 cross-checks); disagreement signals where the inducing lens doesn't transfer

Without the deploy → detect steps, the SSP is back to inert text — the loop is what makes it a mirror.

---

## Triage Taxonomy [41]

**3-bucket (classification SSPs)**:
1. **Feature gap** — model lacks a discriminating feature; induce it, retrain
2. **Label noise** — ground truth wrong, subjective, or ambiguous; flag or accept boundary
3. **DK gap** — domain knowledge missing outside what the corpus supports; park or extend corpus

**4-bucket extension (policy/predictive SSPs)** — adds:
4. **Multi-valid** — both actions reasonable, not a real disagreement
5. **Trace error** — demonstrator was wrong; the model is actually better (model becomes critic of corpus). Only applies to predictive SSPs where demonstrator ≠ optimal.

**5th bucket (both kinds)**:
5. **Segmentation gap** — disagreement comes from a unit being two things lumped together OR one thing split apart. See `docs/architecture.md#segmentation`.

**3-round stopping heuristic**: empirical regularity across CatBoost and Python-policy variants of crowdstrike feature induction — features past round 3 have diminishing returns. Plausible reason: by round 3 residual errors are increasingly idiosyncratic, so features induced to address them are by construction corpus-specific (overfit). The 3-round point is roughly where induction's overfit-rate crosses its signal-rate. Treat as load-bearing regularity, not arbitrary: flag any continuation past round 3 as overfit-risk territory.

---

## Five-Mode Mirror Taxonomy [42]

The runnable SSP supports five distinct mirror modes, each assessing a different layer at a different structural resolution:

| Mode | Level | What it catches |
|---|---|---|
| **Perception** | Point (external mirror) | Feature-extraction errors; model output vs ground truth |
| **kNN** | Neighborhood (internal, no model needed) | Local incoherence in mixed neighborhoods; anomalies; coverage gaps; drift via points landing in previously-empty neighborhoods |
| **Cluster** | Global discrete | Cluster definitions misaligned with conceptual categories; per-cluster agreement rate localizes fuzzy vs well-defined clusters |
| **Layout** | Global continuous (visual) | Global structure failures; missing axes; human spatial cognition in the loop; axis-naming is itself tail-to-head induction on projected coordinates |
| **Feature quality** | Feature-level | Redundant/overfit/artifact features; disagreement BETWEEN CatBoost class loadings and PCA loadings is sharpest signal |

**Feature quality diagnostic**: high class importance + low PCA loading → feature is class-relevant but doesn't drive global geometry (consider LDA). Low class importance + high PCA loading → varies a lot but not for the right reasons, likely artifact/overfit.

Cross-induction extension at cluster level: surfaces robust (appears across inductions) vs framing-specific (unique to one induction) structure.

These five modes are the SSP quality test framework — see `docs/architecture.md#testing`.

---

## Feature Overfitting and the Ensemble Defense [43]

Feature overfitting is the induction-side analog of model overfitting: SSP induction can overfit features themselves to corpus artifacts rather than domain structure.

**Flavors**:
- **Corpus-collection artifacts**: feature exists only because of how data was sampled (e.g., "uses-emoji" from a single-channel corpus)
- **Inducer-LLM bias**: feature reflects inducer's framing prior, not real domain structure
- **Value-coverage sparsity**: feature value fires on 1-2 training points, can't be reliably scored
- **Co-occurrence artifacts**: two features always co-occur in training — one feature in disguise that decorrelates in production
- **Meta-prompt artifacts**: for synthesized corpora, sampling prompt injects structure about prompt format, not domain

**Detection** (composing with existing machinery):
- Held-out corpus split: induce on subset, score held-out; features whose value distribution shifts → overfit
- Cross-induction stability [11]: features not recurring across inducer models or framings are corpus-specific
- Production-corpus drift monitor: feature-value distribution on live data vs training corpus
- Coverage threshold: drop features with dominant value (high Gini) or tail values firing on < N points
- Cross-substrate sensitivity [39]: CatBoost AND rules wild disagreement → flaky features
- Class loadings + PCA loadings disagreement [42]: features flagged low-importance by both → safe removal candidates

Hard limit: Karto should warn past ~15 features (design imperative from [50]).

---

## Product Surfaces [44]

Six operational surfaces, each implementing one lifecycle stage [36]:

| Surface | Command | Implements |
|---|---|---|
| **Induction** | `/karto induct` | tail-to-head [38], ensemble framing iteration [11] |
| **Refinement** | `/karto debug` + `/karto induct --refine` | triage-driven targeted SSP edits [41] |
| **Visualization UI** | `/karto render` | layout-mirror + feature-quality-mirror [42], belief_state viewer |
| **Operational model** | `/karto apply` | substrate scoring [39][46], semlabel [45] |
| **Story mode** | (generated output) | prose narrative [26] for read-mode delivery |
| **Learning mode** | (interactive induction) | user builds SSP to internalize domain; progress trace exportable |

All six surfaces share the human-vetting backbone — vetting is the legitimacy mechanism, not a quality-control gate. The product is "induce, vet, refine, vet, operationalize, vet, deploy, monitor, vet drift signals."

---

## Semlabel as Bounded-Region Backend [45]

Semlabel sits at Tier-1.5 between regex and small-LLM — a distinct band where bounded-region semantics earn their cost.

**Cost / semantic-richness ladder**:
- Regex/code: ~µs, lexical-only richness, exact-match patterns
- Semlabel concept: ~ms (one dot product), bounded-embedding-region richness, AL-refined boundary
- Small-LLM Q-A feature: ~100ms–s, high free-reasoning richness
- Frontier-LLM escalation: ~s and expensive, maximal richness

**The bounded-region property**: semlabel asks "is this point inside the region characterized by these positives and outside the negatives?" — not "is this similar to X?" The AL loop refines the boundary so paraphrase/synonym/structural variation are handled where regex would miss them.

**Distinctive use cases**:
- **Triage gate**: "is this security-relevant?" → semlabel concept gates whether to escalate to LLM, saves LLM calls on bulk input
- **Pre-tagging**: 10k-paper corpus → semlabel topical tags → LLM or human refines on smaller subset
- **High-volume per-feature scoring**: when a feature must be computed on every example in a large corpus, semlabel's ~ms cost makes it viable where LLM Q-A would be prohibitive

**Substrate-pairing cross-check**: when semlabel and LLM Q-A disagree on the same feature, either the semlabel region needs more AL boundary refinement OR the LLM is reasoning-overkilling a fundamentally simple distinction.
