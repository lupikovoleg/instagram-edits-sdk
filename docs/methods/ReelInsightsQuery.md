# ReelInsightsQuery

Альтернативная ветка аналитики Reels в общем коде Instagram. Не доказано, что экран Edits использует именно её.

- **client_doc_id:** `34117726176169458716316101`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `live-verified`

Проверено запросом SDK 18 октября 2026 на одном аккаунте. [Область проверки](../verification.md).

**Наблюдение:** Alternative retention curve and demographics returned; NDJSON response parsed

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `mediaIgid` | string |
| `bloksVersioningId` | string; tested APK version: 8dc50e9193c9b70a3f9dbcc25fc5f444bbac27bb56a8c1359ede836b8069c4b8 |

## Ответ

ig_reel_insights.retention.retention_curve: [{timestamp_seconds, 1fpercentage}]. Retention percentage is a fraction in the observed response (1 = 100%); other percentage fields have different units.

## Вызов из вашей системы

```python
response = client.execute(
    "ReelInsightsQuery",
    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить
)
payload = response.payload
```

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `decompiled/sources/X/C71556TdZ.java:1403`
- `analysis/schema/pando-strings.txt:16440`
- `bytecode/sources/com/instagram/insights/organic/reel/data/graphql/GraphQLReelInsightsDataSource$subscribe$1.java:740`
- `bytecode/sources/X/AnonymousClass218.java:22`
- `decompiled/sources/X/AnonymousClass000.java:5540`
