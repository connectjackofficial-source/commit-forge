#!/usr/bin/env python3
"""Weekly activity profile of a git repo: commits per ISO week and the
longest active streak. Stdlib only; shells out to `git log`.

Usage:
    python scripts/activity.py [repo] [--weeks 8]
"""
import argparse
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta


def _iso_week(d: date):
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def git_log(repo: str) -> list:
    out = subprocess.run(
        ["git", "-C", repo, "log", "--pretty=format:%ai|%s"],
        capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"git log failed: {out.stderr.strip()}")
    return [ln for ln in out.stdout.splitlines() if ln]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--weeks", type=int, default=8)
    args = ap.parse_args(argv)

    per_week = Counter()
    per_day = Counter()
    for ln in git_log(args.repo):
        iso, _ = ln.split("|", 1)
        day = date.fromisoformat(iso[:10])
        per_week[_iso_week(day)] += 1
        per_day[day.isoformat()] += 1

    if not per_week:
        print("no commits")
        return 1

    weeks = sorted(per_week)[-args.weeks:]
    width = max(len(str(n)) for n in per_week.values()) + 1
    for w in weeks:
        bar = "#" * per_week[w]
        print(f"{w}  {per_week[w]:>{width}}  {bar}")

    # longest streak of consecutive active days
    best = cur = 0
    last = None
    for day_str in sorted(per_day):
        d = date.fromisoformat(day_str)
        if last is not None and (d - last).days == 1:
            cur += 1
        else:
            cur = 1
        best = max(best, cur)
        last = d
    print(f"\nactive days: {len(per_day)}   longest streak: {best} days")
    return 0


if __name__ == "__main__":
    sys.exit(main())
