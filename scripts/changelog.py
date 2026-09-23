#!/usr/bin/env python3
"""Turn conventional commits since the last tag into a Keep-a-Changelog block.

Only feat / fix / perf / breaking changes are user-facing. The agent edits the
output into polished language; this gives it a correct first draft.

Usage:
    python changelog.py                 # since last tag
    python changelog.py --since v1.2.0
"""
import argparse
import re
import subprocess
import sys

HEADER_RE = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[\w.\-/]*)\))?(?P<breaking>!)?: (?P<subject>.+)$"
)
USER_FACING = {"feat": "Added", "fix": "Fixed", "perf": "Performance"}


def run(args):
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except FileNotFoundError:
        print("git not found on PATH.", file=sys.stderr)
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None)
    args = ap.parse_args()

    since = args.since or run(["git", "describe", "--tags", "--abbrev=0"])
    if not since:
        since = "HEAD~10"
        range_spec = since
    else:
        range_spec = f"{since}..HEAD"

    log = run(["git", "log", range_spec, "--pretty=format:%s%n%b%n---"])

    buckets = {"Added": [], "Fixed": [], "Performance": []}
    breaking = []
    for line in log.splitlines():
        line = line.strip()
        if not line or line == "---":
            continue
        m = HEADER_RE.match(line)
        if not m:
            continue
        t = m["type"]
        subj = m["subject"]
        if m["breaking"] or line.startswith("BREAKING CHANGE"):
            breaking.append(subj)
        if t in USER_FACING:
            buckets[USER_FACING[t]].append(subj)

    out = [f"## Unreleased (since {since})"]
    if breaking:
        out.append("### BREAKING CHANGES")
        out += [f"- {b}" for b in breaking]
    for section, items in buckets.items():
        if items:
            out.append(f"### {section}")
            out += [f"- {i}" for i in items]
    if len(out) == 1:
        out.append("_No user-facing changes._")
    print("\n".join(out))


if __name__ == "__main__":
    main()
