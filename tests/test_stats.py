"""Tests for commit_stats parsing and aggregation."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.commit_stats import parse_lines, render, stats

SAMPLE = [
    "2026-10-10\tfeat(cli): add --by-model flag",
    "2026-10-10\tfix(core): handle null token",
    "2026-10-11\tfeat!: drop legacy API",
    "2026-10-11\tdocs: update README",
    "2026-10-12\tfeat(api): batch endpoints",
    "not-a-commit-line\tignored garbage",
]


def test_parse_lines():
    rows = parse_lines(SAMPLE)
    assert len(rows) == 5  # garbage line skipped
    assert rows[0]["type"] == "feat" and rows[0]["scope"] == "cli"
    assert rows[2]["breaking"] is True
    print("test_parse_lines: ok")


def test_stats_aggregation():
    rows = parse_lines(SAMPLE)
    s = stats(rows)
    assert s["total"] == 5
    assert s["by_type"]["feat"] == 3
    assert s["active_days"] == 3
    assert s["breaking_changes"] == 1
    assert abs(s["avg_commits_per_active_day"] - 5 / 3) < 0.01
    assert s["top_scopes"]["cli"] == 1
    print("test_stats_aggregation: ok")


def test_render_contains_fields():
    rows = parse_lines(SAMPLE)
    out = render(stats(rows))
    assert "commits:" in out and "by type:" in out
    assert "feat" in out
    print("test_render_contains_fields: ok")


def test_git_log_integration():
    # smoke test against a real (tiny) repository, skipped if git is absent
    import shutil
    import subprocess
    if not shutil.which("git"):
        print("test_git_log_integration: skipped (no git)")
        return
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-b", "main", d],
                       capture_output=True, check=True)
        subprocess.run(["git", "-C", d, "config", "user.email", "t@t.t"],
                       capture_output=True, check=True)
        subprocess.run(["git", "-C", d, "config", "user.name", "t"],
                       capture_output=True, check=True)
        (Path(d) / "a.txt").write_text("x", encoding="utf-8")
        subprocess.run(["git", "-C", d, "add", "."], capture_output=True)
        subprocess.run(["git", "-C", d, "commit", "-q",
                        "-m", "feat(scaffold): init"], capture_output=True)
        rows = parse_lines(
            subprocess.run(
                ["git", "-C", d, "log", "--pretty=format:%ad%x09%s",
                 "--date=short"],
                capture_output=True, text=True, check=True).stdout.splitlines())
        assert len(rows) == 1 and rows[0]["type"] == "feat"
    print("test_git_log_integration: ok")


if __name__ == "__main__":
    test_parse_lines()
    test_stats_aggregation()
    test_render_contains_fields()
    test_git_log_integration()
    print("commit-forge stats tests passed")
