# Instagram Edits SDK

Unofficial Python SDK for Instagram Edits: Reel statistics, audience analytics,
retention curves, and documented internal GraphQL operations. Not affiliated with Meta.

## Install

```bash
python -m pip install instagram-edits-sdk
```

Python 3.10 or newer. No runtime dependencies. The Python import is `edits_api`;
the command-line entry point is `edits-api`.

If you installed the earlier local distribution `instagram-edits-research`,
uninstall it before installing this package: both provide the same import module.

## Quickstart

Supply `IG_SESSIONID` through your backend's environment or secret manager.
Use the Instagram session of the Reel owner. Do not embed it in frontend code.
The SDK uses an existing session; it does not log in or obtain browser cookies.

```python
from edits_api import EditsClient

client = EditsClient.from_env()
reel = client.reel_insights("https://www.instagram.com/reel/YOUR_SHORTCODE/")

plays = reel.metrics.get("play_count")
likes = reel.metrics.get("like_count")

if reel.retention_available:
    points = [{"index": p.index, "percent": p.percent} for p in reel.retention]
else:
    points = None

# Optional: export to a new directory. JSON always; CSV/SVG with available retention.
reel.export("results/my-reel")
```

Missing, null, empty, or all-null retention does not discard other Reel metrics.
`client.retention()` is strict and raises `EditsError` when no curve is available.
Zero and null are preserved as different values.

## Other read methods

```python
page = client.reels_page(first=3)
if page.has_next_page:
    next_page = client.reels_page(first=3, after=page.next_cursor)

account = client.account_insights(period="LAST_30_DAYS", include_time_series=True)
views = account.get_data("xig_user_by_igid_v2", "basel_insights", "reels_views", "value")

audience = client.audience_insights(period="LAST_30_DAYS", client_timezone="UTC")
public_metrics = client.public_insights("YOUR_NUMERIC_MEDIA_ID")
```

Also available: `account_reels`, `reels_delta`, `comment_insights`, `kits`,
`extended_reel_insights`, and an explicit `execute` interface. `QueryResult.get_data`
resolves observed canonical field names; `payload` keeps the original response.

## Documentation and evidence

- [Authentication and passing session credentials](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/docs/authentication.md)
- [Data fields and examples for all documented read methods](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/docs/data-reference.md)
- [Retention example](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/retention.py)
- [HTTP contract and response handling](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/docs/http-api.md)
- [Operation catalog](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/docs/methods.md)
- [OpenAPI and local Swagger viewer](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/docs/swagger.md)
- [Verification scope](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/docs/verification.md)

Nine read operations were exercised on one consenting account on 2026-10-18,
plus a second page of Reels. Seven returned data; comment analysis was null and
Kits was empty. Other accounts, every parameter combination, and populated
comment/Kits results are not verified. The source includes 15 detailed contracts
and a broader static operation registry, not a claim that all entries work.

These are internal, versioned endpoints and can change. No automatic login,
challenge bypass, session refresh, retries, or unbounded pagination. Mutations
are untested and require explicit opt-in. Keep credentials private and use only
accounts and data you are authorized to access.

Original SDK and documentation: MIT. The source distribution includes a local
Swagger UI with its Apache-2.0 license and dependency notices. No APK, decompiled
Meta source, real session credentials, or private response dumps are included.
