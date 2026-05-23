# Publishing

`montageai` uses PyPI Trusted Publishing through GitHub Actions.

## Registry setup

Configure a PyPI trusted publisher for:

- Project: `montageai`
- Owner: `usemontage`
- Repository: `python`
- Workflow file: `.github/workflows/publish.yml`
- Environment: `pypi-publish`

The package version is controlled by `pyproject.toml`.

## Release

1. Confirm the local package:

   ```bash
   .venv/bin/pytest -q
   .venv/bin/mypy src/montageai --ignore-missing-imports
   .venv/bin/python -m build
   ```

2. Push `main`.

3. Run the `Publish to PyPI` GitHub Actions workflow manually with:

   ```text
   confirm=publish
   ```

The workflow builds the sdist/wheel and publishes through `pypa/gh-action-pypi-publish`.

## Current first-publish failure

If PyPI returns:

```text
invalid-publisher: valid token, but no corresponding publisher
```

then the GitHub workflow is valid, but PyPI does not yet have a trusted publisher matching the repository, workflow file, and `pypi-publish` environment.
