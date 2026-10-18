# Авторизация для backend

## Что принимает клиент

1. Cookie `sessionid` существующей сессии Instagram владельца Reel.
2. Готовый заголовок `Authorization: Bearer IGT:2:…` мобильного клиента.
3. Сохранённые настройки instagrapi с `authorization_data`, `cookies`, `user_agent` и `uuids`.

OAuth access token публичного Instagram Graph API не является такой сессией.
SDK не реализует регистрацию OAuth-приложения, вход с паролем, обновление сессии,
двухфакторную проверку или автоматическое извлечение cookie из браузера.

## Через менеджер секретов

Предпочтительный способ для сервиса: получить секрет из своего хранилища и создать
сессию непосредственно в памяти:

```python
from edits_api import EditsClient, Session

# Функция вашего проекта, а не API этой библиотеки:
sessionid = secret_store.get("instagram/sessionid")
client = EditsClient(Session.from_sessionid(sessionid))
insights = client.reel_insights(reel_url)
```

Для окружения процесса поддерживается **ровно одна** переменная:
`IG_SESSIONID` или `IG_AUTHORIZATION`. Дополнительно можно передать `IG_APP_ID`
и `IG_USER_AGENT`. Файлы `.env` автоматически не читаются.

```python
client = EditsClient.from_env()
```

Не передавайте sessionid аргументом CLI, в URL вашего публичного сервиса или в
браузерный JavaScript. Подключение клиента должно происходить на сервере.
Не логируйте объект со всеми переменными окружения.

## Формат IGT:2

Для cookie SDK строит заголовок:

```text
Authorization: Bearer IGT:2:<base64(JSON)>
```

Содержимое JSON:

```json
{
  "ds_user_id": "ACCOUNT_ID",
  "sessionid": "SESSION_COOKIE",
  "should_use_header_over_cookies": true
}
```

Если `user_id` не задан, он извлекается из числового префикса sessionid.
Можно задать явно: `Session.from_sessionid(secret, user_id="ACCOUNT_ID")`.
Суффикс составного media ID в ответе сверяется с этим ID. Если владельца в ответе
нет, библиотека возвращает `owner_verified=False`, а не выдумывает подтверждение.

## Профиль клиента

Для `from_sessionid()` и `from_authorization()` по умолчанию используются:

```text
User-Agent: Instagram 1.0 Android
X-IG-App-ID: 954255173121948
```

Это fallback-профиль, найденный в исследованном Edits APK. Именно с ним исходный
клиент получил реальный ответ. Это не User-Agent браузера и не гарантия приёма
сессий любого аккаунта. Используйте фактические заголовки своего клиента, когда они доступны:

```python
session = Session.from_sessionid(secret, user_agent=actual_user_agent, app_id=actual_app_id)
```

Устройства, идентификаторы и cookies не генерируются случайно. При загрузке
instagrapi settings сохраняются переданные идентификаторы. Если его settings не
содержат app_id, для распознанного формата используется default instagrapi
`567067343352427`; приём именно такого профиля этим методом отдельно не проверен.

## Сессионный файл и stdin

```python
from pathlib import Path
session = Session.from_settings(Path("private/settings.json"))
```

Минимальный формат файла:

```json
{
  "cookies": {"sessionid": "YOUR_SESSION_COOKIE"},
  "user_agent": "Instagram 1.0 Android",
  "app_id": "954255173121948"
}
```

Это шаблон, не рабочий секрет. Также поддерживается `headers.Authorization`.
Для CLI `--session -` читает такой JSON из stdin. Не отправляйте файл в Git.

## Получение собственной сессии для локальной разработки

После входа в свой аккаунт значение sessionid можно прочитать в инструментах
браузера. Chrome: Application → Storage → Cookies → Instagram.
Safari: Хранилище → Файлы cookie → Instagram. Не публикуйте HAR или снимок этой
таблицы. Для backend с несколькими клиентами нужны их явно предоставленные
сессии; общий sessionid разработчика не даёт доступ к чужой статистике.

Источники: [формат авторизации instagrapi](https://github.com/subzeroid/instagrapi/blob/master/instagrapi/mixins/auth.py),
[Chrome DevTools cookies](https://developer.chrome.com/docs/devtools/application/cookies).
