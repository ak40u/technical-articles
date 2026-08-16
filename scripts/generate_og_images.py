#!/usr/bin/env python3
import subprocess
import tempfile
from pathlib import Path

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "static" / "og"

RU_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1920px;
    height: 1080px;
    background: #090d16;
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    padding: 80px 100px;
    gap: 70px;
    align-items: center;
    position: relative;
    overflow: hidden;
  }
  
  /* Subtle glow effects */
  .glow-1 {
    position: absolute;
    width: 700px;
    height: 700px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, rgba(0,0,0,0) 70%);
    top: -200px;
    left: -200px;
    pointer-events: none;
  }
  .glow-2 {
    position: absolute;
    width: 800px;
    height: 800px;
    background: radial-gradient(circle, rgba(34, 197, 94, 0.06) 0%, rgba(0,0,0,0) 70%);
    bottom: -250px;
    right: -200px;
    pointer-events: none;
  }

  .left-col {
    flex: 0 0 780px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;
    z-index: 10;
  }

  .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 20px;
    font-weight: 700;
    color: #38bdf8;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 28px;
  }

  .eyebrow::before {
    content: "";
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #38bdf8;
    box-shadow: 0 0 12px #38bdf8;
  }

  h1 {
    font-size: 54px;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -1.5px;
    color: #ffffff;
    margin-bottom: 30px;
  }

  .highlight {
    color: #38bdf8;
  }

  .desc {
    font-size: 24px;
    line-height: 1.5;
    color: #94a3b8;
    margin-bottom: 45px;
  }

  .meta-footer {
    display: flex;
    align-items: center;
    gap: 20px;
    font-size: 20px;
    font-weight: 600;
    color: #cbd5e1;
    border-top: 1px solid #1e293b;
    padding-top: 30px;
  }

  .avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #1e293b;
    border: 2px solid #38bdf8;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: ui-monospace, monospace;
    font-weight: 800;
    font-size: 18px;
    color: #38bdf8;
  }

  .domain {
    margin-left: auto;
    font-family: ui-monospace, monospace;
    color: #64748b;
    font-size: 19px;
  }

  /* Right Schematic Card */
  .right-col {
    flex: 1;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
  }

  .diagram-card {
    width: 100%;
    height: 840px;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 24px;
    padding: 35px 30px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    position: relative;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 20px;
    margin-bottom: 25px;
  }

  .card-title {
    font-family: ui-monospace, monospace;
    font-size: 16px;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }

  .card-badge {
    font-family: ui-monospace, monospace;
    font-size: 14px;
    padding: 6px 14px;
    border-radius: 20px;
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.3);
    font-weight: 700;
  }

  .flow {
    display: flex;
    flex-direction: column;
    gap: 16px;
    flex: 1;
    justify-content: space-between;
  }

  .step-node {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 18px;
    position: relative;
  }

  .step-node.active {
    border-color: #38bdf8;
    background: #172554;
  }

  .step-node.gate {
    border-color: #f87171;
    background: #2a1215;
  }

  .step-node.qa {
    border-color: #4ade80;
    background: #0d2818;
  }

  .step-num {
    font-family: ui-monospace, monospace;
    font-size: 15px;
    font-weight: 800;
    padding: 4px 10px;
    border-radius: 8px;
    background: #0f172a;
    color: #94a3b8;
  }

  .step-info {
    flex: 1;
  }

  .step-title {
    font-size: 18px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 3px;
  }

  .step-desc {
    font-size: 14px;
    color: #94a3b8;
    font-family: ui-monospace, monospace;
  }

  .connector {
    width: 2px;
    height: 12px;
    background: #475569;
    margin: 0 auto;
  }

  .metrics-row {
    margin-top: 20px;
    padding-top: 18px;
    border-top: 1px solid #1e293b;
    display: flex;
    justify-content: space-between;
  }

  .metric-item {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }

  .metric-val {
    font-size: 20px;
    font-weight: 800;
    color: #38bdf8;
    font-family: ui-monospace, monospace;
  }

  .metric-label {
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
</style>
</head>
<body>
  <div class="glow-1"></div>
  <div class="glow-2"></div>

  <div class="left-col">
    <div class="eyebrow">Findrates.ai · Практика SDD</div>
    <h1>Agentic SDD: как заставить нейросети писать код по <span class="highlight">жестким спекам</span></h1>
    <p class="desc">Изоляция контекстов, синтез контрактов, враждебное ревью моделей и 240+ закрытых задач в продакшене без вайбкодинга.</p>
    <div class="meta-footer">
      <div class="avatar">PV</div>
      <span>Павел Волков</span>
      <span class="domain">pvolkov.com</span>
    </div>
  </div>

  <div class="right-col">
    <div class="diagram-card">
      <div class="card-header">
        <span class="card-title">Архитектура конвейера спецификаций</span>
        <span class="card-badge">240+ Closed Plans</span>
      </div>

      <div class="flow">
        <div class="step-node">
          <span class="step-num">01</span>
          <div class="step-info">
            <div class="step-title">Scout &amp; Worktree Isolation</div>
            <div class="step-desc">Read-only скан репозитория, типы, декомпозиция на слайсы</div>
          </div>
        </div>

        <div class="connector"></div>

        <div class="step-node active">
          <span class="step-num">02</span>
          <div class="step-info">
            <div class="step-title">Синтез независимых критериев</div>
            <div class="step-desc">Ольга (Anti-anchoring AC + Must-Not) + Ева (UX контракт)</div>
          </div>
        </div>

        <div class="connector"></div>

        <div class="step-node gate">
          <span class="step-num">03</span>
          <div class="step-info">
            <div class="step-title">Враждебное ревью плана</div>
            <div class="step-desc">Codex / Hunyuan / Opus атакуют спеку до 0 замечаний</div>
          </div>
        </div>

        <div class="connector"></div>

        <div class="step-node qa">
          <span class="step-num">04</span>
          <div class="step-info">
            <div class="step-title">Генерация кода, TDD &amp; QA Loop</div>
            <div class="step-desc">BDD + Stryker, гейт code-vs-plan, 5 раундов e2e Марины</div>
          </div>
        </div>
      </div>

      <div class="metrics-row">
        <div class="metric-item">
          <span class="metric-val">84%</span>
          <span class="metric-label">Автономный стейджинг</span>
        </div>
        <div class="metric-item">
          <span class="metric-val">$2–$6</span>
          <span class="metric-label">Стоимость слайса</span>
        </div>
        <div class="metric-item">
          <span class="metric-val">15–25 мин</span>
          <span class="metric-label">Время закрытия</span>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

EN_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1920px;
    height: 1080px;
    background: #090d16;
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    padding: 80px 100px;
    gap: 70px;
    align-items: center;
    position: relative;
    overflow: hidden;
  }
  
  .glow-1 {
    position: absolute;
    width: 700px;
    height: 700px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, rgba(0,0,0,0) 70%);
    top: -200px;
    left: -200px;
    pointer-events: none;
  }
  .glow-2 {
    position: absolute;
    width: 800px;
    height: 800px;
    background: radial-gradient(circle, rgba(34, 197, 94, 0.06) 0%, rgba(0,0,0,0) 70%);
    bottom: -250px;
    right: -200px;
    pointer-events: none;
  }

  .left-col {
    flex: 0 0 780px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;
    z-index: 10;
  }

  .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 20px;
    font-weight: 700;
    color: #38bdf8;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 28px;
  }

  .eyebrow::before {
    content: "";
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #38bdf8;
    box-shadow: 0 0 12px #38bdf8;
  }

  h1 {
    font-size: 54px;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -1.5px;
    color: #ffffff;
    margin-bottom: 30px;
  }

  .highlight {
    color: #38bdf8;
  }

  .desc {
    font-size: 24px;
    line-height: 1.5;
    color: #94a3b8;
    margin-bottom: 45px;
  }

  .meta-footer {
    display: flex;
    align-items: center;
    gap: 20px;
    font-size: 20px;
    font-weight: 600;
    color: #cbd5e1;
    border-top: 1px solid #1e293b;
    padding-top: 30px;
  }

  .avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #1e293b;
    border: 2px solid #38bdf8;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: ui-monospace, monospace;
    font-weight: 800;
    font-size: 18px;
    color: #38bdf8;
  }

  .domain {
    margin-left: auto;
    font-family: ui-monospace, monospace;
    color: #64748b;
    font-size: 19px;
  }

  .right-col {
    flex: 1;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
  }

  .diagram-card {
    width: 100%;
    height: 840px;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 24px;
    padding: 35px 30px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    position: relative;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 20px;
    margin-bottom: 25px;
  }

  .card-title {
    font-family: ui-monospace, monospace;
    font-size: 16px;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }

  .card-badge {
    font-family: ui-monospace, monospace;
    font-size: 14px;
    padding: 6px 14px;
    border-radius: 20px;
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.3);
    font-weight: 700;
  }

  .flow {
    display: flex;
    flex-direction: column;
    gap: 16px;
    flex: 1;
    justify-content: space-between;
  }

  .step-node {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 18px;
    position: relative;
  }

  .step-node.active {
    border-color: #38bdf8;
    background: #172554;
  }

  .step-node.gate {
    border-color: #f87171;
    background: #2a1215;
  }

  .step-node.qa {
    border-color: #4ade80;
    background: #0d2818;
  }

  .step-num {
    font-family: ui-monospace, monospace;
    font-size: 15px;
    font-weight: 800;
    padding: 4px 10px;
    border-radius: 8px;
    background: #0f172a;
    color: #94a3b8;
  }

  .step-info {
    flex: 1;
  }

  .step-title {
    font-size: 18px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 3px;
  }

  .step-desc {
    font-size: 14px;
    color: #94a3b8;
    font-family: ui-monospace, monospace;
  }

  .connector {
    width: 2px;
    height: 12px;
    background: #475569;
    margin: 0 auto;
  }

  .metrics-row {
    margin-top: 20px;
    padding-top: 18px;
    border-top: 1px solid #1e293b;
    display: flex;
    justify-content: space-between;
  }

  .metric-item {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }

  .metric-val {
    font-size: 20px;
    font-weight: 800;
    color: #38bdf8;
    font-family: ui-monospace, monospace;
  }

  .metric-label {
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
</style>
</head>
<body>
  <div class="glow-1"></div>
  <div class="glow-2"></div>

  <div class="left-col">
    <div class="eyebrow">Findrates.ai · SDD Practice</div>
    <h1>Agentic SDD: Forcing AI Agents to Write Code by <span class="highlight">Strict Contract</span></h1>
    <p class="desc">Context isolation, contract synthesis, adversarial model reviews, and 240+ closed plans in production without vibecoding.</p>
    <div class="meta-footer">
      <div class="avatar">PV</div>
      <span>Pavel Volkov</span>
      <span class="domain">pvolkov.com</span>
    </div>
  </div>

  <div class="right-col">
    <div class="diagram-card">
      <div class="card-header">
        <span class="card-title">Specification Pipeline Architecture</span>
        <span class="card-badge">240+ Closed Plans</span>
      </div>

      <div class="flow">
        <div class="step-node">
          <span class="step-num">01</span>
          <div class="step-info">
            <div class="step-title">Scout &amp; Worktree Isolation</div>
            <div class="step-desc">Read-only repo scan, signatures, slice decomposition</div>
          </div>
        </div>

        <div class="connector"></div>

        <div class="step-node active">
          <span class="step-num">02</span>
          <div class="step-info">
            <div class="step-title">Independent Contract Synthesis</div>
            <div class="step-desc">Olga (Anti-anchoring AC + Must-Not) + Eva (UX Contract)</div>
          </div>
        </div>

        <div class="connector"></div>

        <div class="step-node gate">
          <span class="step-num">03</span>
          <div class="step-info">
            <div class="step-title">Adversarial Plan Review</div>
            <div class="step-desc">Codex / Hunyuan / Opus attack spec until 0 issues</div>
          </div>
        </div>

        <div class="connector"></div>

        <div class="step-node qa">
          <span class="step-num">04</span>
          <div class="step-info">
            <div class="step-title">Code Generation, TDD &amp; QA Loop</div>
            <div class="step-desc">BDD + Stryker, code-vs-plan gate, 5 Marina E2E rounds</div>
          </div>
        </div>
      </div>

      <div class="metrics-row">
        <div class="metric-item">
          <span class="metric-val">84%</span>
          <span class="metric-label">Autonomous Staging</span>
        </div>
        <div class="metric-item">
          <span class="metric-val">$2–$6</span>
          <span class="metric-label">Cost Per Slice</span>
        </div>
        <div class="metric-item">
          <span class="metric-val">15–25 min</span>
          <span class="metric-label">Runtime</span>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

def render_image(html: str, output_path: Path):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        temp_path = f.name
        
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1920,1080",
        f"--screenshot={output_path}",
        f"file://{temp_path}",
    ]
    subprocess.run(cmd, check=True)
    Path(temp_path).unlink(missing_ok=True)
    print(f"Generated: {output_path}")

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    render_image(RU_HTML, OUTPUT_DIR / "sdd-in-production-hero.png")
    render_image(EN_HTML, OUTPUT_DIR / "sdd-in-production-hero-en.png")

if __name__ == "__main__":
    main()
