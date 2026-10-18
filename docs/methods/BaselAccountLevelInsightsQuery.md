# BaselAccountLevelInsightsQuery

Сводная аналитика аккаунта, с опциональными временными рядами.

- **client_doc_id:** `279077652713939115792325780352`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `live-verified`

Проверено запросом SDK 18 октября 2026 на одном аккаунте. [Область проверки](../verification.md).

**Наблюдение:** Account aggregates and time series returned; LAST_30_DAYS

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `user_id` | string: userId текущей UserSession |
| `period` | LAST_7_DAYS \| LAST_14_DAYS \| LAST_30_DAYS \| LAST_60_DAYS \| LAST_90_DAYS \| LAST_180_DAYS; live tested LAST_30_DAYS |
| `shouldIncludeTimeSeries` | boolean |

## Ответ

xig_user_by_igid_v2 и вложенные агрегаты аккаунта

## Вызов из вашей системы

```python
response = client.execute(
    "BaselAccountLevelInsightsQuery",
    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить
)
payload = response.payload
```

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `decompiled/sources/com/instagram/basel/insight/data/remote/BaselAccountLevelInsightsRemoteSource.java:494`
- `decompiled/sources/X/EnumC38315FHu.java`
- `decompiled/sources/X/C73666Usk.java:1844`
