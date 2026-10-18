#!/usr/bin/env python3
"""Per-author contribution summary: commits, files touched, insertions.

Lets maintainers see who drives the project. Uses `git shortlog` plus
`git log --numstat`, summed per author. Stdlib only.

Usage:
    python scripts/contributor.py [repo] [--top 10]
"""
import argparse
import subprocess
import sys
from collections import defaultdict


def shortlog(repo: str):
    out = subprocess.run(
        ["git", "-C", repo, "shortlog", "-sne", "HEAD"],
        capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"git shortlog failed: {out.stderr.strip()}")
    authors = []
    for ln in out.stdout.splitlines():
        count, _, name_email = ln.strip().partition("\t")
        authors.append((int(count.strip()), name_email.strip()))
    return authors


def numstat(repo: str):
    out = subprocess.run(
        ["git", "-C", repo, "log", "--pretty=format:%an <%ae>", "--numstat"],
        capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"git log --numstat failed: {out.stderr.strip()}")
    stats = defaultdict(lambda: [0, 0, 0])  # author -> [files, +, -]
    author = None
    for ln in out.stdout.splitlines():
        if not ln:
            author = None
            continue
        if author is None:
            author = ln
            continue
        added, removed, _ = ln.split("\t")
        if added == "-" or removed == "-":  # binary file
            continue
        stats[author][0] += 1
        stats[author][1] += int(added)
        stats[author][2] += int(removed)
    return stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", nargs="?", default=".",
                    help="path to the git repository (default: current dir)")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args(argv)

    commits = shortlog(args.repo)
    stats = numstat(args.repo)
    print(f"{'author':<36} {'commits':>8} {'files':>6} {'insertions':>10} "
          f"{'deletions':>9}")
    for count, identity in commits[: args.top]:
        files, ins, dele = stats.get(identity, [0, 0, 0])
        print(f"{identity:<36} {count:>8} {files:>6} {ins:>10} {dele:>9}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
