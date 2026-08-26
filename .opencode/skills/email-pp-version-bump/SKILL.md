---
name: email-pp-version-bump
description: Use when bumping, changing, or releasing the Hermes Email++ version, including requests to update pyproject.toml, plugin.yaml, or package metadata.
---

# Hermes Email++ Version Bump

Keep every current-version source synchronized. Do not create a Git tag, commit,
or publish a release unless the user explicitly requests it.

## Update

For a requested version `X.Y.Z`, update all of these files:

1. `pyproject.toml`: `[project].version`
2. `plugin.yaml`: top-level `version`
3. `hermes_email_pp/__init__.py`: `__version__`
4. `CHANGELOG.md`: add a dated `## X.Y.Z (YYYY-MM-DD)` entry above the prior
   release with a concise description of the shipped changes.

Treat historical changelog entries and README release examples as documentation,
not stale version metadata. Do not rewrite them solely because they mention an
older release.

## Verify

1. Search `*.toml`, `*.yaml`, `*.yml`, and `*.py` for the old version. Confirm
   any remaining matches are intentional historical documentation.
2. Keep or add a test asserting that `pyproject.toml`, `plugin.yaml`, and
   `hermes_email_pp.__version__` agree.
3. Run:

```console
.venv/bin/ruff check .
.venv/bin/pytest tests/test_hermes_email_pp.py
uv build --out-dir /tmp/opencode/email-pp-X.Y.Z
```

4. Report the version and build artifacts, and state explicitly if no tag or
   publication was requested.
