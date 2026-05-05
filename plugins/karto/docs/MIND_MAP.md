<!-- Methodology reference shipped with the Karto plugin. Working copy: <repo>/MIND_MAP.md; this is the user-facing snapshot. -->
> **For AI Agents:** This mind map is your primary knowledge index. Read overview nodes [1]–[5] first, then follow links to find what you need. Always reference node IDs. When you make changes, update outdated nodes immediately — especially [1]–[5]. Add new nodes only for genuinely new concepts. The mind map wraps every task: consult it, rely on it, update it.

# Karto — Mind Map

> **What this is:** planning and methodology notes for **Kartographer**, a Claude Code plugin packaging the SSP induction/apply/audit/debug methodology. Not a codebase mapper, SLAM library, GIS tool, or Dataset Cartography clone — and not a replacement for semlabel [16] or belief_state [17], which it uses.

---

[1] **Identity & Overview** - Kartographer (`karto` CLI, `/karto` slash command) takes any domain → trace corpus → induced SSP → small-model-runnable inference → credit-assignable failure analysis [2][35]. Core design commitment: discriminations not embeddings [13] — 3-6 categorical hyphenated values per feature. The mirror thesis [35] is the unifying frame. Six product surfaces [44]; four commands [14]. V1 criterion: re-induce p8 end-to-end [50][27]. Dev `~/Code/karto/` private; public release `github.com/horiacristescu/karto-plugin` [32]. Python package `src/karto/` [48]; testing [53]. Deep methodology: `docs/methodology.md`; implementation decisions: `docs/architecture.md`. Sister projects [33]; current build state [24].

[2] **Core methodology** - seed/domain → corpus [37] → tail-to-head induction [38] → SSP → inference [39] → failure analysis [41][42]. Intent/Data/Compute/Confidence are the four constraint dimensions; Framing is the hub [3]. Six framing strategies [6]; credit assignment four layers [7]. Closed-loop: frame → sample → induce → VET → perceive → VET → train → VET → deploy → triage [41] → refine ↺ [40]. Dogfood-on-p8 is V1 self-test [50][27]. Resources: semlabel [16], belief_state [17], generative-ssp [18], crowdstrike [20][21].

[3] **4-stage matrix (framing as hub)** - Intent/Data/Compute/Confidence are the four constraint-bearing dimensions; Framing propagates choices through all four simultaneously [2][50]. A good framing move double-relaxes at least two tight constraint pairs [4]. Intent: goals, error cost matrix, action authority. Data: quality, GT status, sharing topology. Compute: budget, volume, cost ceiling. Confidence: evals, Goodhart risk [11][43], reversibility envelope. The compass [5] applies per-action, not globally.

[4] **Tight constraint pairs** - Four pairs where leverage lives [3]: Compute×Confidence (eval rigor costs compute); Data×Confidence (noisy data caps rigor [11][43]); Intent×Confidence (tighter cost matrix → tighter eval); Intent×Compute (ceilings force cascade [46]). Cascade [46] relieves Compute×Confidence; ensemble [11] relieves Data×Confidence. Each pair has a corresponding design imperative [50].

[5] **The compass** - *Calibrate confidence to consequence* — never let an action's reversibility-cost exceed the trust built for it [3][4]. Two levers: build more confidence OR bound consequence (reversibility, abstention, rate caps). Applied per-action, not globally. Dual-substrate [46] and five mirror modes [42] are the operational instruments. Vetting [36] is the legitimacy mechanism at each transition.

[6] **6 framing strategies** - Induced from p8 [27][18]: (1) Residual over scaffold; (2) Target substitution; (3) Action reframe (match action authority to demonstrated confidence); (4) Pipeline decompose — most common, 7/21 in p8; (5) Label align (labels point at wrong signal); (6) Constraint project (separate prediction from constraint satisfaction). These are the discriminators in p8's SSP [38] and what `/karto induct` teaches [14].

[7] **4-layer credit assignment** - Blame localizes to: Perception (features misclassified), Understanding (state wrong from correct features), Policy (right state, wrong action), Label (wrong GT). Plus 5th implicit mode: representation gap — all four correct but SSP lacks the decisive axis; "everything looks right but the call was bad." Taxonomy maps to triage [41] and mirror modes [42]; forward/backward blame spec in ssp_v4.md [28].

[8] **3-layer methodology stack** - Layer 1: Structure — frontier-LLM-induced SSP, rare and expensive [38]. Layer 2: Perception — score each axis via semlabel [16] / small-LLM / regex/code; per-feature backend selection [15][9][45]. Layer 3: Application — small model applies, ProTeGi-optimized prompts [22], constant and cheap [39]. Layer 4 (Audit): frontier neighborhood walk, periodic [42]. The cascade [46] routes across layers at runtime.

[9] **Capacity-aware feature tiers** - Each feature picks its backend [8][45]: Tier-1 regex/code (~µs); Tier-1.5 semlabel bounded-region concept (~ms, handles paraphrase/synonym) [45]; Tier-2 small-LLM prompt (~100ms); Tier-3 frontier or decompose into sub-features. Decomposition example: "Goodhart proximity" = `same_corpus_holdout` AND `metric_used_for_selection` AND `metric_used_for_gate`. Backend declaration format: `{feature_name, backend, backend_config}` [15].

[10] **Vector-as-data, not prompt-as-runtime** - Concept lives as a 384-float vector + training set, not runtime LLM compute [16]. Inference = one dot product (~ms). Audit by analogy: "show 5 nearest training examples." Materialization makes continuous-mirror operation practical [35] — cheap enough to run on every input.

[11] **Ensemble SSPs as Goodhart defense** - Multiple inductions (different inducer models, prompt formulations, trace types): features surviving across inductions = robust signal; unique = inducer-bias [43]. Ensemble isolation enforced by infrastructure (separate subagents, clean contexts), not discipline [50]. Three-round stopping [41] is the per-induction stopping rule; ensemble defense is the between-induction defense.

[13] **Discriminations vs embeddings** - 3-6 hyphenated categorical values per feature, not continuous vectors [1]. Discrete features are inspectable: every placement arguable in language, every feature splittable/mergeable, every iteration leaves a readable diff. Hyphenated names avoid false ordinality. One-hot restores numeric structure for PCA without imposing gradients [17][42]. This is what makes the mirror thesis [35] work: discrete positions make disagreement legible.

[14] **Slash commands** - `/karto induct <corpus> [--ensemble N]` (Phase 3); `/karto apply <ssp> <input>` (Phase 1); `/karto audit <ssp>` (Phase 4 [42]); `/karto debug <case>` (Phase 2 [7]); `/karto concept <name> <corpus>` (semlabel backend [16]); `/karto render <ssp>` (→ belief_state [17]). Cost routing: frontier for induct/audit/debug; small-LLM + concepts for apply [46][8]. Python CLI: `python -m karto.validate <ssp.py>`, `python -m karto.score <ssp.py> <input.json>` [48][53].

[15] **File schemas** - (1) SSP JSON [17][29]: `core_topic`, `state_features` (5-10 × 3-6 values), `positions` (10-25), optional `clusters`/`cluster_labels`/`axis_labels`; renderer: JSON → one-hot → PCA via `numpy.linalg.eigh`. (2) semlabel concept JSON [16]: `description`, `positives[]`, `negatives[]`, `weight[384]`; inference = `embedding · weight`. (3) Per-feature backend: `{feature_name, backend: concept|llm_question|code|regex, backend_config}` [9][45]. SSP Python module [48] is canonical; JSON is a derived snapshot.

[16] **semlabel** - `~/Code/semlabel/`; source `src/semlabel.py`; ~19 trained concepts in `fixtures/concepts/*.json` [10][45]. Provides: concept training (AL loop, ridge regression, unit-norm weights), embed daemon, `tag` subcommand. Integration: `/karto concept <name>` wraps `semlabel train`; concepts become Tier-1.5 backends [9]. MIND_MAP: `~/Code/semlabel/MIND_MAP.md` [33].

[17] **belief_state** - `~/Code/belief_state/`; canonical SSP JSON schema at `BELIEF_STATE_MAPPING.md` [29]; browser-based PCA visualizer. Schema changes go there, not silently in Kartographer. `/karto render` delegates here. kNN/cluster-purity/PCA-loadings audit machinery implements mirror modes [42].

[18] **generative-ssp** - `~/Documents/writing/2026-05-generative-ssp/`; canonical methodology MIND_MAP; AGENTS.md for the manual workflow. Specs: `docs/ssp_v1.md`–`ssp_v4.md` (v4 = unified theory + forward/backward blame [7]). Prompts: `prompts/p1.md`–`p9.md`. Fully-induced p8 SSP: `data/p8_constraint_framing_cases/` [27]. V1 acceptance criterion [50].

[19] **rl_book** - `~/Documents/writing/rl_book/`; renderer `src/render_map.py` (JSON → PCA → PNG; `uv run python src/render_map.py path/to/map.json`). Maps: `study/rl_book.json` (38 RL methods × 10 features × 8 clusters); `systems_design/cybersec_ml.json` (39 cybersec patterns × 8 features — OLD positioning-style SSP, contrast to p8 [27]). `/karto render` uses this until ported to belief_state [17].

[20] **crowdstrike** - `~/Documents/writing/crowdstrike/`; MIND_MAP [SD1]–[SD5]. Problems: `systems_design/stories/p{1,5,6,7}.md` + readings + flashcard sets (`p{1,5,6,7}-cards/`, 33 cards total). These are test corpora — exactly what Kartographer should ingest, induce from, place against, and credit-assign [7][40].

[21] **crowdstrike — constraint-framing prompt** - `~/Documents/writing/crowdstrike/systems_design/stories/p8.md` — meta-prompt for generating senior-DS case studies; embeds [3][4][6] inline. Bootstrap prompt for inducing new domain SSPs, canonical seed for `/karto induct` [14]. The 21 p8 cases at [27] were produced by this prompt.

[22] **Auxiliary material** - MatX inference trace: `~/Documents/writing/2026-05-generative-ssp/prompts/p9.discretized3.md` (63 discretized propositions on batch/sparsity/KV cache — worked example of encoding lecture content as SSP-trainable trace data [37]). ProTeGi (Microsoft Research, "Prompt Optimization with Textual Gradients"): `~/Documents/writing/crowdstrike/.agent/tasks/010-paper-presentation-prep/`; sits at Layer 3 of the methodology stack [8].

[23] **Phasing** - Phase 1: `/karto apply` ~1 week; Phase 2: `/karto debug` ~1 week [7]; Phase 3: `/karto induct` ~2-3 weeks; Phase 4: `/karto audit` ~3-5 days [42]; Phase 5: `/karto render` glue ~1-2 days [17][19]. Total ~4-6 weeks. Phase 1 alone = proof-of-concept. V1 8-task build plan in `.agent/tasks/` [24].

[24] **Current state** - Done: semlabel [16], belief_state [17], rl_book renderer [19], p8 SSP [27], 33 flashcards [20], ssp_v4.md [28], this MIND_MAP. Not yet built: plugin commands/skills [52], `/karto apply` engine, `/karto debug` subagent, semlabel-as-feature glue, `/karto induct` automation, ProTeGi integration [22], `src/karto/` Python library [48][53]. Task 001 done (commit 8c590cb); Task 002 in progress.

[25] **Open design questions** - Feature alignment across ensemble inductions [11]: LLM or human? `/karto apply` per-feature confidence per blame layer [7][46][49]? (Probably yes — cheap to add now.) SSP storage between commands: file-on-disk [29] or session state? ProTeGi: manual (`/karto optimize-prompts`) or auto when accuracy drops [22]? Install command syntax vs marketplace.json relative source — needs cross-check.

[26] **Canonical SSP reading** - `~/Documents/writing/2026-05-generative-ssp/data/p8_constraint_framing_cases/induction/story_v1.md` — ~1800-word narrative explaining [3][6] + 3 meta-observations, induced from 21 positions across 24 traces. Source of [3]–[7]. Required reading for anyone working on Kartographer. Story-mode surface [44] generates outputs in this format.

[27] **Canonical SSP JSON (p8)** - `~/Documents/writing/2026-05-generative-ssp/data/p8_constraint_framing_cases/induction/ssp_v1.md`. 21 positions × 8 features: `framing_strategy`, `tight_constraint_pair`, `gt_profile`, `action_reversibility`, `temporal_validity`, `confidence_target`, `gt_resolution`, `decision_temporality`. V1 acceptance criterion [50]; fixture for `tests/fixtures/p8_minimal_ssp.py` [53]; reference for `/karto apply` [14].

[28] **Methodology spec** - `~/Documents/writing/2026-05-generative-ssp/docs/ssp_v4.md` — unified theory: Markov triple, scaffold/rubric dual use, forward/backward blame assignment (spec for [7]), multi-level compression, semantic iteration rules. Source of truth for credit-assignment design.

[29] **Contract spec** - `~/Code/belief_state/BELIEF_STATE_MAPPING.md` — extraction prompt defining canonical SSP JSON shape [15][17]. Schema changes go here, not silently in Kartographer.

[32] **Naming rules (locked)** - CLI: `karto`. Slash command: `/karto`. Project: Kartographer. Dev: `github.com/horiacristescu/karto` (private). Release: `github.com/horiacristescu/karto-plugin` (public). Tagline: *Make latent structure explicit enough to measure, critique, update.* K-spelling chosen 2026-05-02: `cartographer` namespace occupied (kingbootoshi ~420+ stars, llm-cartographer on PyPI, Google Cartographer SLAM); `karto` clean in AI/LLM tooling space. Do not use "Cartographer."

[33] **Sister mind maps** - Consult before working here: `~/Documents/writing/2026-05-generative-ssp/MIND_MAP.md` (methodology source-of-truth); `~/Documents/writing/crowdstrike/MIND_MAP.md` (applied workspace [SD1]–[SD5]); `~/Code/semlabel/MIND_MAP.md` (perception substrate [16]); `~/Documents/writing/rl_book/study/rl_book.json` (example SSP output [19]).

[35] **Mirror thesis** - An SSP as text is weak; rendered as runnable code it becomes a mirror — disagreement between model and reality is forced into legibility rather than remaining invisible. This justifies [13][10][11][5]. The closed loop [40] and mirror modes [42] both exist because text alone cannot mirror. Full detail: `docs/methodology.md#mirror-thesis`.

[36] **Consumption modes and lifecycle** - Two always-available modes: read (human consumes) and run (agent scores). Three stages: A Research (tolerates incompleteness), B Operationalize (locked schemas, `karto promote` marks boundary), C Operate. The quality-bar difference between A and B is the key dev constraint. Six use-cases over one artifact. Vetting at every transition, not at the end [40]. Full: `docs/methodology.md#lifecycle` [44][52].

[37] **Inputs and coordinate system** - Single pipeline: seed ± grounding → LLM-sampled corpus. State and action spaces are bags of discrete features — the standard (S,A) formalism is the degenerate case. Sequence data (CUA, conversations) enables transition modeling; collection data (papers, cases) enables distribution modeling only. Segmentation decides the unit [51][38]. Full: `docs/methodology.md#inputs`.

[38] **Induction: tail-to-head** - Labels DEFINE features, not vice versa — name the leaf, then find what discriminates it. Four-prong framing decision: unit of analysis, state features, action features, discriminator. Different framings yield different SSPs from the same data [11][3]. Full: `docs/methodology.md#induction`.

[39] **Substrate fungibility** - Rules / CatBoost / small-LLM all valid over the same SSP feature space. Rules win on audit; CatBoost on soft combinators; LLM on coverage. SSP is the durable artifact — substrate is replaceable, justifying heavy induction investment [8][46]. Full: `docs/methodology.md#substrate-fungibility`.

[40] **Closed-loop pipeline** - frame → sample → induce → VET → perceive → VET → train substrate → VET → deploy → detect disagreement → triage [41] → refine ↺. Vetting at every transition, not at the end [36]. Same-distribution traces signal drift; different-corpus probes test generalization [37]. Full: `docs/methodology.md#pipeline`.

[41] **Triage taxonomy** - 3-bucket (classification): feature gap / label noise / DK gap. 4-bucket (predictive): adds multi-valid + trace error (model outperforms demonstrator). 5th bucket: segmentation gap [51]. 3-round stopping heuristic: diminishing returns past round 3, treat as load-bearing regularity [43]. Full: `docs/methodology.md#triage`.

[42] **Five-mode mirror taxonomy** - Five validation surfaces: Perception (point, model vs GT), kNN (neighborhood purity, no model needed), Cluster (semantic vs structural agreement), Layout (PCA + axis naming, visual), Feature quality (CatBoost loadings vs PCA loadings — disagreement between them is the sharpest signal [43]). These five modes ARE the SSP quality test framework [53]. Full: `docs/methodology.md#mirror-modes`.

[43] **Feature overfitting** - Induction can overfit features to corpus artifacts (inducer-bias, value sparsity, co-occurrence, meta-prompt). Detection: held-out split, cross-induction stability [11], coverage threshold, cross-substrate sensitivity [39][42]. Hard-warn past ~15 features [50]. Full: `docs/methodology.md#feature-overfitting`.

[44] **Product surfaces** - Six surfaces: Induction (`/karto induct`), Refinement (`/karto debug` + `induct --refine`), Visualization UI (belief_state [17]), Operational model (`/karto apply`), Story mode (narrative [26]), Learning mode (interactive induction). All share the human-vetting backbone [36]. Full: `docs/methodology.md#product-surfaces`.

[45] **Semlabel as Tier-1.5 backend** - Bounded region of embedding space, not a point: ~ms inference, handles paraphrase/synonym where regex fails [16][9]. Triage gate before LLM escalation; pre-tagging large corpora; high-volume per-feature scoring. Disagreement with LLM Q-A on same feature → AL boundary needs refinement. Full: `docs/methodology.md#semlabel-backend`.

[46] **Dual-substrate by default** - Every SSP ships rules + CatBoost (+ optional LLM); `score()` runs all and surfaces divergence. Diagnostic asymmetry: rules-wins → CatBoost overfit; CatBoost-wins → rules missing soft combinator; agree → high confidence. Single-substrate SSPs lose the unlabeled quality metric — hard warning [53]. Full: `docs/architecture.md#dual-substrate`.

[47] **SSP_META** - Every SSP declares: `input_concept`, `feature_concept`, `state_concept`, `leaf_concept`, `maintainer`, `version`, `decomposition_kind`. Tooling reads this for prose/errors/viz labels. `decomposition_kind`: descriptive (3-bucket triage) vs predictive (4-bucket triage [41]). Full: `docs/architecture.md#ssp-meta`.

[48] **SSP as Python module** - Each SSP is a self-contained `.py`, not JSON. Why: feature extractors, LLM sub-calls, policy, CatBoost all want code; JSON would force escape-to-Python. Exports: `score()`, `SSP_META`, `SSP_FEATURES`, `SSP_POSITIONS`, `SSP_CLUSTERS`; optional `score_rules`/`score_catboost`/`score_llm` for cascade [46]. Lives in `ssps/<name>/` folder. Full: `docs/architecture.md#ssp-module`.

[49] **Forward-pass trace** - Every `score()` captures per-feature value/backend/evidence/elapsed_ms + cluster assignment + divergence. Schema standardized across SSPs so meta-SSPs over traces work generically — `karto.ssp_base` defines this. Storage: `audits/traces/<date>/<trace_id>.json` [50]. Full: `docs/architecture.md#trace`.

[50] **Design imperatives** - Five: (1) hard-warn past ~15 features; (2) cascade by tier in every SSP [46]; (3) ensemble isolation via infrastructure not discipline [11]; (4) lightweight vetting UX (batch not individual [36]); (5) corpus ingestion first-class [51]. V1 criterion: dogfood-on-p8 [27]. Full: `docs/architecture.md#design-imperatives`.

[51] **Segmentation** - Segmentation IS the unit-of-analysis decision (first prong of framing [38]), not upstream preprocessing. Plugin ships adapters (`karto:ingest-yt`, `karto:ingest-pdf`, `karto:ingest-jsonl`); project keeps `ingestion.py` for bespoke sources. Adds 5th triage bucket: segmentation gap [41]. Full: `docs/architecture.md#segmentation`.

[52] **Three registers of instruction** - Process-level skills (`skills/karto/`, reusable across SSPs); per-SSP prompts (inline in `.py` [48], domain-specific); agent explanations (`CLAUDE.md` + `agents/` cards). Node→skill file map: [38]→`framing.md`, [42]→`mirror-modes.md`, [41]→`triage.md`, [46]→`substrate-cascade.md`, [43]→`overfit-defense.md`, [11]→`ensemble.md`. Full: `docs/architecture.md#instruction-registers`.

[53] **Testing strategy** - Three registers: (1) Contract (pytest): completeness (one FeatureTrace per declared feature [48]) + legality (values in declared space) + divergence categorization + error message quality; (2) SSP quality: five mirror modes [42] are the framework; dual-substrate disagreement = quality metric not CI failure [46]; (3) Command boundary: smoke tests only, never pin LLM output. Full: `docs/architecture.md#testing`.

---

## History

- 2026-05-02: Project conceived. p8 SSP fully induced as proof-of-concept. Naming locked. Nodes [1]–[34] written.
- 2026-05-02 (later): Methodology refinement session. Nodes [35]–[45] added: mirror thesis, lifecycle stages, induction algorithm, substrate fungibility, closed-loop pipeline, triage taxonomy, five-mode mirror, feature overfitting, product surfaces, semlabel Tier-1.5.
- 2026-05-04: Implementation-design session. Nodes [46]–[52] added: dual-substrate default, SSP_META, SSP as Python module, forward-pass trace, design imperatives, segmentation, three registers of instruction. V1 8-task build plan drafted. Commits: 1a09180 (initial scaffolding), 8c590cb (complete plugin scaffolding — README, docs/MIND_MAP.md, scripts/init, bin/release). Node [53] added: testing strategy.
- 2026-05-04 (later): MIND_MAP reformatted to single-line-per-node. Detailed content offloaded to `docs/methodology.md` (nodes [35]–[45]) and `docs/architecture.md` (nodes [46]–[53]). Nodes [12][30][31] merged into [32]; [34] folded into intro.
