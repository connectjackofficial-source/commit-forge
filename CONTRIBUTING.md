## Contributing

PRs welcome. Keep scripts dependency-free (no pip installs).

## Development

Run the test suite from the repository root:

```bash
python tests/test_lint.py
python tests/test_hook.py
```

Tests are plain-script style (no pytest dependency), matching the
dependency-free rule.

## Commit style

This repo enforces Conventional Commits on itself. Before pushing, lint your
message:

```bash
echo "your message" | python scripts/commit_lint.py
```

Contributors can also install the local git hook so invalid messages are
rejected automatically:

```bash
python scripts/install_hook.py
```

## License

MIT
