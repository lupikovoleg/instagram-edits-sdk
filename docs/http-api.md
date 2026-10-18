# HTTP-контракт

## Подтверждённый запрос удержания

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

Тело — **form-urlencoded**, а `variables` внутри него — JSON-строка:

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

Список выше показан построчно для чтения. В HTTP это одна URL-encoded форма;
готовый SDK кодирует её сам. Не отправляйте всё тело как application/json.

`b.i.instagram.com` — явно выбираемый альтернативный host из реализации
instagrapi. Живой тест этого проекта использовал **i.instagram.com**. Автоматического
переключения host при отказе нет. Схема `distillery` использует другой транспорт
и не поддержана универсальным `execute()`.

## Ответ и canonical-имена

Реальный успешный ответ пришёл с `Content-Type: text/javascript; charset=utf-8`,
хотя его тело — JSON. Нельзя проверять успех только по Content-Type.

Синтетический пример с подтверждённой структурой (значения вымышлены):

```json
{
  "data": {
    "1$xig_fetch_media(id:$media_id)": {
      "id": "12345_67890",
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

Сериализаторы APK оперируют логическими именами `xig_fetch_media` и `value`.
Включённые canonical-флаги дали поля `1$xig_fetch_media(id:$media_id)` и `1fvalue`.
SDK распознаёт оба варианта и отклоняет неоднозначные совпадения.

`response.payload` остаётся исходным. Для прикладного кода используйте
`client.reel_insights()` — он преобразует только подтверждённые поля.
Для других методов `response.get_data("xig_user_by_igid_v2", "basel_insights")`
разрешает canonical-имена пути; неоднозначные пути отклоняются.

## Завершение чтения

Сервер в живой проверке оставлял chunked-соединение открытым после JSON-документа.
Поэтому клиент читает блоками и не ждёт закрытия соединения, когда получил полный
JSON без `hasNext=true`. Поддержаны обычный JSON, NDJSON, несколько вариантов
incremental patches, gzip и deflate. Это не полная реализация всех transport modes Pando;
multipart/mixed и SSE отдельно не реализованы.

## Отказы

- HTTP не 200 → исключение, без автоматического повтора.
- GraphQL `errors` или `status=fail` → исключение, даже при HTTP 200.
- Незавершённый `hasNext=true` → исключение.
- Удержание отсутствует/null/пусто → остальные метрики доступны в `reel_insights()`,
  `retention_available=False`; строгий `retention()` выдаёт исключение.
- Другой media ID/владелец → исключение.
- Точки с `null` сохраняются как пропуски, не как нули.

Timeout: 30 секунд по умолчанию, разрешён диапазон 1..120. Ответ ограничен
32 MiB. TLS проверяется. HTTP redirects не выполняются, чтобы не пересылать
авторизацию на другое направление.

Источники: APK 448.0.0.53.84 и
[private_graphql_www_request в instagrapi](https://github.com/subzeroid/instagrapi/blob/master/instagrapi/mixins/graphql.py).

## OpenAPI

[Спецификация](openapi.json) описывает этот же POST и девять примеров формы.
[Swagger UI](swagger.md) служит локальным справочником, отправка запросов из UI отключена.
`ReelInsightsQuery` реально вернул NDJSON с Content-Type `text/html; charset=utf-8`;
тип MIME не заменяет проверку и сборку JSON-ответа.
