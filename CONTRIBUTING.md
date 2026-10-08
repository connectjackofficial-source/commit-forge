## Contributing

PRs welcome. Keep scripts dependency-free (no pip installs).

## Development

Run the test suite from the repository root:

```bash
python tests/test_lint.py
```

Tests are plain-script style (no pytest dependency), matching the
dependency-free rule.

## Commit style

This repo enforces Conventional Commits on itself. Before pushing, lint your
message:

```bash
echo "your message" | python scripts/commit_lint.py
```

## License

MIT
