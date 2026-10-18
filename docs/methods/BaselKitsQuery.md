# BaselKitsQuery

Чтение наборов переиспользуемых элементов Edits.

- **client_doc_id:** `57198449616693595270598413994`
- **schema:** `instagram`
- **kind:** `query`
- **evidence:** `static-contract`

**На сервере не проверено.** Параметры восстановлены из APK; ниже нет гарантии актуальной доступности этому аккаунту.

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `after` | string/null: cursor |

## Ответ

xig_basel_kits; точная вложенная структура — в schema/коде

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
