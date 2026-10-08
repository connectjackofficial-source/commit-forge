#!/usr/bin/env python3
"""Tests for commit_lint: JSON mode and custom types."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from commit_lint import lint

VALID = "feat(auth): add magic-link login\n"
BAD = "ADD login button.\n"


def test_lint_valid():
    assert lint(VALID) == []
    assert len(lint(BAD)) > 0
    print("test_lint_valid: ok")


def test_custom_types():
    # 'release' is not built-in
    msg = "release(api): cut 2.0.0\n"
    assert any("Unknown type" in p for p in lint(msg))
    # allowed via extra_types
    assert lint(msg, extra_types=("release",)) == []
    print("test_custom_types: ok")


def test_json_mode():
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "commit_lint.py"),
         "--message", "ADD login button.", "--json"],
        capture_output=True, text=True)
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert data["valid"] is False
    assert len(data["problems"]) > 0
    assert "feat" in data["types"]
    print("test_json_mode: ok")


if __name__ == "__main__":
    test_lint_valid()
    test_custom_types()
    test_json_mode()
    print("commit_lint tests passed")
