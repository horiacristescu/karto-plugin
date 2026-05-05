---
name: segmentation
description: Given a raw corpus file, produce segmented units in corpus/units/ (static) or corpus/traces/ (temporal). Each unit is a self-contained chunk with provenance metadata.
applies-to: ssps/<domain>/corpus/
output: corpus/units/*.json or corpus/traces/*.json
---

# Segmentation Skill

## Purpose

Turn a raw corpus into individually addressable units. Each unit becomes one candidate position in an SSP induction. The unit is the atom — everything downstream (discretization, scoring, comparison) operates on units.

---

## Step 1 — Scope the corpus

Before reading anything, measure it:

```bash
wc -l -c corpus/raw/*
```

If a file is large (>500 lines), do NOT read it whole. Instead, view its spine:

```bash
# The spine: line numbers + first 50 chars — reveals structure at a glance
cat corpus/raw/file.md | cut -c -50 | nl | head -80

# Find section/heading markers
grep -n "^#\|^##\|^\[" corpus/raw/file.md | head -40

# Find turn or timestamp markers (for temporal logs)
grep -n "^User\|^Assistant\|^---\|^\d\{4\}-\d\{2\}" corpus/raw/file.md | head -40

# Sample tail to see how it ends
tail -30 corpus/raw/file.md

# Sample a mid-file window
sed -n '200,230p' corpus/raw/file.md
```

`cut -c -50 | nl` is the primary spine tool for large text: it shows the first 50 characters of every line with line numbers, giving the document's structure without reading its content.

From this, identify:
- **Format kind**: markdown, jsonl, plain transcript, structured log
- **Corpus kind**: static (collection of ideas/cases) or temporal (sequence of steps/turns)
- **Natural boundaries**: heading changes, blank-line clusters, timestamp jumps, separator tokens
- **Approximate unit count**: number of sections / turns / episodes

Record findings before proceeding. If the spine is ambiguous, sample two or three mid-file windows with `sed -n '200,230p' file.md`.

---

## Step 2 — Identify the segmentation strategy

**Static corpora** (lecture transcripts, papers, design case collections, conceptual discussions):

| Signal | Strategy |
|--------|----------|
| One file per position already | No segmentation needed — each file IS a unit (e.g., `corpus/runs/run_01.md`) |
| One large file with all positions | Extract each position: split on headings, table rows, or numbered entries |
| Markdown headings (`##`, `###`) | Split on headings — each section is a unit |
| Numbered propositions or cases | Split on proposition boundaries |
| Paragraph clusters with blank lines | Split on double-blank-line groups |
| No clear structure | LLM-assisted: ask LLM to identify proposition-level chunks (see Step 3b) |

When `corpus/` already contains one file per position (conceptual SSPs induced from agent-generated cases), segmentation is done — go directly to induction. When it contains one large file with all positions (e.g., a position-matrix markdown), extract each row/section as a unit.

Output: `corpus/units/unit_NNN.json`

**Temporal corpora** (CUA logs, coding agent sessions, chat logs, task.md gate sequences, conversation transcripts):

For agent-generated data, segmentation comes naturally from the source — the structure IS the segmentation. Each turn, action, or gate is already a discrete unit. No LLM assistance needed; just parse the existing boundaries.

| Format | Natural boundary | Unit |
|--------|-----------------|------|
| `chat_log.md` | `User:` / `Assistant:` markers | one exchange (user turn + response) |
| `bash_history` | newline per command | one command invocation |
| `task.md` | `- [ ]` / `- [x]` lines | one gate + its annotation |
| jsonl | newline | one JSON object |
| JSON array file | array element | one step/action (extract with `jq '.[]'`) |
| CUA trace (timestamped) | timestamp + action type | one action or completed episode |
| conversation log | turn separator | one turn |

The main decision: **what is the unit of analysis?** A CUA session could be segmented by individual action OR by completed task episode — different framings yield different SSPs [38]. Make this choice explicitly before writing `segmentation.py`.

Output: `corpus/traces/step_NNN.json`

---

## Step 3a — Segment (structural, automatic)

For corpora with clear structural boundaries, write `segmentation.py` in the domain folder:

```python
# segmentation.py — adapt to actual format
from pathlib import Path
import re, json

def segment(source: str, mode: str = "headings") -> list[dict]:
    text = Path(source).read_text()
    units = []
    if mode == "headings":
        parts = re.split(r'\n(?=## )', text)
        for i, part in enumerate(parts):
            if part.strip():
                first_line = part.splitlines()[0]
                units.append({
                    "id": f"unit_{i+1:03d}",
                    "source": source,
                    "line_start": None,   # fill if needed
                    "text": part.strip(),
                    "heading": first_line.lstrip("#").strip(),
                })
    return units

if __name__ == "__main__":
    import sys
    units = segment(sys.argv[1], mode=sys.argv[2] if len(sys.argv) > 2 else "headings")
    out = Path("corpus/units")
    out.mkdir(parents=True, exist_ok=True)
    for u in units:
        (out / f"{u['id']}.json").write_text(json.dumps(u, indent=2))
    print(f"Segmented {len(units)} units → corpus/units/")
```

Run it: `python segmentation.py corpus/raw/source.md headings`

Always include in each unit:
- `id`: stable identifier (`unit_001`, `step_042`)
- `source`: path to raw file
- `line_start` / `line_end` or `timestamp`: provenance — required for audit
- `text`: the actual content

---

## Step 3b — Segment (LLM-assisted, unstructured)

When the corpus has no clear structural markers, ask an LLM to identify proposition-level chunks. Prompt pattern:

> Read the following text. Identify each distinct proposition, claim, or conceptual unit. For each, output: ID, a one-sentence summary, the verbatim text span, and approximate line range. Output as JSON array.

Then write the results to `corpus/units/unit_NNN.json` with the same schema as Step 3a.

Use this path for:
- Raw lecture transcripts without timestamps
- Free-form discussion documents
- Corpora where units are semantic, not syntactic

---

## Step 4 — Handle pre-segmented corpora

If `corpus/` already contains a discretized file (e.g., `p9.discretized3.md` with one proposition per line), it is already segmented. Skip Steps 1–3.

Verify: does each line/block represent one independent unit? If yes, treat it as the unit source directly and skip to induction. If the pre-segmentation is coarser than needed, run a second pass.

---

## Step 5 — Verify output

```bash
ls corpus/units/ | wc -l        # count units produced
head -20 corpus/units/unit_001.json   # spot-check first unit
grep -l '"source"' corpus/units/*.json | wc -l   # confirm provenance in all
```

Expect: unit count roughly matches the section/turn/episode count identified in Step 1. If wildly off (10× too many or too few), re-examine the boundary detection.

---

## Outputs

| Path | Contents |
|------|----------|
| `corpus/units/unit_NNN.json` | Static corpus units |
| `corpus/traces/step_NNN.json` | Temporal corpus traces |
| `segmentation.py` | Reproducible parser (commit this) |

The unit files are the input to the induction skill (`induct.md`).
