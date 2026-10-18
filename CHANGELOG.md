# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/).

## [1.6.0] - 2026-10-18

### Added
- `scripts/release.py` — turn the newest changelog block into a
  GitHub-release-ready body; `--check-tag` refuses duplicate releases
- `scripts/contributor.py` — per-author summary (commits, files,
  insertions, deletions) via shortlog + numstat

## [1.5.0] - 2026-10-14

### Added
- `trend()` — weekly (ISO week) commit counts for cadence charts;
  `--trend WEEKS` flag on the CLI
- `tests/test_trend.py` covering ISO-week grouping and edge cases

## [1.4.0] - 2026-10-14

### Added
- `commit_stats.py` — analyze `git log` for type mix, daily cadence,
  top scopes and breaking-change counts; pipe or `--repo` mode
- `tests/test_stats.py` covering parsing, aggregation, rendering and a
  real-repo smoke test

## [1.3.0] - 2026-10-10

### Added
- `suggest_type()` — guess the Conventional Commits type from subject wording
- Tests for type suggestion (feat/fix/docs/test/refactor/perf/revert/chore)

## [1.2.0] - 2026-10-10

### Added
- `install_hook.py` — commit-msg git hook installer (auto-lint every commit)
- `tests/test_hook.py` — hook render + install/uninstall tests

## [1.1.0] - 2026-10-08

### Added
- `commit_lint.py --json` — machine-readable validation for CI hooks
- `commit_lint.py --extra-types` — custom commit types support
- `tests/test_lint.py` — unit tests for lint, JSON mode, custom types

## [1.0.0] - 2026-09-23

### Added
- `commit_lint.py` — Conventional Commits 1.0.0 linter
- `diff_context.py` — structured staged/branch diff context
- `pr_body.py` — review-ready PR template
- `changelog.py` — Keep-a-Changelog draft from feat/fix/perf commits
- `SKILL.md` — agent skill instructions
