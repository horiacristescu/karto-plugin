<!-- Methodology reference shipped with the Karto plugin. Working copy: <repo>/MIND_MAP.md; this is the user-facing snapshot. -->
# Karto — Mind Map

> **What this is:** initial planning notes for **Kartographer**, a Claude Code plugin that packages the SSP induction/apply/audit/debug methodology developed across the `2026-05-generative-ssp`, `semlabel`, `belief_state`, and `crowdstrike` projects.

---

## [1] Identity

- **Project name:** Kartographer
- **CLI command:** `karto` (and `/karto` as Claude Code slash command)
- **Tagline:** *Make latent structure explicit enough to measure, critique, update.*
- **Methodological commitment:** *Discriminations, not embeddings.* Categorical features with hyphenated values, not continuous gradients. (See [13])
- **Naming rationale:** K-spelling disambiguates from the kingbootoshi/cartographer codebase-mapping family ([34]). German-tech-tooling flavor (Kafka, Kubernetes). Namespace search 2026-05-02 confirmed `karto` clean in AI/LLM CLI tooling space.

## [2] One-line answer to "what does it do?"

It packages the workflow that takes any domain → trace corpus → induced SSP (named axes + positions) → small-model-runnable inference → credit-assignable failure analysis. The user is the cartographer; the tool is the workshop.

---

## The idea, exposed

## [3] The 4-stage matrix with framing as hub

```
            Intent
              |
              |
   Data ── FRAMING ── Compute
              |
              |
          Confidence
```

**Each stage exposes its own constraints:**

- **Intent** — goals, hard constraints, **error cost matrix** (which mistakes cost how much), action authority (what is the system allowed to do).
- **Data** — quality, diversity, staleness, trust; ground-truth status (clean / noisy / event-not-GT / no-GT); sharing topology (single / multi-tenant / pooled / hierarchical).
- **Compute** — budget, latency, volume; per-decision cost ceiling; throughput floor.
- **Confidence** — evals, metric hacking, gradual deployment risk, **reversibility envelope** (alias-flip / canary-only / deploy-then-rollback / irreversible).

**Framing** is the hub: choosing the unit of analysis, the state decomposition, the feature factoring, the correctness regime. It propagates through all 4 stages simultaneously. A *good* framing move **double-relaxes** at least two stages at once (relieves a tight constraint pair).

## [4] Tight constraint pairs — where leverage lives

- **Compute × Confidence** — more eval rigor costs more compute (judges, panels, shadow runs)
- **Data × Confidence** — noisier or less-independent data caps eval rigor (Goodhart proximity)
- **Intent × Confidence** — tighter cost matrix forces tighter eval (must distinguish what costs more)
- **Intent × Compute** — cost ceilings force architecture decompositions (cascade routing, multi-model)

## [5] The compass

> **Calibrate confidence to consequence** — never let an action's reversibility-cost exceed the trust you've built for it. Pull either side of the lever: build more confidence (data, eval, calibration, judges, shadow) OR bound consequence (reversibility, abstention, slicing, rate caps, escalation).

Applied per-action, not globally. Calibration is local to each decision boundary; aggregate calibration is meaningless.

## [6] The 6 framing strategies (from p8 induction, [27])

1. **Residual over scaffold** — when a deterministic baseline captures the hard structure, train ML on the *residual* not as replacement (ETA prediction)
2. **Target substitution** — when label is censored/sparse/rare, predict a tractable intermediate (hospital deterioration → physiological-score slope)
3. **Action reframe** — match action authority to demonstrated confidence (radiology triage = queue-jump not diagnosis)
4. **Pipeline decompose** — what looks like one problem is many sub-problems with different requirements (the *most common* — 7/21 in p8)
5. **Label align** — labels point at the wrong signal (satellite crop classification: midsummer survey but spring phenology is discriminative)
6. **Constraint project** — separate prediction from constraint satisfaction entirely (electricity grid: per-zone forecasts + reconciliation matrix)

## [7] 4-layer credit assignment

When the system fails, blame is localizable to one of:

- **Perception (features)** — feature value misclassified from input
- **Understanding (state)** — state computed wrong from correct features (aggregation, projection, missing axis)
- **Policy (action/prediction)** — right state, wrong action chosen (threshold, decision rule)
- **Label (ground truth)** — the "error" wasn't an error; the label was wrong

Plus the **5th implicit failure mode**: *representation gap* — all four layers correct but the SSP doesn't include the actually-decisive axis. This surfaces as "everything looks right but the call was bad," and is the failure framing tries to prevent.

## [8] The 3-layer (4-with-audit) methodology stack

| Layer | Role | Tool |
|---|---|---|
| 1. Structure | Latent → explicit coordinate system | Frontier-LLM-induced SSP |
| 2. Perception | Score each axis on new inputs | semlabel concept (vector + AL training set) OR small-LLM question OR regex/code |
| 3. Application | Small model reads + applies | ProTeGi-optimized prompts |
| 4. Audit | Debug structure, validate placements | Frontier-LLM neighborhood walk (occasional) |

Cost asymmetry: Layer 1 is rare/expensive (months, frontier model). Layer 2 is per-feature (small model + concept vector). Layer 3 is constant/cheap (sub-cent per inference). Layer 4 is periodic (refresh cycles).

## [9] Capacity-aware feature design

Each SSP feature picks its own implementation tier per its capacity needs:

- **Tier-1**: surface-readable bools (regex / code-derived) — any model handles
- **Tier-2**: pattern-matchable (small LLM with optimized prompt OR semlabel concept vector)
- **Tier-3**: requires reasoning (escalate to frontier OR decompose into Tier-1/2 sub-features)

Subtle features can be decomposed (e.g., "Goodhart proximity" = `same_corpus_holdout` AND `metric_used_for_selection` AND `metric_used_for_gate` → composite from bools).

## [10] Vector-as-data, not prompt-as-runtime

Concept lives as a 384-float vector + training set, not as runtime LLM compute. Inference = one dot product. Audit by analogy: "show me the 5 nearest training examples." The concept is **materialized**.

This is structurally what semlabel does; Kartographer's perception layer reuses this substrate ([14]).

## [11] Ensemble SSPs as Goodhart defense

Multiple inductions (different inducer models, prompt formulations, trace types, sampling shapes) — features surviving across inductions = robust signal; features unique to one induction = inducer-bias. Cheap because traces are LLM-sampled and induction is interactive structure-extraction (not statistical smoothing). HITL irreducible at axis-alignment + cross-validation.

## [12] Why "Cartographer"

The metaphor is *load-bearing, not decorative.* Cartography literally takes territory (latent, there-but-not-inspectable) and produces a map (explicit, navigable, contestable). Same epistemic move SSPs make on latent structure. Three things cartographers know that SSP-builders should: all maps are projections (ensemble SSPs), maps are versioned (refresh cycles), a map is good when it lets you act (calibrate confidence to consequence).

## [13] Discriminations vs embeddings — the load-bearing design choice

From `2026-05-generative-ssp/MIND_MAP.md` [3]: categorical features with 3-6 hyphenated named values, *not* continuous vectors. Embeddings cluster by style/voice and are hard to contest. Discrete SSP features are inspectable: every placement can be argued in language, every feature can be split/merged, every iteration leaves a readable diff. Hyphenated value names avoid false ordinality (`off-policy` and `on-policy` are kinds, not points on a scale). One-hot encoding restores numeric structure for PCA without imposing gradients.

---

## Refined SSP understanding (working session 2026-05-02)

Nodes [35]–[45] follow the playbook one-line-per-node format (see `/playbook:mindmap`). They extend [3]–[13] with conceptual refinements; original nodes are unchanged.

[35] **The mirror thesis (unifying frame)** - An SSP as pure text is weak — read once, agreed with, forgotten. Rendered as a runnable model it works like a mirror, flagging inconsistencies in either the data or the SSP itself by forcing disagreement to become legible. The mirror doesn't tell you what's true; it makes the gap between your model and reality visible enough that you can't unsee it. This is the load-bearing claim of the project, retroactively justifying several existing commitments: discriminations not embeddings [13] (embeddings reflect disagreement but not which axis drove it; discrete SSPs preserve legibility so the mirror can say "you're wrong about axis X"), vector-as-data not prompt-as-runtime [10] (materialization is what makes the SSP cheap enough to use as a continuous mirror), ensemble SSPs [11] (multiple mirrors cross-checking each other; disagreement is itself signal), and calibrate confidence to consequence [5] (the compass works because the mirror tells you when you've outrun your trust budget). The metaphor answers "why bother making latent structure explicit at all" — without rendering it as something that can disagree with you, you cannot tell when you are wrong. This frames the entire closed loop in [40] and the validation surfaces in [42] — both exist because text alone cannot mirror.

[36] **Consumption modes, lifecycle stages, use-cases, vetting** - The SSP is one artifact with two consumption ontologies always available: read-mode (human directly consumes for understanding via narrative, flashcards, slides, neighborhood walk, viewer) and run-mode (agent applies it to inputs and emits scored positions via a scoring API or classifier or policy). What varies between use-cases is which mode dominates; the other is always present (operational SSPs need read-mode for debug/audit/drift, didactic SSPs need run-mode for self-test/drill generation). Three temporal lifecycle stages: Stage A Research (induct, walk, narrate, ensemble cross-check via [11], internalize — read-mode-dominant; many use-cases stop here), Stage B Operationalize (assign per-feature backends [9][15][45], train substrate [39], build eval harness — explicit `karto promote` gesture marks the boundary), Stage C Operate (apply, monitor drift, debug failures — read-mode returns here for diagnostic walking). A and B have different quality bars: A tolerates incompleteness and ensemble disagreement; B needs locked schemas. Six use-cases all over the same artifact: domain expertise breakdown, agent policy/classifier (the original CUA use), learning materials production for others, architectural design support, runtime cross-checker [42], and learning-by-construction (the human builds the SSP to learn the domain themselves — distinct from materials production; the deliverable is the user's internalized model, not the SSP — see [44] surface 6). Human vetting is first-class throughout, not a bottleneck step at the end — happens at every transition (framing decision, leaf-naming, feature naming, cluster definition, axis interpretation, triage, substrate behavior). HITL as legitimacy mechanism, not as cost.

[37] **Inputs and the discrete coordinate system** - Single input pipeline: seed (idea / domain / question / problem / expertise space) plus optional grounding (traces / documents / papers / reference data) feeds subagent sampling (with or without web search) producing a sampled trajectory corpus that IS the dataset. Variability lives in the seed (what you're mapping) and grounding (what anchors the sampling); pure-idea seeds have no grounding while trace-grounded sampling has rich grounding, but the same generation pipeline runs in both cases — this collapses earlier "captured / curated / synthesized" categorizations into points on one grounding-richness axis. State and action spaces are both compositional: state space is bags over discrete features {f_i ∈ V_i}, action space is bags over {a_j ∈ U_j} (compositional) or atomic a ∈ U (degenerate case). Both states and actions are bags of discrete features, not atoms — the standard (S, A) formalism is the special case where both bags collapse to single values. The compositional generalization justifies action-side feature induction (e.g., crowdstrike's `action_type`, `api_domain`, `in_question_tactic` are action-side features, not state). Data shape is either sequence (s_0, a_0) → (s_1, a_1) → ... — trajectories enabling transition modeling i.e. policy + dynamics — or collection {(s_k, a_k)} of scattered points enabling only distribution modeling. CUA / conversations / agent runs are sequence; papers / cases / methods are collection. Most existing SSPs are atemporal collections; CUA work needs the temporal extension. The perception step (`karto apply`) assigns (s(x), a(x)) feature-bags to each example — this discretization step IS what makes the SSP runnable [38][39].

[38] **Induction: framing-first, tail-to-head, labels-induce-states** - The conceptual hinge sharpening [13]: labels DEFINE features, not the other way around. A "state" is the set of points sharing a feature-value, where the feature was named by asking "what discriminates this label?" Choosing labels = choosing the SSP's structure. Features cluster the space the way the labels carve it. The framing decision (sharpening [3]) is four-prong: unit of analysis (what's a position?), state-side feature space (what describes a state?), action-side feature space (what describes an action?), and discriminator (which label drives induction?). Different framings yield different SSPs from the same data; ensemble inductions [11] vary the framing to find robust features. The tail-to-head algorithm runs within a framing: for each example name the leaf (position / stance / action / outcome); for each leaf-value find features that distinguish examples sharing that leaf-value from examples with other leaf-values; discretize features into 3-6 hyphenated categorical values per feature [13]; cluster feature-value combinations into named states (or let states emerge as feature-bags). This is the inverse problem: standard ML maps state → action, while SSP induction observes leaves and reverse-engineers states. The leaf is what you can label cheaply and reliably; the state must be inferred. Every feature is named in the act of being induced — interpretability is built-in, not retrofit. The loop continues by triage of disagreements [41] and refinement [44], guarded against feature overfitting by [43].

[39] **Substrate fungibility: rules / CatBoost / small-LLM over one SSP** - Layer-3 of the methodology stack [8] is substrate-fungible: the same SSP feature space can be scored by hand-coded Python rules (maximal per-decision interpretability since every decision = one rule, edit-rerun cycle with no train, weak coverage of soft combinators, excellent audit ergonomics — line-readable), or CatBoost over feature columns (global SHAP plus per-case SHAP but inferred, retrain cycle, strong coverage learning interactions, medium audit), or small-LLM with prompt over feature description (LLM reasoning trace only, prompt-edit no retrain, very strong coverage of novel framings, weak audit since no fixed decision tree). Substrate choice is real engineering — Python rules win on early iteration / audit / debug / decisions-as-statements-in-SSP-vocabulary; CatBoost wins on soft combinators and unanticipated interactions; small-LLM wins on coverage but loses interpretability. Substrate-pairing as cross-check: run two substrates over the same SSP, treat disagreement as signal (CatBoost wins → rules likely missing a soft interaction; rules win → CatBoost likely overfit). Substrate-layer Goodhart defense, complement to [11]'s induction-layer defense — diversity at the model layer with the SSP as shared vocabulary that makes disagreement legible (not just a gap between two opaque scores). The substrate-fungibility property is also why the SSP is the durable artifact: it survives multiple substrate generations, justifying heavy spending on induction (Layer 1) since the substrate (Layer 3) is replaceable. Semlabel adds a Tier-1.5 backend [45] for bounded-region scoring between regex and small-LLM.

[40] **Closed-loop pipeline (methodology end-to-end)** - The full loop runs frame [38] (unit, state space, action space, discriminator) → sample [37] (seed ± grounding → corpus) → tail-to-head induce [38] (label leaves → cluster → name discriminators → discretize) → VET (human reviews features, cluster definitions, axis names per [36]) → perceive (assign feature-values to each example, the discretization step) → VET (sanity-check perception assignments on a sample) → train substrate [39] (rules / CatBoost / small-LLM over feature space) → VET (inspect decision rules / SHAP / prompt behavior) → deploy on new traces (continuous scoring) → detect disagreement (model output vs ground truth or other source) → flag → triage [41] → refine (new features / re-train / park) ↺ back to induce with vetting at each refine. Vetting is integrated at each transition, not appended at the end — this is what "vet it as humans" means in practice [36]. Two flavors of new traces: same-distribution (production-like; disagreement signals drift, coverage gap, or label noise) and different-corpus probe (deliberate generalization test, problem-SSP vs domain-SSP, the p1/p5/p6/p7 cross-checks; disagreement signals where the inducing lens doesn't transfer). This is the loop that makes the SSP the mirror it is [35] — without the deploy → detect steps, the SSP is back to inert text.

[41] **Triage taxonomy and the 3-round stopping heuristic** - When disagreement surfaces, triage into buckets. Three-bucket triage for classification (validated empirically across crowdstrike feature-discovery rounds): feature gap (model lacks a discriminating feature — induce it, retrain), label noise (ground truth wrong, subjective, or ambiguous — flag for review or accept boundary), DK gap (domain knowledge missing that's outside what the corpus supports — park or extend corpus). Four-bucket extension for policy learning where the demonstrator ≠ optimal: feature gap (as above), multi-valid (both actions reasonable, not a real disagreement), trace error (demonstrator was wrong — the model is actually better, the model becomes critic of corpus not just corpus critic of model), model error (substrate fit issue [39]). The trace-error case matters for any policy SSP induced from imperfect demonstrations: SSP should be allowed to outperform the trace when framing makes the trace's mistake legible. Three-round stopping heuristic: empirical regularity across CatBoost and Python-policy variants of crowdstrike feature induction shows adding features past round 3 has diminishing returns. Plausible deeper reason — by round 3 residual errors are increasingly idiosyncratic, so features induced to address them are by construction more corpus-specific (overfit). The 3-round stopping point is roughly where induction's overfit-rate crosses its signal-rate [43]. Treat as a load-bearing regularity not arbitrary: target ≤ 3 rounds in induction by default; explicitly flag any continuation past round 3 as overfit-risk territory.

[42] **Five-mode mirror taxonomy (validation surfaces)** - The runnable SSP [35] supports five distinct mirror modes, each assessing a different layer of "what could be wrong" at a different structural resolution — together they are the validation-surface inventory the tool needs to expose. Perception (point-level): model output vs ground truth (external mirror) — catches feature-extraction errors. Local kNN (neighborhood): shared-label among k neighbors over discrete feature-bags (internal mirror, no model needed) — catches local incoherence in mixed neighborhoods, anomalies, coverage gaps, decision-boundary discoveries, and drift via points landing in previously-empty neighborhoods. Cluster (global discrete): semantic agent cluster assignment vs structural cluster assignment (e.g., nearest centroid or hierarchical clustering) — catches cluster definitions that don't align with conceptual categories; per-cluster agreement rate localizes which clusters are well-defined vs fuzzy. Layout (global continuous, visual): PCA projection plus axis naming — catches global structure failures and missing axes; the only mode putting human spatial cognition in the loop, bandwidth-asymmetric and best for Stage A research [36]; axis-naming is itself a tail-to-head induction [38] applied to projected coordinates. Feature quality (feature-level): CatBoost class loadings plus PCA axis loadings — catches redundant / overfit / artifact features; disagreement BETWEEN the two readings is sharpest signal (high class importance + low PCA loading → feature is class-relevant but doesn't drive global geometry, consider supervised projection like LDA; low class importance + high PCA loading → varies a lot but not for the right reasons, likely artifact or overfit per [43]). Cross-induction extension at cluster level surfaces robust vs framing-specific structure, complementing [11].

[43] **Feature overfitting and the ensemble defense** - Feature overfitting is the induction-side analog of model overfitting: standard ML overfits parameters to training noise; SSP induction overfits features themselves to corpus artifacts. Flavors include corpus-collection artifacts (feature only exists because of how data was sampled, e.g., a "uses-emoji" axis from a single-channel corpus), inducer-LLM bias (feature reflects the inducer model's framing prior not real domain structure), value-coverage sparsity (feature value firing on 1-2 training points, can't be reliably scored), co-occurrence artifacts (two features always co-occur in training — one feature in disguise that decorrelates in production), and meta-prompt artifacts (for synthesized corpora, the sampling prompt injects a dimension about prompt structure not domain). Detection methods composing with existing machinery: held-out corpus split (induce on subset, score on held-out — features whose value distribution shifts → overfit), cross-induction stability via [11] (features that don't recur across inducer models or framings are corpus-specific — this was already the Goodhart defense, overfitting is exactly what it defends against), production-corpus drift monitor (feature-value distribution on live data vs training corpus), coverage threshold (drop features with one value dominating per high Gini, or tail values firing on < N points), cross-substrate sensitivity per [39] (train CatBoost AND Python rules over the same features — wild disagreement → flaky features), and class-loadings + PCA-loadings disagreement per [42] (features flagged low-importance by both → safe removal candidates; substitutability via mutual information or held-out drop tests). Ensemble inductions [11] are the standing defense at the SSP level; same logic at cluster level surfaces robust vs framing-specific structure. The 3-round empirical heuristic [41] is plausibly the manifestation of overfit-rate crossing signal-rate.

[44] **Product surfaces (operational footprint)** - The tool exposes six operational surfaces, each implementing one stage of the lifecycle [36] and supporting both read- and run-mode consumption. Induction: corpus → induced SSP, implements [38], supports framing iteration via [11] ensemble, maps to existing `/karto induct` from [14]. Refinement: credit-assignment-driven targeted edits to the SSP — triage outputs from [41] become feature additions, removals, value renaming, or cluster boundary adjustments. This is the loop that makes the SSP a living artifact not a one-shot output, combining `/karto debug` and `/karto induct --refine` from [14]. Visualization UI: interactive PCA plus cluster plus axis-loading inspection, implements layout-mirror and feature-quality-mirror from [42], wraps belief_state's web viewer from [17]. Operational model: substrate over the SSP feature space (rules / CatBoost / small-LLM / semlabel-bounded-region), implements [39][45], deployable for runtime scoring, maps to existing `/karto apply` and concept training from [14]. Story mode: prose narrative form for human consumption (the `story_v1.md` format from [26]), generated from the SSP for read-mode delivery — used for didactic delivery, stakeholder communication, learning-material production, and learning-by-construction reflection [36]. Learning / explainability mode: the human-as-learner surface — user runs induction interactively, vetting each framing decision / feature naming / cluster boundary; the act of building the SSP is the expertise-acquisition; outputs are both the SSP AND the user's internalized model. Needs scaffolding for prompted reflection at decision points, comparison against prior inductions [11], exposure of disagreement signals from [42] as teaching moments, exportable progress trace. All six surfaces share the human-vetting backbone from [36] — the product is "induce, vet, refine, vet, operationalize, vet, deploy, monitor, vet drift signals" not "induce SSP then deploy." Vetting is the legitimacy mechanism not a quality-control gate. This implies [23] phasing should be revisited; re-phasing TBD.

[45] **Semlabel as the bounded-region feature backend** - Semlabel [16] sits in a specific niche in the per-feature backend spectrum [9] that the existing tier descriptions undersold: it captures a bounded region of embedding space (not a point), giving semantic robustness regex can't match while staying orders of magnitude cheaper than LLM Q-A features. Cost / semantic-richness ladder: regex/code at ~µs scoring with lexical-only richness via exact-match patterns; semlabel concept at ~ms (one dot product) with bounded-embedding-region richness via trained directional vector + AL training set; small-LLM Q-A feature at ~100ms-s with high free-reasoning richness via prompted question per input; frontier-LLM escalate at ~s and expensive with maximal richness via full reasoning. The bounded-region property matters: a semlabel concept asks "is this point inside the region characterized by these positives and outside the region of these negatives?" — not "is this similar to X?" The active-learning loop refines the boundary, so paraphrase / synonym / structural variation are handled where regex would miss them. Distinctive use cases enabled by the cost-semantic tradeoff: triage (first-pass bucketing before expensive processing — e.g., "is this security-relevant?" → semlabel concept gates whether to escalate to LLM, saves LLM calls), pre-tagging (cheap initial labeling before refinement — e.g., 10k-paper corpus → semlabel topical tags → LLM or human refines on a smaller subset), and high-volume per-feature scoring (when a feature must be computed on every example in a large corpus, semlabel's per-call cost makes it viable where LLM Q-A would be prohibitive). Substrate-pairing cross-check [39] extends naturally: when semlabel and LLM Q-A disagree on the same feature, either the semlabel region needs more AL boundary refinement or the LLM is reasoning-overkilling a fundamentally simple distinction. This re-reads [9]'s capacity-aware tier picture: semlabel is Tier 1.5 between regex and small-LLM — a distinct band where bounded-region semantics earn their cost, not a Tier-2 alternative.

[46] **Dual-substrate by default + frontier-LLM tiebreaker cascade** - Sharpens [39] from "substrate-fungible" to substrate-pairing as the *default* SSP design. Every SSP module ships at least two substrate scorers (Python rules + CatBoost over feature columns) plus optionally a third (frontier LLM); the score() entry point runs all and surfaces divergence directly. The diagnostic asymmetry per [39] becomes explicit per case: rules-wins → CatBoost likely overfit on a spurious correlation, inspect what feature combination it latched onto; CatBoost-wins → rules likely missing a soft combinator, inspect what signals failed to add together; agree → high confidence. Cascade keeps cost bounded: rules + CatBoost cheap on every input; frontier LLM only on disagreement (rules ≠ CatBoost OR any model ≠ label). Labels come for free from data — for trajectory data the next action IS the label (every (s_t, a_t) supervises); for problem corpora GT is bundled (multi-choice answer keys, dataset categories). The 4-way comparison (label + 3 model outputs) gives a richer diagnostic vocabulary than [41]'s 3-bucket triage: all-3-agree + label matches → high confidence; all-3-agree + label says other → strong evidence of label noise (or shared blind spot); rules vs CatBoost split with LLM tiebreak → substrate-specific failure on the loser; rules + CatBoost agree, LLM dissents → either representation gap (LLM sees what features can't capture) or LLM hallucination, vet; all 3 disagree → genuinely ambiguous, refine framing or accept boundary. The dual policy is *the smallest viable mirror* — divergence rate / per-feature breakdown / direction skew are quality metrics with no external GT required. Single-substrate SSPs lose this external-mirror-without-labels property — too much capability to give up. Active-learning queue auto-populates from divergent cases per [49].

[47] **SSP_META: declared domain vocabulary + descriptive/predictive split** - The structural decomposition (features → state-region/cluster → leaf) is invariant across domains, but the *naming* of the leaf shifts per domain and matters for prose, tooling, vetting prompts. Literature review uses "stance" or "method"; CUA uses "action" or "policy"; multi-choice uses "answer" or "class"; system-design uses "framing strategy"; conversation analysis uses "turn-type" or "move"; behavioral data uses "behavior" or "outcome." Resolution: framework standardizes generically (`leaf`, `cluster`, `feature` everywhere internally); each SSP module declares its own domain vocabulary in `SSP_META` (input_concept, feature_concept, state_concept, leaf_concept, maintainer, version). Karto tooling reads SSP_META when generating prose, error messages, viz labels, vetting prompts — gives readable narratives ("the paper's *stance* was misclassified") without forcing the framework to know about stances vs actions. This is [38]'s fourth prong (discriminator naming) made concrete; should be the first interactive step of induction. Also expose **decomposition_kind**: descriptive (classify what something IS — stance, framing pattern; discriminator's job: classify accurately) vs predictive (forecast what will happen / what should be done — CUA next action, policy classifier; discriminator's job: forecast accurately). Same structural form, different epistemics: descriptive disagreement = "is this case in category X or Y?" (semantic); predictive disagreement = "will this state lead to outcome X or Y?" (counterfactual). The 4-bucket policy triage from [41] (with trace-error / multi-valid) really belongs to *predictive* SSPs; descriptive SSPs use the simpler 3-bucket triage. Segmentation gap [51] applies to both kinds.

[48] **SSP as Python module (the canonical form)** - Each SSP is a self-contained Python module rather than a JSON file plus separate dispatch. Justified because all four needs of an SSP — code-based features (regex, parsing), agent sub-calls (LLM-Q-A, semlabel), explicit policy logic, CatBoost training — naturally want code. JSON would force escape-to-Python for any of these, defeating its purpose. Convention IS the API: every SSP module exports `score(input) → dict`, `SSP_META` [47], `SSP_FEATURES`, `SSP_POSITIONS`, `SSP_CLUSTERS`, optionally `train_catboost()` plus `score_rules` / `score_catboost` / `score_llm` for [46]'s cascade. Code is needed for behavior (feature extractors, policy, substrate scorers, training hooks); data for declarations (META, feature value spaces, position lists, cluster definitions) — better as Python literals inside the .py for self-containedness; generate `projection.json` as derived snapshot for non-Python tooling like the visualizer [17]. Definitely not in the .py: catboost.cbm (binary, regenerated from corpus), corpus/ (source data with provenance), tests/ (pytest cases), audits/ (markdown reports including trace dumps per [49]), narrative.md (story-mode prose), README.md (overview), segmentation.py [51]. Typical SSP module is 200-500 lines: ~10-15 feature functions (50-200 lines feature code) + 30-line score() + 50-200 lines policy rules + 30 lines declarative literals. Sized for the human cognitive unit of "one SSP" — small enough to fit in your head, large enough to express real domain knowledge. SSPs become composable (import features from sibling SSPs), testable (pytest against score()), versionable (readable git diffs), importable from non-Karto contexts (production systems can `from ssps.<name> import score` — Karto disappears from the deploy path; the SSP outlives the tool that built it). Each SSP lives in `ssps/<name>/` per-project (folder, not single file) holding ssp.py + sibling artifacts.

[49] **Forward-pass trace as first-class artifact + recursive Karto** - When score(input) runs, capture full execution trace: each feature's value + backend used + prompt sent + LLM response + matched regex / SHAP / rule fired / elapsed time per substrate; cluster assignments per substrate including the matched rule or SHAP per case; result with divergence info. Trace is much richer than bare output and enables: per-step debugging (when user disagrees with output, walk back through which feature gave what value, which rule fired — the 5-bucket triage from [41]+[51] becomes precise, failure localizes to a step), substrate-disagreement diagnosis per [46] (trace shows exactly what each substrate saw — not just two opaque scores), reflection corpus (traces become inputs for *meta-SSPs* — induct an SSP over traces themselves: features = "frontier-LLM-escalated?" / "rules-CatBoost-agreed?" / "feature-X-uncertain?"; clusters = "high-confidence" / "ambiguous" / "model-overconfident" / "missing-feature"; leaf = downstream-success pattern), active-learning queue auto-population (disagreement-flagged traces are exactly the cases worth labeling next; trace gives labeler all context). Storage: per-trace 1-10 KB; corpus of hundreds of inputs = 100KB-1MB; default always-trace, sample-down only if cost demands; layout `audits/traces/<date>/<trace_id>.json` or aggregated daily JSONL. Trace structure must be **standardized across SSPs** so meta-SSPs over traces work generically — that standard is part of what `karto.ssp_base` defines. Without standardization, every meta-SSP re-writes trace parsing per source SSP, killing the recursion. **Recursive Karto** is the load-bearing pattern this enables: methodology applied to its own outputs at multiple levels (per-inference traces become a corpus; per-induction-project records become a corpus; per-refinement-event records become a corpus) — same methodology, different unit of analysis at each level [50].

[50] **Karto's own framing — Intent/Data/Compute/Confidence applied to the build itself** - Karto framed using its own [3] hub as a fractal-application demonstration: Intent = agentic induction + agentic update + agentic policy execution + use for analysis/understanding/research/concept-mapping/learning (worst error: false confidence on flawed SSP poisoning downstream); Data = dozens-to-hundreds of points per SSP, heterogeneous types (traces / docs / papers / sessions / problems), variable noise, GT status varies (multi-choice bundled, trajectory derived from next-step, free-form needs agent labeling); Compute = asymmetric — induction expensive (frontier + ensemble, minutes-to-hours, infrequent) but application cheap (cascade [46], ms-to-s); Confidence = central goal, achieved via cycles of held-out + cross-induction + dual-substrate + label-disagreement, sensitive to framing, ensembling required, isolation between ensemble members critical. Tight constraint pairs from [4] play out as: Confidence × Compute relieved by cascade [46]; Confidence × Data relieved by ensemble + cross-induction stability [11] (replaces statistical confidence with structural confidence) — label-noise detection becomes the *default* triage path not exception case; Intent × Compute = asymmetric budget (heavy on induct, light on apply, infrequent on refine); Intent × Confidence requires lightweight vetting UX or agentic intent dies under vetting cost. Five design imperatives follow: (1) few-features constraint (~10-20 max) is load-bearing — Karto should hard-warn past ~15 features; (2) cascade by compute tier built into every SSP module per [46]; (3) ensemble isolation enforced by infrastructure (separate subagents, clean contexts) not discipline; (4) vetting UX is currently under-specified — needs lightweight checkpoint patterns (vet framing once, vet feature batches not individuals, vet refinements via diff-review); (5) heterogeneous data → corpus ingestion is a first-class command [51]. **Dogfood-on-p8 is the V1 acceptance criterion** — Karto V1 is "good enough" only when it can re-induce p8 end-to-end producing an SSP comparable to the manual one (one canonical reference relaxes Confidence × Data; V1 scope = whatever's needed for that one task, V2-V4 is everything else). Methodology is *fractal* per [12]: same Intent/Data/Compute/Confidence + framing-first analysis works at any level (domain SSP, the tool itself, recursively per-operation).

[51] **Segmentation as part of framing + 5th triage bucket + ingestion pipeline split** - Segmentation IS the unit-of-analysis decision (the first prong of [38]'s framing), so it lives *inside* framing not upstream as ingest preprocessing. Flow: `karto:ingest <source>` normalizes source and extracts *candidate* boundaries (multiple schemes if available) without committing; `karto:frame <source>` interactively picks the unit-of-analysis (which boundary scheme to use) plus the rest of [38]'s prongs; `karto:induct <framed-corpus>` induces over the segmented units. Segmentation strategies in roughly increasing semantic depth: structural (existing markup like YT chapters, book chapters, paper sections, thread breaks — cheap, lossless when available); temporal (fixed-time chunks, easy but arbitrary); topical (sliding-window embedding-similarity drops, default for unstructured long sources without markup); argumentative (rhetorical structure breaks, needs LLM analysis); action-bounded (for traces, group by completed action / episode / error-recovery cycle, needs trace understanding). Multiple segmentations of the same source coexist as different SSPs (a book at chapter level for topical patterns AND paragraph level for rhetorical patterns are two valid SSPs; Karto must not assume one segmentation per source). Provenance is non-negotiable: every unit must remember its source location (timestamp range, page range, line range) so audits can navigate back — goes in unit metadata not a separate index. Segmentation can itself be a small SSP (induct a "is this a unit boundary?" classifier from a few human-segmented examples, apply to a large trace corpus — Karto applied to itself one layer up). The 4-bucket triage from [41] gets a **5th bucket: segmentation gap** — disagreement comes from a unit being two distinct things lumped together OR one thing split apart. Each SSP folder needs `segmentation.py` (executable, reproducible: `from ssps.<name>.segmentation import segment; units = segment(source, mode="chapters")`). **Ingestion pipeline split**: plugin ships common adapters (`karto:ingest-yt`, `karto:ingest-pdf`, `karto:ingest-jsonl`, `karto:ingest-text`); each project also keeps `ingestion.py` at root for bespoke sources (custom Slack export, internal log schema) — both feed the same `karto:frame` step.

[52] **Three registers of LLM-facing instruction** - Karto's LLM/agent instructions split three ways with different lifecycles. **Process-level skills** (plugin, `skills/karto/`) — methodology knowledge telling agents *how to do* each step, evolves with the methodology rarely. Map to MIND_MAP nodes: framing.md [38], sampling.md [37], segmentation.md [51], induct.md [38], feature-design.md [9][45], vet-batch.md [36], mirror-modes.md [42], triage.md [41], refine.md [44], ensemble.md [11], overfit-defense.md [43], substrate-cascade.md [46], story-mode.md [44], learning-mode.md [44]. Each is procedural (algorithm + checkpoints + outputs); MIND_MAP is conceptual; skills reference MIND_MAP nodes for the why. **Per-SSP prompts** (each SSP module, `ssps/<name>/`) — domain-specific instruction inside feature extractors and policy, evolves with the SSP. Includes per-feature prompts (one short prompt per LLM-Q-A feature, typically 5-15 per SSP), tiebreaker prompt for [46]'s cascade, cluster-semantic-assignment prompt for cluster-mode mirror in [42], story-mode template instantiation, vetting question templates. Inline strings in the .py [48] or `prompts/` subdirectory — default inline until prompts grow long. **Agent-level explanations** (plugin and agent boundaries) — context for the AI's role itself, lives at boundaries. Plugin `CLAUDE.md` (loaded when active, tells agents what Karto is + where things live + when not to act), per-agent cards (`agents/karto-inducer.md`, `agents/karto-debugger.md` — scope role / tools / when-to-invoke / when-NOT-to-invoke / handoff format; critical for ensemble isolation per [11]/[50]), vetting interface cards (process-level templates filled with SSP-specific content; "here are the 8 features the inducer proposed; please mark each: keep / refine / reject"). The split that matters: process-level instruction reusable across SSPs (in plugin); per-SSP instruction domain-specific (in SSP module); explanations bridge the two and scope agent authority. Methodology evolves → update plugin skills; SSP evolves → update its prompts; agent permissions change → update explanations.

---

## Architecture

## [14] Slash commands (target shape)

```
/karto induct <corpus> [--ensemble N]   # induce SSP from traces (Phase 3)
/karto apply <ssp> <input>              # place input on existing SSP (Phase 1)
/karto audit <ssp>                      # neighborhood walk, flag inconsistencies (Phase 4)
/karto debug <case>                     # 4-layer credit assignment (Phase 2)
/karto concept <name> <corpus>          # train semlabel concept as feature backend
/karto render <ssp>                     # JSON → PCA → 2D map (delegates to belief_state)
```

Each subcommand is a subagent class; cost-routing differs (frontier for induct/audit/debug; small-LLM + concept-vectors for apply).

## [15] File schemas

- **SSP JSON**: matches `~/Code/belief_state/BELIEF_STATE_MAPPING.md` contract — `core_topic`, `state_features` (5-10 features × 3-6 categorical values), `positions` (10-25), `positions_metadata`, optional `clusters`, `cluster_labels`, `axis_labels`. Renderer pipeline: JSON → one-hot matrix → PCA via `numpy.linalg.eigh` → 2D map + audit Markdown.
- **semlabel concept JSON**: `description` (semantic intent), `positives[]` (training examples), `negatives[]` (training examples), `weight[384]` (unit-norm trained direction). Inference = `embedding · weight`.
- **Per-feature backend declaration** (new): `{feature_name, backend: concept|llm_question|code|regex, backend_config}`. Lets each SSP feature pick its own implementation tier ([9]).

---

## Resources to pull in

## [16] semlabel — perception-layer substrate

- **Path:** `~/Code/semlabel/`
- **Mind map:** `~/Code/semlabel/MIND_MAP.md`
- **CLAUDE.md:** `~/Code/semlabel/CLAUDE.md`
- **Concept files:** `~/Code/semlabel/fixtures/concepts/*.json` (~19 trained concepts)
- **Source:** `~/Code/semlabel/src/semlabel.py`
- **What we use:** concept training (active learning loop, ridge regression, unit-norm weights), embed daemon, `tag` subcommand for scoring, JSON concept format
- **Integration:** semlabel concepts become Kartographer's per-feature perception backends. `/karto concept <name>` wraps `semlabel train` with SSP-feature-aware naming.

## [17] belief_state — visualization + JSON contract

- **Path:** `~/Code/belief_state/`
- **Mapping spec:** `~/Code/belief_state/BELIEF_STATE_MAPPING.md` (the LLM extraction prompt — defines the SSP JSON schema)
- **What we use:** browser-based PCA visualizer, the canonical JSON schema, the kNN/cluster-purity/PCA-loadings audit machinery
- **Integration:** `/karto render` delegates here. SSP JSONs produced by Kartographer are loadable in the existing viewer.

## [18] generative-ssp — methodology source-of-truth

- **Path:** `~/Documents/writing/2026-05-generative-ssp/`
- **Mind map:** `~/Documents/writing/2026-05-generative-ssp/MIND_MAP.md` (the canonical methodology mind map)
- **Workflow doc:** `~/Documents/writing/2026-05-generative-ssp/AGENTS.md`
- **Spec versions:** `~/Documents/writing/2026-05-generative-ssp/docs/ssp_v1.md` … `ssp_v4.md` (v4 is the unified theory — has Markov triple, scaffold/rubric duality, **forward/backward blame assignment** ← maps onto [7])
- **Prompts:** `~/Documents/writing/2026-05-generative-ssp/prompts/p1.md` … `p9.md` (incl. p9 discretized hardware-economics traces)
- **Fully-induced SSPs:** `~/Documents/writing/2026-05-generative-ssp/data/p8_constraint_framing_cases/` — *the canonical worked example*, source of [3]–[7], 21 positions × 8 features
- **What we use:** the manual workflow → automated; v4 specification → source of truth for credit-assignment design; p8 → reference SSP for testing `/karto apply`

## [19] rl_book — renderer + sibling SSPs

- **Path:** `~/Documents/writing/rl_book/`
- **Renderer:** `~/Documents/writing/rl_book/src/render_map.py` (JSON → PCA → PNG + audit Markdown; uses `numpy.linalg.eigh` with sign-canonicalization)
- **Worked map (RL):** `~/Documents/writing/rl_book/study/rl_book.json` (38 RL methods × 10 features × 8 clusters)
- **Worked map (cybersec):** `~/Documents/writing/rl_book/systems_design/cybersec_ml.json` (39 cybersec ML patterns × 8 features × 7 clusters) — *the OLD positioning-style SSP, useful as contrast to p8's constraint-framing style*
- **Invocation:** `uv run python src/render_map.py path/to/map.json`
- **What we use:** the Python renderer for `/karto render` (until/unless we port to belief_state's web view as canonical)

## [20] crowdstrike — applied workspace + 33 flashcards

- **Path:** `~/Documents/writing/crowdstrike/`
- **Mind map (Systems Design Study):** `~/Documents/writing/crowdstrike/MIND_MAP.md` sections [SD1]–[SD5]
- **Problem prompts:** `~/Documents/writing/crowdstrike/systems_design/stories/p{1,5,6,7}.md` (4 cybersec systems-design problems)
- **Problem readings:** `~/Documents/writing/crowdstrike/systems_design/stories/p{1,5,6,7}_reading.md` (4 didactic narratives, ~50-110 lines each)
- **Flashcard sets:** `~/Documents/writing/crowdstrike/systems_design/stories/p{1,5,6,7}-cards/` — 33 cards total (8 + 7 + 7 + 7), each `(slide.md + slide.png)` pair
- **Chapter slides (bonus):** `~/Documents/writing/crowdstrike/systems_design/stories/Horia-{01-tenancy,02-llm-gateway,03-agent-insider}/`
- **LLM efficiency reading:** `~/Documents/writing/crowdstrike/systems_design/llm_efficiency.md` (applies the methodology to inference economics)
- **What we use:** these are *test corpora* — the 4 problems + readings + cards are exactly the kind of artifacts Kartographer should be able to ingest, induce a domain SSP from, place new problems against, and credit-assign failures on.

## [21] crowdstrike (continued) — the constraint-framing prompt

- **p8 prompt (constraint-framing case generator):** `~/Documents/writing/crowdstrike/systems_design/stories/p8.md` — the meta-prompt for generating diverse senior-DS systems-design case studies; embeds [3]–[5] inline. *This is the bootstrap prompt for inducing new domain SSPs.*

## [22] Auxiliary referenced material

- **Reiner Pope / MatX inference economics trace:** `~/Documents/writing/2026-05-generative-ssp/prompts/p9.discretized3.md` (63 discretized propositions on batch / sparsity / context / KV cache tiering — used as worked example of how to encode hardware lecture content as SSP-trainable trace data)
- **MetaSPO / ProTeGi reference:** see `~/Documents/writing/crowdstrike/.agent/tasks/010-paper-presentation-prep/` (paper presentation work, includes literature on prompt optimization). ProTeGi (Microsoft Research, "Prompt Optimization with Textual Gradients") sits at Layer 3 of the methodology stack ([8]).

---

## Plan

## [23] Phasing

| Phase | Scope | Time | Why first |
|---|---|---|---|
| **Phase 1: `/karto apply`** | Score input against existing SSP using mixed feature backends (semlabel / small-LLM / regex / code) | ~1 week | Makes existing SSPs (p8, cybersec_ml, rl_book) operational at scale. Highest immediate value. |
| **Phase 2: `/karto debug`** | 4-layer credit assignment subagent walking perception/understanding/policy/label | ~1 week | Makes failures debuggable — the leverage point identified in [7]. Specified in v4 ([18]) as forward/backward blame assignment. |
| **Phase 3: `/karto induct`** | Automate the 4-agent → consolidate → induce → story workflow from `2026-05-generative-ssp/AGENTS.md` | ~2-3 weeks | Makes new SSPs producible without manual orchestration. |
| **Phase 4: `/karto audit`** | Frontier neighborhood walk; flag inconsistent neighborhoods; suggest refactors | ~3-5 days | Maintenance loop; runs occasionally per refresh cycle. |
| **Phase 5: `/karto render` glue** | Wire to belief_state viewer + rl_book renderer | ~1-2 days | Already-existing tools; just plumbing. |

Total: 4-6 weeks of focused work for the full plugin. Phase 1 alone (~1 week) is enough for proof-of-concept and interview narrative anchor.

## [24] What's already done vs what's needed

**Done:**
- semlabel concept training + AL loop ([16])
- belief_state PCA viewer + JSON schema ([17])
- rl_book Python renderer ([19])
- generative-ssp manual workflow with one fully-induced SSP (p8) ([18])
- 33 flashcards exemplifying card-format outputs ([20])
- v4 spec with forward/backward blame ([18])
- The methodology itself (this MIND_MAP)

**Missing:**
- Plugin packaging (commands, skills, subagent prompts)
- `/karto apply` engine (per-feature backend dispatch)
- `/karto debug` subagent (4-layer credit assignment in code, not just spec)
- semlabel-concept-as-SSP-feature glue
- `/karto induct` automation of the file-mediated subagent workflow
- ProTeGi integration for Layer 3 prompt optimization

## [25] Open design questions

- How to align features across ensemble inductions ([11])? LLM semantic alignment or human?
- Should `/karto apply` output structured per-feature confidence per blame layer (so debug is automatic when something fails)? Probably yes — the feature is cheap to add now.
- Where does the SSP "live" between commands? File-on-disk JSON (matches belief_state contract) or in-memory session state? Probably file-on-disk for portability.
- Should ProTeGi prompt optimization be invoked manually (`/karto optimize-prompts`) or automatically when small-model accuracy on validation set drops? Latter is sharper but adds dependency on validation-set maintenance.
- How does Kartographer relate to the playbook plugin (`~/.claude/plugins/cache/claude-playbook-marketplace/playbook/`)? Both are methodology-tools for Claude Code. Probably orthogonal — playbook is for *task execution*, Kartographer is for *domain knowledge representation*.

---

## Connections to existing methodology canon

## [26] The canonical SSP induction reading

- **`~/Documents/writing/2026-05-generative-ssp/data/p8_constraint_framing_cases/induction/story_v1.md`**

This is the ~1800-word didactic narrative explaining the 4-stage matrix + 6 framing strategies + 3 meta-observations, induced from 21 positions across 24 traces. **Source of [3]–[7].** Required reading for anyone working on Kartographer.

## [27] The canonical SSP JSON

- **`~/Documents/writing/2026-05-generative-ssp/data/p8_constraint_framing_cases/induction/ssp_v1.md`** (and the corresponding JSON when produced)

The 21 positions × 8 features grid. The first fully-induced SSP from the generative methodology. Demonstrates the `framing_strategy`, `tight_constraint_pair`, `gt_profile`, `action_reversibility`, `temporal_validity`, `confidence_target`, `gt_resolution`, `decision_temporality` feature set.

## [28] The methodology spec

- **`~/Documents/writing/2026-05-generative-ssp/docs/ssp_v4.md`** (unified theory)

Markov triple, scaffold/rubric dual use, **forward/backward blame assignment** (the spec for [7]), multi-level compression, semantic iteration rules, use-case-vs-operational-function divergence.

## [29] The contract spec

- **`~/Code/belief_state/BELIEF_STATE_MAPPING.md`**

The LLM extraction prompt that defines the canonical Profile/Position-map JSON shape. Treat as the extraction contract. If schema must change, change it there, not silently in Kartographer.

---

## Naming history

## [30] Why not "Cartographer"

Heavily occupied namespace as of 2026-05-02:
- `kingbootoshi/cartographer` — Claude Code plugin for codebase mapping (~420+ stars)
- `ichal1113/cartographer`, `konankikesava/K-cartographer` — variants
- `llm-cartographer` on PyPI (Simon Willison's tool)
- `anthony-maio/cartograph` at cartograph.making-minds.ai
- `cartographer.ai` domain
- Google Cartographer (SLAM)
- Many others

Spelling variants (Kartographer, Kartograf) fuzzy-match in search engines back to the same family. The cartographer-as-codebase-mapper metaphor is established and dominant.

## [31] Why "Kartographer" + "karto" anyway

The K-spelling carries the project (German-tech-tooling flavor, recognizably the same word). The CLI command `karto` lives in a sparser namespace (existing `karto` projects: a dormant npm mapping library and a few unrelated GitHub repos in adjacent maps-rendering verticals — none in AI/LLM tooling). Internal Claude Code slash command `/karto` is fully namespaced.

## [32] Naming rules locked

- **Project:** Kartographer
- **CLI:** karto
- **Slash command:** /karto
- **Repo:** ~/Code/karto/ (this folder)
- **Tagline:** *Make latent structure explicit enough to measure, critique, update.*
- **Methodology slogan (insider):** *Discriminations, not embeddings.*

---

## Cross-reference index

## [33] Sister mind maps to consult before working here

- `~/Documents/writing/2026-05-generative-ssp/MIND_MAP.md` — methodology source-of-truth
- `~/Documents/writing/crowdstrike/MIND_MAP.md` — applied workspace, [SD1]-[SD5] systems design study section
- `~/Code/semlabel/MIND_MAP.md` — perception-layer substrate
- `~/Documents/writing/rl_book/study/rl_book.json` and sibling — example SSP outputs

## [34] What this project is NOT

- Not a codebase-mapping tool (that's the kingbootoshi/cartographer family)
- Not a SLAM library (that's Google Cartographer)
- Not a GIS tool (that's CARTO)
- Not a Dataset Cartography clone (that's allenai/cartography for ML training dynamics)
- Not a replacement for semlabel — Kartographer *uses* semlabel as its perception-layer backend
- Not a replacement for belief_state — Kartographer *delegates* visualization to belief_state

This project is: **the workflow tool that takes a domain trace corpus and produces a measurable, critique-able, update-able SSP that small models can apply at runtime, with frontier-model assist for induction and audit, and with explicit blame-assignable failure analysis.**

---

## History

- 2026-05-02: Project conceived. Methodology developed across `crowdstrike` (applied) + `2026-05-generative-ssp` (canonical) projects. p8 SSP fully induced as proof-of-concept. Naming locked. Initial mind map written.
- 2026-05-02 (later): Working session refined SSP methodology — added [35]–[45]. Mirror thesis as unifying frame; read/run modes + 3-stage lifecycle + 6 use-cases (incl. learning-by-construction); single input pipeline + compositional state/action spaces; framing-first + tail-to-head + labels-induce-states; substrate fungibility with Python-rules / CatBoost / small-LLM and substrate-pairing cross-check; closed-loop pipeline with vetting at every transition; triage taxonomy (3-bucket + policy 4-bucket) + 3-round stopping heuristic; 5-mode mirror taxonomy (perception / kNN / cluster / layout / feature-quality) as validation surfaces; feature-overfitting analysis with ensemble defense; 6 product surfaces (induction / refinement / viz UI / operational model / story mode / learning); semlabel as bounded-region Tier-1.5 backend.
- 2026-05-04: Implementation-design session refined the methodology toward a buildable plugin — added [46]–[52]. Dual-substrate by default with frontier-LLM tiebreaker cascade and 4-way comparison matrix (sharpens [39]); SSP_META domain vocabulary + descriptive/predictive split (sharpens [38]/[41]); SSP as Python module as canonical form with 200-500-line size sweet spot (resolves the JSON-vs-substrate config tension and [25]'s open question on where SSPs live); forward-pass trace as first-class artifact enabling recursive Karto (meta-SSPs over traces); Karto's own framing using Intent/Data/Compute/Confidence demonstrating fractal application + dogfood-on-p8 V1 acceptance criterion; segmentation as part of framing with 5th triage bucket (segmentation gap) + ingestion pipeline split (plugin adapters + per-project ingestion.py); three registers of LLM-facing instruction (process-level skills / per-SSP prompts / agent-level explanations) with distinct lifecycles. V1 implementation plan drafted (8 tasks, see .agent/tasks/).
