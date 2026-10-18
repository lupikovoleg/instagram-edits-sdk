# Instagram Edits SDK

Unofficial Python SDK and developer documentation for Instagram Edits analytics,
Reel insights, audience statistics, and retention curves. Python 3.10+, no runtime
dependencies. This is not an official Meta SDK or a hosted service.

## Install and use

The PyPI release is prepared for installation with:

```sh
python -m pip install instagram-edits-sdk
```

Until the first upload completes, install from source:

```sh
git clone https://github.com/lupikovoleg/instagram-edits-sdk.git
cd instagram-edits-sdk
python -m pip install .
```

Distribution: `instagram-edits-sdk` 0.2.1. Import: `edits_api`. CLI: `edits-api`.
If migrating from the earlier local `instagram-edits-research` distribution,
uninstall it first: both distributions provide the same `edits_api` module.
Inject your own Instagram owner's session into `IG_SESSIONID` using a secret manager.
The library does not log in or read browser cookies.

```python
from edits_api import EditsClient

client = EditsClient.from_env()
reel = client.reel_insights("https://www.instagram.com/reel/YOUR_SHORTCODE/")
plays = reel.metrics.get("play_count")
retention = [{"index": p.index, "percent": p.percent} for p in reel.retention] \
    if reel.retention_available else None
snapshot = reel.to_dict()

page = client.reels_page(first=3)
if page.has_next_page:
    second_page = client.reels_page(first=3, after=page.next_cursor)

account = client.account_insights(include_time_series=True)
account_metrics = account.get_data("xig_user_by_igid_v2", "basel_insights")
```

Missing/null/empty/all-null retention does not discard other Reel statistics.
`retention()` remains strict. Exports include JSON; CSV and SVG require available
retention. Null values are not replaced by zeros. Response aliases are resolved by
`QueryResult.get_data()`; the original payload remains available.

## Available methods and evidence

On 2026-10-18, the SDK made nine successful read-operation requests on one consenting
account and an additional pagination request. Seven operations returned data.
`comment_insights()` returned a null analysis block; `kits()` returned an empty list.
These two results do not verify populated feature responses. Account availability,
other enum combinations, batch limits, and future server compatibility are not guaranteed.

Methods: `reel_insights`, `retention`, `public_insights`, `reels_page`, `account_reels`,
`account_insights`, `audience_insights`, `reels_delta`, `comment_insights`, `kits`,
`extended_reel_insights`, and the explicit `execute` interface.

The source includes 15 detailed operation contracts, an 88-entry Basel/Eddy index,
and the full 1663-operation APK registry. Mutations are untested and require explicit
opt-in. No automatic retries, token refresh, challenge bypass, or unbounded pagination.

[Russian quickstart](README.md) · [Data reference and all-method examples](docs/data-reference.md)
· [Authentication](docs/authentication.md) · [HTTP](docs/http-api.md)
· [Swagger / OpenAPI](docs/swagger.md) · [Verification scope](docs/verification.md)

```sh
python -m unittest discover -s tests -v
python examples/offline_demo.py
python tools/check_release.py
```

Tests use synthetic data without network access. Sanitized live evidence is separate.
No APK, decompiled Meta sources, credentials, or personal response dumps are shipped.
Original project code/docs: MIT. Bundled Swagger UI: Apache-2.0.
