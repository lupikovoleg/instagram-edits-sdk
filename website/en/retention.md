# Get a retention curve

`BaselReelDetailsQuery` returns the Reel's statistics and, when available, the
numerical `reels_retentions` curve. The live check returned **62 points**.

## Request the curve

```python
from edits_api import EditsClient

client = EditsClient.from_env()
reel = client.reel_insights("https://www.instagram.com/reel/YOUR_SHORTCODE/")

if reel.retention_available:
    points = [
        {"index": point.index, "fraction": point.value, "percent": point.percent}
        for point in reel.retention
    ]
else:
    points = None
    reason = reel.metadata["retention_unavailable_reason"]
```

| Field | Meaning |
|---|---|
| `index` | Source integer position in the curve |
| `value` | Original fraction: `1.0` means 100% |
| `percent` | `value × 100`, or `None` |

The SDK preserves order, nulls, zero and values above 100%. It does not smooth,
sort, interpolate or clamp. The Edits UI treats a consecutive `0..N−1` grid as
seconds; arbitrary indices are not silently converted to time. Check warnings
in `reel.metadata["warnings"]`.

## Statistics without retention

A missing, null, empty or all-null curve sets `retention_available=False`. The
other metrics remain available. An all-null array is preserved in JSON; no chart
is produced. These absence cases were tested with synthetic responses; the owned
Reel in the live check had an available curve.

For a strict call:

```python
points = client.retention(reel_url)  # Raises EditsError when no curve is available.
```

A malformed curve or missing statistics object remains an error. The SDK does
not silently treat a broken response as an unavailable feature.

## Export

```python
reel.export("results/my-reel")
```

Always writes `insights.json`, `response.json` and `manifest.json`. When retention
is available, it also writes `retention.csv` and `retention.svg`. The directory
must be new. POSIX files use mode 0600 and the new directory uses 0700; Windows
permissions depend on ACLs.

Raw responses can contain private metrics and media URLs. Exports are optional;
use `to_dict()` when saving selected fields in your own system.

[Runnable retention script](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/retention.py){ .md-button }

## Other retention-related operations

`skip_rate` is a separate metric, not the full curve. The alternative
`ReelInsightsQuery` returns `retention_curve` with `timestamp_seconds` and
`1fpercentage`. In the observed curve, percentage is a fraction; some other
percentage fields in that same response use percent units. Never apply one
multiplier to every field.

The two query branches can produce different curves. Do not substitute one for
the other without considering this difference. [Alternative query](methods/ReelInsightsQuery.md).
