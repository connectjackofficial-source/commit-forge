"""Tests for commit-forge batch 3: release.py and contributor.py."""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def _make_repo():
    """Build a throwaway git repo with two commits from one author."""
    tmp = Path(tempfile.mkdtemp())
    r = tmp / "repo"
    r.mkdir()
    env = {"GIT_AUTHOR_NAME": "Jack", "GIT_AUTHOR_EMAIL": "jack@example.com",
           "GIT_COMMITTER_NAME": "Jack", "GIT_COMMITTER_EMAIL": "jack@example.com"}
    def git(*args):
        subprocess.run(["git", "-C", str(r), *args], check=True,
                       capture_output=True, env=env)
    git("init", "-q")
    git("config", "user.name", "Jack")
    git("config", "user.email", "jack@example.com")
    (r / "a.txt").write_text("hello\n", encoding="utf-8")
    git("add", "a.txt")
    git("commit", "-q", "-m", "feat: first")
    (r / "a.txt").write_text("hello\nworld\n", encoding="utf-8")
    git("add", "a.txt")
    git("commit", "-q", "-m", "fix: second")
    (r / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 0.9.0 - 2026-10-18\n\n- new release helper\n"
        "- fixed parsing\n\n## 0.8.0\n\n- older\n", encoding="utf-8")
    return r


def test_release_parses_newest_version():
    r = _make_repo()
    out = subprocess.run([sys.executable, "scripts/release.py", str(r)],
                         capture_output=True, text=True,
                         cwd=Path(__file__).parent.parent)
    assert out.returncode == 0, out.stderr
    assert out.stdout.startswith("## 0.9.0"), out.stdout
    assert "new release helper" in out.stdout
    assert "older" not in out.stdout  # only newest block
    print("test_release_parses_newest_version: ok")


def test_release_check_tag_refuses_duplicate():
    r = _make_repo()
    subprocess.run(["git", "-C", str(r), "tag", "v0.9.0"], check=True)
    out = subprocess.run(
        [sys.executable, "scripts/release.py", str(r), "--check-tag"],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    assert out.returncode != 0
    assert "already exists" in out.stderr
    print("test_release_check_tag_refuses_duplicate: ok")


def test_contributor_sums():
    r = _make_repo()
    out = subprocess.run(
        [sys.executable, "scripts/contributor.py", str(r)],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    assert out.returncode == 0, out.stderr
    assert "Jack <jack@example.com>" in out.stdout
    line = next(ln for ln in out.stdout.splitlines()
                if "jack@example.com" in ln)
    assert line.split()[2] == "2", line  # commits column
    print("test_contributor_sums: ok")


if __name__ == "__main__":
    test_release_parses_newest_version()
    test_release_check_tag_refuses_duplicate()
    test_contributor_sums()
    print("commit-forge batch3 tests passed")
