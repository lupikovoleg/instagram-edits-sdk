# Какие данные получить и как читать ответ

Далее описан фактически наблюдавшийся ответ от 18 октября 2026. Наличие данных
зависит от аккаунта, ролика, периода и доступа к аналитике. Примеры требуют уже
созданный `client = EditsClient.from_env()` и свою ссылку `reel_url`.

`QueryResult.get_data(*fields)` начинает с `payload["data"]`, разрешает имена
вида `1$xig_fetch_media(id:$media_id)` и числовые `1fvalue`. Возвращает исходное
значение без пересчёта единиц. Отсутствующий/неоднозначный путь — ошибка; явно
вернувшийся `null` — `None`. Для анализа новых полей есть `response.payload`.

## 1. Подробная статистика и удержание — BaselReelDetailsQuery

```python
reel = client.reel_insights(reel_url)
plays = reel.metrics.get("play_count")
skip = reel.metrics.get("skip_rate")
skip_value = skip.get("value") if isinstance(skip, dict) else None
retention = [{"index": p.index, "percent": p.percent} for p in reel.retention] \
    if reel.retention_available else None
```

Наблюдались:

| Поля | Содержимое |
|---|---|
| `play_count`, `like_count`, `comment_count`, `repost_count`, `save_count`, `reshare_count` | Счётчики воспроизведений и взаимодействий |
| `skip_rate`, `reshares_rate`, `likes_rate`, `comments_rate`, `reposts_rate`, `saves_rate` | Объекты метрик: value, delta, type, subtitle, delta_trend в зависимости от поля |
| `average_watch_time` | Среднее время просмотра; SDK оставляет единицы ответа, не объявляет их секундами |
| `follow_count_from_media`, `reach_count`, `viewer_count` | Объекты количества подписок, охвата и зрителей |
| `views_over_time` | Временные ряды просмотров в исходной вложенной структуре |
| `content_view_source_breakdown`, `viewer_distribution`, `top_ten_badge` | Источники просмотров, распределение зрителей, дополнительный бейдж |
| `reels_retentions` | Массив удержания; SDK отдельно возвращает `reel.retention` |

`metrics` нормализует верхний уровень metric-объектов `1fvalue/1fdelta` в
`value/delta`. Вложенные структуры сохраняются. Доля удержания 1 = 100%; `None`
не равен нулю. Отсутствующий график не уничтожает статистику. [Подробнее](retention.md).

## 2. Сокращённая статистика — BaselPublicInsightsQuery

```python
response = client.public_insights(reel_url)
metrics = response.get_data("xig_fetch_media", "basel_media_public_insights")
```

Вернулись счётчики и коэффициенты взаимодействий. Графика удержания в этом блоке
нет. Слово Public в имени не означает работу без авторизации или подтверждённый
доступ к чужим роликам: проверка выполнена только на собственном Reel.

## 3. Список Reels — BaselAccountLevelReelsQuery

```python
page = client.reels_page(first=3, timeframe="LIFETIME", order_by="BY_DATE",
                         sort_direction="DESCENDING")
for reel in page.items:
    reel_id = reel["id"]
    metrics = reel.get("basel_media_level_insights")
if page.has_next_page:
    next_page = client.reels_page(first=3, after=page.next_cursor)
```

Путь: `xig_user_by_igid_v2 → basel_insights → user_reel_dicts → edges[].node`.
Узлы содержали id, permalink, taken_at, caption, image_versions2, clips_metadata,
is_promoted, is_active_trial, coauthor_producers и basel_media_level_insights.
Пагинация — `page_info.has_next_page/end_cursor`. Проверены две страницы по три
ролика без пересечений. `account_reels()` возвращает тот же ответ без разбора страницы.

Значения из APK:

- timeframe: `LIFETIME`, `ONE_WEEK`, `TWO_WEEKS`, `ONE_MONTH`, `ONE_YEAR`.
- order_by: `BY_DATE`, `BY_VIEWS`, `BY_LIKES`, `BY_COMMENTS`, `BY_REPOSTS`,
  `BY_SHARES`, `BY_SAVES`, `BY_FOLLOWERS`, `BY_SKIP_RATE`.
- sort_direction: `ASCENDING`, `DESCENDING`, `None`.

Живой тест: `LIFETIME/BY_DATE/DESCENDING`, `skip_follow_count=False`. Остальные
комбинации восстановлены статически, а не проверены перебором.

## 4. Аналитика аккаунта — BaselAccountLevelInsightsQuery

```python
response = client.account_insights(period="LAST_30_DAYS", include_time_series=True)
metrics = response.get_data("xig_user_by_igid_v2", "basel_insights")
views = response.get_data("xig_user_by_igid_v2", "basel_insights", "reels_views")
views_value = response.get_data("xig_user_by_igid_v2", "basel_insights", "reels_views", "value")
```

Наблюдались reels_views, total_reach, followers_net_growth, like_count,
comment_count, repost_count, reshare_count, save_count, viewer_count. Объекты
метрик содержат значение, изменение и `time_series` при запрошенной серии.
Доступны флаги has_access_to_audience_insights, has_access_to_demographic_insights;
can_see_organic_insights находится в узле пользователя.

Периоды: `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `LAST_60_DAYS`,
`LAST_90_DAYS`, `LAST_180_DAYS`. Проверен `LAST_30_DAYS`, остальные найдены в APK.

## 5. Аудитория — BaselAudienceInsightsQuery

```python
response = client.audience_insights(period="LAST_30_DAYS", client_timezone="Europe/Moscow")
metrics = response.get_data("xig_user_by_igid_v2", "basel_insights")
ages = response.get_data("xig_user_by_igid_v2", "basel_insights", "audience_age_distribution")
countries = response.get_data("xig_user_by_igid_v2", "basel_insights",
                             'audience_top_locations(breakdown_type:"COUNTRY")')
```

Наблюдались семь возрастных групп, пять стран, пять городов, две группы пола,
общее число подписчиков, прирост/подписки/отписки с временными рядами, наиболее
активное время подписчиков. popular_topics_preview был пуст. Эти количества —
размеры ответа конкретной проверки, не ограничения API. Периоды как выше.

## 6. Обновление метрик по ID — XIGBaselAccountLevelReelsDataDeltaQuery

```python
response = client.reels_delta(["NUMERIC_MEDIA_ID"])
items = response.get_data("xig_basel_multi_media_insights_query")
```

Ответ — список узлов `id/basel_media_level_insights`: media_id, счётчики
просмотров/комментариев/лайков/репостов/отправок/сохранений,
follow_count_from_media(should_include_delta:false), top_ten_badge.
В реальном запросе был один ID. Размер пакета и многоэлементный ответ не проверены.

## 7. Комментарии — XIGBaselInsightsCommentsQuery

```python
response = client.comment_insights(reel_url, sort_order="recent")
analysis = response.get_data("xig_fetch_media", "ai_comment_insights")
if analysis is None:
    # Функция недоступна или данных нет; это не список из нуля комментариев.
    pass
```

sort_order из APK: `recent`, `popular`. Проверен `recent`, HTTP 200,
`ai_comment_insights=null`. Структура заполненного анализа живым ответом не проверена.

## 8. Kits — BaselKitsQuery

```python
response = client.kits(after=None)
connection = response.get_data("xig_basel_kits", "kits")
edges = connection["edges"]
page_info = connection["page_info"]
```

В запросе скрытый в persisted query `first:50`; SDK меняет только `after`.
Проверено: HTTP 200, edges=[], has_next_page=false. Заполненные элементы и следующая
страница Kits не проверены. Никакие Kits не создавались ради теста.

## 9. Альтернативная аналитика — ReelInsightsQuery

```python
response = client.extended_reel_insights(
    reel_url,
    bloks_versioning_id="8dc50e9193c9b70a3f9dbcc25fc5f444bbac27bb56a8c1359ede836b8069c4b8",
)
insights = response.get_data("ig_reel_insights")
curve = insights["retention"]["retention_curve"]
```

Реальный ответ был NDJSON. SDK собирает его в payload. В кривой используются
`timestamp_seconds` и `1fpercentage`; здесь 1 соответствует 100%. Демография
также содержит percentage, но у стран наблюдались уже проценты, а не доли.
**Нельзя умножать все percentage в ответе на 100.**

bloksVersioningId найден в APK и передаётся явно: версия может измениться.
Кривая этой ветки и BaselReelDetailsQuery может отличаться; нельзя подменять одну
другой без учёта этого различия. Связь именно этой ветки с UI Edits не доказана.
[Готовый скрипт](../examples/extended_insights.py).

## Полный каталог

[Методы](methods.md) содержат ID, variables и источники. 15 контрактов подробно
разобраны, но только девять операций чтения имеют живую проверку. Оставшиеся
операции и mutations — статические находки. [Область доказательств](verification.md).
