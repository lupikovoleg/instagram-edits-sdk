# Удержание и статистика одного Reel

```python
from edits_api import EditsClient, EditsError

client = EditsClient.from_env()
try:
    reel = client.reel_insights("https://www.instagram.com/reel/YOUR_SHORTCODE/")
except EditsError as exc:
    # Текст исключения не содержит Authorization; исходный секрет не логировать.
    raise RuntimeError(f"Instagram insights unavailable: {exc}") from exc

records = [
    {"position": point.index, "fraction": point.value, "percent": point.percent}
    for point in reel.retention
]
```

## Данные для вашего графика

- `index` — исходная целочисленная позиция. UI Edits трактует сетку как время,
  с концом оси `число точек − 1` секунд. Не превращайте произвольные индексы в
  секунды без проверки сетки.
- `value` — исходная доля: `1.0` соответствует 100%.
- `percent` — вычисленное `value × 100`, либо `None`.

Порядок точек сохранён. Нет сглаживания, интерполяции, сортировки или обрезки
значений выше 100%. Если индексы не идут от 0 подряд, появляется предупреждение
в `reel.metadata["warnings"]`. Числа можно отдавать собственному фронтенду,
не передавая туда сессию Instagram.

## Метрики того же ответа

```python
play_count = reel.metrics.get("play_count")
likes = reel.metrics.get("like_count")
skip = reel.metrics.get("skip_rate")
skip_fraction = skip.get("value") if isinstance(skip, dict) else None
```

В живом ответе были `play_count`, `like_count`, `comment_count`, `repost_count`,
`save_count`, `reshare_count`, `skip_rate`, `average_watch_time`, `reach_count`,
`viewer_count`, `views_over_time` и другие поля. Доступность конкретной метрики
не гарантируется для каждого ролика. `None`, отсутствие поля и ноль различаются.

У metric-объектов SDK нормализует подтверждённые `1fvalue` → `value` и
`1fdelta` → `delta`. Остальные поля остаются исходными. `average_watch_time`
не конвертируется автоматически: единицы требуют отдельной проверки контракта.
`views_over_time` также остаётся исходной вложенной структурой.

## Экспорт

```python
reel.export("results/reel-123")
```

Создаются `insights.json`, `retention.csv`, `retention.svg`, `response.json` и
`manifest.json`. На POSIX файлы создаются с правами 0600, новый каталог — 0700;
на Windows эти биты не заменяют ACL. Существующий каталог не перезаписывается.

`response.json` может содержать другие приватные метрики и URL медиа; по умолчанию
экспорт вообще не выполняется. Для сервиса используйте `to_dict()` и сохраняйте
только нужные поля. Никогда не принимайте файл manifest за подтверждение будущего
успеха: он описывает конкретный выполненный запрос.

## Не смешивать разные показатели

`skip_rate` — отдельная метрика, не весь график. `ReelInsightsQuery` — другая ветка
общего Instagram-кода, с `retention_curve`, `timestamp_seconds` и `percentage`.
Её шкала и доступность живым ответом здесь не проверены. Не переносите на неё
множитель 100 автоматически.
