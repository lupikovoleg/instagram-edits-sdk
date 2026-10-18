# Integrate with your backend

## Save snapshots

```python
from edits_api import EditsClient

def collect(client: EditsClient, reel_url: str):
    reel = client.reel_insights(reel_url)
    return {
        "media_id": reel.media_id,
        "collected_at": reel.response.fetched_at,
        "metrics": reel.metrics,
        "retention_available": reel.retention_available,
        "retention": [{"index": p.index, "value": p.value} for p in reel.retention]
                     if reel.retention_available else None,
        "warnings": reel.metadata["warnings"],
        "owner_verified": reel.metadata["owner_verified"],
    }
```

Store a timestamp with each snapshot. Missing retention is a valid data outcome;
HTTP or GraphQL failure is an error. A 120-second cache was found in the Android
client, but it is not a server rate limit or freshness guarantee.

## Paginate Reels

```python
page = client.reels_page(first=3, timeframe="LIFETIME", order_by="BY_DATE")
items = list(page.items)

if page.has_next_page:
    next_page = client.reels_page(
        first=3, after=page.next_cursor,
        timeframe="LIFETIME", order_by="BY_DATE",
    )
    items.extend(next_page.items)
```

Each call sends one request. Two consecutive pages of three Reels were checked
live, with no overlapping IDs. Keep filters and ordering unchanged between pages.
Use the returned cursor, not the last media ID. Page-size limits are unknown.

## Batch updates

```python
response = client.reels_delta(["NUMERIC_MEDIA_ID_1", "NUMERIC_MEDIA_ID_2"])
items = response.get_data("xig_basel_multi_media_insights_query")
```

Only a one-ID request was exercised live. The APK contract supports an array;
maximum batch size and multi-ID responses have not been tested.

## Errors and background jobs

The SDK is synchronous. Run calls in a worker/thread in asynchronous applications.
Use separate clients and sessions for separate accounts. The default timeout is
30 seconds; the supported range is 1–120 seconds.

No automatic retries or refresh are implemented. Stop jobs on HTTP 429, an expired
session or a challenge and investigate. If you add retries for transient network
errors, keep them bounded and handle duplicate snapshots.

## Explicit queries

```python
response = client.execute("BaselPublicInsightsQuery", {"media_id": media_id})
```

Only the `instagram` transport is implemented. Mutations require an explicit
`allow_mutation=True` on that call. No mutation was run live; do not include them
in health checks or routine analytics collection.
