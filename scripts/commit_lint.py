#!/usr/bin/env python3
"""Lint a commit message against the Conventional Commits 1.0.0 spec.

Usage:
    echo "feat(scope): add login button" | python commit_lint.py
    python commit_lint.py --message "fix(api): handle null token"

Exit code 0 = valid, 1 = invalid. Prints human-readable findings.
"""
import argparse
import re
import sys

TYPES = {
    "feat": "A new feature (maps to MINOR in SemVer)",
    "fix": "A bug fix (maps to PATCH)",
    "docs": "Documentation only",
    "style": "Formatting, no code meaning change",
    "refactor": "Neither fix nor feature",
    "perf": "Performance improvement",
    "test": "Adding or correcting tests",
    "build": "Build system / external deps",
    "ci": "CI configuration",
    "chore": "Other changes that don't touch src/tests",
    "revert": "Reverts a previous commit",
}

# type(scope)!: subject   <- first line, <= 72 chars
HEADER_RE = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[\w.\-/]*)\))?(?P<breaking>!)?: (?P<subject>.+)$"
)


def lint(message: str):
    problems = []
    # Drop trailing newline / CR
    lines = message.replace("\r", "").split("\n")
    header = lines[0].strip() if lines else ""

    if not header:
        return ["Empty commit message."]

    if len(header) > 72:
        problems.append(
            f"Header too long: {len(header)} chars (max 72). "
            "Keep the first line a tight summary."
        )

    m = HEADER_RE.match(header)
    if not m:
        problems.append(
            "Header does not match Conventional Commits pattern:\n"
            "    type(scope)!: subject\n"
            "Example: feat(auth): add magic-link login"
        )
        return problems

    if m["type"] not in TYPES:
        problems.append(
            f"Unknown type '{m['type']}'. Use one of: {', '.join(TYPES)}."
        )

    subject = m["subject"]
    if subject.endswith("."):
        problems.append("Subject should not end with a period.")
    if subject[0].isupper():
        problems.append("Subject should be lowercase (imperative mood).")
    if len(subject) > 50:
        problems.append(
            f"Subject is {len(subject)} chars; aim for <= 50 for the summary line."
        )

    # Body: blank-separated after header
    if len(lines) > 1:
        if lines[1].strip() != "":
            problems.append("Insert a blank line between header and body.")

    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--message", "-m", help="Commit message to lint")
    args = ap.parse_args()

    if args.message is not None:
        msg = args.message
    else:
        msg = sys.stdin.read()

    problems = lint(msg)
    if not problems:
        print("OK: conventional commit looks good.")
        sys.exit(0)
    print("INVALID COMMIT MESSAGE:")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)


if __name__ == "__main__":
    main()
