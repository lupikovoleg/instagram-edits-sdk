# BaselAccountLevelInsightsQuery

Сводная аналитика аккаунта, с опциональными временными рядами.

- **client_doc_id:** `279077652713939115792325780352`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `static-contract`

**На сервере не проверено.** Параметры восстановлены из APK; ниже нет гарантии актуальной доступности этому аккаунту.

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `user_id` | string: userId текущей UserSession |
| `period` | string, диапазон допустимых значений в этой работе не подтверждён |
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
