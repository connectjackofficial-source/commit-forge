#!/usr/bin/env python3
"""Gather structured context from git so the agent writes a *specific* commit
message instead of a generic one.

Usage:
    python diff_context.py          # staged changes
    python diff_context.py --unstaged
    python diff_context.py --branch # what this branch changed vs main

Prints a compact, token-aware summary the agent can reason over.
"""
import argparse
import shutil
import subprocess
import sys


def run(args):
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except FileNotFoundError:
        print("git not found on PATH. Install git first.", file=sys.stderr)
        sys.exit(2)
    except subprocess.TimeoutExpired:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unstaged", action="store_true")
    ap.add_argument("--branch", action="store_true",
                    help="Summarize changes vs the merge-base with main/master")
    ap.add_argument("--stat-only", action="store_true",
                    help="Skip the actual patch, just file stats (saves tokens)")
    args = ap.parse_args()

    if shutil.which("git") is None:
        print("git not found on PATH.", file=sys.stderr)
        sys.exit(2)

    branch = run(["git", "branch", "--show-current"])
    print(f"## branch: {branch or '(detached)'}")

    recent = run(["git", "log", "--oneline", "-10"])
    if recent:
        print("## recent commits (style reference):")
        print(recent)

    if args.branch:
        base = "main" if run(["git", "rev-parse", "--verify", "main"]) else "master"
        print(f"\n## files changed vs {base}:")
        print(run(["git", "diff", "--stat", f"{base}...HEAD"]))
        if not args.stat_only:
            patch = run(["git", "diff", f"{base}...HEAD"])
    else:
        name = "--name-status" if args.stat_only else "--cached"
        print("\n## staged files:")
        print(run(["git", "diff", "--cached", "--stat"]))
        if not args.stat_only:
            patch = run(["git", "diff", "--cached"])

    if not args.stat_only:
        print("\n## patch (truncated to 8000 chars):")
        print((patch if isinstance(patch, str) else "")[:8000])


if __name__ == "__main__":
    main()
