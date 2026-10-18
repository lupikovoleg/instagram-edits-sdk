# Интеграция в свой сервис

## Запрос → ваш формат → хранение

```python
from edits_api import EditsClient

def collect_retention(client: EditsClient, reel_url: str):
    result = client.reel_insights(reel_url)
    return {
        "media_id": result.media_id,
        "collected_at": result.response.fetched_at,
        "retention": [
            {"index": p.index, "value": p.value}
            for p in result.retention
        ],
        "warnings": result.metadata["warnings"],
        "owner_verified": result.metadata["owner_verified"],
    }
```

Храните каждый snapshot отдельно либо обновляйте по `(account_id, media_id)`
с timestamp. Статистика меняется со временем. Рекомендованного сервером TTL в этом
исследовании нет. Кэш 120 секунд найден только во внутреннем репозитории Android-
клиента; он не является rate limit или обещанием свежести API.

## Список Reels и пагинация — статически восстановлено

```python
page = client.account_reels(
    first=10, after=None, timeframe="ONE_MONTH",
    order_by="BY_VIEWS", sort_direction="DESCENDING",
)
raw_page = page.payload
```

Восстановлены переменные запроса, но точный wire-путь списка/cursor живым ответом
не подтверждён. SDK возвращает raw page и **не выдумывает** `.items`/`.next_cursor`.
Сначала проверьте свою страницу ответа, затем передавайте фактически полученный
cursor в `after`. Автоматической загрузки всех страниц нет.

## Пакетное обновление — статически восстановлено

```python
response = client.reels_delta(["NUMERIC_MEDIA_ID_1", "NUMERIC_MEDIA_ID_2"])
raw = response.payload
```

Неизвестные серверные пределы пакета не подменяются числом из предположения.
Для начала используйте небольшой явно выбранный список и проверяйте ответ.

## Аналитика аккаунта, аудитории и комментариев

```python
account = client.account_insights(period=known_period, include_time_series=True)
audience = client.audience_insights(period=known_period, client_timezone="Europe/Moscow")
comments = client.comment_insights(reel_url, sort_order=known_sort_order)
```

`known_period` и `known_sort_order` должны происходить из подтверждённого вами
контракта текущего клиента. Их допустимые enum здесь не восстановлены. Примеры
показывают API библиотеки, а не обещают, что произвольная строка будет принята сервером.

## Ошибки, лимиты и фоновые задачи

Библиотека синхронная. В async web-приложении выполняйте вызов в worker/thread,
не блокируя event loop. Timeout задаётся конструктором. Для каждого аккаунта
используйте его собственную сессию; не помещайте несколько сессий в глобальный
одиночный клиент.

Автоматических retries нет. HTTP 429 или challenge — сигнал остановить задания
аккаунта и разбирать причину, а не менять host, IP или sessionid в цикле.
Если добавляете повтор чтения после временной сетевой ошибки, ограничивайте
число попыток и учитывайте возможные дубликаты snapshots.

## Изменяющие операции

По умолчанию `execute()` принимает только записи каталога с типом `query`.
Для найденной mutation нужен **явный флаг на конкретном вызове**:

```python
# Пример интерфейса, НЕ часть автоматического сбора статистики.
# Параметры mutation требуется предварительно проверить.
response = client.execute(operation_name, validated_input, allow_mutation=True)
```

В текущем проекте ни одна mutation не запускалась на реальном аккаунте.
Не используйте их как часть health-check, примеров, CI или автоматической диагностики.
