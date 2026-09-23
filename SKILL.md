---
name: commit-forge
description: >
  Ship-ready git workflow skill for AI coding agents (Claude Code, Cursor,
  Codex, Gemini CLI, Doubao). Use whenever the user says "commit", "write a
  commit message", "create a PR", "open a pull request", "draft a PR",
  "update the changelog", "release notes", or asks the agent to stage/commit/
  push work. It gathers the real diff, writes a specific Conventional Commit,
  lints it, scaffolds a review-ready PR body, and extracts user-facing
  changelog entries. Replaces generic "update docs"-style messages with
  review-grade output.
---

# commit-forge

You are helping a developer ship work that an AI agent produced. The #1
problem with AI-generated commits is they are vague (`fix: update stuff`) and
PRs are blank. This skill makes the output read like it was written by a
careful senior engineer.

## Golden rules

1. **Never invent changes.** Base the message on the actual diff, not on what
   you think the code does. Run `scripts/diff_context.py` first.
2. **Be specific.** "Adds magic-link login that expires in 10 min" beats
   "adds auth". Name the behavior, the edge case, or the bug being fixed.
3. **Imperative mood, lowercase subject, no trailing period.**
   `feat(auth): reject expired magic links` — not `Added login`.
4. **One logical change per commit.** If the diff mixes a feature + a refactor,
   split it and say so.

## Workflows

### 1. User says "commit" / "commit this"

1. Run `python scripts/diff_context.py --stat-only` to see what changed cheaply.
   If the change is subtle, re-run without `--stat-only` to read the patch.
2. Pick the type: `feat` / `fix` / `docs` / `refactor` / `perf` / `test` /
   `build` / `ci` / `chore`. Scope = the module touched (e.g. `auth`, `api`).
3. Draft the header: `type(scope): subject` (<= 72 chars total, subject <= 50).
   Add a body with **why** when the change is non-obvious, and a
   `BREAKING CHANGE:` footer if applicable.
4. Validate it:
   ```bash
   echo "<your message>" | python scripts/commit_lint.py
   ```
   Fix any finding until it prints `OK`.
5. Stage relevant files (don't `git add -A` blindly — explain what you stage),
   then commit with the validated message.

### 2. User says "open a PR" / "create a PR"

1. Run `python scripts/pr_body.py` to scaffold the body.
2. Fill in **Why** (the problem, not the implementation) and **How to test**
   with concrete commands the reviewer can copy.
3. Title follows Conventional Commits too: `feat(auth): magic-link login`.
4. If `gh` is available, open the PR with the filled body; otherwise print the
   title + body so the user can paste it.

### 3. User says "update changelog" / "release notes"

1. Run `python scripts/changelog.py` (or `--since vX.Y.Z`).
2. Copy the block into `CHANGELOG.md` under the matching version.
3. Rewrite bullet points into user language ("users can now…" not "added
   function foo"), and group breaking changes prominently.

## Scripts

| Script | Purpose |
| --- | --- |
| `scripts/diff_context.py` | Structured staged/branch diff + recent commit style |
| `scripts/commit_lint.py` | Enforces Conventional Commits 1.0.0 |
| `scripts/pr_body.py` | Review-ready PR template from commits + files |
| `scripts/changelog.py` | Keep-a-Changelog draft from feat/fix/perf commits |

All scripts need Python 3.8+ and `git` on PATH. They print to stdout so you can
pipe or read their output directly.

## Anti-patterns (do not do)

- `fix: bug`, `update: changes`, `wip`, `committing stuff` — never.
- Dumping the entire diff into the commit body.
- Writing a PR body that only restates the diff.
- Marking `[x]` test checkboxes you did not actually run.
