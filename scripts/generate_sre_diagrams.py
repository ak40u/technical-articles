#!/usr/bin/env python3
"""Generate the four page-bundle diagrams of the ai-sre-engineer article, in Russian and English.

The visual language follows the ai-tech-teams-lead diagrams: warm background, teal boxes for
the model, neutral boxes for plain code, green for the agents, rust for the owner. The canvas
is 1200 px wide with large type, so a diagram stays legible when scaled to a phone screen.
Every label is plain SVG text and can be edited here or in the output file.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
BUNDLES = {
    "ru": ROOT / "content/ru/articles/ai-sre-engineer",
    "en": ROOT / "content/en/articles/ai-sre-engineer",
}
WIDTH = 1200

STYLE = """
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#7a776f"/>
    </marker>
    <marker id="arrow-owner" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#8f4f2f"/>
    </marker>
    <marker id="arrow-ok" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#4f7b5d"/>
    </marker>
    <marker id="arrow-warn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#a34a3f"/>
    </marker>
    <style>
      .bg { fill: #fcfbf7; }
      .owner { fill: #f7eadc; stroke: #8f4f2f; stroke-width: 3; }
      .core { fill: #e8f2f4; stroke: #245f73; stroke-width: 3; }
      .chip { fill: #ffffff; stroke: #245f73; stroke-width: 2; }
      .chip-quiet { fill: #f3f0e8; stroke: #8b867d; stroke-width: 2; }
      .project { fill: #edf6ef; stroke: #4f7b5d; stroke-width: 2.5; }
      .task { fill: #f3f0e8; stroke: #8b867d; stroke-width: 2; }
      .code { fill: #f3f0e8; stroke: #2b2a27; stroke-width: 3; }
      .warn { fill: #fae9e5; stroke: #a34a3f; stroke-width: 2.5; }
      .dark { fill: #2b2a27; }
      .line { fill: none; stroke: #7a776f; stroke-width: 3; marker-end: url(#arrow); }
      .plain { fill: none; stroke: #7a776f; stroke-width: 3; }
      .okline { fill: none; stroke: #4f7b5d; stroke-width: 3; marker-end: url(#arrow-ok); }
      .warnline { fill: none; stroke: #a34a3f; stroke-width: 3; marker-end: url(#arrow-warn); }
      .ownerline { fill: none; stroke: #8f4f2f; stroke-width: 3; stroke-dasharray: 10 8; marker-end: url(#arrow-owner); }
      .blocked { fill: none; stroke: #a34a3f; stroke-width: 3; stroke-dasharray: 8 8; }
      .cross { fill: #fcfbf7; stroke: #a34a3f; stroke-width: 3; }
      .cross-x { stroke: #a34a3f; stroke-width: 4; stroke-linecap: round; }
      .divider { stroke: #8b867d; stroke-width: 2.5; stroke-dasharray: 10 8; }
      .rule { stroke: #ded9cd; stroke-width: 1.5; }
      .title { fill: #1d1d1b; font: 800 40px Arial, Helvetica, sans-serif; }
      .subtitle { fill: #6c6860; font: 400 23px Arial, Helvetica, sans-serif; }
      .label { fill: #1d1d1b; font: 700 26px Arial, Helvetica, sans-serif; text-anchor: middle; }
      .label-l { fill: #1d1d1b; font: 700 24px Arial, Helvetica, sans-serif; }
      .chip-t { fill: #1d1d1b; font: 700 22px Arial, Helvetica, sans-serif; text-anchor: middle; }
      .small { fill: #5f5b54; font: 400 21px Arial, Helvetica, sans-serif; text-anchor: middle; }
      .small-l { fill: #5f5b54; font: 400 20px Arial, Helvetica, sans-serif; }
      .edge { fill: #5f5b54; font: 700 19px Arial, Helvetica, sans-serif; }
      .edge-m { fill: #5f5b54; font: 700 19px Arial, Helvetica, sans-serif; text-anchor: middle; }
      .edge-owner { fill: #8f4f2f; font: 700 19px Arial, Helvetica, sans-serif; }
      .edge-warn { fill: #a34a3f; font: 700 19px Arial, Helvetica, sans-serif; }
      .on-dark { fill: #fcfbf7; font: 700 22px Arial, Helvetica, sans-serif; }
      .on-dark-2 { fill: #d9d4c7; font: 400 20px Arial, Helvetica, sans-serif; }
    </style>"""


def t(x, y, text, cls):
    return f'  <text class="{cls}" x="{x}" y="{y}">{escape(text)}</text>'


def box(x, y, w, h, cls, label, lines=(), label_dy=42, line_gap=28):
    out = [f'  <rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/>']
    cx = x + w / 2
    out.append(t(cx, y + label_dy, label, "label"))
    for i, line in enumerate(lines):
        out.append(t(cx, y + label_dy + 34 + i * line_gap, line, "small"))
    return out


def line(x1, y1, x2, y2, cls="line"):
    return [f'  <line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>']


def path(d, cls="line"):
    return [f'  <path class="{cls}" d="{d}"/>']


def band(y, h, head, lines):
    out = [f'  <rect class="dark" x="60" y="{y}" width="{WIDTH - 120}" height="{h}" rx="16"/>']
    out.append(t(90, y + 42, head, "on-dark"))
    for i, text in enumerate(lines):
        out.append(t(90, y + 78 + i * 30, text, "on-dark-2"))
    return out


def svg(height, title, desc, heading, subheading, body):
    head = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{escape(title)}</title>',
        f'  <desc id="desc">{escape(desc)}</desc>',
        f"  <defs>{STYLE}\n  </defs>",
        f'  <rect class="bg" width="{WIDTH}" height="{height}"/>',
        t(60, 68, heading, "title"),
        t(60, 106, subheading, "subtitle"),
    ]
    return "\n".join(head + body + ["</svg>", ""])


# --------------------------------------------------------------------------- 1. who does what

def who_does_what(L):
    b = []
    b += box(60, 140, 1080, 100, "task", L["prod"], [L["prod_line"]], label_dy=40)
    # the watchdog and the duty container both observe production
    b += box(60, 330, 440, 150, "task", L["watch"], L["watch_lines"])
    b += box(640, 330, 500, 150, "core", L["duty"], L["duty_lines"])
    b += line(280, 240, 280, 326)
    b.append(t(296, 292, L["watch_reads"], "edge"))
    b += line(760, 240, 760, 326)
    b.append(t(776, 292, L["duty_reads"], "edge"))
    # no write path back into production
    b += path("M 1040 330 V 240", "blocked")
    b.append('  <circle class="cross" cx="1040" cy="285" r="17"/>')
    b += line(1031, 276, 1049, 294, "cross-x")
    b += line(1049, 276, 1031, 294, "cross-x")
    b.append(t(1066, 280, L["no_write_1"], "edge-warn"))
    b.append(t(1066, 302, L["no_write_2"], "edge-warn"))
    b += line(500, 405, 636, 405)
    b.append(t(568, 393, L["journal"], "edge-m"))
    # alert channel
    b += line(890, 480, 890, 556)
    b.append(t(906, 526, L["posts"], "edge"))
    b += box(60, 560, 1080, 100, "task", L["channel"], [L["channel_line"]], label_dy=40)
    # agents behind the channel
    b += line(280, 660, 280, 736)
    b += line(920, 660, 920, 736)
    b += box(60, 740, 440, 130, "project", L["support"], L["support_lines"])
    b += box(700, 740, 440, 130, "project", L["lead"], L["lead_lines"])
    b += line(500, 805, 696, 805)
    b.append(t(598, 793, L["defect"], "edge-m"))
    # the owner
    b += path("M 280 870 V 1000 H 396", "ownerline")
    b += path("M 920 870 V 1000 H 804", "ownerline")
    b.append(t(296, 940, L["owner_edge"], "edge-owner"))
    b += box(400, 950, 400, 100, "owner", L["me"], [L["me_line"]], label_dy=40)
    b += band(1100, 120, L["band"], L["band_lines"])
    return svg(1260, L["title"], L["desc"], L["heading"], L["subheading"], b)


WHO = {
    "ru": dict(
        title="Кто что делает на дежурстве",
        desc="Облачный сторож и контейнер дежурного на Claude Opus 5.5 наблюдают за продакшеном FindRates. "
             "Дежурный только читает код и базу, пути записи в продакшен у него нет. Находки он публикует "
             "в канале тревог, откуда их забирают ИИ-техподдержка и ИИ-руководитель; вопросы владельца "
             "уходят мне в Telegram.",
        heading="Кто что делает",
        subheading="Дежурный видит всё, но ничего не меняет",
        prod="Продакшен FindRates",
        prod_line="сервисы, база, переписки с клиентами, ставки перевозчиков",
        watch="Облачный сторож",
        watch_lines=["жив ли интерфейс,", "ошибки и события в логах"],
        duty="Контейнер дежурного",
        duty_lines=["Claude Opus 5.5", "только чтение: код и база"],
        watch_reads="проверяет",
        duty_reads="читает",
        no_write_1="записи",
        no_write_2="нет",
        journal="журнал",
        posts="карточка",
        channel="Канал тревог",
        channel_line="у каждого поста источник и адресат",
        support="ИИ-техподдержка",
        support_lines=["отвечает клиенту", "и оператору"],
        lead="ИИ-руководитель",
        lead_lines=["чинит платформу,", "сдерживает инцидент"],
        defect="дефект кода",
        owner_edge="вопросы владельца",
        me="Я",
        me_line="в Telegram",
        band="У дежурного нет прав менять прод",
        band_lines=["Он не пишет в данные, не перезапускает сервисы и не правит настройки."],
    ),
    "en": dict(
        title="Who does what on call",
        desc="A cloud watchdog and the duty container running Claude Opus 5.5 observe FindRates production. "
             "The duty engineer only reads code and the database and has no write path into production. "
             "It posts findings to the alert channel, where the AI support agent and the AI lead pick them "
             "up; owner questions go to me on Telegram.",
        heading="Who does what",
        subheading="The duty engineer sees everything and changes nothing",
        prod="FindRates production",
        prod_line="services, database, client chats, carrier rates",
        watch="Cloud watchdog",
        watch_lines=["is the interface alive,", "errors and events in logs"],
        duty="Duty container",
        duty_lines=["Claude Opus 5.5", "read only: code and database"],
        watch_reads="checks",
        duty_reads="reads",
        no_write_1="no",
        no_write_2="writes",
        journal="journal",
        posts="card",
        channel="Alert channel",
        channel_line="every post names its source and its addressee",
        support="AI support",
        support_lines=["answers the client", "and the operator"],
        lead="AI lead",
        lead_lines=["fixes the platform,", "contains incidents"],
        defect="code defect",
        owner_edge="owner questions",
        me="Me",
        me_line="on Telegram",
        band="The duty engineer has no rights to change production",
        band_lines=["It does not write data, restart services or change settings."],
    ),
}


# --------------------------------------------------------------------------- 2. model judges, code checks

def model_and_code(L):
    b = []
    b += box(360, 140, 480, 90, "task", L["event"], [L["event_line"]], label_dy=38)
    b += line(600, 230, 600, 276)
    # assessment with four outcomes
    b.append('  <rect class="core" x="60" y="280" width="1080" height="210" rx="16"/>')
    b.append(t(600, 322, L["assess"], "label"))
    b.append(t(600, 354, L["assess_line"], "small"))
    chips = [(90, "chip"), (360, "chip"), (630, "chip-quiet"), (900, "chip-quiet")]
    for (x, cls), name in zip(chips, L["outcomes"]):
        b.append(f'  <rect class="{cls}" x="{x}" y="385" width="210" height="64" rx="32"/>')
        b.append(t(x + 105, 425, name, "chip-t"))
    b.append(t(870, 476, L["quiet"], "small"))
    # investigation
    b += line(465, 449, 465, 546)
    b += box(330, 550, 540, 130, "core", L["investigate"], L["investigate_lines"])
    # notify goes straight to the card
    b += path("M 195 449 V 785 H 326")
    b += line(600, 680, 600, 736)
    b += box(330, 740, 540, 90, "core", L["card"], [L["card_line"]], label_dy=38)
    b += line(600, 830, 600, 876)
    # the check in plain code
    b += box(160, 880, 880, 130, "code", L["check"], L["check_lines"])
    b += path("M 400 1010 V 1076", "warnline")
    b += path("M 800 1010 V 1076", "okline")
    b.append(t(416, 1050, L["mismatch"], "edge-warn"))
    b.append(t(816, 1050, L["match"], "edge"))
    b += box(160, 1080, 440, 110, "warn", L["held"], [L["held_line"]], label_dy=40)
    b += box(640, 1080, 400, 110, "project", L["published"], [L["published_line"]], label_dy=40)
    # legend
    b.append('  <rect class="core" x="60" y="1236" width="34" height="26" rx="6"/>')
    b.append(t(106, 1257, L["legend_model"], "small-l"))
    b.append('  <rect class="code" x="520" y="1236" width="34" height="26" rx="6"/>')
    b.append(t(566, 1257, L["legend_code"], "small-l"))
    return svg(1300, L["title"], L["desc"], L["heading"], L["subheading"], b)


MODEL = {
    "ru": dict(
        title="Модель судит, код проверяет",
        desc="Событие сначала оценивает модель: уведомить, расследовать, отложить в сводку или пропустить. "
             "При расследовании она читает код версии в проде и делает запросы к базе только на чтение. "
             "Карточку находки проверяет обычный код: номера заявок и суммы должны совпасть с тем, что "
             "вернула база. Не сошлось — карточка задержана, сошлось — опубликована в канале тревог.",
        heading="Модель судит, код проверяет",
        subheading="Суждение отдано модели, числа сверяет программа",
        event="Событие",
        event_line="журнал, база, переписки, ставки",
        assess="Оценка моделью",
        assess_line="без инструментов, с историей за неделю",
        outcomes=["уведомить", "расследовать", "в сводку", "пропустить"],
        quiet="без сообщения сейчас",
        investigate="Расследование",
        investigate_lines=["читает код версии в проде,", "запросы к базе только на чтение"],
        card="Карточка находки",
        card_line="что произошло, дефект, влияние",
        check="Код сверяет карточку с базой",
        check_lines=["каждый номер заявки и каждая сумма", "должны быть в выдаче базы этого прогона"],
        mismatch="не сошлось",
        match="сошлось",
        held="Карточка задержана",
        held_line="в канал не попадает",
        published="Опубликована",
        published_line="в канале тревог",
        legend_model="работает модель",
        legend_code="проверяет обычный код",
    ),
    "en": dict(
        title="The model judges, code checks",
        desc="The model assesses each event first: notify, investigate, add to the digest or skip. "
             "An investigation reads the code of the version in production and runs read-only database "
             "queries. Plain code checks the finding card: every order number and amount must match what "
             "the database returned. On a mismatch the card is held; on a match it is posted to the alert channel.",
        heading="The model judges, code checks",
        subheading="Judgement goes to the model, numbers are checked by a program",
        event="Event",
        event_line="journal, database, chats, rates",
        assess="Model assessment",
        assess_line="no tools, with the past week's history",
        outcomes=["notify", "investigate", "digest", "skip"],
        quiet="no message now",
        investigate="Investigation",
        investigate_lines=["reads the code in production,", "read-only database queries"],
        card="Finding card",
        card_line="what happened, defect, impact",
        check="Code checks the card against the database",
        check_lines=["every order number and every amount", "must appear in this run's query results"],
        mismatch="mismatch",
        match="match",
        held="Card held",
        held_line="never reaches the channel",
        published="Posted",
        published_line="to the alert channel",
        legend_model="the model works",
        legend_code="plain code checks",
    ),
}


# --------------------------------------------------------------------------- 3. autonomy boundary

def autonomy_boundary(L):
    b = []
    cols = ((60, "project", L["auto"], L["auto_sub"], L["auto_items"]),
            (640, "owner", L["mine"], L["mine_sub"], L["mine_items"]))
    for x, cls, head, sub, items in cols:
        b.append(f'  <rect class="{cls}" x="{x}" y="140" width="500" height="540" rx="16"/>')
        b.append(t(x + 250, 186, head, "label"))
        b.append(t(x + 250, 218, sub, "small"))
        b.append(f'  <line class="rule" x1="{x + 24}" y1="242" x2="{x + 476}" y2="242"/>')
        y = 286
        for label, notes in items:
            b.append(t(x + 30, y, label, "label-l"))
            for i, note in enumerate(notes):
                b.append(t(x + 30, y + 30 + i * 27, note, "small-l"))
            y += 54 + 27 * len(notes) + 14
    b += line(600, 150, 600, 670, "divider")
    b += band(720, 150, L["band"], L["band_lines"])
    return svg(910, L["title"], L["desc"], L["heading"], L["subheading"], b)


AUTONOMY = {
    "ru": dict(
        title="Граница автономии по обратимости",
        desc="Слева то, что агенты делают сами: расследуют, отвечают клиентам и операторам, пишут хотфиксы, "
             "вливают проверенные изменения и сдерживают инцидент обратимыми мерами. Справа то, что требует "
             "моего согласия: релизы, запись в продакшен-базу, деньги и любые необратимые шаги.",
        heading="Граница автономии по обратимости",
        subheading="Обратимое агенты делают сами, необратимое ждёт меня",
        auto="Агенты сами",
        auto_sub="шаг можно отменить",
        auto_items=[
            ("Расследование", ["читают код и базу"]),
            ("Ответы", ["клиентам и операторам"]),
            ("Хотфиксы", ["и вливание проверенных изменений"]),
            ("Сдерживание инцидента", ["переключить маршрут,", "откатить сборку,", "отсеять ложную тревогу"]),
        ],
        mine="Только с моего согласия",
        mine_sub="шаг меняет прод насовсем",
        mine_items=[
            ("Релизы", ["выкатка в прод"]),
            ("Запись в прод-базу", ["любая"]),
            ("Деньги", ["любые траты"]),
            ("Всё необратимое", ["что нельзя быстро отменить"]),
        ],
        band="Цена паузы и цена ошибки",
        band_lines=["Слева ожидание человека стоит минут простоя, а ошибка отменяется.",
                    "Справа ошибка стоит дороже короткого подтверждения."],
    ),
    "en": dict(
        title="The autonomy boundary follows reversibility",
        desc="On the left, what the agents do on their own: investigate, answer clients and operators, write "
             "hotfixes, merge reviewed changes and contain an incident with reversible steps. On the right, "
             "what needs my approval: releases, writes to the production database, money and any irreversible step.",
        heading="The autonomy boundary follows reversibility",
        subheading="Agents take reversible steps; irreversible ones wait for me",
        auto="Agents on their own",
        auto_sub="the step can be undone",
        auto_items=[
            ("Investigation", ["read code and the database"]),
            ("Replies", ["to clients and operators"]),
            ("Hotfixes", ["and merging reviewed changes"]),
            ("Incident containment", ["switch a route,", "roll back a build,", "dismiss a false alarm"]),
        ],
        mine="Only with my approval",
        mine_sub="the step changes production for good",
        mine_items=[
            ("Releases", ["deploying to production"]),
            ("Production database writes", ["any of them"]),
            ("Money", ["any spending"]),
            ("Anything irreversible", ["that cannot be quickly undone"]),
        ],
        band="The cost of a pause and the cost of a mistake",
        band_lines=["On the left, waiting for a person costs minutes of downtime; a mistake is undone.",
                    "On the right, a mistake costs more than a short confirmation."],
    ),
}


# --------------------------------------------------------------------------- 4. where a finding goes

def finding_routing(L):
    b = []
    b += box(330, 140, 540, 90, "core", L["finding"], [L["finding_line"]], label_dy=38)
    b += line(600, 230, 600, 262, "plain")
    b += line(230, 262, 970, 262, "plain")
    xs = (60, 430, 800)
    for x in xs:
        b += line(x + 170, 262, x + 170, 296)
    for x, (head, notes) in zip(xs, L["kinds"]):
        b += box(x, 300, 340, 170, "task", head, notes)
    classes = ("project", "project", "owner")
    for x, cls, (head, notes) in zip(xs, classes, L["targets"]):
        cls_line = "ownerline" if cls == "owner" else "line"
        b += line(x + 170, 470, x + 170, 546, cls_line)
        b += box(x, 550, 340, 160, cls, head, notes)
    b += path("M 230 710 V 746 H 600 V 716")
    b.append(t(415, 774, L["handover"], "edge-m"))
    b += band(810, 120, L["band"], L["band_lines"])
    return svg(970, L["title"], L["desc"], L["heading"], L["subheading"], b)


ROUTING = {
    "ru": dict(
        title="Куда идёт находка",
        desc="Находка дежурного попадает в канал тревог с адресатом. Клиентское забирает ИИ-техподдержка, "
             "платформенное — ИИ-руководитель, вопрос владельца приходит мне в Telegram. Дефект кода "
             "техподдержка передаёт руководителю.",
        heading="Куда идёт находка",
        subheading="Каждый пост в канале тревог размечен адресатом",
        finding="Находка дежурного",
        finding_line="карточка в канале тревог",
        kinds=[
            ("Клиентское", ["частный сбой клиента,", "переписки, ставки"]),
            ("Платформенное", ["ошибки платформы,", "новые виды сбоев,", "состояние основной ветки"]),
            ("Вопрос владельца", ["платформа, деньги,", "безопасность,", "сомнение модели"]),
        ],
        targets=[
            ("ИИ-техподдержка", ["отвечает клиенту", "и оператору"]),
            ("ИИ-руководитель", ["чинит и сдерживает", "обратимыми мерами"]),
            ("Я", ["в Telegram"]),
        ],
        handover="дефект кода",
        band="Мой телефон молчит, пока дело не касается владельца",
        band_lines=["Клиентское и платформенное агенты разбирают без меня."],
    ),
    "en": dict(
        title="Where a finding goes",
        desc="A finding reaches the alert channel with an addressee. Client issues go to the AI support agent, "
             "platform issues to the AI lead, owner questions to me on Telegram. The support agent hands code "
             "defects to the lead.",
        heading="Where a finding goes",
        subheading="Every post in the alert channel names its addressee",
        finding="Duty engineer's finding",
        finding_line="a card in the alert channel",
        kinds=[
            ("Client issue", ["one client's failure,", "chats, rates"]),
            ("Platform issue", ["platform errors,", "new kinds of failure,", "main branch health"]),
            ("Owner question", ["platform, money,", "security,", "the model's doubt"]),
        ],
        targets=[
            ("AI support", ["answers the client", "and the operator"]),
            ("AI lead", ["fixes and contains", "with reversible steps"]),
            ("Me", ["on Telegram"]),
        ],
        handover="code defect",
        band="My phone stays quiet unless the owner is needed",
        band_lines=["Agents handle client and platform issues without me."],
    ),
}


DIAGRAMS = (
    ("system-architecture.svg", who_does_what, WHO),
    ("investigation-flow.svg", model_and_code, MODEL),
    ("autonomy-boundary.svg", autonomy_boundary, AUTONOMY),
    ("finding-routing.svg", finding_routing, ROUTING),
)


if __name__ == "__main__":
    for locale, directory in BUNDLES.items():
        directory.mkdir(parents=True, exist_ok=True)
        for name, render, labels in DIAGRAMS:
            target = directory / name
            target.write_text(render(labels[locale]), encoding="utf-8")
            print(target.relative_to(ROOT))
