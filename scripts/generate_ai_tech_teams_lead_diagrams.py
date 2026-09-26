#!/usr/bin/env python3
"""Generate the four page-bundle diagrams of the ai-tech-teams-lead article, in Russian and English."""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
BUNDLES = {
    "ru": ROOT / "content/ru/articles/ai-tech-teams-lead",
    "en": ROOT / "content/en/articles/ai-tech-teams-lead",
}

STYLE = """
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#7a776f"/>
    </marker>
    <marker id="arrow-owner" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#8f4f2f"/>
    </marker>
    <style>
      .bg { fill: #fcfbf7; }
      .owner { fill: #f7eadc; stroke: #8f4f2f; stroke-width: 3; }
      .core { fill: #e8f2f4; stroke: #245f73; stroke-width: 3; }
      .project { fill: #edf6ef; stroke: #4f7b5d; stroke-width: 2.5; }
      .task { fill: #f3f0e8; stroke: #8b867d; stroke-width: 2; }
      .warn { fill: #fae9e5; stroke: #a34a3f; stroke-width: 2; }
      .dark { fill: #2b2a27; }
      .line { fill: none; stroke: #7a776f; stroke-width: 2.5; marker-end: url(#arrow); }
      .plain { fill: none; stroke: #7a776f; stroke-width: 2.5; }
      .ownerline { fill: none; stroke: #8f4f2f; stroke-width: 2.5; stroke-dasharray: 9 7; marker-end: url(#arrow-owner); }
      .rule { stroke: #ded9cd; stroke-width: 1.5; }
      .title { fill: #1d1d1b; font: 800 38px Arial, Helvetica, sans-serif; }
      .subtitle { fill: #6c6860; font: 400 21px Arial, Helvetica, sans-serif; }
      .label { fill: #1d1d1b; font: 700 21px Arial, Helvetica, sans-serif; text-anchor: middle; }
      .label-l { fill: #1d1d1b; font: 700 19px Arial, Helvetica, sans-serif; }
      .small { fill: #5f5b54; font: 400 16px Arial, Helvetica, sans-serif; text-anchor: middle; }
      .small-l { fill: #5f5b54; font: 400 16px Arial, Helvetica, sans-serif; }
      .edge { fill: #5f5b54; font: 700 16px Arial, Helvetica, sans-serif; }
      .edge-owner { fill: #8f4f2f; font: 700 16px Arial, Helvetica, sans-serif; }
      .band { fill: #1d1d1b; font: 400 18px Arial, Helvetica, sans-serif; }
      .band-b { fill: #1d1d1b; font: 700 18px Arial, Helvetica, sans-serif; }
      .on-dark { fill: #fcfbf7; font: 700 21px Arial, Helvetica, sans-serif; }
      .on-dark-2 { fill: #d9d4c7; font: 400 18px Arial, Helvetica, sans-serif; }
      .mono { fill: #1d1d1b; font: 400 15px Menlo, Consolas, monospace; }
      .footer { fill: #245f73; font: 700 20px Arial, Helvetica, sans-serif; text-anchor: middle; }
    </style>"""


def t(x, y, text, cls):
    return f'  <text class="{cls}" x="{x}" y="{y}">{escape(text)}</text>'


def box(x, y, w, h, cls, label, lines=(), label_dy=40, line_gap=26):
    out = [f'  <rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/>']
    cx = x + w / 2
    out.append(t(cx, y + label_dy, label, "label"))
    for i, line in enumerate(lines):
        out.append(t(cx, y + label_dy + 30 + i * line_gap, line, "small"))
    return out


def line(x1, y1, x2, y2, cls="line"):
    return [f'  <line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>']


def path(d, cls="line"):
    return [f'  <path class="{cls}" d="{d}"/>']


def svg(title, desc, heading, subheading, body):
    head = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{escape(title)}</title>',
        f'  <desc id="desc">{escape(desc)}</desc>',
        f"  <defs>{STYLE}\n  </defs>",
        '  <rect class="bg" width="1600" height="900"/>',
        t(60, 62, heading, "title"),
        t(60, 98, subheading, "subtitle"),
    ]
    return "\n".join(head + body + ["</svg>", ""])


def lead_and_teams(L):
    b = []
    b += box(60, 140, 340, 170, "owner", L["me"], L["me_lines"])
    b += box(630, 140, 440, 170, "core", L["lead"], L["lead_lines"])
    b += box(1200, 140, 340, 170, "project", L["corpus"], L["corpus_lines"])
    b += line(400, 200, 626, 200)
    b.append(t(420, 188, L["take"], "edge"))
    b += line(630, 262, 404, 262)
    b.append(t(420, 290, L["report"], "edge"))
    b += line(1200, 225, 1074, 225)
    b.append(t(1082, 213, L["precedents"], "edge"))
    b += line(850, 310, 850, 390, "plain")
    b += line(210, 390, 1390, 390, "plain")
    centers = [210, 505, 800, 1095, 1390]
    for cx in centers:
        b += line(cx, 390, cx, 466)
    b.append(t(868, 362, L["fanout"], "edge"))
    for i, (cx, (label, stage)) in enumerate(zip(centers, L["teams"])):
        b += box(cx - 135, 470, 270, 110, "warn" if i == 4 else "project", label, [stage])
    b += line(120, 470, 120, 314, "ownerline")
    b.append(t(134, 346, L["direct_1"], "edge-owner"))
    b.append(t(134, 368, L["direct_2"], "edge-owner"))
    b.append('  <rect class="task" x="75" y="640" width="1450" height="70" rx="14"/>')
    b.append(t(100, 682, L["roles"], "band"))
    b.append('  <rect class="warn" x="75" y="730" width="1450" height="70" rx="14"/>')
    b.append(t(100, 772, L["watch"], "band"))
    b.append(t(800, 856, L["footer"], "footer"))
    return svg(L["title"], L["desc"], L["heading"], L["subheading"], b)


def question_routing(L):
    b = []
    b += box(560, 130, 480, 90, "task", L["ask"], [L["ask_line"]], label_dy=36)
    b += line(800, 220, 800, 245, "plain")
    b += line(290, 245, 1310, 245, "plain")
    for cx in (290, 800, 1310):
        b += line(cx, 245, cx, 276)
    for x, cls, (head, sub), items in zip(
        (60, 570, 1080), ("project", "core", "owner"), L["cols"], L["items"]
    ):
        b.append(f'  <rect class="{cls}" x="{x}" y="280" width="460" height="440" rx="16"/>')
        b.append(t(x + 230, 322, head, "label"))
        b.append(t(x + 230, 350, sub, "small"))
        b.append(f'  <line class="rule" x1="{x + 24}" y1="372" x2="{x + 436}" y2="372"/>')
        for i, (label, note) in enumerate(items):
            y = 412 + i * 80
            b.append(t(x + 28, y, label, "label-l"))
            b.append(t(x + 28, y + 28, note, "small-l"))
    b.append('  <rect class="dark" x="60" y="750" width="1480" height="110" rx="16"/>')
    b.append(t(90, 792, L["night"], "on-dark"))
    b.append(t(90, 830, L["night_line"], "on-dark-2"))
    return svg(L["title"], L["desc"], L["heading"], L["subheading"], b)


def precedent_loop(L):
    b = []
    for x, (label, lines) in zip((110, 420, 730), L["sources"]):
        b += box(x, 140, 280, 120, "project", label, lines, label_dy=38)
    b += box(60, 380, 250, 140, "task", L["situation"], L["situation_lines"])
    b += box(380, 380, 300, 140, "core", L["search"], L["search_lines"])
    b += box(750, 380, 310, 140, "core", L["rules"], L["rules_lines"])
    b += box(1130, 380, 410, 140, "core", L["decision"], L["decision_lines"])
    for sx in (250, 560, 870):
        b += line(sx, 260, 530 + (sx - 560) * 0.25, 376)
    b += line(310, 450, 376, 450)
    b += line(680, 450, 746, 450)
    b += line(1060, 450, 1126, 450)
    b += box(1130, 630, 410, 130, "core", L["report"], L["report_lines"])
    b += box(700, 630, 330, 130, "owner", L["verdict"], L["verdict_lines"])
    b += line(1335, 520, 1335, 626)
    b += line(1130, 695, 1034, 695)
    b += path("M 700 695 H 40 V 200 H 106", "ownerline")
    b.append(t(80, 682, L["loop"], "edge-owner"))
    b.append(t(800, 856, L["footer"], "footer"))
    return svg(L["title"], L["desc"], L["heading"], L["subheading"], b)


def stall_watch(L):
    b = []
    for i, (label, lines) in enumerate(L["inputs"]):
        b += box(60, 150 + i * 150, 300, 120, "task", label, lines, label_dy=42)
        b += line(360, 210 + i * 150, 456, 210 + i * 150)
    b.append('  <rect class="core" x="460" y="130" width="440" height="580" rx="16"/>')
    b.append(t(680, 172, L["detector"], "label"))
    b.append('  <line class="rule" x1="484" y1="194" x2="876" y2="194"/>')
    for i, (code, text) in enumerate(L["kinds"]):
        y = 230 + i * 44
        b.append(t(488, y, code, "mono"))
        b.append(t(648, y, text, "small-l"))
    b += line(900, 420, 996, 420, "line")
    steps = L["steps"]
    classes = ("task", "project", "project", "owner")
    for i, ((label, lines), cls) in enumerate(zip(steps, classes)):
        y = 130 + i * 150
        b += box(1000, y, 540, 120, cls, label, lines, label_dy=44)
        if i:
            b += line(1270, y - 30, 1270, y - 4)
    b.append('  <rect class="warn" x="60" y="740" width="1480" height="120" rx="16"/>')
    b.append(t(90, 780, L["case"], "band-b"))
    b.append(t(90, 810, L["case_1"], "band"))
    b.append(t(90, 838, L["case_2"], "band"))
    return svg(L["title"], L["desc"], L["heading"], L["subheading"], b)


TEXT = {
    "ru": {
        "lead-and-teams.svg": (lead_and_teams, {
            "title": "Руководитель между мной и командами",
            "desc": "Я запускаю руководителя словом «принимай» и получаю отчёт о смене. Руководитель берёт прецеденты из моего корпуса решений, запускает пять команд и решает их споры. Команды сами спрашивают меня в Telegram только о проде, продукте, цифрах клиента и тратах.",
            "heading": "Руководитель между мной и командами",
            "subheading": "Человек здесь один — я. Руководитель и все роли в командах — ИИ-агенты.",
            "me": "Я",
            "me_lines": ["раскладываю задачи", "отвечаю на шесть видов вопросов", "ставлю вердикт по отчёту"],
            "lead": "ИИ-руководитель",
            "lead_lines": ["действует в своих полномочиях", "решает по моим прецедентам", "следит за зависаниями"],
            "corpus": "Мой корпус",
            "corpus_lines": ["11 138 решений из сессий", "ответы в Telegram", "калибровка"],
            "take": "«принимай»",
            "report": "отчёт о смене",
            "precedents": "прецеденты",
            "fanout": "запускает, решает споры, перезапускает, вливает в develop",
            "teams": [
                ("Команда 1", "этап: план"),
                ("Команда 2", "этап: код и PR"),
                ("Команда 3", "этап: QA на стенде"),
                ("Команда 4", "этап: аудит QA"),
                ("Команда 5", "ждёт staging"),
            ],
            "direct_1": "Telegram: прод, продукт,",
            "direct_2": "цифры клиента, траты",
            "roles": "Каждая команда — ИИ-агенты: техлид, ревьюер плана, аналитик приёмки, ревьюер нагрузки, QA, аудитор QA, UX-ревьюер, инженер окружения",
            "watch": "Раз в две минуты руководитель сверяет журналы всех сессий с процессами и открытыми файлами",
            "footer": "Команды спрашивают меня сами только по шести причинам. Остальное решают они или руководитель.",
        }),
        "question-routing.svg": (question_routing, {
            "title": "Куда идёт вопрос команды",
            "desc": "Вопрос техлида уходит в одну из трёх колонок. Команда сама решает лишний раунд ревью, занятый стенд, спор об интерфейсе и спорную сумму. Руководитель решает споры команд, долгие прогоны, ревью по кругу и очередь. Меня спрашивают о проде, продукте, цифрах клиента и новых тратах. Ночной вопрос ждёт утра.",
            "heading": "Куда идёт вопрос команды",
            "subheading": "Правила собраны из моих прошлых ответов",
            "ask": "Вопрос у ИИ-техлида",
            "ask_line": "роли команды наружу не пишут",
            "cols": [
                ("Решает команда", "и пишет решение в журнал"),
                ("Решает руководитель", "так, как решил бы я"),
                ("Спрашивают меня", "в Telegram, с кнопками ответа"),
            ],
            "items": [
                [("Ещё раунд ревью", "я одобрил 21 раз из 21"),
                 ("Стенд занят", "«жди»: так я ответил в 6 случаях из 7"),
                 ("Спор об интерфейсе", "решает UX-ревьюер"),
                 ("Спорная сумма", "пометить, не менять")],
                [("Чей стенд или PR", "спор между командами"),
                 ("Прогон дольше двух часов", "только машинное время"),
                 ("Ревью по кругу", "ещё раунд или закрыть остаток"),
                 ("Очередь", "порядок и перезапуск упавших")],
                [("Прод и клиенты", "выкатка, письма клиентам"),
                 ("Продукт и право", "8 из 10 моих правок делали продукт полнее"),
                 ("Цифра у клиента", "которую он уже видел"),
                 ("Новые траты", "и мои «спроси перед»")],
            ],
            "night": "Ночью я почти не отвечаю",
            "night_line": "С 01:00 до 06:00 — два ответа за 50 дней, в девятом часу утра — 24. Ночной вопрос ждёт 08:30, команда пока делает другие задачи.",
        }),
        "precedent-loop.svg": (precedent_loop, {
            "title": "Как руководитель решает за меня",
            "desc": "Ситуация уходит в поиск прецедентов по трём источникам: калибровке, решениям из сессий и ответам в Telegram. Записанное правило побеждает прецедент. Решение с датами прецедентов попадает в отчёт о смене, мой вердикт возвращается в корпус как калибровка.",
            "heading": "Как руководитель решает за меня",
            "subheading": "Решение начинается с прецедентов и заканчивается моим вердиктом",
            "sources": [
                ("Калибровка", ["прогноз против моего выбора"]),
                ("Решения из сессий", ["11 138, Claude Code и Codex"]),
                ("Ответы в Telegram", ["вопрос, варианты, мой выбор"]),
            ],
            "situation": "Ситуация",
            "situation_lines": ["«стенд занят", "три часа»"],
            "search": "Поиск прецедентов",
            "search_lines": ["по словам, не по смыслу", "свежий побеждает старый"],
            "rules": "Правило или прецедент",
            "rules_lines": ["побеждает правило,", "спор уходит мне в отчёт"],
            "decision": "Решение в его полномочиях",
            "decision_lines": ["ссылки на прецеденты по дате", "без сырого текста корпуса"],
            "report": "Отчёт о смене",
            "report_lines": ["решения, факты, прецеденты", "мои новые ответы против правил"],
            "verdict": "Мой вердикт",
            "verdict_lines": ["согласен или нет", "правило меняю я"],
            "loop": "несогласие возвращается в корпус как калибровка",
            "footer": "Индекс обновляется при каждой приёмке смены. В первый раз он отставал на три недели.",
        }),
        "stall-watch.svg": (stall_watch, {
            "title": "Зависания видно только снаружи",
            "desc": "Руководитель раз в две минуты сверяет журналы сессий, список процессов и открытые файлы. Детектор различает 11 видов вечной остановки. Находку руководитель подтверждает по системе, затем будит сессию, перезапускает её или сообщает мне. Пример: канал, который держали серверы стенда.",
            "heading": "Зависания видно только снаружи",
            "subheading": "Раз в две минуты руководитель сверяет журналы сессий с процессами и открытыми файлами",
            "inputs": [
                ("Журналы сессий", ["последняя запись, чего ждёт"]),
                ("Процессы", ["ps: кто ещё жив"]),
                ("Открытые файлы", ["lsof: кто держит канал"]),
            ],
            "detector": "Детектор: 11 видов остановки",
            "kinds": [
                ("LOST_NOTIFY", "уведомление не дошло"),
                ("PIPE_HELD", "канал держит чужой процесс"),
                ("DEAD_TASK", "задача умерла молча"),
                ("NO_WAKE", "сессию нечему разбудить"),
                ("DELEGATE_HUNG", "завис субагент"),
                ("OWNER_Q", "ждёт моего ответа"),
                ("API_ERROR", "ошибка API"),
                ("MODEL_HUNG", "модель не ответила"),
                ("TOOL_HUNG", "инструмент висит 20 минут"),
                ("LONG_IDLE", "долгий простой"),
                ("SESSION_DEAD", "процесс Claude пропал"),
            ],
            "steps": [
                ("Подтвердить по системе", ["один сигнал — ещё не остановка"]),
                ("Разбудить или показать вывод", ["сообщение сессии с фактами и шагом"]),
                ("Перезапустить", ["два сигнала, не чаще раза в час на задачу"]),
                ("Сообщить мне", ["сессия снова умерла в течение часа"]),
            ],
            "case": "Суббота, утро: PIPE_HELD",
            "case_1": "Скрипт стенда завершился, но запущенные им серверы унаследовали пишущий конец канала. tail ждал конца данных, сессия ждала tail.",
            "case_2": "Руководитель нашёл держателей канала через lsof и написал команде: стенд поднят, не жди, иди на QA.",
        }),
    },
    "en": {
        "lead-and-teams.svg": (lead_and_teams, {
            "title": "A lead between me and the teams",
            "desc": "I start the lead with the word 'take over' and get a shift report back. The lead draws precedents from my decision corpus, launches five teams and settles their disputes. The teams ask me in Telegram themselves only about production, product, client numbers and spend.",
            "heading": "A lead between me and the teams",
            "subheading": "I am the only human here. The lead and every team role are AI agents.",
            "me": "Me",
            "me_lines": ["split the work", "answer six kinds of questions", "give a verdict on the report"],
            "lead": "AI lead",
            "lead_lines": ["acts within its authority", "decides from my precedents", "watches for stalls"],
            "corpus": "My corpus",
            "corpus_lines": ["11,138 session decisions", "Telegram answers", "calibration"],
            "take": "“take over”",
            "report": "shift report",
            "precedents": "precedents",
            "fanout": "launches, settles disputes, restarts, merges into develop",
            "teams": [
                ("Team 1", "stage: plan"),
                ("Team 2", "stage: code and PR"),
                ("Team 3", "stage: QA on a stand"),
                ("Team 4", "stage: QA audit"),
                ("Team 5", "waiting for staging"),
            ],
            "direct_1": "Telegram: production,",
            "direct_2": "product, client numbers, spend",
            "roles": "Every team is AI agents: tech lead, plan reviewer, acceptance analyst, load reviewer, QA, QA auditor, UX reviewer, environment engineer",
            "watch": "Every two minutes the lead checks every session's transcript against processes and open files",
            "footer": "The teams ask me themselves for six reasons only. They or the lead decide the rest.",
        }),
        "question-routing.svg": (question_routing, {
            "title": "Where a team's question goes",
            "desc": "A tech lead's question goes to one of three columns. The team decides an extra review round, a busy stand, a UI dispute and a disputed amount. The lead decides disputes between teams, long runs, looping reviews and the queue. I am asked about production, product, client numbers and new spend. A night question waits for the morning.",
            "heading": "Where a team's question goes",
            "subheading": "The rules come from my past answers",
            "ask": "The AI tech lead has a question",
            "ask_line": "team roles never write outside",
            "cols": [
                ("The team decides", "and logs the decision"),
                ("The lead decides", "the way I would"),
                ("They ask me", "in Telegram, with answer buttons"),
            ],
            "items": [
                [("One more review round", "I approved 21 times out of 21"),
                 ("The stand is busy", "“wait”: my answer in 6 cases of 7"),
                 ("A UI dispute", "the UX reviewer decides"),
                 ("A disputed amount", "flag it, do not change it")],
                [("Whose stand or PR", "a dispute between teams"),
                 ("A run over two hours", "machine time only"),
                 ("A looping review", "one more round or close the rest"),
                 ("The queue", "order and restarting the fallen")],
                [("Production and clients", "rollouts, client emails"),
                 ("Product and legal", "8 of my 10 edits made the product fuller"),
                 ("A number the client saw", "already delivered to them"),
                 ("New spend", "and my “ask me before”")],
            ],
            "night": "I barely answer at night",
            "night_line": "From 01:00 to 06:00, two answers in 50 days; between 08:00 and 09:00, 24. A night question waits for 08:30 while the team works on other tasks.",
        }),
        "precedent-loop.svg": (precedent_loop, {
            "title": "How the lead decides for me",
            "desc": "A situation goes into a precedent search over three sources: calibration, session decisions and Telegram answers. A written rule beats a precedent. The decision, with dated precedents, goes into the shift report, and my verdict returns to the corpus as calibration.",
            "heading": "How the lead decides for me",
            "subheading": "A decision starts from precedents and ends with my verdict",
            "sources": [
                ("Calibration", ["prediction versus my choice"]),
                ("Session decisions", ["11,138, Claude Code and Codex"]),
                ("Telegram answers", ["question, options, my choice"]),
            ],
            "situation": "Situation",
            "situation_lines": ["“the stand has been", "busy for three hours”"],
            "search": "Precedent search",
            "search_lines": ["by words, not by meaning", "recent beats old"],
            "rules": "Rule or precedent",
            "rules_lines": ["the rule wins,", "the conflict goes to my report"],
            "decision": "A decision within its authority",
            "decision_lines": ["precedents cited by date", "no raw corpus text"],
            "report": "Shift report",
            "report_lines": ["decisions, facts, precedents", "my new answers against the rules"],
            "verdict": "My verdict",
            "verdict_lines": ["agree or not", "I change the rules"],
            "loop": "a disagreement returns to the corpus as calibration",
            "footer": "The index is refreshed at every takeover. The first time, it was three weeks behind.",
        }),
        "stall-watch.svg": (stall_watch, {
            "title": "Stalls are visible only from outside",
            "desc": "Every two minutes the lead checks session transcripts, the process list and open files. The detector tells 11 kinds of permanent stop apart. The lead confirms a finding against the system, then wakes the session, restarts it or tells me. Example: a pipe held by the stand's servers.",
            "heading": "Stalls are visible only from outside",
            "subheading": "Every two minutes the lead checks session transcripts against processes and open files",
            "inputs": [
                ("Session transcripts", ["last entry, what it waits for"]),
                ("Processes", ["ps: who is still alive"]),
                ("Open files", ["lsof: who holds the pipe"]),
            ],
            "detector": "Detector: 11 kinds of stop",
            "kinds": [
                ("LOST_NOTIFY", "a notification never arrived"),
                ("PIPE_HELD", "another process holds the pipe"),
                ("DEAD_TASK", "a task died silently"),
                ("NO_WAKE", "nothing can wake the session"),
                ("DELEGATE_HUNG", "a subagent hung"),
                ("OWNER_Q", "waiting for my answer"),
                ("API_ERROR", "an API error"),
                ("MODEL_HUNG", "the model never replied"),
                ("TOOL_HUNG", "a tool hung for 20 minutes"),
                ("LONG_IDLE", "a long idle"),
                ("SESSION_DEAD", "the Claude process is gone"),
            ],
            "steps": [
                ("Confirm against the system", ["one signal is not yet a stop"]),
                ("Wake it or show the output", ["a message with the facts and the next step"]),
                ("Restart", ["two signals, at most once an hour per task"]),
                ("Tell me", ["the session died again within the hour"]),
            ],
            "case": "Saturday morning: PIPE_HELD",
            "case_1": "The stand script had exited, but the servers it started inherited the write end of the pipe. tail waited for end of data; the session waited for tail.",
            "case_2": "The lead found the pipe's holders with lsof and told the team: the stand is up, stop waiting, go to QA.",
        }),
    },
}


def main() -> None:
    for lang, diagrams in TEXT.items():
        BUNDLES[lang].mkdir(parents=True, exist_ok=True)
        for name, (build, labels) in diagrams.items():
            (BUNDLES[lang] / name).write_text(build(labels), encoding="utf-8")
            print(BUNDLES[lang] / name)


if __name__ == "__main__":
    main()
