# Публикация в PyPI

Пакет: `instagram-edits-sdk`. Импорт: `edits_api`. Публикацию может выполнять
владелец PyPI-проекта или настроенный им Trusted Publisher.

## Первая публикация

Нужен аккаунт на [PyPI](https://pypi.org/account/register/) с подтверждённой почтой
и настроенной двухфакторной защитой. Пароль, коды восстановления и сессия аккаунта
не должны попадать в репозиторий, Actions secrets или переписку.

На [странице Publishing](https://pypi.org/manage/account/publishing/) владельца
добавляется pending publisher:

| Поле | Значение |
|---|---|
| PyPI project name | `instagram-edits-sdk` |
| Owner | `lupikovoleg` |
| Repository name | `instagram-edits-sdk` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

Это разрешает workflow этого репозитория публиковать данный PyPI-проект.
Настройку должен подтвердить владелец аккаунта. Постоянный PyPI API token не нужен.
Pending publisher не резервирует имя проекта: оно закрепляется при успешной загрузке.

После настройки и проверки исходников создаётся тег, совпадающий с версией пакета:

```sh
git tag v0.2.2
git push origin v0.2.2
```

Тег запускает [publish.yml](../.github/workflows/publish.yml). Workflow проверяет
совпадение версии, запускает тесты, собирает sdist/wheel, проверяет метаданные Twine,
устанавливает именно wheel в чистое окружение и только затем публикует два файла.
OIDC-разрешение находится только у job публикации; постоянные токены не используются.

## Следующие версии

Обновите версию в `pyproject.toml`, `src/edits_api/__init__.py` и changelog,
перегенерируйте OpenAPI и обновите номер версии в Swagger. После проверки и push
создайте соответствующий тег. Не изменяйте уже опубликованный тег/версию:
загрузки в PyPI не предназначены для перезаписи содержимого той же версии.

Локальная проверка:

```sh
python -m unittest discover -s tests -v
python tools/check_release.py
python -m build --outdir dist/pypi-0.2.2
python -m twine check --strict dist/pypi-0.2.2/*
```

Загружайте только файлы выбранной версии, а не все старые артефакты из `dist`.

## Проверка после публикации

В новом окружении:

```sh
python -m venv /tmp/edits-pypi-check
/tmp/edits-pypi-check/bin/python -m pip install --index-url https://pypi.org/simple instagram-edits-sdk==0.2.2
/tmp/edits-pypi-check/bin/python -c 'from edits_api import EditsClient, Session; import importlib.metadata; print(importlib.metadata.version("instagram-edits-sdk"))'
/tmp/edits-pypi-check/bin/edits-api catalog
```

Официальные источники:
[создание проекта через Trusted Publishing](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/),
[публикация](https://docs.pypi.org/trusted-publishers/using-a-publisher/).
