# BaselAudienceInsightsQuery

Аналитика аудитории аккаунта с учётом периода и часового пояса.

- **client_doc_id:** `416010146012703390907640345604`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `live-verified`

Проверено запросом SDK 18 октября 2026 на одном аккаунте. [Область проверки](../verification.md).

**Наблюдение:** Age, gender, location, follower activity and growth data returned

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `user_id` | string: текущий UserSession.userId |
| `period` | LAST_7_DAYS \| LAST_14_DAYS \| LAST_30_DAYS \| LAST_60_DAYS \| LAST_90_DAYS \| LAST_180_DAYS; live tested LAST_30_DAYS |
| `client_timezone` | string |

## Ответ

xig_user_by_igid_v2 и метрики аудитории; точные разделы зависят от доступности данных

## Вызов из вашей системы

```python
response = client.execute(
    "BaselAudienceInsightsQuery",
    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить
)
payload = response.payload
```

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `decompiled/sources/com/instagram/basel/insight/data/remote/BaselAudienceInsightsRemoteSource.java:427`
- `decompiled/sources/X/EnumC38315FHu.java`
- `decompiled/sources/X/C73666Usk.java:1844`
