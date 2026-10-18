# XIGBaselAccountLevelReelsDataDeltaQuery

Пакетное обновление метрик выбранных Reels.

- **client_doc_id:** `15638181364556178962628739248`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `live-verified`

Проверено запросом SDK 18 октября 2026 на одном аккаунте. [Область проверки](../verification.md).

**Наблюдение:** Metrics returned for one supplied media ID; multi-ID capacity not tested

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `media_ids` | array<string> |

## Ответ

xig_basel_multi_media_insights_query

## Вызов из вашей системы

```python
response = client.execute(
    "XIGBaselAccountLevelReelsDataDeltaQuery",
    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить
)
payload = response.payload
```

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `decompiled/sources/X/C93740nPz.java:361`
