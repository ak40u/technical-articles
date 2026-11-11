#!/usr/bin/env python3
"""Render the hero OG images for the ai-sre-engineer article.

Reuses the hero layout CSS from generate_og_images.py so every article card
shares one visual language; only the right-hand card is article-specific:
the six layers of the monitoring and response loop, and three figures from
the article.
"""
from generate_og_images import OUTPUT_DIR, RU_HTML, render_image

BASE_CSS = RU_HTML[RU_HTML.index("<style>") + len("<style>"):RU_HTML.index("</style>")]

EXTRA_CSS = """
  .layers { display: flex; flex-direction: column; gap: 14px; flex: 1; justify-content: center; }
  .layer { display: flex; align-items: center; gap: 16px; padding: 12px 18px;
           border: 1px solid #1e293b; border-radius: 12px; background: rgba(15, 23, 42, 0.6); }
  .num { font-family: ui-monospace, monospace; font-size: 16px; color: #64748b; width: 18px; }
  .dot { width: 12px; height: 12px; border-radius: 6px; flex: none; }
  .name { font-size: 22px; font-weight: 700; color: #f8fafc; }
  .note { font-size: 15px; color: #94a3b8; margin-left: auto; }
"""

COLORS = ["#38bdf8", "#a78bfa", "#4ade80", "#fbbf24", "#f87171", "#2dd4bf"]

TEXT = {
    "ru": {
        "lang": "ru",
        "eyebrow": "FindRates · ИИ-мониторинг и реагирование",
        "h1": 'Когда метрики зелёные, а сделка сорвана: <span class="highlight">архитектура ИИ-дежурства</span>',
        "desc": "Шесть слоёв от сбора сигналов до разбора сбоев. Модель судит о смысле, код держит инварианты, граница автономии проходит по обратимости.",
        "author": "Павел Волков",
        "card": "Контур мониторинга и реагирования",
        "badge": "6 слоёв",
        "layers": [
            ("Сбор сигналов", "логи, база, чаты"),
            ("Первичная оценка", "шум отсекается"),
            ("Расследование", "только чтение"),
            ("Маршрутизация", "кому закрыть"),
            ("Сдерживание", "обратимые шаги"),
            ("Разбор", "новый инвариант"),
        ],
        "metrics": [("$7,65", "смена в сутки"), ("7 мин", "до сдерживания"), ("0", "путей записи в прод")],
    },
    "en": {
        "lang": "en",
        "eyebrow": "FindRates · AI monitoring and response",
        "h1": 'When metrics are green and the deal falls through: <span class="highlight">AI on-call architecture</span>',
        "desc": "Six layers from signal collection to post-incident review. The model judges meaning, code holds the invariants, autonomy ends where reversibility does.",
        "author": "Pavel Volkov",
        "card": "Monitoring and response loop",
        "badge": "6 layers",
        "layers": [
            ("Signal collection", "logs, DB, chats"),
            ("Initial assessment", "noise dropped"),
            ("Investigation", "read only"),
            ("Routing", "who closes it"),
            ("Containment", "reversible steps"),
            ("Review", "a new invariant"),
        ],
        "metrics": [("$7.65", "shift per day"), ("7 min", "to containment"), ("0", "write paths to prod")],
    },
}


def build_html(t: dict) -> str:
    """Assemble the hero page for one language."""
    layers = "".join(
        f'<div class="layer"><span class="num">{i + 1}</span>'
        f'<span class="dot" style="background:{COLORS[i]}"></span>'
        f'<span class="name">{name}</span><span class="note">{note}</span></div>'
        for i, (name, note) in enumerate(t["layers"])
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
    <div class="layers">{layers}</div>
    <div class="metrics-row">{metrics}</div>
  </div></div>
</body></html>"""


def main() -> None:
    """Render the Russian and English hero images."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    render_image(build_html(TEXT["ru"]), OUTPUT_DIR / "ai-sre-engineer-hero.png")
    render_image(build_html(TEXT["en"]), OUTPUT_DIR / "ai-sre-engineer-hero-en.png")


if __name__ == "__main__":
    main()
