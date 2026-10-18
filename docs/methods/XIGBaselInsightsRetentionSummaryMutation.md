# XIGBaselInsightsRetentionSummaryMutation

Генерация текстового разбора удержания и hook analysis. Это отдельный вызов, не массив точек графика.

- **client_doc_id:** `26704303781083176767119591657`
- **schema:** `instagram`
- **kind:** `mutation`
- **evidence:** `static-contract`

**На сервере не проверено.** Параметры восстановлены из APK; ниже нет гарантии актуальной доступности этому аккаунту.

## Variables

| Поле | Восстановленный контракт |
|---|---|
| `input` | object с media_id:string |

## Ответ

xig_retention_summary: success, summary, start_time, end_time, hook_analysis.summary или error.error_code/error_message

## Изменение состояния

Операция не входит в автоматический сбор статистики. `execute()` блокирует её без `allow_mutation=True`. Для частично восстановленных input нет готового payload: поля нельзя угадывать по названию метода.

## Источники статического разбора

Пути ниже относятся к исходному исследовательскому набору. Декомпилированные исходники в этот репозиторий не включены.

- `analysis/RetentionSource.java:85`
