"""Render every SSP found under ssps/ to map.png + map_audit.md.

Usage:
    python -m karto.render_all
    python -m karto.render_all --k 5 --center
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--center", action="store_true")
    ap.add_argument("--root", type=Path, default=Path("ssps"),
                    help="root directory to search (default: ssps/)")
    args = ap.parse_args()

    ssp_files = sorted(args.root.rglob("ssp_v*.py"))
    if not ssp_files:
        print(f"No ssp_v*.py files found under {args.root}")
        sys.exit(1)

    print(f"Found {len(ssp_files)} SSP(s):\n")
    ok = failed = 0
    for path in ssp_files:
        cmd = [sys.executable, "-m", "karto.render_report", str(path), "--k", str(args.k)]
        if args.center:
            cmd.append("--center")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
            ok += 1
        else:
            print(f"FAILED: {path}")
            print(result.stderr.strip())
            failed += 1
        print()

    print(f"Done: {ok} rendered, {failed} failed.")


if __name__ == "__main__":
    main()
