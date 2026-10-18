#!/usr/bin/env python3
"""Turn the top CHANGELOG section into a GitHub-release-ready body.

Reads the newest "# [version]" block from CHANGELOG.md and prints a
markdown release note. With --check-tag it also verifies whether the
matching git tag already exists (so releases aren't cut twice).

Usage:
    python scripts/release.py [repo] [--check-tag] [--out notes.md]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def parse_changelog(path: Path):
    """Return (version, body_lines) of the newest version block."""
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^##\s+", text)
    for block in blocks[1:]:
        head, _, rest = block.partition("\n")
        m = re.match(r"([0-9]+(?:\.[0-9]+)+)", head.strip())
        if m:
            return m.group(1), [ln for ln in rest.splitlines() if ln.strip()]
    raise SystemExit("no version block found in CHANGELOG.md")


def tag_exists(repo: str, version: str) -> bool:
    out = subprocess.run(
        ["git", "-C", repo, "tag", "-l", f"v{version}"],
        capture_output=True, text=True)
    return bool(out.stdout.strip())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", nargs="?", default=".",
                    help="path to the git repository (default: current dir)")
    ap.add_argument("--check-tag", action="store_true",
                    help="fail if the v<version> tag already exists")
    ap.add_argument("--out", help="write notes to a file instead of stdout")
    args = ap.parse_args(argv)

    changelog = Path(args.repo) / "CHANGELOG.md"
    version, lines = parse_changelog(changelog)
    if args.check_tag and tag_exists(args.repo, version):
        sys.exit(f"tag v{version} already exists; refusing to re-release")

    body = [f"## {version}", ""]
    body += [ln.lstrip("- ") if ln.startswith("-") else ln for ln in lines]
    body += ["", "---", "Full changelog: [CHANGELOG.md](CHANGELOG.md)"]
    text = "\n".join(body) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({len(lines)} bullet points)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
