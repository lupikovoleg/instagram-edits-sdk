# Evidence & verification

This project distinguishes a successful transport request, populated data and
a static finding. These are observations, not guarantees of future API support.

## Evidence levels

| Level | Meaning |
|---|---|
| `live-verified` | A request was exercised against the server; read the recorded availability outcome |
| `static-contract` | Purpose and variables/response handling were recovered from the APK |
| `static-reference` | Registry entry plus a code reference, without a complete contract |
| `registry-only` | Name and persisted ID only; reachability and parameters unproven |

## Live SDK checks

On **18 October 2026**, nine read operations and one additional pagination request
returned HTTP 200 on one consenting account. The Reel requests used an owned Reel.

| Operation | Actual result |
|---|---|
| `BaselReelDetailsQuery` | Metrics and 62 retention points |
| `BaselPublicInsightsQuery` | Owned Reel counts and rates |
| `BaselAccountLevelInsightsQuery` | Aggregates and time series for `LAST_30_DAYS` |
| `BaselAccountLevelReelsQuery` | Two pages of three Reels, accepted cursor, no overlapping IDs |
| `BaselAudienceInsightsQuery` | Demographics, geography, follower growth and activity |
| `XIGBaselAccountLevelReelsDataDeltaQuery` | Metrics for one supplied ID |
| `XIGBaselInsightsCommentsQuery` | Accepted request; analysis was null |
| `BaselKitsQuery` | Accepted request; list was empty |
| `ReelInsightsQuery` | Alternative retention and demographics, assembled from NDJSON |

Populated comments/Kits, other accounts, every enum combination, larger batches
and session lifetime were not verified. No mutation was run. Private responses
and credentials are excluded from the public project.

[Sanitized method evidence](evidence/method-verification.json){ .md-button }

A response digest identifies the private recorded artifact. It does not let a
reader independently reconstruct or verify the undisclosed payload.

## Package checks

Version **0.2.1** was installed from public PyPI into a clean environment. Its
wheel passed 45 offline tests; CLI catalog and import worked. The downloaded hash
matched PyPI metadata. GitHub Actions also built and published the distributions.

Eleven example scenarios were replayed against saved private responses. Missing,
null, empty and all-null retention were tested synthetically; the live Reel had
an available curve. These replays are not additional live requests.

[PyPI verification](evidence/pypi-release-validation.json) ·
[Earlier package checks](evidence/package-validation.json)

## APK provenance

| Field | Value |
|---|---|
| Package | `com.instagram.basel` |
| Version | `448.0.0.53.84` |
| versionCode | `864801371` |
| DEX files | 15 |
| Shared operation registry | 1663 entries |
| Basel/Eddy name matches | 88 entries |

APK SHA-256:

```text
bd88ea0ab6771f47f807524f380ac29b5628c9ebcf9db519808afb420f169757
```

Certificate SHA-256:

```text
5367570bad488d8da6a0fab78d9766a1a4c23c3c70fac0ad2e91c8f0bd58b432
```

The APK signature and DEX checksums were checked in the original investigation.
Source-reference paths in method cards refer to that research workspace; the
APK and decompiled Meta files are not distributed with this SDK.
