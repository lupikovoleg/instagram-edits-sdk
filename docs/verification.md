# Что проверено и откуда взяты данные

## Уровни доказательств

| Уровень | Значение |
|---|---|
| `live-verified` | Исходный исследовательский Python-клиент получил успешный ответ сервера |
| `static-contract` | Назначение, переменные и/или разбор ответа восстановлены по APK |
| `static-reference` | Найдена запись в реестре и ссылка из Java-кода; полного контракта нет |
| `registry-only` | Найдены имя и persisted ID; достижимость и параметры не доказаны |

Эти статусы описывают исследование, а не обещание будущей работы API.

## Реальный запрос

18 октября 2026, 12:29 UTC исходный клиент выполнил
`BaselReelDetailsQuery` к `https://i.instagram.com/graphql_www` с
`client_doc_id=3261342854360971614358769315`, `include_creative_tools=false`.
Получены HTTP 200, JSON с Content-Type `text/javascript; charset=utf-8`,
62 числовые точки, последовательные индексы 0..61. Владелец из составного media ID
совпал с ID сессии. Авторизация была получена по явному разрешению владельца,
использована в памяти и не опубликована.

[Обезличенное свидетельство](evidence/live-verification.json) содержит digest
ответа, размер и свойства схемы. Исходный ответ намеренно не включён: он содержит
персональную аналитику и URL медиа. Digest — ссылка на зафиксированный локальный
артефакт, не возможность независимо восстановить или проверить его содержимое.

Этот репозиторий — последующая упаковка рабочего транспорта в библиотеку.
Его тесты и offline demo не выполняют живые запросы. Приватный исходный ответ
используется локально для проверки совместимости парсера, но не является
общедоступной тестовой fixture. Дополнительные операции не получили live-статус.

## APK

| Поле | Значение |
|---|---|
| Package | `com.instagram.basel` |
| Version | `448.0.0.53.84` |
| versionCode | `864801371` |
| APK SHA-256 | `bd88ea0ab6771f47f807524f380ac29b5628c9ebcf9db519808afb420f169757` |
| Certificate SHA-256 | `5367570bad488d8da6a0fab78d9766a1a4c23c3c70fac0ad2e91c8f0bd58b432` |
| DEX | 15 |
| Registry entries | 1663, включая общую инфраструктуру Instagram/Meta |
| Edits-related name matches | 88 (`Basel` / `Eddy`, не гарантия принадлежности всех вызовов UI Edits) |

При исходном исследовании проверены подпись APK и DEX checksums. Сохранённые
`source_references` в каталоге — пути внутри исходного исследовательского набора;
эти декомпилированные файлы не поставляются с публичным репозиторием.
Каталог воспроизводит извлечённые метаданные, но сам по себе не позволяет повторно
декомпилировать APK. Серверный код Meta в исследовании отсутствует.

## Локальные проверки

```sh
python -m unittest discover -s tests -v
python examples/offline_demo.py
python tools/check_release.py
```

Проверки охватывают wire envelope, заголовки, canonical-поля, ownership,
сохранение null/0, ошибки GraphQL, HTTP-отказы, NDJSON, незавершённые ответы,
закрытие редиректов, API библиотеки, CLI, каталоги и отсутствие секретов в экспорте.

## Дополнительные источники

- [instagrapi: `/graphql_www`](https://github.com/subzeroid/instagrapi/blob/master/instagrapi/mixins/graphql.py)
- [instagrapi: IGT авторизация](https://github.com/subzeroid/instagrapi/blob/master/instagrapi/mixins/auth.py)
- [Meta: официальный Instagram Media Insights](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/)

Два первых источника использованы для проверки конверта HTTP и авторизации;
сами Edits operation ID и response paths получены из APK и живого запроса.
