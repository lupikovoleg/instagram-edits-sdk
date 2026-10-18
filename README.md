# Instagram Edits SDK

[**Сайт документации (EN)**](https://lupikovoleg.github.io/instagram-edits-sdk/) · [**На русском**](https://lupikovoleg.github.io/instagram-edits-sdk/ru/) · [**Swagger**](https://lupikovoleg.github.io/instagram-edits-sdk/swagger-ui/)

Неофициальный Python SDK и документация внутренних методов Instagram Edits:
статистика Reels, удержание, аналитика аккаунта и аудитории. Для интеграции в свой
backend или аналитический сервис. Python 3.10+, без зависимостей во время работы.

**Проверено 18 октября 2026:** девять методов чтения через реальные запросы SDK
на одном аккаунте, плюс следующая страница Reels. Семь методов вернули данные;
анализ комментариев вернул `null`, Kits — пустой список. Это не официальный SDK
Meta и не гарантия доступности данных у любого аккаунта.

[English](README.en.md) · [Какие данные доступны](docs/data-reference.md)
· [Методы](docs/methods.md) · [Авторизация](docs/authentication.md)
· [Интеграция](docs/integration.md) · [HTTP](docs/http-api.md)
· [Swagger / OpenAPI](docs/swagger.md) · [Проверки](docs/verification.md) · [Выпуск в PyPI](docs/releasing.md)

## Установка

Установка из [PyPI](https://pypi.org/project/instagram-edits-sdk/):

```sh
python -m pip install instagram-edits-sdk
```

Установка из исходников:

```sh
git clone https://github.com/lupikovoleg/instagram-edits-sdk.git
cd instagram-edits-sdk
python -m pip install .
```

Имя дистрибутива — `instagram-edits-sdk`, импорт — `edits_api`, команда —
`edits-api`. Версия 0.2.2. При переходе с локального `instagram-edits-research`
удалите старый дистрибутив: оба используют один Python-модуль `edits_api`.

```sh
python -m pip uninstall instagram-edits-research
```

## Статистика Reel, даже без удержания

Передайте процессу `IG_SESSIONID` из своего менеджера секретов. Нужна сессия
Instagram владельца ролика. Пароль и токен публичного Graph API её не заменяют.
SDK не извлекает cookie из браузера и не выполняет вход.

```python
from edits_api import EditsClient

client = EditsClient.from_env()
reel = client.reel_insights("https://www.instagram.com/reel/YOUR_SHORTCODE/")

print(reel.metrics.get("play_count"))
print(reel.metrics.get("like_count"))
print(reel.metrics.get("skip_rate"))  # Объект с value/delta или None.

if reel.retention_available:
    points = [{"index": p.index, "percent": p.percent} for p in reel.retention]
else:
    points = None  # Нет данных, а не нулевое удержание.

snapshot = reel.to_dict()  # Можно сохранить в своей БД.
reel.export("results/my-reel")  # Новый каталог: JSON; CSV/SVG только с удержанием.
```

Отсутствующее, `null`, пустое или полностью `null`-удержание не мешает получить
остальные метрики. Некорректная структура ответа, отказ сервера или другой владелец
вызывают `EditsError`. `client.retention()` — строгий вариант: без графика выдаёт ошибку.
[Пример статистики](examples/reel_statistics.py), [подробно об удержании](docs/retention.md).

## Методы SDK

| Метод | Данные | Результат живой проверки |
|---|---|---|
| `reel_insights()` / `retention()` | Метрики Reel, кривая удержания | Данные, 62 точки |
| `public_insights()` | Счётчики и коэффициенты Reel | Данные; проверен свой Reel |
| `reels_page()` / `account_reels()` | Список Reels, метрики, cursor | Две страницы по 3 ролика |
| `account_insights()` | Агрегаты и временные ряды | Данные за `LAST_30_DAYS` |
| `audience_insights()` | Демография, рост, активность подписчиков | Данные за `LAST_30_DAYS` |
| `reels_delta()` | Обновление метрик списка ID | Данные для одного ID |
| `comment_insights()` | Блок AI-анализа комментариев | Запрос принят, блок `null` |
| `kits()` | Наборы элементов Edits | Запрос принят, список пуст |
| `extended_reel_insights()` | Альтернативная ветка Instagram insights | Кривая удержания и демография |

```python
page = client.reels_page(first=3)
for item in page.items:
    print(item["id"], item.get("permalink"))
if page.has_next_page:
    next_page = client.reels_page(first=3, after=page.next_cursor)

account = client.account_insights(include_time_series=True)
metrics = account.get_data("xig_user_by_igid_v2", "basel_insights")
```

`QueryResult.payload` хранит исходный ответ. `get_data()` разрешает фактические
canonical-имена (`1$xig_user_by_igid_v2(id:$user_id)` и подобные) по логическим
именам. Он не нормализует единицы метрик. [Работа со всеми девятью методами](docs/data-reference.md).

## Консоль и примеры

```sh
edits-api insights "https://www.instagram.com/reel/YOUR_SHORTCODE/" --output results/reel
edits-api retention "https://www.instagram.com/reel/YOUR_SHORTCODE/" --output results/curve
edits-api catalog
python examples/list_reels.py --first 3 --output results/page.json
python examples/account_statistics.py --period LAST_30_DAYS --output results/account.json
python examples/account_statistics.py --audience --output results/audience.json
```

Каталоги/файлы вывода должны быть новыми. Сессия берётся из окружения, `--session
settings.json` либо `--session -` (JSON из stdin). Секреты не передаются аргументами.

## Документация, проверка, границы

В репозитории 15 подробно разобранных контрактов, индекс 88 операций с именами
Basel/Eddy и общий реестр 1663 операций APK 448.0.0.53.84. Наличие записи в APK
само по себе не доказывает работоспособность. У каждой записи свой уровень доказательств.

Swagger содержит реальный `POST /graphql_www` и девять примеров формы запроса,
а не выдуманные REST-endpoints. Просмотр работает локально без CDN; отправка запросов
в UI отключена. [Как открыть](docs/swagger.md).

```sh
python -m unittest discover -s tests -v
python examples/offline_demo.py
python tools/generate_docs.py --check
python tools/check_release.py
```

Тесты синтетические и не обращаются к Instagram. [Обезличенные свидетельства живых
запросов](docs/evidence/method-verification.json) отдельно фиксируют реальную проверку.

Автоматических retries, входа, обновления сессии и обхода challenge нет. Пределы
запросов и пакетов не установлены. Mutations требуют `allow_mutation=True`, не
входят в проверенную часть SDK и в исследовании на сервере не запускались.

В репозитории нет APK, исходников Meta, cookies, личной аналитики и медиа.
MIT относится к оригинальному коду и документации проекта; Swagger UI имеет свою
[лицензию Apache-2.0](docs/swagger/vendor/LICENSE).
