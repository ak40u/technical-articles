#!/usr/bin/env python3
"""Render the hero OG images for the jev-classification article.

Reuses the hero layout CSS from generate_og_images.py so every article card
shares one visual language; only the right-hand card is article-specific.
"""
from generate_og_images import OUTPUT_DIR, RU_HTML, render_image

BASE_CSS = RU_HTML[RU_HTML.index("<style>") + len("<style>"):RU_HTML.index("</style>")]

EXTRA_CSS = """
  .rows { display: flex; flex-direction: column; gap: 44px; flex: 1; justify-content: center; }
  .row { display: flex; flex-direction: column; gap: 10px; }
  .row-head { display: flex; justify-content: space-between; align-items: baseline; }
  .row-name { font-size: 24px; font-weight: 700; color: #f8fafc; }
  .row-kind { font-family: ui-monospace, monospace; font-size: 15px; color: #64748b; margin-left: 12px; }
  .row-score { font-family: ui-monospace, monospace; font-size: 26px; font-weight: 800; color: #cbd5e1; }
  .bar { height: 16px; border-radius: 8px; background: #1e293b; overflow: hidden; }
  .fill { height: 100%; border-radius: 8px; background: #38bdf8; }
  .row.best .row-score { color: #4ade80; }
  .row.best .fill { background: #4ade80; }
  .row.jev .row-name, .row.jev .row-score { color: #f87171; }
  .row.jev .fill { background: #f87171; }
  .card-badge.red { background: rgba(248, 113, 113, 0.15); color: #f87171; border-color: rgba(248, 113, 113, 0.3); }
"""

ROWS = [
    ("DeepSeek V4.1 Flash", 47, "best"),
    ("GLM 5.3 Flash", 46, ""),
    ("Xiaomi MiMo v2.5", 46, ""),
    ("Jev 1.13", 45, "jev"),
]

TEXT = {
    "ru": {
        "lang": "ru",
        "eyebrow": "Держи лида · Бенчмарк моделей",
        "h1": 'Идеальная задача для Jev: модель для классификации <span class="highlight">проиграла универсальным LLM</span>',
        "desc": "47 реальных сообщений из Telegram-чатов, четыре модели, один набор правил. Специализированная модель решений оказалась последней и не дешевле.",
        "author": "Павел Волков",
        "card": "Классификация лидов · 47 тестов",
        "badge": "Jev — последний",
        "general": "универсальная",
        "decision": "модель решений",
        "metrics": [("$0.00032", "Jev за решение"), ("$0.00015", "DeepSeek за решение"), ("13%", "Jev: смена ответа при повторе")],
    },
    "en": {
        "lang": "en",
        "eyebrow": "Derzhi Lida · Model benchmark",
        "h1": 'The Perfect Task for Jev: a classification model <span class="highlight">lost to general-purpose LLMs</span>',
        "desc": "47 real messages from Telegram chats, four models, one rulebook. The specialized decision model came last and was not cheaper.",
        "author": "Pavel Volkov",
        "card": "Lead classification · 47 tests",
        "badge": "Jev came last",
        "general": "general-purpose",
        "decision": "decision model",
        "metrics": [("$0.00032", "Jev per decision"), ("$0.00015", "DeepSeek per decision"), ("13%", "Jev flips on identical retry")],
    },
}


def build_html(t: dict) -> str:
    """Assemble the hero page for one language."""
    rows = []
    for name, score, cls in ROWS:
        kind = t["decision"] if cls == "jev" else t["general"]
        width = round(100 * score / 47, 1)
        rows.append(
            f'<div class="row {cls}"><div class="row-head">'
            f'<span><span class="row-name">{name}</span><span class="row-kind">{kind}</span></span>'
            f'<span class="row-score">{score}/47</span></div>'
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
    <div class="card-header"><span class="card-title">{t['card']}</span><span class="card-badge red">{t['badge']}</span></div>
    <div class="rows">{''.join(rows)}</div>
    <div class="metrics-row">{metrics}</div>
  </div></div>
</body></html>"""


def main() -> None:
    """Render the Russian and English hero images."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    render_image(build_html(TEXT["ru"]), OUTPUT_DIR / "jev-classification-hero.png")
    render_image(build_html(TEXT["en"]), OUTPUT_DIR / "jev-classification-hero-en.png")


if __name__ == "__main__":
    main()
