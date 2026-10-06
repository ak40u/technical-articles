#!/usr/bin/env python3
"""Render the hero OG images for the openrouter-provider-routing article.

Reuses the hero layout CSS from generate_og_images.py so every article card
shares one visual language; only the right-hand card is article-specific.
"""
from generate_og_images import OUTPUT_DIR, RU_HTML, render_image

BASE_CSS = RU_HTML[RU_HTML.index("<style>") + len("<style>"):RU_HTML.index("</style>")]

EXTRA_CSS = """
  .rows { display: flex; flex-direction: column; gap: 40px; flex: 1; justify-content: center; }
  .row { display: flex; flex-direction: column; gap: 10px; }
  .row-head { display: flex; justify-content: space-between; align-items: baseline; }
  .row-name { font-size: 24px; font-weight: 700; color: #f8fafc; }
  .row-kind { font-family: ui-monospace, monospace; font-size: 15px; color: #64748b; margin-left: 12px; }
  .row-score { font-family: ui-monospace, monospace; font-size: 26px; font-weight: 800; color: #cbd5e1; }
  .bar { height: 16px; border-radius: 8px; background: #1e293b; overflow: hidden; }
  .fill { height: 100%; border-radius: 8px; background: #38bdf8; }
  .row.best .row-score { color: #4ade80; }
  .row.best .fill { background: #4ade80; }
  .row.fail .row-name, .row.fail .row-score { color: #f87171; }
  .row.fail .fill { background: #f87171; }
"""

# Mean actual cost per review, from the article's results table.
ROWS = [
    ("DeepInfra", 0.063, "fp8", "best"),
    ("auto", 0.107, "auto", ""),
    ("Fireworks", 0.193, "premium", ""),
    ("Open Inference", 0.561, "fp4", "fail"),
]
MAX_COST = max(cost for _, cost, _, _ in ROWS)

TEXT = {
    "ru": {
        "lang": "ru",
        "decimal": ",",
        "eyebrow": "OpenRouter · Бенчмарк провайдеров",
        "h1": 'Одна модель, 32 провайдера: маршрут OpenRouter надо <span class="highlight">проверять, закреплять и отслеживать</span>',
        "desc": "DeepSeek V4.1 Flash, шесть коммитов с известными дефектами, ревью кода через разных провайдеров. Цена различалась втрое при близком качестве.",
        "author": "Павел Волков",
        "card": "Средняя цена одного ревью",
        "badge": "одна модель",
        "kinds": {"auto": "выбор OpenRouter", "premium": "без метки"},
        "fail_suffix": " · тайм-аут",
        "metrics": [("32", "эндпоинта у модели"), ("−41%", "DeepInfra против auto"), ("0 из 4", "ревью у fp4 за 30 мин")],
    },
    "en": {
        "lang": "en",
        "decimal": ".",
        "eyebrow": "OpenRouter · Provider benchmark",
        "h1": 'One model, 32 endpoints: an OpenRouter route has to be <span class="highlight">tested, pinned and watched</span>',
        "desc": "DeepSeek V4.1 Flash, six commits with known defects, the same code review through different providers. The price differed threefold at similar quality.",
        "author": "Pavel Volkov",
        "card": "Mean cost per review",
        "badge": "same model",
        "kinds": {"auto": "OpenRouter's choice", "premium": "no label"},
        "fail_suffix": " · timed out",
        "metrics": [("32", "endpoints for one model"), ("−41%", "DeepInfra vs auto"), ("0 of 4", "fp4 reviews in 30 min")],
    },
}


def build_html(t: dict) -> str:
    """Assemble the hero page for one language."""
    rows = []
    for name, cost, kind, cls in ROWS:
        label = t["kinds"].get(kind, kind)
        price = f"${cost:.3f}".replace(".", t["decimal"])
        if cls == "fail":
            price += t["fail_suffix"]
        width = round(100 * cost / MAX_COST, 1)
        rows.append(
            f'<div class="row {cls}"><div class="row-head">'
            f'<span><span class="row-name">{name}</span><span class="row-kind">{label}</span></span>'
            f'<span class="row-score">{price}</span></div>'
            f'<div class="bar"><div class="fill" style="width:{width}%"></div></div></div>'
        )
    metrics = "".join(
        f'<div class="metric-item"><span class="metric-val">{v}</span><span class="metric-label">{l}</span></div>'
        for v, l in t["metrics"]
    )
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}"><head><meta charset="utf-8"><style>{BASE_CSS}{EXTRA_CSS}</style></head>
<body>
  <div class="glow-1"></div><div class="glow-2"></div>
  <div class="left-col">
    <div class="eyebrow">{t['eyebrow']}</div>
    <h1>{t['h1']}</h1>
    <p class="desc">{t['desc']}</p>
    <div class="meta-footer"><div class="avatar">PV</div><span>{t['author']}</span><span class="domain">pvolkov.com</span></div>
  </div>
  <div class="right-col"><div class="diagram-card">
    <div class="card-header"><span class="card-title">{t['card']}</span><span class="card-badge">{t['badge']}</span></div>
    <div class="rows">{''.join(rows)}</div>
    <div class="metrics-row">{metrics}</div>
  </div></div>
</body></html>"""


def main() -> None:
    """Render the Russian and English hero images."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    render_image(build_html(TEXT["ru"]), OUTPUT_DIR / "openrouter-provider-routing-hero.png")
    render_image(build_html(TEXT["en"]), OUTPUT_DIR / "openrouter-provider-routing-hero-en.png")


if __name__ == "__main__":
    main()
