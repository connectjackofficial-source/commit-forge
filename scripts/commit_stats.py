#!/usr/bin/env python3
"""Analyze a git history for commit-type and cadence statistics.

Turns a plain `git log` into actionable numbers: which Conventional
Commits types dominate, how busy the repo is per day, and which scopes
get the most churn.

Usage:
    git log --pretty=format:%ad%x09%s --date=short | python commit_stats.py
    python commit_stats.py --repo /path/to/repo --days 90
    python commit_stats.py --log commits.txt
"""
import argparse
import re
import subprocess
import sys
from collections import Counter

TYPE_RE = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[\w.\-/]*)\))?(?P<breaking>!)?: .+")


def parse_lines(lines):
    """Parse "<iso-date>\\t<message>" lines into (date, type, scope, breaking)."""
    rows = []
    for line in lines:
        line = line.rstrip("\n")
        if not line or "\t" not in line:
            continue
        date, message = line.split("\t", 1)
        m = TYPE_RE.match(message)
        if not m:
            continue
        rows.append({"date": date, "type": m.group("type"),
                     "scope": m.group("scope") or "",
                     "breaking": bool(m.group("breaking"))})
    return rows


def stats(rows):
    """Aggregate parsed rows into summary statistics."""
    total = len(rows)
    by_type = Counter(r["type"] for r in rows)
    by_day = Counter(r["date"] for r in rows)
    by_scope = Counter(r["scope"] for r in rows if r["scope"])
    breaking = sum(1 for r in rows if r["breaking"])
    days = len(by_day)
    return {
        "total": total,
        "by_type": dict(by_type.most_common()),
        "by_day": dict(sorted(by_day.items())),
        "top_scopes": dict(by_scope.most_common(10)),
        "breaking_changes": breaking,
        "active_days": days,
        "avg_commits_per_active_day": round(total / days, 2) if days else 0,
    }


def render(stats_dict):
    lines = [f"commits:        {stats_dict['total']}",
             f"active days:    {stats_dict['active_days']}",
             f"commits/day:    {stats_dict['avg_commits_per_active_day']}",
             f"breaking:       {stats_dict['breaking_changes']}",
             ""]
    lines.append("by type:")
    for t, n in stats_dict["by_type"].items():
        lines.append(f"  {t:<12} {n}")
    if stats_dict["top_scopes"]:
        lines.append("top scopes:")
        for s, n in stats_dict["top_scopes"].items():
            lines.append(f"  {s:<16} {n}")
    return "\n".join(lines)


def git_log_lines(repo, days):
    cmd = ["git", "-C", repo, "log",
           "--pretty=format:%ad%x09%s", "--date=short"]
    if days:
        cmd += [f"--since={days} days ago"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return out.stdout.splitlines()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--repo", help="path to a git repository")
    src.add_argument("--log", help="file with '<iso-date>\\t<message>' lines")
    ap.add_argument("--days", type=int, default=0,
                    help="only look back N days (with --repo)")
    args = ap.parse_args(argv)

    if args.repo:
        lines = git_log_lines(args.repo, args.days)
    else:
        with open(args.log, encoding="utf-8") as f:
            lines = f.read().splitlines()
    rows = parse_lines(lines)
    print(render(stats(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
