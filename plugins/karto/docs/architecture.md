# Karto Architecture Decisions

Full-detail companion to `MIND_MAP.md` nodes [46]–[53]. MIND_MAP carries the routing pointer + key dev insight; this file carries the reasoning.

---

## Dual-Substrate by Default [46]

Every SSP module ships **at least two substrate scorers** (Python rules + CatBoost) plus optionally a third (frontier LLM). `score()` runs all and surfaces divergence directly. This sharpens [39] from "substrate-fungible" to substrate-pairing as the *default* SSP design — not an option.

**Diagnostic asymmetry per case**:
- rules-wins → CatBoost likely overfit on a spurious correlation; inspect what feature combination it latched onto
- CatBoost-wins → rules likely missing a soft combinator; inspect what signals failed to add together
- agree → high confidence

**Cascade cost bounding**: rules + CatBoost cheap on every input; frontier LLM invoked only on disagreement (rules ≠ CatBoost OR any model ≠ label).

**Labels come for free**: trajectory data — next action IS the label (every (s_t, a_t) supervises); problem corpora — GT is bundled (multi-choice answer keys, dataset categories).

**4-way comparison vocabulary** (label + 3 model outputs):
- all-3-agree + label matches → high confidence
- all-3-agree + label says other → strong evidence of label noise (or shared blind spot)
- rules vs CatBoost split, LLM tiebreak → substrate-specific failure on the loser
- rules + CatBoost agree, LLM dissents → either representation gap or LLM hallucination; vet
- all 3 disagree → genuinely ambiguous; refine framing or accept boundary

**The self-testing property**: divergence rate / per-feature breakdown / direction skew are quality metrics requiring no external GT. Single-substrate SSPs lose this entirely — too much capability to give up. Hard warning from framework if only one substrate present.

Active-learning queue auto-populates from divergent cases.

---

## SSP_META: Domain Vocabulary [47]

The structural decomposition (features → cluster → leaf) is invariant across domains, but the *naming* of the leaf shifts per domain and matters for prose, tooling, vetting prompts.

Examples:
- Literature review → "stance" or "method"
- CUA → "action" or "policy"
- Multi-choice → "answer" or "class"
- System-design → "framing strategy"
- Conversation analysis → "turn-type" or "move"

**Resolution**: framework standardizes generically (`leaf`, `cluster`, `feature` everywhere internally); each SSP module declares its own domain vocabulary in `SSP_META`. Karto tooling reads SSP_META when generating prose, error messages, viz labels, vetting prompts — gives readable narratives ("the paper's *stance* was misclassified") without forcing the framework to know about stances vs actions.

**Required SSP_META fields**: `input_concept`, `feature_concept`, `state_concept`, `leaf_concept`, `maintainer`, `version`, `decomposition_kind`.

**Decomposition kind** (`descriptive` vs `predictive`):
- Descriptive — classify what something IS (stance, framing pattern); disagreement is semantic ("is this case X or Y?")
- Predictive — forecast what will happen / what should be done (CUA next action, policy); disagreement is counterfactual ("will this lead to X or Y?")

Same structural form, different epistemics. The 4-bucket policy triage (with trace-error / multi-valid) belongs to *predictive* SSPs only; descriptive SSPs use the simpler 3-bucket triage.

---

## SSP as Python Module [48]

Each SSP is a self-contained Python module, not a JSON file plus separate dispatch.

**Why Python not JSON**: all four SSP needs want code — feature extractors (regex, parsing), agent sub-calls (LLM-Q-A, semlabel), explicit policy logic, CatBoost training hooks. JSON would force escape-to-Python for any of these, defeating its purpose.

**Convention IS the API** — every SSP module must export:
- `score(input) → dict` — main entry point
- `SSP_META` — domain vocabulary dict
- `SSP_FEATURES` — feature value spaces
- `SSP_POSITIONS` — position list
- `SSP_CLUSTERS` — cluster definitions
- Optional: `score_rules`, `score_catboost`, `score_llm` for dual-substrate cascade
- Optional: `train_catboost()` — training hook

**What goes in the `.py`**: feature extractor functions, `score()`, policy rules, `SSP_META` / `SSP_FEATURES` / `SSP_POSITIONS` / `SSP_CLUSTERS` as Python literals.

**What does NOT go in the `.py`**: `catboost.cbm` (binary, regenerated), `tests/` (pytest cases), `audits/` (trace dumps), `narrative.md` (story-mode prose), `README.md`, `segmentation.py`.

**Derived artifacts**: generate `projection.json` as a snapshot for non-Python tooling (the belief_state visualizer).

**Typical size**: 200–500 lines — ~10-15 feature functions (50-200 lines) + 30-line `score()` + 50-200 lines policy rules + 30 lines declarative literals. Sized for one cognitive unit: small enough to fit in your head, large enough to express real domain knowledge.

**Composability**: SSPs can import features from sibling SSPs. Production systems can `from ssps.<name> import score` — Karto disappears from the deploy path. The SSP outlives the tool that built it.

**Layout**: each SSP folder is a domain workspace, not a single-artifact container:

```
ssps/<name>/
  corpus/               ← source data (one or more files; see corpus kinds below)
  models/
    ssp_v1/             ← first induction (one subfolder per model)
      ssp_v1.py
      <discretized>.md  ← the discretized corpus that produced this model
      projection.json   ← optional snapshot for belief_state visualizer [17]
    ssp_v2/             ← re-induction for cross-comparison [11]
      ssp_v2.py
      corpus/units/     ← segmented units (if produced during induction)
  segmentation.py       ← present only for temporal corpora
  __init__.py
```

Each model subfolder contains exactly what produced it — the `.py` module, the discretized corpus or segmented units, and any derived artifacts (e.g. `projection.json`). This coupling is intentional: changing the model means changing its discretization [51].

**Corpus kinds**:
- **Static** (literature review, conceptual discussion, lecture transcript): source documents go directly in `corpus/`; positions are the unit already, no segmentation needed. Example: `corpus/lecture_transcript.md`.
- **Temporal** (agent traces, execution logs, conversations): raw log goes in `corpus/`; `segmentation.py` parses it into individual trace files in `corpus/traces/`, one file per step/episode. Each trace is one (s_t, a_t) point in the SSP. Primary sources: CUA session logs, coding agent bash/chat logs, Playbook task.md files (each gate sequence is a trajectory), conversation logs (each turn is a step).

**`models/` discipline**: multiple inductions of the same corpus surface robust features (appear across inductions) vs corpus-specific ones (unique to one induction) — the primary cross-induction ensemble defense [11][43]. Each induction lives in its own subfolder with its paired artifacts. Re-induction is the practice mechanism; comparison is the quality signal.

---

## Forward-Pass Trace [49]

Every `score(input)` call captures a full execution trace. Trace structure per feature:
- `feature`: name
- `value`: assigned value
- `backend`: which backend ran (rules/catboost/semlabel/llm)
- `evidence`: matched regex / rule text / SHAP values / LLM response / prompt sent
- `confidence`: float
- `elapsed_ms`: per-backend timing

Plus: cluster assignments per substrate, matched rule or SHAP per case, result with divergence info.

**Why standardized across SSPs**: so meta-SSPs over traces work generically. Without standardization, every meta-SSP re-writes trace parsing per source SSP, killing the recursion. The standard is what `karto.ssp_base` defines.

**What the trace enables**:
- Per-step debugging: walk back through which feature gave what value, which rule fired → triage localizes to a step
- Substrate-disagreement diagnosis: trace shows exactly what each substrate saw, not just two opaque scores
- Reflection corpus: traces become inputs for *meta-SSPs* (features = "frontier-LLM-escalated?" / "rules-CatBoost-agreed?" / "feature-X-uncertain?"; leaf = downstream-success pattern)
- Active-learning queue: disagreement-flagged traces are exactly the cases worth labeling next

**Storage**: per-trace 1-10 KB; corpus of hundreds = 100KB–1MB. Default always-trace; sample down only if cost demands. Layout: `audits/traces/<date>/<trace_id>.json` or aggregated daily JSONL.

**Recursive Karto**: traces → corpus → meta-SSP. Same methodology, different unit of analysis at each level.

---

## Design Imperatives [50]

Applying Karto's own Intent/Data/Compute/Confidence framing to itself yields five concrete design rules:

1. **Few-features constraint**: ~10–20 features max is load-bearing. Hard-warn past ~15 features. Past that point, per-feature coverage drops, overfit risk rises, and the SSP no longer fits in one cognitive unit.

2. **Cascade by compute tier**: every SSP module must implement the rules → CatBoost → LLM cascade. Not optional. The self-testing property depends on it.

3. **Ensemble isolation via infrastructure**: separate subagents, clean contexts, no shared state between ensemble members. Discipline fails at scale; infrastructure enforces this.

4. **Lightweight vetting UX**: vet framing once (not per-feature), vet feature batches not individuals, vet refinements via diff-review. Vetting per-individual feature kills agentic throughput.

5. **Corpus ingestion is first-class**: `karto:ingest` is a proper command with adapters, not a preprocessing script. Heterogeneous data types (traces, docs, papers, sessions, problems) are the norm.

**V1 acceptance criterion**: dogfood-on-p8. Karto V1 is "good enough" only when it can re-induce p8 end-to-end producing an SSP comparable to the manually-induced one. One canonical reference relaxes Confidence×Data (the hardest constraint pair for V1). V1 scope = whatever's needed for that task; V2–V4 is everything else.

---

## Segmentation [51]

Segmentation IS the unit-of-analysis decision (first prong of the four-prong framing [38]), not upstream preprocessing. It lives inside framing.

**Pipeline**:
- `karto:ingest <source>` — normalizes source, extracts *candidate* boundaries (multiple schemes) without committing
- `karto:frame <source>` — interactively picks the unit-of-analysis scheme plus the rest of the framing prongs
- `karto:induct <framed-corpus>` — induces over the segmented units

**Segmentation strategies** (roughly increasing semantic depth):
1. Structural — existing markup (YT chapters, paper sections, thread breaks); cheap, lossless when available
2. Temporal — fixed-time chunks; easy but arbitrary
3. Topical — sliding-window embedding-similarity drops; default for unstructured long sources
4. Argumentative — rhetorical structure breaks; needs LLM analysis
5. Action-bounded — group by completed action/episode/error-recovery cycle; needs trace understanding

Multiple segmentations of the same source coexist as different SSPs (chapter-level AND paragraph-level on the same book are two valid SSPs). Karto must not assume one segmentation per source.

**Provenance is non-negotiable**: every unit must remember its source location (timestamp range, page range, line range) for audits. Goes in unit metadata, not a separate index.

**Ingestion pipeline split**: plugin ships common adapters (`karto:ingest-yt`, `karto:ingest-pdf`, `karto:ingest-jsonl`, `karto:ingest-text`); each project keeps `ingestion.py` at root for bespoke sources (custom Slack export, internal log schema). Both feed `karto:frame`.

**5th triage bucket**: segmentation gap — disagreement from a unit being two things lumped together OR one thing split apart.

Each SSP folder needs `segmentation.py` (executable, reproducible): `from ssps.<name>.segmentation import segment; units = segment(source, mode="chapters")`.

---

## Three Registers of LLM-Facing Instruction [52]

Three distinct instruction registers with different lifecycles. Getting this wrong means either re-documenting methodology per SSP (waste) or putting SSP-specific prompts in the plugin (coupling).

**Register 1 — Process-level skills** (`skills/karto/`): methodology knowledge telling agents *how to do* each step. Evolves with the methodology rarely. Node → skill file mapping:

| MIND_MAP node | Skill file |
|---|---|
| [38] Induction | `framing.md`, `induct.md` |
| [37] Inputs | `sampling.md` |
| [51] Segmentation | `segmentation.md` |
| [9][45] Feature tiers | `feature-design.md` |
| [36] Vetting | `vet-batch.md` |
| [42] Mirror modes | `mirror-modes.md` |
| [41] Triage | `triage.md` |
| [44] Refinement | `refine.md` |
| [11] Ensemble | `ensemble.md` |
| [43] Overfit | `overfit-defense.md` |
| [46] Cascade | `substrate-cascade.md` |
| [44] Story mode | `story-mode.md` |
| [44] Learning mode | `learning-mode.md` |

Each skill is procedural (algorithm + checkpoints + outputs). MIND_MAP is conceptual. Skills reference MIND_MAP node IDs for the why.

**Register 2 — Per-SSP prompts** (`ssps/<name>/`): domain-specific instruction inside feature extractors and policy. Evolves with the SSP. Includes: per-feature prompts (5-15 per SSP, one short prompt per LLM-Q-A feature), tiebreaker prompt for cascade, cluster-semantic-assignment prompt, story-mode template instantiation, vetting question templates. Inline strings in the `.py` by default; move to `prompts/` subdirectory if they grow long.

**Register 3 — Agent-level explanations** (plugin boundaries and agent cards): context for the AI's role. `CLAUDE.md` (loaded when plugin active), per-agent cards (`agents/karto-inducer.md`, `agents/karto-debugger.md` — scope role / tools / when-to-invoke / when-NOT-to-invoke / handoff format; critical for ensemble isolation), vetting interface cards (templates filled with SSP-specific content at vet time).

**The split that matters**: process-level reusable across SSPs (in plugin); per-SSP domain-specific (in SSP module); explanations bridge and scope authority. Methodology evolves → update plugin skills. SSP evolves → update its prompts. Agent permissions change → update explanations.

---

## Testing Strategy [53]

Three registers with distinct tools, semantics, and oracles. Conflating them causes over-testing the wrong layer or missing load-bearing properties.

### Register 1 — Contract/Plumbing

pytest, deterministic, fast, in `tests/`. Two structural properties serve as oracles requiring no external ground truth:

- **Completeness**: every `ScoreResult` has exactly one `FeatureTrace` per feature declared in `SSP_FEATURES`
- **Legality**: every emitted feature value is in the declared value space

Additional contract tests:
- Divergence categorization: given rules-wins / catboost-wins / all-agree / all-disagree synthetic inputs → assert exact category
- Validation rejection messages name the broken feature/position (agent-readable error quality is load-bearing — agents act on these)
- Loader idempotency: repeated imports don't collide or reuse stale module state
- Trace diagnostic quality: when two substrates disagree, does the trace identify *which feature* drove the split? (This is a Register 1 test because it's a structural property of the trace, not a semantic judgment)

Do not assert on semantic correctness — whether a value is *correct* for a given input is a domain question, not a plumbing question.

### Register 2 — SSP Quality

Per-SSP, living in `ssps/<name>/tests/` or `tests/ssps/`. The five mirror modes [42] are the test framework. The declared value space plus fixture inputs are the oracle; no external annotator required.

**Minimal viable form**: curated inputs → expected positions (regression against the SSP's own declarations) + completeness + legality properties from Register 1.

**Full form**: kNN purity (k nearest feature-bag neighbors share a cluster), cluster coherence (semantic vs structural agreement rate), dual-substrate agreement rate on held-out corpus, CatBoost-vs-PCA loading disagreement per [43].

**Critical semantic distinction**: high dual-substrate disagreement is **not a CI failure** — it is a signal the SSP needs refinement, consumed by the triage loop [41]. CI fails on structural violations (Register 1); SSP quality metrics surface to the developer for triage.

**The boundary**: if the SSP declares an illegal value or omits a feature → framework bug (Register 1 catches it). If the SSP assigns a semantically wrong value to a specific input → domain disagreement (feeds triage, not CI).

### Register 3 — Command Boundary

Agent-mediated slash commands produce non-deterministic LLM output — **never pin LLM output in tests**. Test the Python boundary only: command calls the right library functions with the right arguments; CLI exits 0 on valid input and non-zero on invalid; output JSON has `result`, `trace`, `divergence` at top level. Nothing deeper.

### Cross-Register: Dual Substrate as Self-Testing Mechanism

The dual-substrate [46] provides an unlabeled quality score requiring no external GT: divergence rate on a held-out corpus is a standing health metric for any operationalized SSP. Single-substrate SSPs lose this property entirely — hard framework warning.

Recursive Karto [49] extends Register 2 upward: meta-SSPs over traces are testable by the same five mirror modes at the next level of abstraction.
