# Готовые примеры

Установите SDK и передайте сессию по [инструкции](authentication.md).
Скачайте скрипт или клонируйте репозиторий. Для вывода используйте новый файл или каталог.

| Скрипт | Назначение |
|---|---|
| [retention.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/retention.py) | Получить удержание и сохранить JSON, CSV, SVG |
| [reel_statistics.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/reel_statistics.py) | Статистика даже без графика удержания |
| [list_reels.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/list_reels.py) | Одна страница Reels |
| [account_statistics.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/account_statistics.py) | Аккаунт или аудитория |
| [read_operation.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/read_operation.py) | Public, delta, комментарии или Kits |
| [extended_insights.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/extended_insights.py) | Альтернативная ветка аналитики |
| [batch_retention.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/batch_retention.py) | Ограниченный список своих Reels |
| [offline_demo.py](https://github.com/lupikovoleg/instagram-edits-sdk/blob/main/examples/offline_demo.py) | Синтетическая демонстрация без сети |

```bash
python examples/retention.py "https://www.instagram.com/reel/YOUR_SHORTCODE/" --output results/curve
python examples/list_reels.py --first 3 --output results/page.json
python examples/account_statistics.py --period LAST_30_DAYS --output results/account.json
```

Примеры не выполняют вход в аккаунт и не обновляют сессию. Ошибка останавливает
выполнение; автоматического перебора сессий или бесконечных повторов нет.
