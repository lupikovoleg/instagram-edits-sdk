# Первая статистика Reel

## 1. Установите SDK

```bash
python -m pip install instagram-edits-sdk
```

Python **3.10+**. Импорт — `edits_api`, консольная команда — `edits-api`.
Текущая версия — **0.2.2**. Зависимостей во время работы нет.

## 2. Передайте сессию

Передайте `IG_SESSIONID` в окружение backend через свой менеджер секретов.
Нужна существующая сессия Instagram владельца ролика. SDK не выполняет вход,
не извлекает cookie и не обновляет сессию. [Инструкция авторизации](authentication.md).

## 3. Получите данные

```python
from edits_api import EditsClient

client = EditsClient.from_env()
reel = client.reel_insights("https://www.instagram.com/reel/YOUR_SHORTCODE/")

print(reel.metrics.get("play_count"))
print(reel.metrics.get("like_count"))
print(reel.retention_available)
```

## Сохраните результат

```python
snapshot = reel.to_dict()
if reel.retention_available:
    points = [{"index": p.index, "percent": p.percent} for p in reel.retention]
else:
    points = None

reel.export("results/my-reel")
```

JSON сохраняется всегда, CSV/SVG — при наличии удержания. Каталог должен быть новым.
`None` не подменяется нулём. [Удержание](retention.md) · [Все данные](data-reference.md) · [Скрипты](examples.md).
