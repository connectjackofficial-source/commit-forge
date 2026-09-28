# Examples

## Before / After

### Bad (what agents produce by default)

```
fix: update stuff
```

No scope. No detail. The reviewer has to open the diff to learn what changed.

### Good (what commit-forge produces)

```
feat(auth): reject expired magic links after 10 minutes

The previous check only compared the token hash, so a link that expired
30 minutes ago was still accepted. Now we compare expires_at against
the current timestamp and return 401.
```

- Type is `feat` (user-visible behavior change), not `fix`
- Scope is `auth`
- Subject says what, body says why
- No trailing period, imperative mood

## PR example

```markdown
## Summary
Fixes the magic-link login bypass where expired links were still accepted.

## How to test
1. Generate a magic link for a test account
2. Wait 10 minutes (or set the clock forward)
3. Click the link -> expect 401, not a session
```
