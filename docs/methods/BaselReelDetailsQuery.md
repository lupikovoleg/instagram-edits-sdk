# BaselReelDetailsQuery

Детальная авторская аналитика Reel, включая числовые точки удержания. Основной найденный метод для исходной задачи.

- **client_doc_id:** `3261342854360971614358769315`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `live-verified`

Проверено запросом SDK 18 октября 2026 на одном аккаунте. [Область проверки](../verification.md).

**Наблюдение:** 62 retention points and Reel metrics returned

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `media_id` | string: внутренний ID Reel |
| `include_creative_tools` | boolean: значение feature flag клиента |

## Ответ

data.xig_fetch_media.basel_media_level_insights; reels_retentions: [{index, value}], skip_rate, average_watch_time, views_over_time и показатели взаимодействий

Логические имена отличаются от фактических canonical-имён: `1$xig_fetch_media(id:$media_id)` и `1fvalue`. [Рабочий пример](../../examples/retention.py), [разбор](../retention.md).

## Вызов из вашей системы

```python
response = client.execute(
    "BaselReelDetailsQuery",
    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить
)
payload = response.payload
```

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `analysis/ReelDetailsSource-fallback.java:162`
- `analysis/ReelDetailsSource-fallback.java:590`
- `decompiled/sources/X/AbstractC83588bo1.java:281`
- `decompiled/sources/X/AbstractC80882aUO.java:26`
