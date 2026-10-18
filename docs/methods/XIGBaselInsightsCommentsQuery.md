# XIGBaselInsightsCommentsQuery

Аналитика комментариев выбранного Reel.

- **client_doc_id:** `29719058955793752815580108112`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `live-verified`

Проверено запросом SDK 18 октября 2026 на одном аккаунте. [Область проверки](../verification.md).

**Наблюдение:** Request accepted; ai_comment_insights was null; populated analysis not verified

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `media_id` | string |
| `sort_order` | recent \| popular; live tested recent |

## Ответ

xig_fetch_media.ai_comment_insights; null in the live test, not an empty comment list

## Вызов из вашей системы

```python
response = client.execute(
    "XIGBaselInsightsCommentsQuery",
    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить
)
payload = response.payload
```

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `bytecode/sources/com/instagram/basel/insight/data/remote/BaselCommentInsightsRemoteDataSource.java:339`
- `decompiled/sources/X/EnumC68193RRy.java`
