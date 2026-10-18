# Интеграция в свой сервис

## Запрос → ваш формат → хранение

```python
from edits_api import EditsClient

def collect(client: EditsClient, reel_url: str):
    reel = client.reel_insights(reel_url)
    return {
        "media_id": reel.media_id,
        "collected_at": reel.response.fetched_at,
        "metrics": reel.metrics,
        "retention_available": reel.retention_available,
        "retention": [{"index": p.index, "value": p.value} for p in reel.retention]
                     if reel.retention_available else None,
        "warnings": reel.metadata["warnings"],
        "owner_verified": reel.metadata["owner_verified"],
    }
```

Сохраняйте snapshots с timestamp. Отсутствие удержания — допустимый результат,
отказ HTTP или GraphQL — ошибка. Для графика не заменяйте `None` нулями.
Кэш 120 секунд найден в Android-клиенте; это не серверный rate limit и не обещание свежести.

## Пагинация

```python
client = EditsClient.from_env()
page = client.reels_page(first=3, timeframe="LIFETIME", order_by="BY_DATE")
items = list(page.items)
if page.has_next_page:
    next_page = client.reels_page(first=3, after=page.next_cursor,
                                  timeframe="LIFETIME", order_by="BY_DATE")
    items.extend(next_page.items)
```

Каждый вызов делает один запрос. SDK не загружает все страницы автоматически.
Проверены две последовательные страницы по три ролика: cursor принят, пересечений
ID не было. При переходе сохраняйте фильтры и сортировку. Предел размера страницы
не установлен. Не используйте ID последнего ролика вместо фактического `end_cursor`.

## Аккаунт и аудитория

```python
account = client.account_insights(period="LAST_30_DAYS", include_time_series=True)
metrics = account.get_data("xig_user_by_igid_v2", "basel_insights")
audience = client.audience_insights(period="LAST_30_DAYS", client_timezone="Europe/Moscow")
demographics = audience.get_data("xig_user_by_igid_v2", "basel_insights")
```

Периоды из APK: `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `LAST_60_DAYS`,
`LAST_90_DAYS`, `LAST_180_DAYS`. Живым запросом проверен `LAST_30_DAYS`.
Наличие аудитории зависит от аккаунта. [Состав данных](data-reference.md).

## Пакетное обновление

```python
response = client.reels_delta(["NUMERIC_MEDIA_ID_1", "NUMERIC_MEDIA_ID_2"])
items = response.get_data("xig_basel_multi_media_insights_query")
```

Серверный размер пакета неизвестен. Живой проверкой подтверждён один ID;
многозначный payload поддержан по контракту APK, но отдельно не проверялся.

## Ошибки и фоновые задачи

Клиент синхронный: в async-приложении выполняйте вызов в worker/thread. У каждого
аккаунта своя сессия. Не отправляйте сессию в браузерный frontend. SDK не пишет
HTTP-заголовки в логи, однако ваше middleware тоже должно скрывать секреты.

Нет автоматических retries. На HTTP 429, истёкшую сессию или challenge остановите
задания аккаунта и разберите причину. При собственных повторах временных сетевых
ошибок ограничивайте число попыток. Таймаут по умолчанию 30 секунд.

## Другие операции

`execute(name, variables)` принимает описанную в реестре операцию схемы `instagram`.
Изменяющие вызовы требуют `allow_mutation=True`; ни одна mutation в этом проекте
на сервере не запускалась. Они не входят в health-check или примеры сбора статистики.
