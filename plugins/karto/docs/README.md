# Karto Plugin Docs

Karto turns state-space profiles (SSPs) into runnable, inspectable Python modules.
The plugin distribution keeps public docs, skills, commands, agents, and runtime
code here. The development repo's root `MIND_MAP.md` is not shipped as plugin
documentation; it is project memory for planning and design history.

## Boundaries

- `docs/` contains curated public documentation for plugin users.
- `skills/karto/` contains process-level methodology instructions for agents.
- `commands/` contains user-facing slash command entry points.
- `agents/` contains role cards and handoff protocols.
- Root `MIND_MAP.md` remains dev-only institutional memory.

## Current Runtime Contract

User-authored SSP modules declare `SSP_META`, `SSP_FEATURES`, `SSP_POSITIONS`,
and a `score(record)` function returning a raw dict. Karto normalizes that into
JSON with `result`, `features`, `divergence`, and `elapsed_ms`.

Use the Python smoke commands while command docs are still being built:

```bash
python -m karto.validate path/to/ssp.py
python -m karto.score path/to/ssp.py path/to/input.json
```
