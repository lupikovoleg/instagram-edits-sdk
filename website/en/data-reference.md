# Data reference

Observed on **18 October 2026**, on one consenting account. A field's presence in
that response does not guarantee availability for every account, Reel or period.

`QueryResult.get_data(*fields)` starts at `payload["data"]`. It resolves canonical
names such as `1$xig_fetch_media(id:$media_id)` and numeric aliases such as
`1fvalue`. Compatible fragments of the same node are combined; conflicts are
rejected. Explicit null is returned as `None`; a missing or ambiguous path is an error.

## Detailed Reel statistics

**`BaselReelDetailsQuery` → `client.reel_insights(reel_url)`**

```python
reel = client.reel_insights(reel_url)
plays = reel.metrics.get("play_count")
skip = reel.metrics.get("skip_rate")
skip_value = skip.get("value") if isinstance(skip, dict) else None
```

| Fields | Observed data |
|---|---|
| `play_count`, `like_count`, `comment_count`, `repost_count`, `save_count`, `reshare_count` | Playback and interaction counts |
| `skip_rate`, `reshares_rate`, `likes_rate`, `comments_rate`, `reposts_rate`, `saves_rate` | Metric objects with values and, depending on the field, deltas, labels and trends |
| `average_watch_time` | Average watch time; the SDK does not assume its unit is seconds |
| `follow_count_from_media`, `reach_count`, `viewer_count` | Follows, reach and viewer metric objects |
| `views_over_time` | Raw nested playback time series |
| `content_view_source_breakdown`, `viewer_distribution`, `top_ten_badge` | Sources, viewer distribution and a badge |
| `reels_retentions` | Retention array, exposed separately as `reel.retention` |

The SDK normalizes top-level metric aliases `1fvalue`/`1fdelta` to `value`/`delta`.
Nested structures remain unchanged. [Retention guide](retention.md).

## Public Reel metrics

**`BaselPublicInsightsQuery` → `client.public_insights(reel_url)`**

```python
response = client.public_insights(reel_url)
metrics = response.get_data("xig_fetch_media", "basel_media_public_insights")
```

Returned interaction counts and rates. This block has no retention curve. The name
“Public” does not prove unauthenticated access: only an owned Reel was checked.

## Paginated Reels

**`BaselAccountLevelReelsQuery` → `client.reels_page()`**

```python
page = client.reels_page(first=3, timeframe="LIFETIME", order_by="BY_DATE")
for item in page.items:
    print(item["id"], item.get("permalink"))
if page.has_next_page:
    next_page = client.reels_page(first=3, after=page.next_cursor)
```

Raw path: `xig_user_by_igid_v2 → basel_insights → user_reel_dicts → edges[].node`.
Observed node fields include `id`, `permalink`, `taken_at`, `caption`,
`image_versions2`, `clips_metadata`, `is_promoted`, `is_active_trial`,
`coauthor_producers` and `basel_media_level_insights`.

Pagination uses `page_info.has_next_page` and `end_cursor`. Two pages of three
Reels were checked without overlapping IDs. `account_reels()` returns the raw response.

| Parameter | APK values |
|---|---|
| `timeframe` | `LIFETIME`, `ONE_WEEK`, `TWO_WEEKS`, `ONE_MONTH`, `ONE_YEAR` |
| `order_by` | `BY_DATE`, `BY_VIEWS`, `BY_LIKES`, `BY_COMMENTS`, `BY_REPOSTS`, `BY_SHARES`, `BY_SAVES`, `BY_FOLLOWERS`, `BY_SKIP_RATE` |
| `sort_direction` | `ASCENDING`, `DESCENDING`, `None` |

The live test used `LIFETIME`, `BY_DATE`, `DESCENDING`, and `skip_follow_count=False`.
Other combinations were recovered statically. Server page-size limits are unknown.

## Account statistics

**`BaselAccountLevelInsightsQuery` → `client.account_insights()`**

```python
response = client.account_insights(period="LAST_30_DAYS", include_time_series=True)
metrics = response.get_data("xig_user_by_igid_v2", "basel_insights")
views = response.get_data("xig_user_by_igid_v2", "basel_insights", "reels_views", "value")
```

Observed metrics: `reels_views`, `total_reach`, `followers_net_growth`,
`like_count`, `comment_count`, `repost_count`, `reshare_count`, `save_count`,
`viewer_count`. Metric objects may include a value, delta and `time_series`.

Access flags: `has_access_to_audience_insights`, `has_access_to_demographic_insights`.
`can_see_organic_insights` is in the user node.

Periods: `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `LAST_60_DAYS`,
`LAST_90_DAYS`, `LAST_180_DAYS`. Only `LAST_30_DAYS` was exercised live.

## Audience statistics

**`BaselAudienceInsightsQuery` → `client.audience_insights()`**

```python
response = client.audience_insights(period="LAST_30_DAYS", client_timezone="Europe/Moscow")
ages = response.get_data("xig_user_by_igid_v2", "basel_insights", "audience_age_distribution")
countries = response.get_data("xig_user_by_igid_v2", "basel_insights",
                             'audience_top_locations(breakdown_type:"COUNTRY")')
```

The response had age groups, countries, cities, gender groups, total followers,
follower growth/follows/unfollows with time series, and most-active follower times.
`popular_topics_preview` was empty. The account-statistics periods above also apply.

## Delta updates

**`XIGBaselAccountLevelReelsDataDeltaQuery` → `client.reels_delta()`**

```python
response = client.reels_delta(["NUMERIC_MEDIA_ID"])
items = response.get_data("xig_basel_multi_media_insights_query")
```

Returns a list of `id`/`basel_media_level_insights` nodes with media ID, interaction
counts, follows and a badge. Only a single-ID request was tested; multi-ID limits
and responses remain unverified.

## Comment analysis

**`XIGBaselInsightsCommentsQuery` → `client.comment_insights()`**

```python
response = client.comment_insights(reel_url, sort_order="recent")
analysis = response.get_data("xig_fetch_media", "ai_comment_insights")
```

APK values: `recent`, `popular`. The live `recent` request returned HTTP 200 and
`ai_comment_insights=null`. A populated analysis was not verified. Null does not
mean the Reel has zero comments.

## Kits

**`BaselKitsQuery` → `client.kits()`**

```python
response = client.kits(after=None)
connection = response.get_data("xig_basel_kits", "kits")
edges = connection["edges"]
```

The persisted query uses `first:50`; the SDK supplies `after`. The live response
had `edges=[]` and `has_next_page=false`. Populated items and further pages were
not verified. No Kits were created for testing.

## Alternative Reel insights

**`ReelInsightsQuery` → `client.extended_reel_insights()`**

```python
response = client.extended_reel_insights(
    reel_url,
    bloks_versioning_id="8dc50e9193c9b70a3f9dbcc25fc5f444bbac27bb56a8c1359ede836b8069c4b8",
)
insights = response.get_data("ig_reel_insights")
curve = insights["retention"]["retention_curve"]
```

The SDK assembles the observed NDJSON response and combines compatible canonical
fragments. Curve fields are `timestamp_seconds` and `1fpercentage`; here `1` means
100%. Some other percentage fields, including country percentages, already use
percent units. Do not multiply every percentage in this response by 100.

The explicit Bloks version comes from the researched APK and may need to change.
This curve can differ from `BaselReelDetailsQuery`. Its use by the Edits UI was
not established. [Method contract](methods/ReelInsightsQuery.md).
