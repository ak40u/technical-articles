#!/usr/bin/env python3
"""Generate bilingual ASIC climate-control diagrams and OpenGraph covers."""

from __future__ import annotations

import html
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHROME_BIN = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
BACKGROUND = ROOT / "assets" / "illustrations" / "asic-climate-guardian" / "og-background.png"

LOCALES = {
    "ru": {
        "article_dir": ROOT / "content" / "ru" / "articles" / "asic-climate-guardian",
        "og_path": ROOT / "static" / "og" / "asic-climate-guardian-hero.png",
        "architecture": {
            "title": "Как устроен ИИ-автопилот отопления",
            "subtitle": "Qwen выбирает стратегию, а независимые правила удерживают физические границы.",
            "inputs": [
                ("КОМНАТЫ", "температура · возраст данных"),
                ("АСИКИ", "мощность · хешрейт · RPM"),
                ("ПОГОДА", "улица · заморозки · ветер"),
                ("ЭКОНОМИКА", "ETC · тариф · энерготемп"),
            ],
            "context": "HOME ASSISTANT + ЕДИНЫЙ КОНТЕКСТ",
            "context_sub": "5 зон · 5 розеток · греющий кабель · режим присутствия",
            "fast_kicker": "БЫСТРЫЙ КОНТУР · КАЖДЫЕ 2 МИНУТЫ",
            "fast_title": "Детерминированная безопасность",
            "fast_items": ["< +10°C: антифриз", "+24 / +33°C: стоп", "чип ≥ +65°C", "вентилятор < 800 RPM", "улица ≤ +2°C: кабель"],
            "ai_kicker": "ИИ-КОНТУР · КАЖДЫЕ 10 МИНУТ",
            "ai_title": "Локальная Qwen 2.5 14B",
            "ai_items": ["комфорт и шум", "приоритет зон", "темп к 1 500 кВт·ч", "JSON-план действий"],
            "validator": "ЖЕСТКИЙ ВАЛИДАТОР",
            "validator_sub": "перегрев · антифриз · максимум 3 асика · защита воды",
            "output": "ФИЗИЧЕСКИЙ РЕЗУЛЬТАТ",
            "output_sub": "5 розеток асиков · кабель водопровода · Telegram владельца",
        },
        "economics": {
            "title": "Отопление, стоимость которого компенсирует ETC",
            "subtitle": "Сравниваем не доход майнера, а чистую стоимость полезного тепла.",
            "heater": "ОБЫЧНЫЙ ОБОГРЕВАТЕЛЬ",
            "heater_main": "0,63 кВт электричества",
            "heater_sub": "→ 0,63 кВт тепла",
            "asic": "JASMINER X16-Q",
            "asic_main": "0,63 кВт электричества",
            "asic_sub": "→ 0,63 кВт тепла + ETC",
            "formula_kicker": "ПОЛЕЗНАЯ ФОРМУЛА",
            "formula": "СЧЕТ ЗА СВЕТ − КОМПЕНСАЦИЯ ETC",
            "formula_result": "= ЧИСТАЯ СТОИМОСТЬ ТЕПЛА",
            "snapshot": "Снимок для 3 лучших асиков · 28,5 дня",
            "stats": [("1 292,8 кВт·ч", "ПОЛЕЗНОЕ ТЕПЛО"), ("5 443 ₽", "СЧЕТ ЗА СВЕТ"), ("12 293 ₽", "КОМПЕНСАЦИЯ ETC"), ("−6 850 ₽", "СТОИМОСТЬ ТЕПЛА")],
            "pacing_title": "Мягкая цель энергобюджета",
            "pacing_sub": "Штрафа за недобор нет. Комфорт важнее использования дешевой квоты.",
            "three": "3 асика · 1 407 кВт·ч",
            "target": "цель · 1 500",
            "limit": "граница тарифа · 1 600",
            "four": "4 асика · 1 876",
            "safe": "ОПТИМАЛЬНЫЙ ТЕМП",
            "risk": "РИСК ДИАПАЗОНА 2",
            "caveat": "Сейчас Pacing прогнозирует темп по активным слотам × 630 Вт. Для точного остатка нужен общий счетчик дома.",
        },
        "og_copy": {
            "eyebrow": "JASMINER X16-Q · ЛОКАЛЬНЫЙ ИИ",
            "headline": "ИИ-АВТОПИЛОТ<br>ДЛЯ ОТОПЛЕНИЯ<br><span>ПЯТЬЮ АСИКАМИ</span>",
            "description": "Пять зон, два независимых контура и тепло, стоимость которого компенсирует ETC.",
            "chips": ["5 ЗОН", "1 500 КВТ·Ч", "БЕЗ ОБЛАКА"],
            "badge": "QWEN 2.5 14B · LOCAL",
            "panel": [("2 МИН", "защитный контур"), ("10 МИН", "стратегия Qwen"), ("1 600", "граница тарифа")],
            "publication": "ТЕХНИЧЕСКИЕ СТАТЬИ",
        },
    },
    "en": {
        "article_dir": ROOT / "content" / "en" / "articles" / "asic-climate-guardian",
        "og_path": ROOT / "static" / "og" / "asic-climate-guardian-hero-en.png",
        "architecture": {
            "title": "How the AI heating autopilot works",
            "subtitle": "Qwen selects the strategy; independent rules enforce the physical boundaries.",
            "inputs": [
                ("ROOMS", "temperature · reading age"),
                ("ASICS", "power · hashrate · RPM"),
                ("WEATHER", "outdoor · frost · wind"),
                ("ECONOMICS", "ETC · tariff · energy pace"),
            ],
            "context": "HOME ASSISTANT + UNIFIED CONTEXT",
            "context_sub": "5 zones · 5 plugs · heating cable · occupancy mode",
            "fast_kicker": "FAST LOOP · EVERY 2 MINUTES",
            "fast_title": "Deterministic safety",
            "fast_items": ["< +10°C: anti-freeze", "+24 / +33°C: stop", "chip ≥ +65°C", "fan < 800 RPM", "outdoor ≤ +2°C: cable"],
            "ai_kicker": "AI LOOP · EVERY 10 MINUTES",
            "ai_title": "Local Qwen 2.5 14B",
            "ai_items": ["comfort and noise", "zone priority", "pace toward 1,500 kWh", "JSON action plan"],
            "validator": "HARD VALIDATOR",
            "validator_sub": "overheat · anti-freeze · max 3 ASICs · water protection",
            "output": "PHYSICAL OUTCOME",
            "output_sub": "5 ASIC plugs · water-pipe cable · owner Telegram",
        },
        "economics": {
            "title": "Heating whose electricity cost is offset by ETC",
            "subtitle": "The relevant metric is not mining income, but the net cost of useful heat.",
            "heater": "RESISTIVE SPACE HEATER",
            "heater_main": "0.63 kW electricity",
            "heater_sub": "→ 0.63 kW heat",
            "asic": "JASMINER X16-Q",
            "asic_main": "0.63 kW electricity",
            "asic_sub": "→ 0.63 kW heat + ETC",
            "formula_kicker": "THE USEFUL FORMULA",
            "formula": "POWER BILL − ETC OFFSET",
            "formula_result": "= NET HEATING COST",
            "snapshot": "Snapshot for the best 3 ASICs · 28.5 days",
            "stats": [("1,292.8 kWh", "USEFUL HEAT"), ("RUB 5,443", "POWER BILL"), ("RUB 12,293", "ETC OFFSET"), ("−RUB 6,850", "HEATING COST")],
            "pacing_title": "Soft energy-budget target",
            "pacing_sub": "There is no under-use penalty. Comfort outranks cheap-tier utilization.",
            "three": "3 ASICs · 1,407 kWh",
            "target": "target · 1,500",
            "limit": "tariff boundary · 1,600",
            "four": "4 ASICs · 1,876",
            "safe": "OPTIMAL PACE",
            "risk": "TIER 2 RISK",
            "caveat": "Pacing currently projects active slots × 630 W. Exact remaining allowance requires whole-property meter data.",
        },
        "og_copy": {
            "eyebrow": "JASMINER X16-Q · LOCAL AI",
            "headline": "AI AUTOPILOT<br>FOR HEATING WITH<br><span>FIVE ASICS</span>",
            "description": "Five zones, two independent control loops, and useful heat whose electricity cost is offset by ETC.",
            "chips": ["5 ZONES", "1,500 KWH", "NO CLOUD"],
            "badge": "QWEN 2.5 14B · LOCAL",
            "panel": [("2 MIN", "safety loop"), ("10 MIN", "Qwen strategy"), ("1,600", "tariff boundary")],
            "publication": "TECHNICAL ARTICLES",
        },
    },
}


SVG_DEFS = """
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#54717c"/>
    </marker>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="7" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="heat" x1="0" x2="1">
      <stop offset="0" stop-color="#f59e0b"/><stop offset="1" stop-color="#fb7185"/>
    </linearGradient>
    <style>
      .bg { fill: #0b121d; }
      .grid { stroke: #173044; stroke-width: 1; opacity: .32; }
      .title { fill: #f8fafc; font: 800 42px Arial, Helvetica, sans-serif; }
      .subtitle { fill: #94a3b8; font: 400 21px Arial, Helvetica, sans-serif; }
      .kicker { fill: #67e8f9; font: 700 16px Arial, Helvetica, sans-serif; letter-spacing: 1.8px; }
      .label { fill: #f8fafc; font: 700 22px Arial, Helvetica, sans-serif; }
      .small { fill: #a7bac6; font: 400 17px Arial, Helvetica, sans-serif; }
      .micro { fill: #7f99a8; font: 600 14px Arial, Helvetica, sans-serif; letter-spacing: .5px; }
      .mono { fill: #d9edf5; font: 700 18px Menlo, Monaco, Consolas, monospace; }
      .line { fill: none; stroke: #54717c; stroke-width: 3; marker-end: url(#arrow); }
      .dash { fill: none; stroke: #8b5cf6; stroke-width: 3; stroke-dasharray: 10 8; marker-end: url(#arrow); }
    </style>
  </defs>
"""


def e(value: str) -> str:
    return html.escape(value, quote=True)


def grid(width: int, height: int, step: int = 80) -> str:
    lines = []
    for x in range(0, width + 1, step):
        lines.append(f'<path class="grid" d="M{x} 0V{height}"/>')
    for y in range(0, height + 1, step):
        lines.append(f'<path class="grid" d="M0 {y}H{width}"/>')
    return "".join(lines)


def build_architecture_svg(copy: dict[str, object]) -> str:
    inputs = []
    for index, (title, subtitle) in enumerate(copy["inputs"]):
        x = 56 + index * 374
        inputs.append(
            f'<rect x="{x}" y="148" width="340" height="104" rx="16" fill="#101f2d" stroke="#315268" stroke-width="2"/>'
            f'<circle cx="{x + 34}" cy="184" r="9" fill="#22d3ee" filter="url(#glow)"/>'
            f'<text class="label" x="{x + 58}" y="190">{e(title)}</text>'
            f'<text class="small" x="{x + 28}" y="224">{e(subtitle)}</text>'
            f'<path class="line" d="M{x + 170} 252V288"/>'
        )

    fast_items = []
    for index, item in enumerate(copy["fast_items"]):
        x = 86 + (index % 2) * 315
        y = 594 + (index // 2) * 58
        width = 292 if index < 4 else 607
        fast_items.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="42" rx="10" fill="#19242b" stroke="#6b4a30"/>'
            f'<circle cx="{x + 22}" cy="{y + 21}" r="6" fill="#fb923c"/>'
            f'<text class="small" x="{x + 39}" y="{y + 27}">{e(item)}</text>'
        )

    ai_items = []
    for index, item in enumerate(copy["ai_items"]):
        x = 864 + (index % 2) * 310
        y = 594 + (index // 2) * 58
        ai_items.append(
            f'<rect x="{x}" y="{y}" width="286" height="42" rx="10" fill="#1c1930" stroke="#5d4a8c"/>'
            f'<circle cx="{x + 22}" cy="{y + 21}" r="6" fill="#a78bfa"/>'
            f'<text class="small" x="{x + 39}" y="{y + 27}">{e(item)}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="980" viewBox="0 0 1600 980" role="img" aria-labelledby="title desc">
  <title id="title">{e(copy["title"])}</title>
  <desc id="desc">{e(copy["subtitle"])}</desc>
{SVG_DEFS}
  <rect class="bg" width="1600" height="980"/>
  <g>{grid(1600, 980)}</g>
  <text class="title" x="56" y="66">{e(copy["title"])}</text>
  <text class="subtitle" x="56" y="104">{e(copy["subtitle"])}</text>
  {''.join(inputs)}

  <rect x="350" y="302" width="900" height="112" rx="20" fill="#102c38" stroke="#22d3ee" stroke-width="3"/>
  <text class="kicker" x="800" y="342" text-anchor="middle">{e(copy["context"])}</text>
  <text class="small" x="800" y="380" text-anchor="middle">{e(copy["context_sub"])}</text>
  <path class="line" d="M650 414V458H410V486"/>
  <path class="dash" d="M950 414V458H1190V486"/>

  <rect x="56" y="488" width="710" height="310" rx="22" fill="#171a1e" stroke="#f59e0b" stroke-width="3"/>
  <text class="kicker" x="86" y="530" fill="#fdba74">{e(copy["fast_kicker"])}</text>
  <text class="label" x="86" y="568">{e(copy["fast_title"])}</text>
  {''.join(fast_items)}

  <rect x="834" y="488" width="710" height="310" rx="22" fill="#151329" stroke="#8b5cf6" stroke-width="3"/>
  <text class="kicker" x="864" y="530" fill="#c4b5fd">{e(copy["ai_kicker"])}</text>
  <text class="label" x="864" y="568">{e(copy["ai_title"])}</text>
  {''.join(ai_items)}
  <rect x="864" y="718" width="596" height="56" rx="12" fill="#241f3d" stroke="#a78bfa" stroke-width="2"/>
  <text class="mono" x="1162" y="752" text-anchor="middle">JSON → actions · cable · reasoning</text>

  <path class="line" d="M410 798V832H800"/>
  <path class="dash" d="M1190 798V832H800"/>
  <rect x="492" y="818" width="616" height="70" rx="16" fill="#202b32" stroke="#f97316" stroke-width="2"/>
  <text class="kicker" x="800" y="846" text-anchor="middle" fill="#fdba74">{e(copy["validator"])}</text>
  <text class="small" x="800" y="874" text-anchor="middle">{e(copy["validator_sub"])}</text>
  <path class="line" d="M800 888V914"/>

  <rect x="258" y="918" width="1084" height="52" rx="16" fill="#0e342a" stroke="#22c55e" stroke-width="3"/>
  <text class="kicker" x="390" y="950" fill="#86efac">{e(copy["output"])}</text>
  <text class="small" x="648" y="950">{e(copy["output_sub"])}</text>
</svg>'''


def build_economics_svg(copy: dict[str, object]) -> str:
    stat_cards = []
    for index, (value, label) in enumerate(copy["stats"]):
        x = 70 + index * 366
        accent = "#34d399" if index == 3 else "#38bdf8"
        stat_cards.append(
            f'<rect x="{x}" y="350" width="336" height="104" rx="14" fill="#111f2c" stroke="#2c4658"/>'
            f'<text x="{x + 24}" y="393" fill="{accent}" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="800">{e(value)}</text>'
            f'<text class="micro" x="{x + 24}" y="428">{e(label)}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc">
  <title id="title">{e(copy["title"])}</title>
  <desc id="desc">{e(copy["subtitle"])}</desc>
{SVG_DEFS}
  <rect class="bg" width="1600" height="900"/>
  <g>{grid(1600, 900)}</g>
  <text class="title" x="56" y="66">{e(copy["title"])}</text>
  <text class="subtitle" x="56" y="104">{e(copy["subtitle"])}</text>

  <rect x="56" y="142" width="350" height="156" rx="18" fill="#181d24" stroke="#64748b" stroke-width="2"/>
  <text class="kicker" x="82" y="180" fill="#cbd5e1">{e(copy["heater"])}</text>
  <text class="label" x="82" y="226">{e(copy["heater_main"])}</text>
  <text x="82" y="266" fill="#fb923c" font-family="Arial, Helvetica, sans-serif" font-size="24" font-weight="700">{e(copy["heater_sub"])}</text>

  <rect x="430" y="142" width="350" height="156" rx="18" fill="#102b2b" stroke="#22c55e" stroke-width="2"/>
  <text class="kicker" x="456" y="180" fill="#86efac">{e(copy["asic"])}</text>
  <text class="label" x="456" y="226">{e(copy["asic_main"])}</text>
  <text x="456" y="266" fill="#34d399" font-family="Arial, Helvetica, sans-serif" font-size="24" font-weight="700">{e(copy["asic_sub"])}</text>

  <path class="line" d="M792 220H838"/>
  <rect x="850" y="142" width="694" height="156" rx="18" fill="#11233a" stroke="#38bdf8" stroke-width="3"/>
  <text class="kicker" x="884" y="180">{e(copy["formula_kicker"])}</text>
  <text x="884" y="226" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="26" font-weight="800">{e(copy["formula"])}</text>
  <text x="884" y="267" fill="#67e8f9" font-family="Arial, Helvetica, sans-serif" font-size="26" font-weight="800">{e(copy["formula_result"])}</text>

  <text class="micro" x="70" y="330">{e(copy["snapshot"])}</text>
  {''.join(stat_cards)}

  <rect x="56" y="490" width="1488" height="326" rx="22" fill="#101b27" stroke="#355066" stroke-width="2"/>
  <text class="label" x="88" y="536">{e(copy["pacing_title"])}</text>
  <text class="small" x="88" y="570">{e(copy["pacing_sub"])}</text>

  <rect x="116" y="636" width="1318" height="36" rx="18" fill="#1e293b"/>
  <rect x="116" y="636" width="988" height="36" rx="18" fill="#0f766e"/>
  <rect x="1104" y="636" width="67" height="36" fill="#ca8a04"/>
  <rect x="1171" y="636" width="263" height="36" rx="18" fill="#9f2d35"/>

  <line x1="1044" y1="614" x2="1044" y2="696" stroke="#34d399" stroke-width="4"/>
  <circle cx="1044" cy="654" r="9" fill="#34d399" filter="url(#glow)"/>
  <text x="1024" y="606" text-anchor="end" fill="#86efac" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700">{e(copy["three"])}</text>

  <line x1="1104" y1="626" x2="1104" y2="682" stroke="#fde047" stroke-width="3"/>
  <text x="1104" y="722" text-anchor="middle" fill="#fde047" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700">{e(copy["target"])}</text>

  <line x1="1171" y1="614" x2="1171" y2="696" stroke="#fb923c" stroke-width="4"/>
  <text x="1191" y="606" text-anchor="start" fill="#fdba74" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700">{e(copy["limit"])}</text>

  <line x1="1352" y1="626" x2="1352" y2="682" stroke="#fb7185" stroke-width="4"/>
  <text x="1352" y="722" text-anchor="middle" fill="#fda4af" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700">{e(copy["four"])}</text>

  <text class="micro" x="116" y="766" fill="#5eead4">{e(copy["safe"])}</text>
  <text class="micro" x="1240" y="766" fill="#fda4af">{e(copy["risk"])}</text>
  <rect x="56" y="838" width="1488" height="42" rx="12" fill="#18202b" stroke="#334155"/>
  <text class="small" x="80" y="865">{e(copy["caveat"])}</text>
</svg>'''


def build_og_html(copy: dict[str, object]) -> str:
    background_uri = BACKGROUND.resolve().as_uri()
    chips = "".join(f'<span class="chip">{e(item)}</span>' for item in copy["chips"])
    metrics = "".join(
        f'<div class="metric"><strong>{e(value)}</strong><span>{e(label)}</span></div>'
        for value, label in copy["panel"]
    )
    return f'''<!doctype html>
<html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; }}
body {{ background: #070d16; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; position: relative; }}
.art {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 72% center; opacity: .96; }}
.shade {{ position: absolute; inset: 0; background: linear-gradient(90deg, #070d16 0%, #070d16 36%, rgba(7,13,22,.91) 49%, rgba(7,13,22,.12) 76%, rgba(7,13,22,.08) 100%); }}
.topline {{ position: absolute; left: 94px; right: 94px; top: 66px; height: 2px; background: linear-gradient(90deg, #22d3ee, rgba(34,211,238,.1)); }}
.copy {{ position: absolute; left: 94px; top: 122px; width: 860px; }}
.eyebrow {{ color: #67e8f9; font: 800 20px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: 2.5px; margin-bottom: 34px; }}
h1 {{ margin: 0; color: #f8fafc; font-size: 68px; line-height: 1.08; letter-spacing: -2px; font-weight: 900; text-shadow: 0 4px 28px rgba(0,0,0,.55); }}
h1 span {{ color: #38bdf8; }}
.description {{ width: 770px; margin: 34px 0 30px; color: #b7c7d3; font-size: 25px; line-height: 1.46; font-weight: 500; }}
.chips {{ display: flex; gap: 12px; }}
.chip {{ display: inline-flex; padding: 10px 15px; border-radius: 999px; border: 1px solid #31546b; background: rgba(12,31,45,.88); color: #d8f7ff; font: 800 15px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: 1px; }}
.badge {{ position: absolute; right: 84px; top: 72px; padding: 12px 18px; border-radius: 999px; border: 1px solid rgba(167,139,250,.6); background: rgba(30,22,55,.82); color: #d8ccff; font: 800 16px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: 1px; }}
.panel {{ position: absolute; right: 76px; bottom: 70px; width: 700px; height: 138px; display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid rgba(75,112,132,.8); border-radius: 20px; background: rgba(6,15,25,.88); backdrop-filter: blur(12px); box-shadow: 0 18px 70px rgba(0,0,0,.38); }}
.metric {{ padding: 26px 24px; border-right: 1px solid rgba(75,112,132,.45); }}
.metric:last-child {{ border-right: 0; }}
.metric strong {{ display: block; color: #67e8f9; font: 900 27px ui-monospace, SFMono-Regular, Menlo, monospace; margin-bottom: 8px; }}
.metric span {{ color: #9fb2bf; font-size: 15px; font-weight: 650; }}
.footer {{ position: absolute; left: 94px; bottom: 74px; width: 720px; padding-top: 24px; border-top: 1px solid #253545; color: #71869a; font: 800 17px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: 1.6px; }}
</style></head><body>
<img class="art" src="{background_uri}" alt="">
<div class="shade"></div><div class="topline"></div>
<div class="badge">{e(copy["badge"])}</div>
<main class="copy"><div class="eyebrow">{e(copy["eyebrow"])}</div><h1>{copy["headline"]}</h1><p class="description">{e(copy["description"])}</p><div class="chips">{chips}</div></main>
<div class="footer">{e(copy["publication"])}</div>
<div class="panel">{metrics}</div>
</body></html>'''


def render_png(html_doc: str, output: Path) -> None:
    if not CHROME_BIN.exists():
        raise RuntimeError(f"Chrome not found: {CHROME_BIN}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
        handle.write(html_doc)
        temp_path = Path(handle.name)
    try:
        subprocess.run(
            [
                str(CHROME_BIN),
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                "--window-size=1920,1080",
                f"--screenshot={output}",
                temp_path.as_uri(),
            ],
            check=True,
        )
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> None:
    if not BACKGROUND.exists():
        raise RuntimeError(f"Missing generated background: {BACKGROUND}")
    for locale, config in LOCALES.items():
        article_dir = config["article_dir"]
        article_dir.mkdir(parents=True, exist_ok=True)
        (article_dir / "system-architecture.svg").write_text(
            build_architecture_svg(config["architecture"]), encoding="utf-8"
        )
        (article_dir / "heating-economics.svg").write_text(
            build_economics_svg(config["economics"]), encoding="utf-8"
        )
        render_png(build_og_html(config["og_copy"]), config["og_path"])
        print(f"Generated ASIC climate visuals ({locale})")


if __name__ == "__main__":
    main()
