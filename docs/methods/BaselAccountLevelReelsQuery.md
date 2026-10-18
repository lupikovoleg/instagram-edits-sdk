# BaselAccountLevelReelsQuery

Постраничный список Reels аккаунта, сортировка по метрикам, в том числе по пропускам.

- **client_doc_id:** `11900819615835482353778696516`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `live-verified`

Проверено запросом SDK 18 октября 2026 на одном аккаунте. [Область проверки](../verification.md).

**Наблюдение:** 3 Reel nodes, next cursor present; second page verified separately

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `user_id` | string |
| `order_by` | BY_DATE \| BY_VIEWS \| BY_LIKES \| BY_COMMENTS \| BY_REPOSTS \| BY_SHARES \| BY_SAVES \| BY_FOLLOWERS \| BY_SKIP_RATE |
| `first` | integer: размер страницы |
| `after` | string/null: cursor |
| `timeframe` | LIFETIME \| ONE_WEEK \| TWO_WEEKS \| ONE_MONTH \| ONE_YEAR |
| `sort_direction` | ASCENDING \| DESCENDING \| null |
| `skip_follow_count` | boolean: клиент выставляет по flag и выбранной сортировке |

## Ответ

xig_user_by_igid_v2; список Reels и информация пагинации

## Вызов из вашей системы

```python
response = client.execute(
    "BaselAccountLevelReelsQuery",
    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить
)
payload = response.payload
```

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `analysis/early-java/sources/com/instagram/basel/insight/data/remote/BaselAccountLevelInsightsRemoteSource.java:973`
