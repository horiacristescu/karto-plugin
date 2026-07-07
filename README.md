# Karto

State-space profiling toolkit for Claude Code. Karto helps you induce, apply, audit, and debug **State-Space Profiles (SSPs)** — discrete coordinate systems that map the positions of data points across any domain. An SSP becomes useful only when rendered runnable: as a model it acts as a mirror, flagging inconsistencies in data or the SSP itself.

**Start here:** [Agents don't need smarter models, they need a map](plugins/karto/docs/ssp-agents.md) — the long-form article on the SSP method: why agents fail, the named-state middle layer, tail-to-head induction from traces, the blame ladder, and running the map in production.

## Install

```bash
/plugin marketplace add horiacristescu/karto-plugin
```

Then bootstrap a project:

```bash
bash scripts/init my-project/
```

## Layout

```
.claude-plugin/       Plugin manifest (plugin.json, marketplace.json)
skills/karto/         Model-invoked methodology skills
commands/             User slash commands (/karto:apply, /karto:induct, /karto:debug)
agents/               Specialized agents (inducer, debugger)
src/karto/            Python library — SSP base types, feature backends, tracing
scripts/              init bootstrap script
docs/                 Curated public plugin docs
mcp/                  MCP server (future)
bin/                  Dev tooling (bin/release syncs to public repo)
release/              Public plugin repo (own git → github.com/horiacristescu/karto-plugin)
```

## Methodology

Karto's development methodology lives in root [MIND_MAP.md](MIND_MAP.md). The released plugin does not ship that dev memory verbatim; public docs, skills, commands, and agents carry the curated user-facing workflow.

Key concepts:
- **SSP** — discrete categorical features (3-6 hyphenated values) describing positions in a domain
- **Mirror thesis** — an SSP-as-text is weak; rendered as a runnable model it forces discrepancy detection
- **Dual substrate** — Python rules + CatBoost score every input by default; divergence is signal
- **Triage** — 3-round stopping heuristic, 5-bucket taxonomy (feature gap / label noise / DK gap / multi-valid / segmentation gap)

## User Project Layout (after `scripts/init`)

```
my-project/
  ssps/                   One subdir per SSP: ssps/<name>/{raw/, traces/, versions/}
  ingestion.py            Implement ingest(source) → list[dict] for your data sources
  CLAUDE.md               Karto-using instructions for agents working in this project
```
