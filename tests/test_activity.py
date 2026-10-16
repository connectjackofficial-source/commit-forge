"""Tests for commit-forge scripts/activity.py (subprocess level)."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _make_repo() -> Path:
    base = tempfile.mkdtemp()
    repo = Path(base) / "repo"
    repo.mkdir()
    env = dict(os.environ, GIT_AUTHOR_DATE="2026-10-10T10:00:00+08:00",
               GIT_COMMITTER_DATE="2026-10-10T10:00:00+08:00")
    subprocess.run(["git", "-C", str(repo), "init", "-b", "main"],
                   capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "T"],
                   capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email",
                    "t@example.com"], capture_output=True)
    (repo / "a.txt").write_text("x\n")
    subprocess.run(["git", "-C", str(repo), "add", "."], capture_output=True,
                   env=env)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "feat: one"],
                   capture_output=True, env=env)
    return repo


def test_activity_output():
    repo = _make_repo()
    out = subprocess.run([sys.executable, str(Path(__file__).parent.parent /
                                              "scripts" / "activity.py"),
                          str(repo)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "2026-W41" in out.stdout
    assert "active days: 1" in out.stdout
    assert "longest streak: 1 days" in out.stdout
    print("test_activity_output: ok")


if __name__ == "__main__":
    test_activity_output()
    print("commit-forge activity tests passed")
