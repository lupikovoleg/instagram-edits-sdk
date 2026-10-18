# Your first Reel statistics

Get from an installed package to an owned Reel in three steps.

## 1. Install

```bash
python -m pip install instagram-edits-sdk
```

Python **3.10+**. Distribution: `instagram-edits-sdk`. Import: `edits_api`.
CLI: `edits-api`. Current release: **0.2.1**.

If you previously installed the local `instagram-edits-research` distribution,
uninstall it first. Both distributions provide the same Python module.

## 2. Provide your session

Supply `IG_SESSIONID` through your backend's environment or secret manager. Use
an existing Instagram session belonging to the owner of the Reel.

The SDK does not log in, read browser cookies, or refresh sessions. An Instagram
Graph API OAuth token is a different credential. [Authentication guide](authentication.md).

## 3. Request a Reel

```python
from edits_api import EditsClient

client = EditsClient.from_env()
reel = client.reel_insights("https://www.instagram.com/reel/YOUR_SHORTCODE/")

print(reel.metrics.get("play_count"))
print(reel.metrics.get("like_count"))
print(reel.retention_available)
```

URLs, numeric media IDs and composite IDs are accepted. The SDK checks the returned
media ID and, when available, the owner ID against your session.

## Use the result

```python
snapshot = reel.to_dict()  # Store the fields your application needs.

if reel.retention_available:
    points = [{"index": p.index, "percent": p.percent} for p in reel.retention]
else:
    points = None

reel.export("results/my-reel")  # Must be a new directory.
```

JSON is exported for any valid statistics result. CSV and SVG are added only when
retention is available. Missing data is not turned into zero.

## Try the command line

```bash
edits-api insights "https://www.instagram.com/reel/YOUR_SHORTCODE/" --output results/reel
edits-api retention "https://www.instagram.com/reel/YOUR_SHORTCODE/" --output results/curve
```

`insights` keeps other statistics if retention is unavailable. `retention` requires
a curve and reports an error if there is none.

## Next

[Get a retention curve](retention.md) · [Explore the data](data-reference.md) ·
[Download runnable examples](examples.md)
