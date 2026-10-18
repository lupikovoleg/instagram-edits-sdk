# BaselPublicInsightsQuery

Публичная сокращённая статистика Reel. Не доказана как источник авторского графика удержания.

- **client_doc_id:** `32880071334541180518965887244`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `static-contract`

**На сервере не проверено.** Параметры восстановлены из APK; ниже нет гарантии актуальной доступности этому аккаунту.

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
