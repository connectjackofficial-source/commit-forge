#!/usr/bin/env python3
"""Scaffold a review-ready PR body from the branch's commits and changed files.

The agent fills in the testing/why sections; this script removes the
blank-canvas problem that makes PR descriptions generic.

Usage:
    python pr_body.py                 # vs main/master
    python pr_body.py --base develop
"""
import argparse
import subprocess
import sys


def run(args):
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except FileNotFoundError:
        print("git not found on PATH.", file=sys.stderr)
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None)
    args = ap.parse_args()

    base = args.base
    if not base:
        base = "main" if run(["git", "rev-parse", "--verify", "main"]) else "master"

    branch = run(["git", "branch", "--show-current"])
    commits = run(["git", "log", "--oneline", f"{base}..HEAD"])
    files = run(["git", "diff", "--stat", f"{base}...HEAD"])

    body = f"""## Summary
<!-- 1-3 bullets: what changed and WHY, not what the code does line by line -->

## Commits on this branch
{commits or '(none)'}

## Files changed
```
{files or '(none)'}
```

## How to test
- [ ] Steps a reviewer can run locally
- [ ] Expected outcome

## Risk / rollback
- Risk level: low / medium / high
- Rollback: revert this PR / toggle feature flag

## Screenshots (if UI)
"""
    print(body)


if __name__ == "__main__":
    main()
