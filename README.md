# Instagram Edits API Research

Неофициальная документация и Python-клиент внутренних методов **Instagram Edits**:
удержание Reels, статистика ролика, списки Reels и аналитика аккаунта.

Для разработчиков, которые хотят получать данные в собственном backend, аналитическом
сервисе или исследовательском скрипте. Это не официальный SDK Meta и не OAuth-приложение.

**Главный подтверждённый результат:** `BaselReelDetailsQuery` возвращает числовую кривую
удержания в `reels_retentions`. 18 октября 2026 выполнен успешный авторизованный запрос
с 62 точками. Остальные методы ниже восстановлены из APK и отдельно сервером не проверены.

[English](README.en.md) · [HTTP API](docs/http-api.md) · [Авторизация](docs/authentication.md)
· [Удержание](docs/retention.md) · [Методы](docs/methods.md)
· [Интеграция](docs/integration.md) · [Проверки и источники](docs/verification.md)

## Установка

Python 3.10+. Во время работы клиент использует только стандартную библиотеку.
Из корня скачанного/клонированного репозитория:

```sh
python -m pip install .
```

Пакет **не опубликован в PyPI**: установка производится из этого репозитория.
На macOS/Linux вместо `python` может требоваться `python3`.

## Получить удержание и статистику в своей системе

Передайте `IG_SESSIONID` процессу через свой менеджер секретов. Это sessionid
авторизованного аккаунта владельца ролика; пароль и публичный Graph API access token
его не заменяют. Библиотека не выполняет вход и не извлекает сессии из браузера.

```python
from edits_api import EditsClient

client = EditsClient.from_env()
result = client.reel_insights("https://www.instagram.com/reel/YOUR_SHORTCODE/")

for point in result.retention:
    print(point.index, point.value, point.percent)

print(result.metrics.get("play_count"))
print(result.metrics.get("skip_rate"))
result.export("results/my-reel")  # Новый каталог: JSON, CSV, SVG, manifest.
```

`point.value` — исходная доля, `point.percent` — доля × 100; `None` сохраняется.
ID/URL можно передавать напрямую. Существующий каталог экспорта не перезаписывается.
Для работы без экспорта достаточно использовать `result.to_dict()` и сохранять
его в своей БД. [Полный пример](examples/retention.py).

## Прямой вызов метода

```python
from edits_api import EditsClient

client = EditsClient.from_env()
response = client.execute("BaselReelDetailsQuery", {
    "media_id": "YOUR_NUMERIC_MEDIA_ID",
    "include_creative_tools": False,
})
payload = response.payload  # Исходная структура GraphQL, включая canonical-имена.
```

Запрос уходит в `POST https://i.instagram.com/graphql_www` с
`client_doc_id=3261342854360971614358769315`. Это ID определения запроса в конкретной
сборке, а не токен доступа. [Заголовки, форма и формат ответа](docs/http-api.md).

## Что есть в репозитории

| Область | Что доступно | Проверка |
|---|---|---|
| Удержание и статистика Reel | `reel_insights()`, `retention()`, JSON/CSV/SVG | Реальный запрос исходного клиента + регрессии SDK |
| Сокращённая статистика | `public_insights()` | Статический контракт APK |
| Список Reels, сортировка, cursor | `account_reels()` | Статический контракт APK |
| Аналитика аккаунта | `account_insights()` | Статический контракт; значения `period` не восстановлены |
| Аудитория | `audience_insights()` | Статический контракт; значения `period` не восстановлены |
| Пакетное обновление статистики | `reels_delta()` | Статический контракт APK |
| Аналитика комментариев | `comment_insights()` | Статический контракт; значения `sort_order` не восстановлены |
| Остальной Edits | Каталог 88 операций, включая mutations | Уровень доказательств указан для каждой операции |
| Общие методы в APK | Дополнительный реестр 1663 операций | Наличие в APK не означает доступность на сервере |

Универсальный вызов `execute()` не восстанавливает неизвестные параметры.
Он поддерживает только схему `instagram` и запрещает mutations без явного
`allow_mutation=True`. Вызовы, меняющие данные, в живой проверке не выполнялись.

## Консоль

```sh
edits-api retention "https://www.instagram.com/reel/YOUR_SHORTCODE/" --output results/my-reel
edits-api catalog
edits-api catalog --all
```

Сессия берётся из окружения. Вместо этого можно использовать `--session settings.json`
или `--session -` для JSON через stdin. Исходный ответ и токены в stdout не выводятся.

## Воспроизведение проверок

```sh
python -m unittest discover -s tests -v
python examples/offline_demo.py
python tools/check_release.py
```

Тесты и offline demo не обращаются к Instagram и используют синтетические данные.
Историческое доказательство реального запроса хранится отдельно в
[docs/evidence/live-verification.json](docs/evidence/live-verification.json).
Новый экземпляр SDK, другой аккаунт или новая версия серверного API требуют своей проверки.

## Границы

Методы зависят от сессии, аккаунта, наличия аналитики и версии persisted query.
Нет автоматического входа, решения challenge, обхода TLS или бесконечных повторов.
Серверный отказ и пустая аналитика не превращаются в нулевые значения удержания.

APK, декомпилированные исходники Meta, cookie, персональные ответы и медиа в репозиторий
не входят. MIT относится к оригинальному коду и документации этого проекта.
