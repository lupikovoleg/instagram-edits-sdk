# XIGBaselAccountLevelReelsDataDeltaQuery

Пакетное обновление метрик выбранных Reels.

- **client_doc_id:** `15638181364556178962628739248`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `static-contract`

**На сервере не проверено.** Параметры восстановлены из APK; ниже нет гарантии актуальной доступности этому аккаунту.

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
