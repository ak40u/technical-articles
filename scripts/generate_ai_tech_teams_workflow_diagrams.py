#!/usr/bin/env python3
"""Generate the four page-bundle diagrams of the ai-tech-teams-workflow article, in Russian and English.

Shares the drawing helpers and palette of generate_ai_tech_teams_lead_diagrams.py.
"""
from __future__ import annotations

from pathlib import Path

from generate_ai_tech_teams_lead_diagrams import box, line, path, svg, t

ROOT = Path(__file__).resolve().parent.parent
BUNDLES = {
    "ru": ROOT / "content/ru/articles/ai-tech-teams-workflow",
    "en": ROOT / "content/en/articles/ai-tech-teams-workflow",
}


def team_roles(L):
    b = []
    b += box(620, 140, 360, 110, "project", L["reviewer"], [L["reviewer_line"]])
    b += box(80, 330, 380, 150, "core", L["orchestrator"], L["orchestrator_lines"])
    b.append('  <rect class="task" x="560" y="360" width="480" height="90" rx="14"/>')
    b.append(t(800, 398, L["queue"], "label"))
    b.append(t(800, 428, L["queue_line"], "small"))
    b += box(1140, 330, 380, 150, "project", L["qa"], L["qa_lines"])
    b += line(460, 392, 556, 392)
    b += line(560, 422, 464, 422)
    b += line(1040, 392, 1136, 392)
    b += line(1140, 422, 1044, 422)
    b += path("M 200 330 V 195 H 616")
    b.append(t(360, 183, L["plan"], "edge"))
    b += line(800, 250, 800, 356)
    b.append(t(814, 310, L["findings"], "edge"))
    b += line(270, 480, 270, 576)
    b.append(t(284, 534, L["screenshots"], "edge"))
    b += line(1330, 480, 1330, 576)
    b.append(t(1344, 534, L["verdict"], "edge"))
    b += box(80, 580, 380, 110, "project", L["ux"], [L["ux_line"]])
    b += box(1140, 580, 380, 110, "project", L["auditor"], [L["auditor_line"]])
    b += line(270, 690, 270, 746)
    b += line(1330, 690, 1330, 746)
    b.append('  <rect class="dark" x="80" y="750" width="1440" height="110" rx="16"/>')
    b.append(t(110, 792, L["gate"], "on-dark"))
    b.append(t(110, 830, L["gate_line"], "on-dark-2"))
    return svg(L["title"], L["desc"], L["heading"], L["subheading"], b)


def chip(x, y, w, h, cls, number, lines):
    out = [f'  <rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>']
    cy = y + h / 2
    out.append(t(x + 16, cy + 7, number, "label-l"))
    if len(lines) == 1:
        out.append(t(x + 80, cy + 6, lines[0], "small-l"))
    else:
        out.append(t(x + 80, cy - 4, lines[0], "small-l"))
        out.append(t(x + 80, cy + 18, lines[1], "small-l"))
    return out


def run_stages(L):
    b = []
    xs = [60, 360, 660, 960, 1260]
    for i, (x, (phase, stages)) in enumerate(zip(xs, L["phases"])):
        b.append(f'  <rect class="task" x="{x}" y="128" width="276" height="56" rx="12"/>')
        b.append(t(x + 138, 164, phase, "label"))
        if i:
            b += line(x - 24, 156, x - 4, 156)
        for j, (number, lines, cls) in enumerate(stages):
            b += chip(x, 204 + j * 78, 276, 66, cls, number, lines)
    b.append('  <rect class="dark" x="60" y="740" width="1476" height="110" rx="16"/>')
    b.append(t(90, 782, L["band"], "on-dark"))
    b.append(t(90, 820, L["band_line"], "on-dark-2"))
    return svg(L["title"], L["desc"], L["heading"], L["subheading"], b)


def parallel_teams(L):
    b = []
    b += box(60, 320, 250, 180, "owner", L["batch"], L["batch_lines"], label_dy=48)
    b += box(380, 360, 200, 100, "core", L["queue"], [L["queue_line"]])
    b += line(310, 410, 376, 410)
    lanes = [190, 350, 510, 670]
    b += line(580, 410, 630, 410, "plain")
    b += line(630, lanes[0], 630, lanes[-1], "plain")
    b.append(t(1100, 142, L["shared"], "edge"))
    for i, (cy, team) in enumerate(zip(lanes, L["teams"])):
        b += line(630, cy, 676, cy)
        b += box(680, cy - 45, 220, 90, "task" if i == 3 else "project", team, label_dy=52)
        chips = [(950, 110, "project", L["pr"]), (1100, 180, "warn", L["stand"]),
                 (1320, 90, "project", "QA"), (1450, 110, "project", L["result"])]
        prev = 900
        for x, w, cls, text in chips:
            b += line(prev, cy, x - 4, cy)
            b.append(f'  <rect class="{cls}" x="{x}" y="{cy - 32}" width="{w}" height="64" rx="12"/>')
            b.append(t(x + w / 2, cy + 7, text, "small"))
            prev = x + w
    b.append('  <rect class="task" x="60" y="755" width="1480" height="100" rx="16"/>')
    b.append(t(90, 795, L["band"], "band-b"))
    b.append(t(90, 830, L["band_line"], "band"))
    return svg(L["title"], L["desc"], L["heading"], L["subheading"], b)


def rule_lifecycle(L):
    b = []
    b += box(60, 150, 220, 100, "task", L["run"], label_dy=58)
    b += box(340, 150, 260, 100, "core", L["retro"], label_dy=58)
    b += box(660, 140, 360, 120, "core", L["question"], [L["question_line"]])
    b += line(280, 200, 336, 200)
    b += line(600, 200, 656, 200)
    b += line(760, 260, 710, 356)
    b.append(t(695, 318, L["yes"], "edge"))
    b += line(920, 260, 1150, 356)
    b.append(t(1060, 300, L["no"], "edge"))
    b += box(560, 360, 300, 120, "project", L["review"], L["review_lines"])
    b += box(1060, 360, 340, 120, "task", L["wait"], [L["wait_line"]])
    b += line(710, 480, 710, 556)
    b.append(t(724, 524, L["accept"], "edge"))
    b += line(1230, 480, 1230, 556)
    b.append(t(1244, 524, L["second"], "edge"))
    b += box(560, 560, 300, 100, "core", L["rule"], label_dy=58)
    b += box(1060, 560, 340, 100, "project", L["promotion"], label_dy=58)
    b += line(1060, 610, 864, 610)
    b += box(60, 360, 420, 150, "warn", L["escaped"], L["escaped_lines"])
    b += line(270, 510, 270, 556)
    b += box(60, 560, 420, 100, "project", L["qa_check"], label_dy=58)
    b += path("M 270 660 V 790 H 476")
    b += line(710, 660, 710, 736)
    b += box(480, 740, 460, 100, "project", L["log"], [L["log_line"]])
    b += line(940, 790, 1056, 790)
    b += box(1060, 740, 340, 100, "warn", L["remove"], [L["remove_line"]])
    return svg(L["title"], L["desc"], L["heading"], L["subheading"], b)


MAIN, SUB, GATE = "project", "task", "core"

TEXT = {
    "ru": {
        "team-roles.svg": (team_roles, {
            "title": "Одна техкоманда: роли и очередь сообщений",
            "desc": "Оркестратор-техлид и QA-агент обмениваются сообщениями через очередь. План-ревьюер получает план и отдаёт находки. UX-ревьюер проверяет скриншоты, QA-аудитор проверяет вердикт QA. Закрывает запуск финальная проверка, которой нужны все вердикты.",
            "heading": "Одна техкоманда: роли и очередь сообщений",
            "subheading": "Роли передают друг другу доказательства, черновики рассуждений остаются у автора",
            "reviewer": "План-ревьюер",
            "reviewer_line": "проверяет план до кода",
            "orchestrator": "Оркестратор-техлид",
            "orchestrator_lines": ["план, код, PR,", "цикл выполнения"],
            "queue": "Очередь сообщений",
            "queue_line": "между ролями ходят доказательства",
            "qa": "QA-агент",
            "qa_lines": ["проходит путь пользователя", "на тестовом стенде"],
            "plan": "план",
            "findings": "находки",
            "screenshots": "скриншоты",
            "verdict": "QA-вердикт",
            "ux": "UX-ревьюер",
            "ux_line": "сверяет скриншоты с UX-договорённостью",
            "auditor": "QA-аудитор",
            "auditor_line": "проверяет доказательства QA",
            "gate": "Закрывает запуск служебная финальная проверка",
            "gate_line": "Закрывает запуск только при положительных вердиктах QA и аудита QA, для UI-задач ещё и UX-ревью. Убедить её нельзя.",
        }),
        "run-stages.svg": (run_stages, {
            "title": "Как проходит один запуск",
            "desc": "Пять групп стадий: подготовка, план, реализация, проверка и завершение. От предпроверки до уборки, с финальной проверкой на стадии 10.",
            "heading": "Как проходит один запуск",
            "subheading": "Стадии от предпроверки до уборки",
            "phases": [
                ("Подготовка", [("0", ["предпроверка"], MAIN), ("1", ["постановка"], MAIN),
                                ("1b", ["воспроизведение бага", "до исправления"], SUB)]),
                ("План", [("2", ["план"], MAIN), ("2b", ["сравнение вариантов", "без подсказок"], SUB),
                          ("2c", ["UX-договорённость"], SUB), ("3", ["ревью плана"], MAIN),
                          ("3b", ["заявка на область", "изменений"], SUB), ("3c", ["критерии → задача"], SUB)]),
                ("Реализация", [("4", ["реализация"], MAIN), ("5", ["тесты"], MAIN),
                                ("5.5", ["сверка с планом"], SUB), ("6", ["PR, CI, слияние"], MAIN),
                                ("7", ["деплой на", "тестовый стенд"], MAIN)]),
                ("Проверка", [("8", ["QA до разрешения"], MAIN), ("8.5", ["аудит QA"], SUB),
                              ("8.6", ["UX-ревью"], SUB), ("9", ["подтверждение"], MAIN),
                              ("10", ["финальная проверка"], GATE)]),
                ("Завершение", [("11", ["ретроспектива"], MAIN), ("12–13", ["уборка"], MAIN)]),
            ],
            "band": "Каждая стадия оставляет доказательства",
            "band_line": "Поэтому запуск восстанавливается после падения процесса, и по каждой стадии видно, что сделано.",
        }),
        "parallel-teams.svg": (parallel_teams, {
            "title": "Несколько команд параллельно",
            "desc": "Пачка задач уходит в очередь, очередь раскладывает её по автономным командам. Каждая команда проходит PR, окно общего стенда и QA до итога. Узкое место — инфраструктура.",
            "heading": "Несколько команд параллельно",
            "subheading": "Очередь раскладывает пачку задач по автономным техкомандам",
            "batch": "Пачка задач",
            "batch_lines": ["12 багов", "5 UI-полировок", "3 интеграционных долга"],
            "queue": "Очередь",
            "queue_line": "раздаёт задачи",
            "shared": "общий стенд, окна по очереди",
            "teams": ["Команда A", "Команда B", "Команда C", "Команда N"],
            "pr": "PR",
            "stand": "окно стенда",
            "result": "итог",
            "band": "Узкое место — инфраструктура: CI, тестовый стенд, лимиты моделей, окна QA",
            "band_line": "Рабочая копия, изолированное хранилище, очередь и окно QA дают ещё одну автономную команду.",
        }),
        "rule-lifecycle.svg": (rule_lifecycle, {
            "title": "Как процесс учится на ошибках",
            "desc": "Урок из ретроспективы становится правилом после внешней проверки или после второго случая. Пропущенный баг добавляет проверку в QA-протокол. Журнал показывает, окупаются ли правила и проверки; неокупившееся снимают и записывают причину.",
            "heading": "Как процесс учится на ошибках",
            "subheading": "Урок становится правилом после внешней проверки или второго случая, и правило можно снять",
            "run": "Запуск",
            "retro": "Ретроспектива",
            "question": "Очевидное исправление?",
            "question_line": "или повторяющийся случай",
            "yes": "да",
            "no": "нет, но повторяется",
            "review": "Внешняя проверка",
            "review_lines": ["повторяется ли проблема,", "не шире ли правило, чем нужно"],
            "wait": "Ждём второго случая",
            "wait_line": "находка ещё не правило",
            "accept": "принять",
            "second": "второй случай",
            "rule": "Правило в справочнике",
            "promotion": "Повышение",
            "escaped": "Пропущенный баг",
            "escaped_lines": ["найден после одобрения QA и аудитора", "какая проверка поймала бы", "этот класс ошибок?"],
            "qa_check": "Новая проверка в QA-протоколе",
            "log": "Журнал и проверка пользы правил",
            "log_line": "растут ли раунды QA, есть ли ложные отказы",
            "remove": "Снятие правила",
            "remove_line": "остаётся запись о причине",
        }),
    },
    "en": {
        "team-roles.svg": (team_roles, {
            "title": "One engineering team: roles and the message queue",
            "desc": "The orchestrator tech lead and the QA agent exchange messages through a queue. The plan reviewer gets the plan and returns findings. The UX reviewer checks screenshots, the QA auditor checks the QA verdict. A final check that needs every verdict closes the run.",
            "heading": "One team: roles and the message queue",
            "subheading": "Roles pass each other evidence; the drafts of their reasoning stay with the author",
            "reviewer": "Plan reviewer",
            "reviewer_line": "checks the plan before code",
            "orchestrator": "Orchestrator tech lead",
            "orchestrator_lines": ["plan, code, PR,", "the execution loop"],
            "queue": "Message queue",
            "queue_line": "evidence travels between roles",
            "qa": "QA agent",
            "qa_lines": ["walks the user path", "on staging"],
            "plan": "plan",
            "findings": "findings",
            "screenshots": "screenshots",
            "verdict": "QA verdict",
            "ux": "UX reviewer",
            "ux_line": "compares screenshots with the UX agreement",
            "auditor": "QA auditor",
            "auditor_line": "checks QA's evidence",
            "gate": "A service final check closes the run",
            "gate_line": "It closes a run only with positive QA and QA-audit verdicts, plus a UX verdict for UI tasks. It cannot be persuaded.",
        }),
        "run-stages.svg": (run_stages, {
            "title": "How one run goes",
            "desc": "Five groups of stages: preparation, plan, implementation, verification and wrap-up. From preflight to cleanup, with the final check at stage 10.",
            "heading": "How one run goes",
            "subheading": "Stages from preflight to cleanup",
            "phases": [
                ("Preparation", [("0", ["preflight"], MAIN), ("1", ["framing"], MAIN),
                                 ("1b", ["reproduce the bug", "before the fix"], SUB)]),
                ("Plan", [("2", ["plan"], MAIN), ("2b", ["blind option", "comparison"], SUB),
                          ("2c", ["UX agreement"], SUB), ("3", ["plan review"], MAIN),
                          ("3b", ["change-scope claim"], SUB), ("3c", ["criteria → task"], SUB)]),
                ("Implementation", [("4", ["implementation"], MAIN), ("5", ["tests"], MAIN),
                                    ("5.5", ["plan alignment"], SUB), ("6", ["PR, CI, merge"], MAIN),
                                    ("7", ["deploy to staging"], MAIN)]),
                ("Verification", [("8", ["QA until approval"], MAIN), ("8.5", ["QA audit"], SUB),
                                  ("8.6", ["UX review"], SUB), ("9", ["confirmation"], MAIN),
                                  ("10", ["final check"], GATE)]),
                ("Wrap-up", [("11", ["retrospective"], MAIN), ("12–13", ["cleanup"], MAIN)]),
            ],
            "band": "Every stage leaves evidence",
            "band_line": "So a run recovers after a process failure, and each stage shows what was done.",
        }),
        "parallel-teams.svg": (parallel_teams, {
            "title": "Several teams in parallel",
            "desc": "A task batch goes into a queue, and the queue distributes it among autonomous teams. Each team goes through a PR, a window on the shared staging and QA to a result. Infrastructure is the bottleneck.",
            "heading": "Several teams in parallel",
            "subheading": "The queue distributes a task batch among autonomous engineering teams",
            "batch": "Task batch",
            "batch_lines": ["12 bugs", "5 UI polish items", "3 integration-debt items"],
            "queue": "Queue",
            "queue_line": "hands out tasks",
            "shared": "shared staging, windows in turn",
            "teams": ["Team A", "Team B", "Team C", "Team N"],
            "pr": "PR",
            "stand": "staging window",
            "result": "result",
            "band": "The bottleneck is infrastructure: CI, staging, model limits, QA windows",
            "band_line": "A worktree, an isolated store, a queue and a QA window add one more autonomous team.",
        }),
        "rule-lifecycle.svg": (rule_lifecycle, {
            "title": "How the process learns from mistakes",
            "desc": "A lesson from a retrospective becomes a rule after an external review or after a second case. An escaped bug adds a check to the QA protocol. The log shows whether rules and checks pay for themselves; one that does not is removed, and the reason is recorded.",
            "heading": "How the process learns from mistakes",
            "subheading": "A lesson becomes a rule after an external review or a second case, and a rule can be removed",
            "run": "Run",
            "retro": "Retrospective",
            "question": "An obvious fix?",
            "question_line": "or a recurring case",
            "yes": "yes",
            "no": "no, but it recurs",
            "review": "External review",
            "review_lines": ["does the problem recur,", "is the rule broader than needed"],
            "wait": "Wait for a second case",
            "wait_line": "the finding is not a rule yet",
            "accept": "accept",
            "second": "second case",
            "rule": "Rule in the handbook",
            "promotion": "Promotion",
            "escaped": "Escaped bug",
            "escaped_lines": ["found after QA and audit approval", "what check would have caught", "this class of bug?"],
            "qa_check": "New check in the QA protocol",
            "log": "Log and rule value check",
            "log_line": "do QA rounds grow, are there false rejections",
            "remove": "Rule removal",
            "remove_line": "a note on the reason stays",
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
