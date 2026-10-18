# HTTP transport

## Request

```http
POST /graphql_www HTTP/1.1
Host: i.instagram.com
Authorization: Bearer IGT:2:<YOUR_SESSION_ENVELOPE>
User-Agent: Instagram 1.0 Android
X-IG-App-ID: 954255173121948
IG-INTENDED-USER-ID: <ACCOUNT_ID>
IG-U-DS-USER-ID: <ACCOUNT_ID>
X-FB-Friendly-Name: BaselReelDetailsQuery
X-Client-Doc-Id: 3261342854360971614358769315
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
```

The body is a URL-encoded form. `variables` is a JSON **string** within that form.
The SDK supplies the transport flags and encodes it:

```text
method=post
pretty=false
format=json
server_timestamps=true
locale=user
fb_api_req_friendly_name=BaselReelDetailsQuery
purpose=fetch
enable_canonical_naming=true
enable_canonical_variable_overrides=true
enable_canonical_naming_ambiguous_type_prefixing=true
client_doc_id=3261342854360971614358769315
variables={"media_id":"YOUR_NUMERIC_MEDIA_ID","include_creative_tools":false}
```

This is shown line by line for readability, not as a literal HTTP body.
`b.i.instagram.com` is an explicitly selectable alternative host from the
instagrapi transport; live checks used `i.instagram.com`. There is no automatic
host switching. The `distillery` schema is not implemented.

## Response aliases

Synthetic values with the observed shape:

```json
{
  "data": {
    "1$xig_fetch_media(id:$media_id)": {
      "id": "12345_999",
      "basel_media_level_insights": {
        "play_count": 100,
        "skip_rate": {"type": "Skip rate", "1fvalue": 0.25},
        "reels_retentions": [
          {"index": 0, "1fvalue": 1.0},
          {"index": 1, "1fvalue": 0.8}
        ]
      }
    }
  }
}
```

The payload stays raw. `reel_insights()` provides normalized retention and metric
objects. `response.get_data()` resolves observed canonical names and compatible
fragments, rejecting conflicting values or ambiguous arguments.

## Streaming and content types

Responses were JSON or NDJSON even with `text/javascript` or `text/html` content
types. The transport detects complete JSON instead of always waiting for EOF on
a connection that may stay open. Supported forms include JSON, observed NDJSON
incremental patches, gzip and deflate. Multipart and SSE are not implemented.

## Failures

| Condition | Result |
|---|---|
| HTTP status other than 200 | `EditsError`, no retry |
| GraphQL errors or `status=fail` | Error, including with HTTP 200 |
| Unfinished `hasNext=true` response | Error |
| Missing/null/empty retention | Other statistics stay available; strict `retention()` raises |
| Wrong media ID or a different reported owner | Error |
| Null point | Preserved as a gap, not zero |

Timeout defaults to 30 seconds, with a 1–120 second range. Responses are limited
to 32 MiB. TLS verification stays enabled; redirects are not followed.
