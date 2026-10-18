# ReelInsightsQuery

Альтернативная ветка аналитики Reels в общем коде Instagram. Не доказано, что экран Edits использует именно её.

- **client_doc_id:** `34117726176169458716316101`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `static-contract`

**На сервере не проверено.** Параметры восстановлены из APK; ниже нет гарантии актуальной доступности этому аккаунту.

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `mediaIgid` | string |
| `bloksVersioningId` | версия Bloks из константы сборки |

## Ответ

data.ig_reel_insights.retention.retention_curve: [{timestamp_seconds: int, percentage: number}]. Поля проверены по Java String.hashCode в обработчике ответа. Шкала percentage живым ответом не проверена.

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
