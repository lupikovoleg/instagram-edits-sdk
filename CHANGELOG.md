# Changelog

## 0.2.2 — 2026-10-18

- Point PyPI Homepage and Documentation links to the published GitHub Pages site.
- Add direct links to Russian documentation and Swagger, including in the package description.
- Include the bilingual documentation site sources and font licenses in the source distribution.
- Credit Oleg Lupikov in the project license. Runtime behavior is unchanged from 0.2.1.

## 0.2.1 — 2026-10-18

- Rename the distribution to `instagram-edits-sdk` for PyPI; the `edits_api` import and `edits-api` CLI stay unchanged.
- Add an English PyPI description, project links and bundled license metadata.
- Add a tag-triggered build and publish workflow using PyPI Trusted Publishing.
- Runtime API and observed live-query evidence remain unchanged from 0.2.0.

## 0.2.0 — 2026-10-18

- Preserve Reel statistics when retention is missing, null, empty, or all-null.
- Add `insights` CLI, canonical path resolution, and typed cursor pages.
- Exercise nine read operations plus a second Reel page against the live API.
- Distinguish populated responses from null comment analysis and empty Kits.
- Recover period and comment-sort enums; add all-method examples and local Swagger.
- Keep live evidence sanitized and private responses outside the repository.

## 0.1.0 — 2026-10-18

- Package the original live-verified retention transport as an importable client.
- Parse standard and observed canonical field names; preserve null and zero.
- Add ownership checks, explicit JSON/CSV/SVG exports and a CLI.
- Document HTTP/authentication, seven analytics wrappers and 15 detailed contracts.
- Include a versioned 88-operation Edits index and 1663-entry shared registry.
- Add synthetic tests, offline demo, release checks and GitHub Actions.

Only the original BaselReelDetailsQuery exchange is server-verified. Other
operations remain static findings. No private responses or credentials are shipped.
