# Karto Plugin — Release Repo

This directory is a separate git repository that holds only the distributable plugin files.
It is pushed to a public GitHub repo so users can install via Claude Code's plugin marketplace.

## Setup (one-time)

Create the public GitHub repo and connect it:

```bash
gh repo create horiacristescu/karto-plugin --public --description "State-space profiling toolkit for Claude Code"
git -C release remote add origin git@github.com:horiacristescu/karto-plugin.git
```

## Releasing

From the dev repo root (`~/Code/karto/`):

```bash
bin/release "Release message"
```

This syncs distributable files from dev → `release/plugins/karto/`, commits, and pushes.
Use `bin/release --no-push "message"` to sync and commit without pushing (useful when remote not yet set).

## Layout

```
release/
  .claude-plugin/marketplace.json   # marketplace manifest (repo root)
  plugins/karto/                    # plugin files
    .claude-plugin/plugin.json
    commands/
    skills/karto/
    agents/
    code/karto/
    docs/
    scripts/
    mcp/
```

## Install (users)

```
/plugin marketplace add horiacristescu/karto-plugin
```
