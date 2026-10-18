# Instagram Edits API Research

An unofficial, evidence-based reference and Python client for Instagram Edits
internal operations. This is not an official Meta SDK or a hosted service.

The original research client successfully called `BaselReelDetailsQuery` on
2026-10-18 and received 62 retention points for an owned Reel. The packaged SDK
is regression-tested; other operations remain static APK findings.

```sh
python -m pip install .
```

Inject `IG_SESSIONID` through your secret manager, then:

```python
from edits_api import EditsClient

client = EditsClient.from_env()
insights = client.reel_insights("https://www.instagram.com/reel/YOUR_SHORTCODE/")
rows = [{"index": p.index, "value": p.value, "percent": p.percent}
        for p in insights.retention]
insights.export("results/my-reel")
```

Python 3.10+, no runtime dependencies. Install from the repository; this package
has not been published to PyPI. Session cookies are credentials. The client
does not log in, scrape browser cookie stores, refresh tokens, bypass challenges,
retry requests, or paginate automatically. Mutations require an explicit flag.

See the [Russian developer documentation](README.md),
[HTTP contract](docs/http-api.md), [catalog](docs/methods.md),
[authentication](docs/authentication.md), and [verification scope](docs/verification.md).
