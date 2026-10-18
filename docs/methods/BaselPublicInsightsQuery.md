# BaselPublicInsightsQuery

Публичная сокращённая статистика Reel. Не доказана как источник авторского графика удержания.

- **client_doc_id:** `32880071334541180518965887244`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `live-verified`

Проверено запросом SDK 18 октября 2026 на одном аккаунте. [Область проверки](../verification.md).

**Наблюдение:** Public metric counts and rates returned for the owned Reel

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `media_id` | string |

## Ответ

xig_fetch_media; basel_media_public_insights; счётчики взаимодействий

## Вызов из вашей системы

```python
response = client.execute(
    "BaselPublicInsightsQuery",
    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить
)
payload = response.payload
```

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `analysis/ReelDetailsSource.java:442`
