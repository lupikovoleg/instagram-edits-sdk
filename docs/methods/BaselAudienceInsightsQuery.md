# BaselAudienceInsightsQuery

Аналитика аудитории аккаунта с учётом периода и часового пояса.

- **client_doc_id:** `416010146012703390907640345604`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `static-contract`

**На сервере не проверено.** Параметры восстановлены из APK; ниже нет гарантии актуальной доступности этому аккаунту.

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `user_id` | string: текущий UserSession.userId |
| `period` | string: допустимые значения не восстановлены |
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
