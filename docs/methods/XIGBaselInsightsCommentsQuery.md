# XIGBaselInsightsCommentsQuery

Аналитика комментариев выбранного Reel.

- **client_doc_id:** `29719058955793752815580108112`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `static-contract`

**На сервере не проверено.** Параметры восстановлены из APK; ниже нет гарантии актуальной доступности этому аккаунту.

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `media_id` | string |
| `sort_order` | string: допустимые значения требуют проверки enum вызывающей стороны |

## Ответ

xig_fetch_media и блок аналитики комментариев

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
