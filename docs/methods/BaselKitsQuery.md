# BaselKitsQuery

Чтение наборов переиспользуемых элементов Edits.

- **client_doc_id:** `57198449616693595270598413994`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `live-verified`

Проверено запросом SDK 18 октября 2026 на одном аккаунте. [Область проверки](../verification.md).

**Наблюдение:** Request accepted; edges empty and has_next_page=false; populated Kits not verified

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `after` | string/null: cursor |

## Ответ

xig_basel_kits.kits(after:$after,first:50): {edges, page_info}; empty in the live test

## Вызов из вашей системы

```python
response = client.execute(
    "BaselKitsQuery",
    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить
)
payload = response.payload
```

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `decompiled/sources/com/instagram/basel/workflows/kits/data/GraphQLKitsServerApi.java:636`
