# Swagger и OpenAPI

[openapi.json](openapi.json) — OpenAPI 3.1.0 для настоящего транспорта Instagram:
`POST https://i.instagram.com/graphql_www`. В одном endpoint девять именованных
примеров с точными persisted query ID. `variables` — JSON-строка внутри
`application/x-www-form-urlencoded`, а не отдельный REST endpoint для каждого метода.

Из корня репозитория:

```sh
python -m http.server 8765 --bind 127.0.0.1 --directory docs
```

Откройте `http://127.0.0.1:8765/swagger/`. Разверните `POST /graphql_www`, выберите
операцию в списке примеров и посмотрите variables/заголовки. Ниже находятся схемы
variables и результата SDK. Значения ID в примерах синтетические.

В UI отключены отправка запросов и ввод Authorization. Viewer загружает только
локальный OpenAPI, использует локальные JS/CSS и не требует CDN. Это справочник,
а не сервер API и не способ хранить sessionid в браузере. Схемы можно импортировать
в свои инструменты; для запросов предпочтителен SDK, который обрабатывает NDJSON,
canonical aliases и GraphQL errors.

Версия и integrity локального Swagger UI: [provenance.json](swagger/vendor/provenance.json).
[Лицензия Swagger UI](swagger/vendor/LICENSE). Спецификация формата:
[OpenAPI 3.1.0](https://spec.openapis.org/oas/v3.1.0).

Перегенерировать и проверить:

```sh
python tools/generate_openapi.py
python tools/generate_openapi.py --check
```

Не все optional/nullable поля ответа известны. Поэтому raw GraphQL payload имеет
открытую схему; наличие поля у другого аккаунта не гарантируется. Это точнее, чем
выдавать один ответ за исчерпывающую серверную схему.
