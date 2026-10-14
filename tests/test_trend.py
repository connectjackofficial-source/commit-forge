"""Tests for commit_stats weekly trend."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.commit_stats import parse_lines, trend


def _rows():
    lines = [
        "2026-10-05\tfeat(core): alpha\n",
        "2026-10-06\tfix: beta\n",
        "2026-10-12\tfeat: gamma\n",       # next ISO week
        "2026-10-12\tfeat: delta\n",
        "not-a-commit\n",
        "2026-10-13\tchore!: breaking\n",
    ]
    return parse_lines(lines)


def test_weekly_grouping():
    rows = _rows()
    weeks = trend(rows, weeks=12)
    counts = {w["week"]: w["commits"] for w in weeks}
    assert counts["2026-W41"] == 2   # 10-05/06
    assert counts["2026-W42"] == 3   # 10-12/13
    print("test_weekly_grouping: ok")


def test_newest_first():
    rows = _rows()
    weeks = trend(rows, weeks=12)
    assert weeks[-1]["week"] == "2026-W42"  # newest last in list
    assert weeks[0]["week"] == "2026-W41"
    print("test_newest_first: ok")


def test_weeks_limit():
    rows = _rows()
    # force a 20-week spread by appending an old commit
    rows.append({"date": "2026-06-01", "type": "feat",
                 "scope": "", "breaking": False})
    weeks = trend(rows, weeks=4)
    assert len(weeks) <= 4  # cap respected; only 3 distinct weeks exist
    assert weeks[0]["week"] == "2026-W23"  # oldest retained
    print("test_weeks_limit: ok")


def test_invalid_dates_skipped():
    rows = [{"date": "garbage", "type": "feat", "scope": "", "breaking": False}]
    assert trend(rows) == []
    print("test_invalid_dates_skipped: ok")


if __name__ == "__main__":
    test_weekly_grouping()
    test_newest_first()
    test_weeks_limit()
    test_invalid_dates_skipped()
    print("commit-forge trend tests passed")
