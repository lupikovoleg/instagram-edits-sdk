"""Importable API, authentication, typed retention and explicit exports."""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
from typing import Any, Callable

from . import _wire
from .registry import get_operation


@dataclass(frozen=True)
class Session:
    """Keep credentials out of repr/logs. This class does not log in or refresh."""
    _headers: dict[str, str] = field(repr=False)
    user_id: str

    @classmethod
    def from_settings(cls, settings: dict | Path) -> Session:
        headers = _wire.session_headers(settings)
        return cls(headers, headers["ig-intended-user-id"])

    @classmethod
    def from_sessionid(cls, sessionid: str, *, user_id: str | None = None,
                       user_agent="Instagram 1.0 Android", app_id="954255173121948") -> Session:
        """Use the Edits APK fallback profile that passed the recorded live test."""
        return cls.from_settings({"cookies": {"sessionid": sessionid, **(
            {"ds_user_id": user_id} if user_id else {})}, "user_agent": user_agent, "app_id": app_id})

    @classmethod
    def from_authorization(cls, authorization: str, *, user_agent="Instagram 1.0 Android",
                           app_id="954255173121948") -> Session:
        return cls.from_settings({"headers": {"Authorization": authorization},
                                  "user_agent": user_agent, "app_id": app_id})

    @classmethod
    def from_env(cls) -> Session:
        sid, auth = os.environ.get("IG_SESSIONID"), os.environ.get("IG_AUTHORIZATION")
        if bool(sid) == bool(auth):
            raise _wire.RetentionError("Set exactly one of IG_SESSIONID or IG_AUTHORIZATION via your secret manager.")
        profile = {"user_agent": os.environ.get("IG_USER_AGENT", "Instagram 1.0 Android"),
                   "app_id": os.environ.get("IG_APP_ID", "954255173121948")}
        return cls.from_sessionid(sid, **profile) if sid else cls.from_authorization(auth, **profile)


@dataclass(frozen=True)
class QueryResult:
    operation: str
    payload: dict[str, Any] = field(repr=False)
    raw_body: bytes = field(repr=False)
    http_status: int
    content_type: str
    fetched_at: str
    live_request: bool

    @property
    def sha256(self):
        return hashlib.sha256(self.raw_body).hexdigest()

    def save_json(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        _wire.private_write(path, json.dumps(self.payload, ensure_ascii=False, indent=2, allow_nan=False))
        return path


@dataclass(frozen=True)
class RetentionPoint:
    index: int | None
    value: float | None

    @property
    def percent(self):
        return self.value * 100 if self.value is not None else None


@dataclass(frozen=True)
class ReelInsights:
    media_id: str
    retention: tuple[RetentionPoint, ...]
    metrics: dict[str, Any] = field(repr=False)
    metadata: dict[str, Any]
    response: QueryResult = field(repr=False)

    def to_dict(self):
        return {"media_id": self.media_id,
                "retention": [{**asdict(point), "percent": point.percent} for point in self.retention],
                "metrics": self.metrics, "metadata": self.metadata}

    def export(self, directory: str | Path) -> Path:
        directory = Path(directory)
        if directory.exists():
            raise _wire.RetentionError("Export directory already exists; choose a new directory.")
        directory.mkdir(mode=0o700, parents=True)
        points = [{"order": i, **asdict(p), "percent": p.percent} for i, p in enumerate(self.retention)]
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=["order", "index", "value", "percent"])
        writer.writeheader(); writer.writerows(points)
        manifest = {**self.metadata, "operation": self.response.operation,
                    "http_status": self.response.http_status, "content_type": self.response.content_type,
                    "fetched_at": self.response.fetched_at, "response_sha256": self.response.sha256,
                    "live_request": self.response.live_request, "point_count": len(self.retention),
                    "credentials_saved": False}
        for name, data in {
            "insights.json": json.dumps(self.to_dict(), ensure_ascii=False, indent=2, allow_nan=False),
            "retention.csv": buffer.getvalue(), "retention.svg": _wire.svg_chart(points, self.media_id),
            "response.json": json.dumps(self.response.payload, ensure_ascii=False, indent=2, allow_nan=False),
            "manifest.json": json.dumps(manifest, ensure_ascii=False, indent=2),
        }.items():
            _wire.private_write(directory / name, data)
        return directory


def _metric(value):
    """Normalize only observed float aliases, without guessing other wire keys."""
    if not isinstance(value, dict):
        return value
    result = dict(value)
    for field_name in ("value", "delta"):
        aliases = [key for key in value if _wire.re.fullmatch(r"[0-9]+f" + field_name, key)]
        if aliases:
            if field_name in value or len(aliases) != 1:
                raise _wire.RetentionError("Ambiguous canonical metric field.")
            result[field_name] = result.pop(aliases[0])
    return result


class EditsClient:
    """One HTTP request per method. No implicit retries, pagination or token refresh."""
    def __init__(self, session: Session, *, host="i.instagram.com", timeout=30,
                 transport: Callable = _wire.send):
        if host not in _wire.HOSTS or not 1 <= timeout <= 120:
            raise _wire.RetentionError("Unsupported host or timeout outside 1..120 seconds.")
        self._session, self._host, self._timeout = session, host, timeout
        self._transport = transport

    @classmethod
    def from_env(cls, **kwargs):
        return cls(Session.from_env(), **kwargs)

    def execute(self, operation: str, variables: dict, *, allow_mutation=False) -> QueryResult:
        contract = get_operation(operation)
        if contract["schema"] != "instagram":
            raise _wire.RetentionError("Only the instagram /graphql_www transport is implemented.")
        if contract["kind"] != "query":
            if contract["kind"] != "mutation" or not allow_mutation:
                raise _wire.RetentionError("Non-query operations require explicit allow_mutation=True; unknown kinds are unsupported.")
        if not isinstance(variables, dict):
            raise _wire.RetentionError("variables must be a dict.")
        # Keep the wire envelope identical to the original verified request.
        from urllib.parse import parse_qsl, urlencode
        request = _wire.make_request("0", dict(self._session._headers), self._host)
        form = dict(parse_qsl(request.data.decode()))
        form.update(fb_api_req_friendly_name=operation, client_doc_id=contract["client_doc_id"],
                    variables=_wire.compact_json(variables))
        request.data = urlencode(form).encode()
        request.add_header("X-FB-Friendly-Name", operation)
        request.add_header("X-Client-Doc-Id", contract["client_doc_id"])
        fetched = dt.datetime.now(dt.timezone.utc).isoformat()
        status, body, kind = self._transport(request, self._timeout)
        if status != 200:
            raise _wire.RetentionError(f"HTTP {status} from {operation}; request was not retried.")
        payload = _wire.parse_response(body)
        return QueryResult(operation, payload, body, status, kind, fetched, self._transport is _wire.send)

    def reel_insights(self, media: str, *, include_creative_tools=False) -> ReelInsights:
        pk = _wire.media_id(media)
        response = self.execute("BaselReelDetailsQuery", {
            "media_id": pk, "include_creative_tools": include_creative_tools})
        points, metadata = _wire.extract_curve(response.payload, pk, self._session.user_id)
        node = response.payload["data"][metadata["wire_media_field"]]["basel_media_level_insights"]
        metrics = {key: _metric(value) for key, value in node.items() if key != "reels_retentions"}
        return ReelInsights(pk, tuple(RetentionPoint(p["index"], p["value"]) for p in points),
                            metrics, metadata, response)

    def retention(self, media: str) -> tuple[RetentionPoint, ...]:
        return self.reel_insights(media).retention

    def public_insights(self, media: str) -> QueryResult:
        return self.execute("BaselPublicInsightsQuery", {"media_id": _wire.media_id(media)})

    def account_insights(self, *, period: str, user_id=None, include_time_series=False) -> QueryResult:
        return self.execute("BaselAccountLevelInsightsQuery", {
            "user_id": user_id or self._session.user_id, "period": period,
            "shouldIncludeTimeSeries": include_time_series})

    def account_reels(self, *, first=10, after=None, timeframe="LIFETIME", order_by="BY_DATE",
                      sort_direction="DESCENDING", skip_follow_count=False, user_id=None) -> QueryResult:
        if type(first) is not int or first < 1:
            raise _wire.RetentionError("first must be a positive integer; server page limits are unknown.")
        if timeframe not in {"LIFETIME", "ONE_WEEK", "TWO_WEEKS", "ONE_MONTH", "ONE_YEAR"}:
            raise _wire.RetentionError("Unknown timeframe in this APK version.")
        if order_by not in {"BY_DATE", "BY_VIEWS", "BY_LIKES", "BY_COMMENTS", "BY_REPOSTS", "BY_SHARES", "BY_SAVES", "BY_FOLLOWERS", "BY_SKIP_RATE"}:
            raise _wire.RetentionError("Unknown order_by in this APK version.")
        if sort_direction not in (None, "ASCENDING", "DESCENDING"):
            raise _wire.RetentionError("Unknown sort_direction.")
        return self.execute("BaselAccountLevelReelsQuery", {
            "user_id": user_id or self._session.user_id, "first": first, "after": after,
            "timeframe": timeframe, "order_by": order_by, "sort_direction": sort_direction,
            "skip_follow_count": skip_follow_count})

    def audience_insights(self, *, period: str, client_timezone: str, user_id=None) -> QueryResult:
        return self.execute("BaselAudienceInsightsQuery", {
            "user_id": user_id or self._session.user_id, "period": period, "client_timezone": client_timezone})

    def reels_delta(self, media_ids: list[str]) -> QueryResult:
        if not media_ids:
            raise _wire.RetentionError("media_ids must not be empty.")
        return self.execute("XIGBaselAccountLevelReelsDataDeltaQuery", {
            "media_ids": [_wire.media_id(media) for media in media_ids]})

    def comment_insights(self, media: str, *, sort_order: str) -> QueryResult:
        return self.execute("XIGBaselInsightsCommentsQuery", {
            "media_id": _wire.media_id(media), "sort_order": sort_order})
