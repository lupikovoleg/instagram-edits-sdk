---
title: Instagram Edits SDK
hide:
  - navigation
  - toc
---

<div class="hero">
<div class="hero-copy">
<p class="eyebrow">INSTAGRAM EDITS SDK · PYTHON</p>
<h1>From a Reel<br>to a <span class="gradient-text">clearer picture.</span></h1>
<p class="hero-lede">Bring Reel statistics, audience insights and retention curves into your own tools. A small Python SDK, with the research behind every method.</p>
<div class="hero-actions"><a class="md-button md-button--primary" href="quickstart/">Get started</a><a class="md-button" href="retention/">Get a retention curve <span aria-hidden="true">↗</span></a></div>
<p class="hero-note">Unofficial · Python 3.10+ · No runtime dependencies</p>
<p class="hero-author">Built by <a href="https://github.com/lupikovoleg/instagram-edits-sdk">Oleg Lupikov</a></p>
</div>
<div class="hero-code">
<div class="code-caption"><span class="status-dot"></span> A REEL, IN A FEW LINES <span>PYTHON</span></div>
<pre><code><span class="syntax-muted">from</span> edits_api <span class="syntax-muted">import</span> EditsClient

client = EditsClient.from_env()
reel = client.reel_insights(reel_url)

<span class="syntax-muted">print</span>(reel.metrics[<span class="syntax-string">"play_count"</span>])

<span class="syntax-muted">if</span> reel.retention_available:
    <span class="syntax-muted">for</span> point <span class="syntax-muted">in</span> reel.retention:
        <span class="syntax-muted">print</span>(point.index, point.percent)</code></pre>
<div class="code-footer">Your account. Your data. Your backend.</div>
</div>
</div>

<div class="proof-strip"><div><strong>9</strong><span>read operations exercised live</span></div><div><strong>15</strong><span>documented operation contracts</span></div><div><strong>45</strong><span>tests passed for the PyPI wheel</span></div></div>

## Start with the question you have

<div class="guide-grid">
<a class="guide-card" href="quickstart/"><span class="card-number">01 / CONNECT</span><h3>Get your first statistics</h3><p>Install the package, provide your session, and read an owned Reel.</p><span class="card-link">Quickstart →</span></a>
<a class="guide-card" href="retention/"><span class="card-number">02 / UNDERSTAND</span><h3>Find where viewers leave</h3><p>Get the numerical curve, preserve gaps, and export the result.</p><span class="card-link">Retention guide →</span></a>
<a class="guide-card" href="data-reference/"><span class="card-number">03 / EXPLORE</span><h3>Go beyond retention</h3><p>Views, engagement, account trends, audience data and paginated Reels.</p><span class="card-link">Data reference →</span></a>
</div>

## Evidence is part of the API

Seven of the nine tested read operations returned data. Comment analysis returned
`null`; Kits returned an empty list. The documentation keeps those results distinct
from a working, populated feature. All live checks were on one consenting account
on **18 October 2026**.

<div class="evidence-note"><strong>Internal endpoints can change.</strong> This project is independent of Meta. A method found in an APK is not automatically a supported or available API. Every contract includes its evidence level.</div>

[See what was verified](verification.md){ .text-link } · [Browse the operation catalog](methods.md){ .text-link } · [Open Swagger](swagger-ui/index.html){ .text-link }
