# Authentication

Use an existing Instagram session in your backend. The SDK has no password login,
OAuth flow, two-factor authentication flow, browser-cookie extractor, or session refresh.

## Environment variables

Set exactly **one** of these through your secret manager:

| Variable | Value |
|---|---|
| `IG_SESSIONID` | Session cookie of the Instagram account |
| `IG_AUTHORIZATION` | Complete mobile `Bearer IGT:2:…` authorization header |

Optional overrides: `IG_USER_AGENT` and `IG_APP_ID`. `.env` files are not loaded
automatically.

```python
from edits_api import EditsClient

client = EditsClient.from_env()
```

## Pass a session directly

```python
from edits_api import EditsClient, Session

# secret_store is part of your application, not this SDK.
sessionid = secret_store.get("instagram/sessionid")
client = EditsClient(Session.from_sessionid(sessionid))
```

You can provide the account ID explicitly:

```python
session = Session.from_sessionid(sessionid, user_id="YOUR_ACCOUNT_ID")
```

Otherwise the SDK derives it from the numeric prefix of the session cookie.

## Mobile authorization and settings

```python
from pathlib import Path
from edits_api import Session

session = Session.from_authorization(authorization_header)
session = Session.from_settings(Path("private/settings.json"))
```

A minimal settings file has this structure. These values are placeholders:

```json
{
  "cookies": {"sessionid": "YOUR_SESSION_COOKIE"},
  "user_agent": "Instagram 1.0 Android",
  "app_id": "954255173121948"
}
```

`headers.Authorization` and compatible instagrapi settings are also accepted.
The CLI accepts `--session settings.json` or `--session -` for JSON from stdin.

## Client profile

The tested Edits fallback uses `Instagram 1.0 Android` and application ID
`954255173121948`. Override them with your client's real profile when available:

```python
session = Session.from_sessionid(
    sessionid, user_agent=actual_user_agent, app_id=actual_app_id
)
```

The instagrapi settings fallback uses its own app ID, `567067343352427`; that profile
was not independently tested in this project.

## Obtain and handle your own session

After signing in to your own Instagram account, inspect the `sessionid` cookie
in your browser's developer tools: **Application → Cookies** in Chrome, or
**Storage → Cookies** in Safari. Store it in your backend's secret manager.
Do not publish cookie tables, HAR files, or screenshots of credentials.

Use one session per account. A developer's session is not authorization to read
someone else's private analytics. Do not send it to your frontend or put it in
URLs, CLI arguments, application logs, or the Swagger viewer.

## What is sent

For cookie authentication, the SDK creates:

```text
Authorization: Bearer IGT:2:<base64-encoded session JSON>
```

The JSON contains `ds_user_id`, `sessionid` and `should_use_header_over_cookies`.
This encoding is not encryption. HTTPS verifies TLS certificates and the client
does not follow redirects with credentials.
