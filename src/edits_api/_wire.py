"""Low-level transport and parsing, derived from the live-verified research client.

No browser extraction, login automation, or automatic retries.
"""

from __future__ import annotations

import argparse

import base64

import csv

import datetime as dt

import hashlib

import html

import io

import json

import math

import os

from pathlib import Path

import re

import sys

import time

import urllib.error

import urllib.parse

import urllib.request

import zlib

QUERY = "BaselReelDetailsQuery"

CLIENT_DOC_ID = "3261342854360971614358769315"

CURVE_PATH = "data.xig_fetch_media.basel_media_level_insights.reels_retentions"

HOSTS = ("i.instagram.com", "b.i.instagram.com")

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

MAX_RESPONSE = 32 * 1024 * 1024

class RetentionError(Exception):
    """A diagnostic safe to display without request credentials."""

def media_id(value: str) -> str:
    """Accept a numeric PK, composite PK_owner, or an Instagram Reel URL."""
    if re.fullmatch(r"[0-9]+(?:_[0-9]+)?", value):
        return value.split("_")[0]
    url = urllib.parse.urlsplit(value)
    if url.scheme != "https" or url.netloc.lower() not in ("instagram.com", "www.instagram.com"):
        raise RetentionError("Нужен числовой media_id или https://www.instagram.com/reel/SHORTCODE/.")
    match = re.fullmatch(r"/(?:reel|reels|p)/([A-Za-z0-9_-]{1,20})/?", url.path)
    if not match:
        raise RetentionError("Не удалось извлечь shortcode из ссылки Instagram.")
    number = 0
    for char in match[1]:
        number = number * 64 + ALPHABET.index(char)
    return str(number)

def compact_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def session_headers(path: Path | dict) -> dict[str, str]:
    """Load explicit mobile headers or instagrapi dump_settings()."""
    if isinstance(path, dict):
        session = path
    else:
        try:
            session = json.load(sys.stdin) if path == Path("-") else json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RetentionError("Файл сессии недоступен или содержит некорректный JSON.") from exc
    if not isinstance(session, dict):
        raise RetentionError("Сессия должна быть JSON-объектом.")
    source_headers = session.get("headers", {})
    if not isinstance(source_headers, dict):
        raise RetentionError("Поле headers должно быть объектом.")
    headers = {str(k).lower(): str(v) for k, v in source_headers.items() if v is not None}
    auth_data = session.get("authorization_data") or {}
    cookies = session.get("cookies") or {}
    if not isinstance(auth_data, dict) or not isinstance(cookies, dict):
        raise RetentionError("authorization_data и cookies должны быть объектами.")
    # The same IGT envelope is used by instagrapi LoginMixin.authorization.
    if "authorization" not in headers and auth_data.get("sessionid"):
        headers["authorization"] = "Bearer IGT:2:" + base64.b64encode(compact_json(auth_data).encode()).decode()
    elif "authorization" not in headers and cookies.get("sessionid"):
        sid = urllib.parse.unquote(str(cookies["sessionid"]))
        uid = str(cookies.get("ds_user_id") or sid.split(":", 1)[0])
        if not uid.isdigit():
            raise RetentionError("Для cookie sessionid требуется числовой ds_user_id.")
        auth_data = {"ds_user_id": uid, "sessionid": sid, "should_use_header_over_cookies": True}
        headers["authorization"] = "Bearer IGT:2:" + base64.b64encode(compact_json(auth_data).encode()).decode()
    authorization = headers.get("authorization", "")
    if not authorization.startswith("Bearer IGT:2:"):
        raise RetentionError("Нужен Authorization: Bearer IGT:2:… либо sessionid/authorization_data вашей сессии.")
    try:
        decoded = json.loads(base64.b64decode(authorization.split(":", 2)[2], validate=True))
        if not isinstance(decoded, dict) or not decoded.get("sessionid"):
            raise ValueError("Missing sessionid")
    except (ValueError, UnicodeError) as exc:
        raise RetentionError("Некорректный Authorization IGT:2; проверьте экспорт сессии.") from exc
    uid = str(decoded.get("ds_user_id") or "")
    if not uid.isdigit():
        raise RetentionError("В IGT:2 отсутствует числовой ds_user_id.")
    headers.setdefault("user-agent", str(session.get("user_agent") or ""))
    if not headers["user-agent"]:
        raise RetentionError("В сессии нужен User-Agent или user_agent исходного мобильного клиента.")
    for name in ("ig-intended-user-id", "ig-u-ds-user-id"):
        if name in headers and headers[name] != uid:
            raise RetentionError("ID аккаунта в заголовках не совпадает с авторизацией.")
        headers[name] = uid
    # Preserve the originating session's identifiers; never generate new device IDs.
    uuids = session.get("uuids") or {}
    if not isinstance(uuids, dict):
        raise RetentionError("uuids должен быть объектом.")
    for header, key in (("x-ig-device-id", "uuid"), ("x-ig-family-device-id", "phone_id"),
                        ("x-ig-android-id", "android_device_id")):
        if uuids.get(key):
            headers.setdefault(header, str(uuids[key]))
    if session.get("mid"):
        headers.setdefault("x-mid", str(session["mid"]))
    if session.get("ig_www_claim"):
        headers.setdefault("x-ig-www-claim", str(session["ig_www_claim"]))
    if session.get("app_id"):
        headers.setdefault("x-ig-app-id", str(session["app_id"]))
    # No fallback app ID: absent identification must not silently become another app.
    if not headers.get("x-ig-app-id") and session.get("device_settings") and session.get("user_agent"):
        # dump_settings does not store app_id. This is the verified instagrapi
        # default, only for its own session format, not an Edits impersonation.
        headers["x-ig-app-id"] = "567067343352427"
    if not headers.get("x-ig-app-id"):
        raise RetentionError("Нужен X-IG-App-ID исходной сессии (для исследованного Edits: 954255173121948).")
    if session.get("locale"):
        headers.setdefault("x-ig-app-locale", str(session["locale"]))
    # urllib determines transport headers; avoid stale lengths/encodings from exports.
    for name in ("host", "content-length", "connection", "transfer-encoding", "accept-encoding"):
        headers.pop(name, None)
    headers.update({"content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "x-fb-friendly-name": QUERY, "x-client-doc-id": CLIENT_DOC_ID,
                    "accept": "application/json", "accept-encoding": "gzip, deflate"})
    for name, value in headers.items():
        if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9a-z-]+", name) or "\r" in value or "\n" in value:
            raise RetentionError("Некорректный HTTP-заголовок в файле сессии.")
        try:
            value.encode("latin-1")
        except UnicodeError as exc:
            raise RetentionError("HTTP-заголовок содержит символы вне Latin-1.") from exc
    return headers

def make_request(pk: str, headers: dict[str, str], host: str = HOSTS[0],
                 include_creative_tools: bool = False) -> urllib.request.Request:
    if host not in HOSTS or not pk.isdigit():
        raise RetentionError("Некорректный host или media_id.")
    fields = {"method": "post", "pretty": "false", "format": "json", "server_timestamps": "true",
              "locale": "user", "fb_api_req_friendly_name": QUERY, "purpose": "fetch",
              "enable_canonical_naming": "true", "enable_canonical_variable_overrides": "true",
              "enable_canonical_naming_ambiguous_type_prefixing": "true", "client_doc_id": CLIENT_DOC_ID,
              "variables": compact_json({"media_id": pk, "include_creative_tools": include_creative_tools})}
    return urllib.request.Request(f"https://{host}/graphql_www", data=urllib.parse.urlencode(fields).encode(),
                                  headers=headers, method="POST")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        # Never forward Authorization to a redirected destination.
        return None

def send(request: urllib.request.Request, timeout: float):
    opener = urllib.request.build_opener(NoRedirect())
    try:
        response = opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        response = exc
    except (urllib.error.URLError, OSError) as exc:
        raise RetentionError("Ошибка сети/TLS. Запрос не повторялся; проверьте соединение.") from exc
    with response:
        parts = bytearray()
        try:
            while len(parts) <= MAX_RESPONSE:
                chunk = response.read1(min(65536, MAX_RESPONSE + 1 - len(parts)))
                if not chunk:
                    break
                parts.extend(chunk)
                # GraphQL may keep a chunked connection open after its complete
                # JSON result. Do not wait for EOF when a full document arrived.
                if not response.headers.get("Content-Encoding"):
                    try:
                        document = json.loads(parts)
                    except (ValueError, UnicodeError):
                        continue
                    if isinstance(document, dict) and document.get("hasNext") is not True:
                        break
        except OSError as exc:
            if not parts:
                raise RetentionError(f"HTTP {response.code}, но чтение тела ответа завершилось сетевой ошибкой.") from exc
            # Preserve partial data for diagnosis; parse_response rejects an
            # incomplete JSON document or an unfinished incremental response.
        body = bytes(parts)
        if len(body) > MAX_RESPONSE:
            raise RetentionError("Ответ превышает лимит 32 MiB.")
        encoding = response.headers.get("Content-Encoding", "").lower()
        if encoding in ("gzip", "deflate"):
            try:
                decoder = zlib.decompressobj(16 + zlib.MAX_WBITS if encoding == "gzip" else zlib.MAX_WBITS)
                body = decoder.decompress(body, MAX_RESPONSE + 1)
                if len(body) > MAX_RESPONSE or decoder.unconsumed_tail:
                    raise RetentionError("Распакованный ответ превышает лимит 32 MiB.")
                if not decoder.eof:
                    raise RetentionError("Неполный сжатый ответ.")
            except zlib.error as exc:
                raise RetentionError("Не удалось распаковать ответ сервера.") from exc
        return response.code, body, response.headers.get("Content-Type", "")

def merge_patch(root: dict, patch: dict):
    path = patch.get("path", [])
    if not isinstance(path, list):
        raise RetentionError("Неизвестная структура incremental GraphQL path.")
    if not path:
        data = patch.get("data")
        if isinstance(data, dict):
            root.setdefault("data", {}).update(data)
        return
    keys = path[1:] if path[0] == "data" else path
    if not keys:
        if isinstance(patch.get("data"), dict):
            root.setdefault("data", {}).update(patch["data"])
        return
    target = root.setdefault("data", {})
    try:
        for key in keys[:-1]:
            target = target[key]
        key = keys[-1]
        if "items" in patch:
            if not isinstance(target, list) or not isinstance(key, int) or key != len(target):
                raise RetentionError("Неизвестная позиция incremental GraphQL items.")
            target.extend(patch["items"])
        elif "data" in patch:
            data = patch["data"]
            current = target.get(key) if isinstance(target, dict) else target[key]
            if isinstance(current, dict) and isinstance(data, dict):
                current.update(data)
            else:
                target[key] = data
    except (KeyError, IndexError, TypeError) as exc:
        raise RetentionError("Не удалось собрать incremental GraphQL ответ.") from exc

def parse_response(body: bytes) -> dict:
    try:
        text = body.decode("utf-8-sig")
        try:
            chunks = [json.loads(text)]
        except json.JSONDecodeError:
            chunks = [json.loads(line) for line in text.splitlines() if line.strip()]
    except (UnicodeError, ValueError) as exc:
        raise RetentionError("Сервер вернул не JSON/NDJSON; исходный ответ сохранён.") from exc
    if not chunks or not all(isinstance(c, dict) for c in chunks):
        raise RetentionError("Ожидался GraphQL JSON-объект.")
    root = {}
    errors = []
    for chunk in chunks:
        errors.extend(chunk.get("errors") or [])
        if chunk.get("status") == "fail":
            raise RetentionError("Instagram вернул status=fail; детали в response.body.")
        if "hasNext" in chunk:
            root["hasNext"] = chunk["hasNext"]
        if "path" in chunk:
            merge_patch(root, chunk)
        else:
            for key, value in chunk.items():
                if key == "data" and isinstance(value, dict) and isinstance(root.get(key), dict):
                    root[key].update(value)
                elif key not in ("errors", "incremental"):
                    root[key] = value
        for patch in chunk.get("incremental", []):
            errors.extend(patch.get("errors") or [])
            merge_patch(root, patch)
    if errors:
        raise RetentionError(f"GraphQL вернул ошибки ({len(errors)}); детали в response.body.")
    if root.get("hasNext") is True:
        raise RetentionError("Получен незавершённый incremental GraphQL ответ (hasNext=true).")
    return root

def extract_media(payload: dict, pk: str, expected_owner: str):
    data = payload.get("data")
    media_key = "xig_fetch_media"
    if isinstance(data, dict) and media_key not in data:
        aliases = [key for key in data if re.fullmatch(r"[0-9]+\$xig_fetch_media\(id:\$media_id\)", key)]
        if len(aliases) > 1:
            raise RetentionError("Несколько canonical-полей xig_fetch_media; ответ неоднозначен.")
        if aliases:
            media_key = aliases[0]
    media = data.get(media_key) if isinstance(data, dict) else None
    if not isinstance(media, dict):
        raise RetentionError("В ответе нет data.xig_fetch_media; доступ к Reel не подтверждён.")
    composite_id = str(media.get("pk") or media.get("id") or media.get("strong_id__") or "")
    returned_id = composite_id.split("_")[0]
    if returned_id and returned_id != pk:
        raise RetentionError("media_id ответа не совпал с запрошенным.")
    user = media.get("user") or {}
    owner = str(user.get("pk") or user.get("id") or "") if isinstance(user, dict) else ""
    owner_source = "user" if owner else None
    if not owner and re.fullmatch(r"[0-9]+_[0-9]+", composite_id):
        owner = composite_id.split("_")[1]
        owner_source = "composite_media_id_suffix"
    if owner and owner != expected_owner:
        raise RetentionError("Reel принадлежит другому аккаунту, а не владельцу этой сессии.")
    return media, {"returned_media_id": returned_id or None, "owner_id": owner or None,
                   "owner_verified": bool(owner), "owner_id_source": owner_source,
                   "wire_media_field": media_key}


def extract_curve(payload: dict, pk: str, expected_owner: str, *, allow_unavailable=False):
    media, metadata = extract_media(payload, pk, expected_owner)
    insights = media.get("basel_media_level_insights")
    if not isinstance(insights, dict):
        raise RetentionError("В ответе отсутствует basel_media_level_insights: статистика недоступна.")
    raw = insights.get("reels_retentions") if isinstance(insights, dict) else None
    if raw is not None and not isinstance(raw, list):
        raise RetentionError("Неизвестный формат reels_retentions: ожидался массив или null.")
    if raw is None or not raw:
        if allow_unavailable:
            reason = ("not_returned" if "reels_retentions" not in insights
                      else "null" if raw is None else "empty")
            return [], {**metadata, "retention_status": "unavailable",
                        "retention_unavailable_reason": reason, "wire_value_fields": [],
                        "warnings": ["Удержание недоступно; остальные метрики сохранены."]}
        raise RetentionError("reels_retentions отсутствует/пуст: график не получен. HTTP 200 не означает успех.")
    points = []
    indices = []
    warnings = []
    value_fields = set()
    for order, point in enumerate(raw):
        if not isinstance(point, dict):
            raise RetentionError("Неизвестный формат точки удержания.")
        value_key = "value"
        if value_key not in point:
            aliases = [key for key in point if re.fullmatch(r"[0-9]+fvalue", key)]
            if len(aliases) > 1:
                raise RetentionError("Несколько canonical-полей value в точке.")
            if aliases:
                value_key = aliases[0]
        value_fields.add(value_key)
        index, value = point.get("index"), point.get(value_key)
        if index is not None and (type(index) is not int or index < 0):
            raise RetentionError("index должен быть целым неотрицательным числом или null.")
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
            raise RetentionError("value должен быть конечным числом или null.")
        points.append({"order": order, "index": index, "value": value,
                       "percent": value * 100 if value is not None else None})
        if index is not None:
            indices.append(index)
        if value is not None and value < 0:
            warnings.append("Есть отрицательное value; исходное значение сохранено без коррекции.")
    available = any(p["index"] is not None and p["value"] is not None for p in points)
    if not available and not allow_unavailable:
        raise RetentionError("Нет ни одной числовой пары index/value для графика.")
    if indices != list(range(len(raw))):
        warnings.append("Индексы не образуют последовательность 0..N-1; секунды не гарантированы, точки не интерполированы.")
    if any(p["index"] is None or p["value"] is None for p in points):
        warnings.append("Есть null: в таблице сохранены, на графике показаны разрывы.")
    if not metadata["owner_id"]:
        warnings.append("В ответе отсутствует ID владельца; владение не проверено по полю user.")
    if not available:
        warnings.append("В кривой нет числовых пар index/value; остальные метрики сохранены.")
    return points, {**metadata, "retention_status": "available" if available else "unavailable",
                    "retention_unavailable_reason": None if available else "no_numeric_points",
                    "wire_value_fields": sorted(value_fields),
                    "warnings": list(dict.fromkeys(warnings))}

def private_write(path: Path, content: str | bytes):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(content.encode("utf-8") if isinstance(content, str) else content)

def svg_chart(points: list[dict], pk: str) -> str:
    finite = [(p["index"], p["percent"]) for p in points if p["index"] is not None and p["percent"] is not None]
    xmax = max(1, max(x for x, y in finite))
    ymin = min(0, min(y for x, y in finite))
    ymax = max(100, max(y for x, y in finite))
    px = lambda x: 85 + x / xmax * 860
    py = lambda y: 365 - (y - ymin) / (ymax - ymin) * 275
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="450" viewBox="0 0 1020 450">',
             '<rect width="1020" height="450" fill="#101725"/>',
             '<g font-family="Arial,sans-serif" fill="#e4ebf5">',
             f'<text x="85" y="42" font-size="23">Reel {html.escape(pk)} — удержание</text>',
             '<text x="85" y="67" font-size="13">value × 100%; null сохранены как разрывы; без сглаживания</text>']
    for k in range(5):
        y = ymin + (ymax - ymin) * k / 4
        parts += [f'<path d="M85,{py(y):.2f} H945" stroke="#303a4c"/>',
                  f'<text x="73" y="{py(y)+5:.2f}" text-anchor="end" font-size="13">{y:g}%</text>']
    for k in range(6):
        x = xmax * k / 5
        parts.append(f'<text x="{px(x):.2f}" y="389" text-anchor="middle" font-size="13">{x:g}</text>')
    parts.append('<text x="515" y="425" text-anchor="middle" font-size="14">index (клиент использует как позицию времени)</text>')
    segment = []
    previous = None
    def flush():
        if segment:
            parts.append('<polyline fill="none" stroke="#5eead4" stroke-width="3" points="' + ' '.join(segment) + '"/>')
            segment.clear()
    for point in points:
        x, y = point["index"], point["percent"]
        if x is None or y is None:
            flush()
            previous = None
            continue
        if previous is not None and x != previous + 1:
            flush()
        segment.append(f"{px(x):.2f},{py(y):.2f}")
        parts.append(f'<circle cx="{px(x):.2f}" cy="{py(y):.2f}" r="2" fill="#5eead4"/>')
        previous = x
    flush()
    return "\n".join(parts + ["</g></svg>"])

def fetch_retention(value: str, session: Path | dict, output: Path, host: str = HOSTS[0],
                    timeout: float = 30, include_creative_tools: bool = False, transport=send) -> dict:
    pk = media_id(value)
    headers = session_headers(session)
    request = make_request(pk, headers, host, include_creative_tools)
    if output.exists():
        raise RetentionError("Каталог результата уже существует; укажите новый, чтобы не затереть данные.")
    output.mkdir(parents=True, mode=0o700)
    manifest = {"query": QUERY, "client_doc_id": CLIENT_DOC_ID, "url": request.full_url,
                "media_id": pk, "requested_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "include_creative_tools": include_creative_tools, "curve_path": CURVE_PATH,
                "live_attempted": transport is send, "success": False, "credentials_saved": False}
    if isinstance(session, dict) and session.get("session_source"):
        manifest["session_source"] = session["session_source"]
    try:
        status, body, content_type = transport(request, timeout)
        private_write(output / "response.body", body)
        manifest.update({"http_status": status, "content_type": content_type,
                         "response_sha256": hashlib.sha256(body).hexdigest(), "response_bytes": len(body)})
        if status != 200:
            raise RetentionError(f"HTTP {status}; исходный ответ сохранён. Автоматических повторов нет.")
        payload = parse_response(body)
        points, details = extract_curve(payload, pk, headers["ig-intended-user-id"])
        private_write(output / "response.json", json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
        private_write(output / "retention.json", json.dumps(points, ensure_ascii=False, indent=2, allow_nan=False))
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=["order", "index", "value", "percent"])
        writer.writeheader()
        writer.writerows(points)
        private_write(output / "retention.csv", buffer.getvalue())
        private_write(output / "retention.svg", svg_chart(points, pk))
        manifest.update(details)
        manifest.update({"success": True, "point_count": len(points),
                         "numeric_point_count": sum(p["index"] is not None and p["value"] is not None for p in points)})
    except RetentionError as exc:
        manifest["error"] = str(exc)
        raise
    finally:
        private_write(output / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest
