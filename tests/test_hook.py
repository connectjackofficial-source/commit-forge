#!/usr/bin/env python3
"""Tests for install_hook: rendering and install/uninstall round-trip."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from install_hook import install, render_hook, uninstall


def test_render_hook_contains_parts():
    script = Path("C:/repos/commit-forge/scripts/commit_lint.py")
    text = render_hook(script)
    assert "commit-msg" in text or "COMMIT_MSG_FILE" in text
    assert "commit_lint.py" in text
    print("test_render_hook_contains_parts: ok")


def test_install_uninstall_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "repo"
        (root / ".git" / "hooks").mkdir(parents=True)
        lint = Path(d) / "commit_lint.py"
        lint.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        target = install(lint, root)
        assert target.exists()
        content = target.read_text(encoding="utf-8")
        assert "COMMIT_MSG_FILE" in content
        assert str(lint).replace("\\", "/") in content

        assert uninstall(root) is True
        assert not target.exists()
        assert uninstall(root) is False  # idempotent
    print("test_install_uninstall_roundtrip: ok")


if __name__ == "__main__":
    test_render_hook_contains_parts()
    test_install_uninstall_roundtrip()
    print("install_hook tests passed")
