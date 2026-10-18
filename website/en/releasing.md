# Project maintenance

The SDK is published as `instagram-edits-sdk` on PyPI. The import stays `edits_api`.

## Documentation

English authored pages live in `website/en/`. Existing Russian pages live in
`docs/`. `tools/build_site.py` stages both languages, generates English method
cards from the versioned registry and translated contracts, fixes source links,
and creates the static preview.

```bash
python -m pip install -r requirements-docs.txt
python tools/build_site.py
python -m http.server 8766 --bind 127.0.0.1 --directory site
```

The documentation is independent of the package runtime. Documentation changes
do not require a new PyPI release. The Pages workflow builds pull requests and
only deploys authorized pushes to `main`.

## Package releases

The PyPI Trusted Publisher is restricted to this repository's `publish.yml`
workflow and `pypi` environment. The package owner configured that trust explicitly.
No permanent PyPI API token is stored in the repository.

Update `pyproject.toml`, `src/edits_api/__init__.py` and the changelog. Regenerate
OpenAPI and update the displayed SDK version. After review, push a version tag
matching package metadata:

```bash
git tag vNEXT_VERSION
git push origin vNEXT_VERSION
```

The release workflow checks the tag, tests, builds sdist/wheel, validates metadata,
tests a clean wheel installation, and publishes. Never repoint a published tag or
attempt to overwrite an existing PyPI release.

[Release workflow](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/.github/workflows/publish.yml) ·
[PyPI project](https://pypi.org/project/instagram-edits-sdk/)
