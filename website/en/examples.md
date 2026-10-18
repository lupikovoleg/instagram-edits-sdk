# Runnable examples

Install the SDK, provide your session as described in [Authentication](authentication.md),
then download or clone the scripts from the repository. Scripts write to a new output
file or directory and do not overwrite existing exports.

| Script | Purpose |
|---|---|
| [retention.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/retention.py) | Require a curve and export JSON, CSV and SVG |
| [reel_statistics.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/reel_statistics.py) | Keep statistics when retention is unavailable |
| [list_reels.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/list_reels.py) | Fetch a page of Reels |
| [account_statistics.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/account_statistics.py) | Account or audience analytics |
| [read_operation.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/read_operation.py) | Public metrics, delta, comments or Kits |
| [extended_insights.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/extended_insights.py) | Alternative Reel insights branch |
| [batch_retention.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/batch_retention.py) | A bounded file of owned Reel IDs or URLs |
| [offline_demo.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/offline_demo.py) | Synthetic demonstration without network access |

## Retention

```bash
python examples/retention.py "https://www.instagram.com/reel/YOUR_SHORTCODE/" --output results/curve
```

## Other statistics

```bash
python examples/reel_statistics.py "https://www.instagram.com/reel/YOUR_SHORTCODE/" --output results/reel
python examples/list_reels.py --first 3 --output results/page.json
python examples/account_statistics.py --period LAST_30_DAYS --output results/account.json
python examples/account_statistics.py --audience --output results/audience.json
python examples/read_operation.py kits --output results/kits.json
```

## Alternative branch

```bash
python examples/extended_insights.py "https://www.instagram.com/reel/YOUR_SHORTCODE/" --output results/extended.json
```

The script includes the Bloks version found in the researched APK. It can be
overridden explicitly when the upstream contract changes.
