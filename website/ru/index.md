---
title: Instagram Edits SDK
hide:
  - navigation
  - toc
---

<div class="hero">
<div class="hero-copy">
<p class="eyebrow">INSTAGRAM EDITS SDK · PYTHON</p>
<h1>От одного Reel<br>к <span class="gradient-text">понятным данным.</span></h1>
<p class="hero-lede">Статистика Reels, аудитория и удержание в ваших системах. Компактный Python SDK с исследованием за каждым методом.</p>
<div class="hero-actions"><a class="md-button md-button--primary" href="quickstart/">Начать</a><a class="md-button" href="retention/">Получить удержание <span aria-hidden="true">↗</span></a></div>
<p class="hero-note">Неофициальный · Python 3.10+ · Без зависимостей</p>
<p class="hero-author">Автор проекта — <a href="https://github.com/lupikovoleg/instagram-edits-sdk">Олег Лупиков</a></p>
</div>
<div class="hero-code">
<div class="code-caption"><span class="status-dot"></span> REEL В НЕСКОЛЬКО СТРОК <span>PYTHON</span></div>
<pre><code><span class="syntax-muted">from</span> edits_api <span class="syntax-muted">import</span> EditsClient

client = EditsClient.from_env()
reel = client.reel_insights(reel_url)

<span class="syntax-muted">print</span>(reel.metrics[<span class="syntax-string">"play_count"</span>])

<span class="syntax-muted">if</span> reel.retention_available:
    <span class="syntax-muted">for</span> point <span class="syntax-muted">in</span> reel.retention:
        <span class="syntax-muted">print</span>(point.index, point.percent)</code></pre>
<div class="code-footer">Ваш аккаунт. Ваши данные. Ваш backend.</div>
</div>
</div>

<div class="proof-strip"><div><strong>9</strong><span>запросов проверены на сервере</span></div><div><strong>15</strong><span>подробно описанных контрактов</span></div><div><strong>45</strong><span>тестов прошёл пакет из PyPI</span></div></div>

## Начните со своей задачи

<div class="guide-grid">
<a class="guide-card" href="quickstart/"><span class="card-number">01 / CONNECT</span><h3>Получите первую статистику</h3><p>Установите SDK, передайте сессию и получите данные своего ролика.</p><span class="card-link">Быстрый старт →</span></a>
<a class="guide-card" href="retention/"><span class="card-number">02 / UNDERSTAND</span><h3>Изучите удержание зрителей</h3><p>Получите числовую кривую, сохраните пропуски и экспортируйте результат.</p><span class="card-link">График удержания →</span></a>
<a class="guide-card" href="data-reference/"><span class="card-number">03 / EXPLORE</span><h3>Посмотрите другие метрики</h3><p>Просмотры, взаимодействия, динамика аккаунта, аудитория и список Reels.</p><span class="card-link">Справочник данных →</span></a>
</div>

## Уровень проверки — часть документации

Семь из девяти проверенных операций вернули данные. Анализ комментариев вернул
`null`, Kits — пустой список. Эти результаты отделены от подтверждения заполненной
функции. Живые проверки выполнены на одном аккаунте с разрешения владельца
**18 октября 2026 года**.

<div class="evidence-note"><strong>Внутренние методы могут измениться.</strong> Проект не связан с Meta. Наличие метода в APK не доказывает его поддержку или доступность. У каждого контракта указан уровень проверки.</div>

[Что проверено](verification.md){ .text-link } · [Каталог методов](methods.md){ .text-link } · [Открыть Swagger](swagger-ui/index.html){ .text-link }
