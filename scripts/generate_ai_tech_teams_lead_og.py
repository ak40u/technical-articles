#!/usr/bin/env python3
"""Render the Open Graph hero images of the ai-tech-teams-lead article with headless Chrome."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "static" / "og"

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1920px; height: 1080px; overflow: hidden; background: #0f1513;
  font-family: Arial, Helvetica, sans-serif; color: #f4f1ea; position: relative; }
.glow { position: absolute; right: -260px; top: -120px; width: 1300px; height: 1300px;
  border-radius: 50%; background: #13221e; }
.kicker { position: absolute; left: 84px; top: 70px; color: #7fc4b0; font-weight: 700;
  font-size: 24px; letter-spacing: 4px; }
h1 { position: absolute; left: 84px; top: 130px; width: 740px; font-size: 64px; line-height: 1.12;
  font-weight: 800; text-transform: uppercase; }
.lede { position: absolute; left: 84px; top: 560px; width: 640px; font-size: 28px; line-height: 1.45;
  color: #c9c4b8; }
.metrics { position: absolute; left: 84px; top: 720px; display: flex; gap: 20px; }
.metric { border: 2px solid #3b4a44; border-radius: 14px; padding: 22px 26px; background: #16201d; }
.metric b { display: block; font-size: 44px; }
.metric span { display: block; margin-top: 10px; font-size: 19px; color: #a9a397; }
.panel { position: absolute; left: 860px; top: 60px; width: 976px; height: 950px;
  border: 2px solid #34413c; border-radius: 22px; background: #121a18; }
.panel-title { position: absolute; left: 48px; top: 36px; color: #a9a397; font-weight: 700;
  font-size: 22px; letter-spacing: 3px; }
.node { position: absolute; border-radius: 14px; border: 3px solid; text-align: center; padding-top: 22px; }
.node b { display: block; font-size: 25px; text-transform: uppercase; }
.node span { display: block; margin-top: 12px; font-size: 19px; color: #c9c4b8; }
.me { border-color: #e0a93b; background: #2b2417; }
.lead { border-color: #3fc7b0; background: #15332e; }
.corpus { border-color: #6fae82; background: #182a1f; }
.team { border-color: #56655f; background: #18211e; border-width: 2px; padding-top: 18px; }
.team b { font-size: 21px; }
.team span { font-size: 17px; }
.stuck { border-color: #d0665b; background: #2e1b19; }
.watch { border-color: #d0665b; background: #2a1917; }
svg { position: absolute; left: 0; top: 0; }
"""


def page(labels: dict) -> str:
    teams = "".join(
        f'<div class="node team{" stuck" if i == 4 else ""}" style="left:{48 + i * 180}px; top:560px; width:160px; height:110px">'
        f"<b>{name}</b><span>{stage}</span></div>"
        for i, (name, stage) in enumerate(labels["teams"])
    )
    arrows = "".join(
        f'<line x1="{128 + i * 180}" y1="500" x2="{128 + i * 180}" y2="552" marker-end="url(#a)"/>' for i in range(5)
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="glow"></div>
<div class="kicker">{labels["kicker"]}</div>
<h1>{labels["title"]}</h1>
<div class="lede">{labels["lede"]}</div>
<div class="metrics">{"".join(f'<div class="metric"><b>{v}</b><span>{k}</span></div>' for v, k in labels["metrics"])}</div>
<div class="panel">
  <div class="panel-title">{labels["panel"]}</div>
  <svg width="976" height="950" viewBox="0 0 976 950">
    <defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 0L10 5L0 10z" fill="#7d8c86"/></marker></defs>
    <g stroke="#7d8c86" stroke-width="3" fill="none">
      <line x1="330" y1="170" x2="392" y2="170" marker-end="url(#a)"/>
      <line x1="396" y1="236" x2="334" y2="236" marker-end="url(#a)"/>
      <line x1="720" y1="200" x2="660" y2="200" marker-end="url(#a)"/>
      <line x1="528" y1="290" x2="528" y2="500"/>
      <line x1="128" y1="500" x2="848" y2="500"/>
      {arrows}
      <line x1="488" y1="760" x2="488" y2="700" marker-end="url(#a)"/>
    </g>
  </svg>
  <div class="node me" style="left:48px; top:110px; width:280px; height:180px"><b>{labels["me"]}</b><span>{labels["me_1"]}</span><span>{labels["me_2"]}</span></div>
  <div class="node lead" style="left:398px; top:110px; width:260px; height:180px"><b>{labels["lead"]}</b><span>{labels["lead_1"]}</span><span>{labels["lead_2"]}</span></div>
  <div class="node corpus" style="left:724px; top:110px; width:204px; height:180px"><b>{labels["corpus"]}</b><span>{labels["corpus_1"]}</span><span>{labels["corpus_2"]}</span></div>
  <div style="position:absolute; left:560px; top:380px; color:#a9a397; font-size:19px; width:360px">{labels["fanout"]}</div>
  {teams}
  <div class="node watch" style="left:48px; top:770px; width:880px; height:120px"><b>{labels["watch"]}</b><span>{labels["watch_1"]}</span></div>
</div>
</body></html>"""


LABELS = {
    "ai-tech-teams-lead-hero.png": {
        "kicker": "ИИ-РУКОВОДИТЕЛЬ · CLAUDE CODE + CODEX",
        "title": "Как я передал ИИ\u2011команды ИИ\u2011руководителю",
        "lede": "Пять ИИ-команд работают параллельно. Руководитель решает за меня по моим прошлым решениям.",
        "metrics": [("139,9 млрд", "токенов за 30 дней"), ("396", "сессий"), ("11 138", "моих решений")],
        "panel": "КТО РЕШАЕТ",
        "me": "Я", "me_1": "задачи · вердикт", "me_2": "6 видов вопросов",
        "lead": "Руководитель", "lead_1": "полномочия", "lead_2": "мои прецеденты",
        "corpus": "Корпус", "corpus_1": "сессии", "corpus_2": "Telegram",
        "fanout": "споры · очередь · перезапуск · develop",
        "teams": [("Команда 1", "план"), ("Команда 2", "код"), ("Команда 3", "QA"), ("Команда 4", "аудит"), ("Команда 5", "стоит")],
        "watch": "Наблюдение снаружи",
        "watch_1": "11 видов вечной остановки · проверка раз в две минуты",
    },
    "ai-tech-teams-lead-hero-en.png": {
        "kicker": "AI LEAD · CLAUDE CODE + CODEX",
        "title": "How I handed my AI teams to an AI lead",
        "lede": "Five AI teams run in parallel. The lead decides for me from my past decisions.",
        "metrics": [("139.9B", "tokens in 30 days"), ("396", "sessions"), ("11,138", "of my decisions")],
        "panel": "WHO DECIDES",
        "me": "Me", "me_1": "tasks · verdict", "me_2": "6 kinds of questions",
        "lead": "The lead", "lead_1": "authority", "lead_2": "my precedents",
        "corpus": "Corpus", "corpus_1": "sessions", "corpus_2": "Telegram",
        "fanout": "disputes · queue · restarts · develop",
        "teams": [("Team 1", "plan"), ("Team 2", "code"), ("Team 3", "QA"), ("Team 4", "audit"), ("Team 5", "stuck")],
        "watch": "Watching from outside",
        "watch_1": "11 kinds of permanent stop · checked every two minutes",
    },
}


def render(html: str, output: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        temp = Path(f.name)
    try:
        subprocess.run(
            [CHROME_BIN, "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=1920,1080",
             f"--screenshot={output}", temp.as_uri()],
            check=True, capture_output=True,
        )
    finally:
        temp.unlink(missing_ok=True)
    print(output)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, labels in LABELS.items():
        render(page(labels), OUTPUT_DIR / name)


if __name__ == "__main__":
    main()
