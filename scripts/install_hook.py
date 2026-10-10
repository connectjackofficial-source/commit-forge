#!/usr/bin/env python3
"""Install a commit-msg git hook that lints commit messages.

Every commit in the repo gets checked against Conventional Commits before
it is created. Invalid messages are rejected with a pointer to the fix.

Usage:
    python install_hook.py              # install
    python install_hook.py --uninstall  # remove
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

HOOK_NAME = "commit-msg"
HOOK_TEMPLATE = """#!/bin/sh
# Managed by commit-forge install_hook.py
# Reject non-conventional commit messages.
COMMIT_MSG_FILE="$1"
exec "{python}" "{lint_script}" --message "$(cat "$COMMIT_MSG_FILE")"
"""


def find_git_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise SystemExit("Not inside a git repository.")
    return Path(out.stdout.strip())


def hook_path(repo_root: Path) -> Path:
    return repo_root / ".git" / "hooks" / HOOK_NAME


def render_hook(lint_script: Path) -> str:
    return HOOK_TEMPLATE.format(
        python=sys.executable.replace("\\", "/"),
        lint_script=str(lint_script).replace("\\", "/"),
    )


def install(lint_script: Path, repo_root: Path) -> Path:
    target = hook_path(repo_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_hook(lint_script), encoding="utf-8")
    return target


def uninstall(repo_root: Path) -> bool:
    target = hook_path(repo_root)
    if target.exists():
        target.unlink()
        return True
    return False


def main():
    ap = argparse.ArgumentParser(prog="install_hook.py")
    ap.add_argument("--uninstall", action="store_true",
                    help="remove the hook instead of installing")
    ap.add_argument("--lint-script", default=None,
                    help="path to commit_lint.py (default: beside this script)")
    args = ap.parse_args()

    repo_root = find_git_root()
    lint_script = Path(args.lint_script) if args.lint_script \
        else Path(__file__).resolve().parent / "commit_lint.py"

    if args.uninstall:
        removed = uninstall(repo_root)
        print("Hook removed." if removed else "No hook was installed.")
        sys.exit(0)

    target = install(lint_script, repo_root)
    print(f"commit-msg hook installed at {target}")
    print("Every commit message is now linted against Conventional Commits.")


if __name__ == "__main__":
    main()
