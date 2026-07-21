#!/usr/bin/env python3
from __future__ import annotations

import shutil
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
ARTICLE_SRC = WORKSPACE / "outputs" / "ii-tekhkomandy-public-human.md"
HERO_SRC = WORKSPACE / "outputs" / "ai-tech-teams-workflow-hero.png"


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def strip_article(md: str) -> str:
    lines = md.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    if lines and lines[0].startswith("*") and lines[0].endswith("*"):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    article = strip_article(ARTICLE_SRC.read_text(encoding="utf-8"))

    write(
        "hugo.toml",
        """
        baseURL = "https://ak40u.github.io/technical-articles/"
        defaultContentLanguage = "ru"
        enableRobotsTXT = true

        [params]
          author = "Pavel Volkov"
          authorLatin = "Павел Волков"
          authorUrl = "https://github.com/ak40u"
          authorRole = "ИИ-архитектор и инженер"
          bio = "Я пишу о практической инженерии: автономные ИИ-команды, продуктовая разработка, QA, релизы, инфраструктура и рабочие процессы, которые можно повторять. Мне важны не лозунги, а устройство систем: кто принимает решения, кто проверяет результат, где лежат доказательства и где автоматизация должна остановиться."
          bioTags = ["ИИ-инженерия", "автономные команды", "QA и аудит", "релизы", "инженерный процесс"]
          github = "https://github.com/ak40u"
          copyright = "© 2026 Pavel Volkov"
          defaultImage = "og/ai-tech-teams-workflow-hero.png"

        [languages]
          [languages.ru]
            label = "Русский"
            locale = "ru"
            contentDir = "content/ru"
            weight = 1
            title = "Технические статьи"
            [languages.ru.params]
              tagline = "Практические разборы инженерных систем, автономной разработки, QA, релизов и инфраструктуры."

        [outputs]
          home = ["HTML", "RSS", "LLMS"]

        [outputFormats]
          [outputFormats.LLMS]
            mediaType = "text/plain"
            baseName = "llms"
            isPlainText = true

        [markup]
          [markup.goldmark.renderer]
            unsafe = true
          [markup.tableOfContents]
            startLevel = 2
            endLevel = 3
            ordered = false

        [taxonomies]
          tag = "tags"
        """,
    )

    write(
        ".github/workflows/hugo.yml",
        """
        name: Deploy Hugo site to GitHub Pages

        on:
          push:
            branches: [main]
          workflow_dispatch:

        permissions:
          contents: read
          pages: write
          id-token: write

        concurrency:
          group: pages
          cancel-in-progress: false

        jobs:
          build:
            runs-on: ubuntu-latest
            env:
              HUGO_VERSION: 0.163.1
            steps:
              - name: Install Hugo extended
                run: |
                  wget -q -O hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb
                  sudo dpkg -i hugo.deb
              - uses: actions/checkout@v6
                with:
                  fetch-depth: 0
              - name: Setup Pages
                id: pages
                uses: actions/configure-pages@v6
              - name: Build
                run: hugo --gc --minify --baseURL "${{ steps.pages.outputs.base_url }}/"
              - name: Upload artifact
                uses: actions/upload-pages-artifact@v5
                with:
                  path: ./public

          deploy:
            needs: build
            runs-on: ubuntu-latest
            environment:
              name: github-pages
              url: ${{ steps.deployment.outputs.page_url }}
            steps:
              - name: Deploy to GitHub Pages
                id: deployment
                uses: actions/deploy-pages@v5
        """,
    )

    write(
        "content/ru/_index.md",
        """
        ---
        title: "Технические статьи"
        ---

        Здесь я собираю технические статьи о том, как я строю и проверяю инженерные системы: автономные ИИ-команды, продуктовую разработку, QA-контуры, релизные процессы и инфраструктуру.
        """,
    )

    write(
        "content/ru/about.md",
        """
        ---
        title: "О проекте"
        ---

        Это публичная витрина моих технических заметок.

        Я пишу о практической инженерии: автономные ИИ-команды, продуктовая разработка, QA, релизы, инфраструктура и рабочие процессы, которые можно повторять. Мне важны не лозунги, а инженерная часть: как устроить доверие к результату, где система должна остановиться и какие доказательства оставить после работы.

        ## Автор

        **Pavel Volkov / Павел Волков** — ИИ-архитектор и инженер.

        GitHub: [ak40u](https://github.com/ak40u)

        ## Как читать

        Статьи здесь длинные и практические. Их можно читать как разбор устройства системы: роли, границы ответственности, проверки, журналы, ретроспективы, релизный контур и инфраструктурные решения.
        """,
    )

    write(
        "content/ru/articles/_index.md",
        """
        ---
        title: "Статьи"
        ---

        Практические разборы инженерных систем: автономные ИИ-команды, QA-контуры, релизы, инфраструктура и ограничения, без которых автоматизация быстро превращается в красивую иллюзию.
        """,
    )

    article_page = textwrap.dedent(
        """
        ---
        title: "Как я построил работу с автономными ИИ-техкомандами"
        date: 2026-07-09
        description: "Как я развёл роли, проверки и релиз так, чтобы несколько ИИ-команд могли работать параллельно без моего постоянного контроля."
        summary: "Практический разбор системы автономных ИИ-техкоманд: роли, очередь задач, QA, аудит, ретроспективы и релизный контур."
        tags: ["ИИ-агенты", "автономная разработка", "QA", "архитектура", "релизы"]
        image: "og/ai-tech-teams-workflow-hero.png"
        ---

        *Как я развёл роли, проверки и релиз так, чтобы несколько ИИ-команд могли работать параллельно без моего постоянного контроля.*

        """
    ).lstrip("\n") + article
    write("content/ru/articles/ai-tech-teams-workflow/index.md", article_page)

    write(
        "i18n/ru.toml",
        """
        [articles]
        other = "Статьи"

        [about]
        other = "О проекте"

        [reading_time]
        one = "минута чтения"
        few = "минуты чтения"
        many = "минут чтения"
        other = "минут чтения"

        [read_more]
        other = "Читать"

        [author_label]
        other = "Автор"

        [toc_title]
        other = "Оглавление"

        [back_to_articles]
        other = "К списку статей"
        """,
    )

    write(
        "layouts/_default/baseof.html",
        """
        <!DOCTYPE html>
        <html lang="{{ .Site.Language.Locale }}">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{{ if .IsHome }}{{ .Site.Title }}{{ else }}{{ .Title }} · {{ .Site.Title }}{{ end }}</title>
          {{ partial "head-seo.html" . }}
          {{ $css := resources.Get "css/main.css" | resources.Minify | resources.Fingerprint }}
          <link rel="stylesheet" href="{{ $css.RelPermalink }}">
        </head>
        <body>
          {{ partial "header.html" . }}
          <main class="container">
            {{ block "main" . }}{{ end }}
          </main>
          {{ partial "footer.html" . }}
        </body>
        </html>
        """,
    )

    write(
        "layouts/partials/head-seo.html",
        """
        {{ $description := "" }}
        {{ with .Description }}{{ $description = . }}{{ else }}{{ with .Summary }}{{ $description = . | plainify | truncate 180 }}{{ else }}{{ $description = .Site.Language.Params.tagline }}{{ end }}{{ end }}
        {{ $image := .Params.image | default .Site.Params.defaultImage }}
        {{ $imageURL := "" }}
        {{ with $image }}{{ $imageURL = (absURL .) }}{{ end }}
        <meta name="description" content="{{ $description }}">
        <meta property="og:type" content="{{ if .IsPage }}article{{ else }}website{{ end }}">
        <meta property="og:title" content="{{ if .IsHome }}{{ .Site.Title }}{{ else }}{{ .Title }} · {{ .Site.Title }}{{ end }}">
        <meta property="og:description" content="{{ $description }}">
        <meta property="og:url" content="{{ .Permalink }}">
        {{ with $imageURL }}<meta property="og:image" content="{{ . }}">{{ end }}
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="{{ if .IsHome }}{{ .Site.Title }}{{ else }}{{ .Title }} · {{ .Site.Title }}{{ end }}">
        <meta name="twitter:description" content="{{ $description }}">
        {{ with $imageURL }}<meta name="twitter:image" content="{{ . }}">{{ end }}
        {{ with .OutputFormats.Get "RSS" }}<link rel="alternate" type="application/rss+xml" href="{{ .Permalink }}" title="{{ $.Site.Title }}">{{ end }}
        """,
    )

    write(
        "layouts/partials/header.html",
        """
        <header class="site-header">
          <div class="container header-inner">
            <a class="brand" href="{{ .Site.Home.RelPermalink }}">{{ .Site.Title }}</a>
            <nav class="site-nav" aria-label="Основная навигация">
              <a href="{{ "articles/" | relLangURL }}">{{ i18n "articles" }}</a>
              <a href="{{ "about/" | relLangURL }}">{{ i18n "about" }}</a>
            </nav>
          </div>
        </header>
        """,
    )

    write(
        "layouts/partials/footer.html",
        """
        <footer class="site-footer">
          <div class="container">
            <p class="foot-author">{{ .Site.Params.copyright }}</p>
            <p class="foot-note">Практические заметки об инженерных системах, ИИ-разработке и рабочих процессах.</p>
          </div>
        </footer>
        """,
    )

    write(
        "layouts/index.html",
        """
        {{ define "main" }}
        <section class="hero">
          <p class="eyebrow">Pavel Volkov · инженерная практика</p>
          <h1>{{ .Site.Title }}</h1>
          <p class="tagline">{{ .Site.Language.Params.tagline }}</p>
          {{ with .Content }}<div class="intro-body">{{ . }}</div>{{ end }}
        </section>

        {{ with .Site.Params }}
        <section class="bio-card" aria-label="Об авторе">
          <div class="bio-mono" aria-hidden="true">PV</div>
          <div class="bio-body">
            <p class="bio-name">{{ .author }} <span>· {{ .authorLatin }}</span></p>
            {{ with .authorRole }}<p class="bio-role">{{ . }}</p>{{ end }}
            {{ with .bio }}<p class="bio-text">{{ . }}</p>{{ end }}
            {{ with .bioTags }}
            <div class="bio-tags">
              {{ range . }}<span class="bio-tag">{{ . }}</span>{{ end }}
            </div>
            {{ end }}
            <div class="bio-links">
              {{ with .github }}<a href="{{ . }}" rel="me noopener" target="_blank">GitHub</a>{{ end }}
              <a href="{{ "about/" | relLangURL }}">{{ i18n "about" }} →</a>
            </div>
          </div>
        </section>
        {{ end }}

        <p class="section-label">{{ i18n "articles" }}</p>
        <section class="article-list">
          {{ range (where .Site.RegularPages "Section" "articles").ByDate.Reverse }}
          <a class="card-link" href="{{ .RelPermalink }}">
            <h2>{{ .Title }}</h2>
            <p class="meta"><time datetime="{{ .Date.Format "2006-01-02" }}">{{ .Date.Format "02.01.2006" }}</time> · {{ .ReadingTime }}&nbsp;{{ i18n "reading_time" .ReadingTime }}</p>
            {{ with .Summary }}<p class="summary">{{ . }}</p>{{ end }}
            <span class="read-more">{{ i18n "read_more" }} →</span>
          </a>
          {{ else }}
          <p class="empty">Пока пусто.</p>
          {{ end }}
        </section>
        {{ end }}
        """,
    )

    write(
        "layouts/_default/list.html",
        """
        {{ define "main" }}
        <section class="list-head">
          <h1>{{ .Title }}</h1>
          {{ with .Content }}<div class="intro-body">{{ . }}</div>{{ end }}
        </section>

        <section class="article-list">
          {{ range .Pages.ByDate.Reverse }}
          <a class="card-link" href="{{ .RelPermalink }}">
            <h2>{{ .Title }}</h2>
            <p class="meta"><time datetime="{{ .Date.Format "2006-01-02" }}">{{ .Date.Format "02.01.2006" }}</time> · {{ .ReadingTime }}&nbsp;{{ i18n "reading_time" .ReadingTime }}</p>
            {{ with .Summary }}<p class="summary">{{ . }}</p>{{ end }}
            <span class="read-more">{{ i18n "read_more" }} →</span>
          </a>
          {{ else }}
          <p class="empty">Пока пусто.</p>
          {{ end }}
        </section>
        {{ end }}
        """,
    )

    write(
        "layouts/_default/single.html",
        """
        {{ define "main" }}
        {{ $isArticle := eq .Section "articles" }}
        <article class="post">
          <header class="post-header">
            <h1>{{ .Title }}</h1>
            {{ if $isArticle }}
            <p class="meta">
              <time datetime="{{ .Date.Format "2006-01-02" }}">{{ .Date.Format "02.01.2006" }}</time>
              · {{ .ReadingTime }}&nbsp;{{ i18n "reading_time" .ReadingTime }}
              · {{ i18n "author_label" }}: {{ .Site.Params.author }}
            </p>
            {{ end }}
          </header>

          {{ if gt (len .TableOfContents) 60 }}
          <nav class="toc" aria-label="Оглавление">
            <div class="toc-title">{{ i18n "toc_title" }}</div>
            {{ .TableOfContents }}
          </nav>
          {{ end }}

          <div class="post-content">
            {{ .Content }}
          </div>

          {{ if $isArticle }}
          <footer class="post-footer">
            <a class="back" href="{{ "articles/" | relLangURL }}">{{ i18n "back_to_articles" }}</a>
          </footer>
          {{ end }}
        </article>
        {{ end }}
        """,
    )

    write(
        "layouts/robots.txt",
        """
        User-agent: *
        Allow: /

        Sitemap: {{ "sitemap.xml" | absURL }}
        """,
    )

    write(
        "layouts/index.llms.txt",
        """
        # {{ .Site.Title }}

        > {{ .Site.Language.Params.tagline }}

        ## Articles

        {{ range (where .Site.RegularPages "Section" "articles").ByDate.Reverse -}}
        - [{{ .Title }}]({{ .Permalink }}) — {{ .Description | default .Summary | plainify }}
        {{ end }}
        """,
    )

    write(
        "assets/css/main.css",
        """
        :root {
          --bg: #fcfbf7;
          --panel: #ffffff;
          --soft: #f3f0e8;
          --ink: #1d1d1b;
          --muted: #6c6860;
          --line: #ded9cd;
          --accent: #245f73;
          --accent-2: #8f4f2f;
          --accent-soft: #e8f2f4;
          --maxw: 900px;
          --readw: 760px;
          --font: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, Roboto, Helvetica, Arial, sans-serif;
          --mono: "SF Mono", ui-monospace, Menlo, Consolas, monospace;
        }

        * { box-sizing: border-box; }
        html { -webkit-text-size-adjust: 100%; }
        body {
          margin: 0;
          background: var(--bg);
          color: var(--ink);
          font-family: var(--font);
          font-size: 18px;
          line-height: 1.68;
          -webkit-font-smoothing: antialiased;
        }

        .container { width: 100%; max-width: var(--maxw); margin: 0 auto; padding: 0 28px; }
        a { color: var(--accent); text-decoration: none; }
        a:hover { text-decoration: underline; text-underline-offset: 3px; }

        .site-header {
          position: sticky;
          top: 0;
          z-index: 10;
          background: rgba(252, 251, 247, 0.92);
          border-bottom: 1px solid var(--line);
          backdrop-filter: blur(8px);
        }
        .header-inner { display: flex; align-items: center; justify-content: space-between; padding: 16px 0; gap: 24px; }
        .brand { color: var(--ink); font-weight: 750; font-size: 1.02rem; }
        .brand:hover { color: var(--accent); text-decoration: none; }
        .site-nav { display: flex; gap: 20px; flex-wrap: wrap; }
        .site-nav a { color: var(--muted); font-size: 0.94rem; }
        .site-nav a:hover { color: var(--accent); text-decoration: none; }

        .hero { padding: 66px 0 34px; }
        .eyebrow {
          margin: 0 0 12px;
          color: var(--accent-2);
          font-size: 0.82rem;
          font-weight: 700;
          letter-spacing: 0.06em;
          text-transform: uppercase;
        }
        .hero h1 {
          margin: 0 0 14px;
          max-width: 12ch;
          font-size: 3rem;
          line-height: 1.06;
          letter-spacing: 0;
        }
        .tagline { max-width: 58ch; margin: 0; color: var(--muted); font-size: 1.18rem; }
        .intro-body { max-width: 68ch; color: var(--muted); }

        .bio-card {
          display: flex;
          gap: 22px;
          align-items: flex-start;
          margin: 8px 0 12px;
          padding: 26px 28px;
          background: var(--soft);
          border: 1px solid var(--line);
          border-radius: 8px;
        }
        .bio-mono {
          flex: 0 0 auto;
          width: 58px;
          height: 58px;
          display: grid;
          place-items: center;
          color: #fff;
          background: var(--accent);
          border-radius: 8px;
          font-weight: 800;
        }
        .bio-name { margin: 0; font-size: 1.22rem; font-weight: 760; }
        .bio-name span { color: var(--muted); font-size: 0.95rem; font-weight: 500; }
        .bio-role { margin: 3px 0 12px; color: var(--accent); font-size: 0.93rem; font-weight: 700; }
        .bio-text { margin: 0 0 14px; font-size: 0.98rem; }
        .bio-tags { display: flex; flex-wrap: wrap; gap: 7px; margin: 0 0 14px; }
        .bio-tag { padding: 3px 10px; color: var(--accent); background: var(--accent-soft); border-radius: 999px; font-size: 0.78rem; font-weight: 650; }
        .bio-links { display: flex; flex-wrap: wrap; gap: 16px; font-size: 0.92rem; }

        .section-label {
          margin: 48px 0 4px;
          color: var(--muted);
          font-size: 0.8rem;
          font-weight: 750;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }
        .article-list { display: grid; gap: 16px; padding: 8px 0 56px; }
        .card-link {
          display: block;
          padding: 23px 24px;
          color: inherit;
          background: var(--panel);
          border: 1px solid var(--line);
          border-radius: 8px;
          transition: border-color .15s ease, box-shadow .15s ease, transform .15s ease;
        }
        .card-link:hover {
          text-decoration: none;
          border-color: var(--accent);
          box-shadow: 0 12px 28px -22px rgba(36, 95, 115, .65);
          transform: translateY(-2px);
        }
        .card-link h2 { margin: 0 0 6px; color: var(--ink); font-size: 1.28rem; line-height: 1.32; }
        .card-link:hover h2 { color: var(--accent); }
        .meta { margin: 0 0 10px; color: var(--muted); font-size: 0.88rem; }
        .summary { margin: 0 0 14px; color: var(--muted); }
        .read-more { color: var(--accent); font-size: 0.92rem; font-weight: 700; }
        .empty { color: var(--muted); }

        .list-head { padding: 56px 0 10px; }
        .list-head h1 { margin: 0 0 12px; font-size: 2.2rem; line-height: 1.15; }

        .post { padding: 48px 0 24px; }
        .post-header,
        .toc,
        .post-content,
        .post-footer {
          max-width: var(--readw);
          margin-left: auto;
          margin-right: auto;
        }
        .post-header h1 { margin: 0 0 14px; font-size: 2.25rem; line-height: 1.17; letter-spacing: 0; }
        .toc {
          margin-top: 28px;
          margin-bottom: 30px;
          padding: 16px 20px;
          background: var(--soft);
          border: 1px solid var(--line);
          border-radius: 8px;
          font-size: 0.93rem;
        }
        .toc-title { margin-bottom: 6px; color: var(--muted); font-size: 0.78rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; }
        .toc ul { margin: 0; padding-left: 20px; }
        .toc li { margin: 3px 0; }
        .toc a { color: var(--muted); }
        .toc a:hover { color: var(--accent); }

        .post-content { font-size: 1.06rem; }
        .post-content h2 { margin: 46px 0 14px; font-size: 1.52rem; line-height: 1.3; }
        .post-content h3 { margin: 32px 0 10px; font-size: 1.2rem; line-height: 1.35; }
        .post-content p { margin: 16px 0; }
        .post-content ul,
        .post-content ol { padding-left: 26px; }
        .post-content li { margin: 7px 0; }
        .post-content blockquote {
          margin: 22px 0;
          padding: 4px 20px;
          color: var(--muted);
          background: var(--accent-soft);
          border-left: 3px solid var(--accent);
          border-radius: 0 8px 8px 0;
        }
        .post-content code {
          font-family: var(--mono);
          font-size: .88em;
          background: var(--soft);
          border: 1px solid var(--line);
          border-radius: 5px;
          padding: 2px 6px;
        }
        .post-content pre {
          overflow-x: auto;
          padding: 16px 18px;
          background: var(--soft);
          border: 1px solid var(--line);
          border-radius: 8px;
          font-size: .85rem;
          line-height: 1.55;
        }
        .post-content pre code { padding: 0; border: 0; background: transparent; }
        .post-content table {
          width: 100%;
          margin: 24px 0;
          border-collapse: collapse;
          font-size: 0.91rem;
        }
        .post-content th,
        .post-content td {
          padding: 9px 11px;
          text-align: left;
          vertical-align: top;
          border-bottom: 1px solid var(--line);
        }
        .post-content th { border-bottom-width: 2px; font-weight: 750; }
        .post-footer { margin-top: 46px; padding-top: 24px; border-top: 1px solid var(--line); }
        .back { font-size: .94rem; font-weight: 700; }

        .site-footer { margin-top: 64px; padding: 28px 0 40px; border-top: 1px solid var(--line); }
        .foot-author { margin: 0 0 4px; font-size: .9rem; font-weight: 700; }
        .foot-note { margin: 0; color: var(--muted); font-size: .84rem; }

        @media (max-width: 680px) {
          body { font-size: 17px; }
          .container { padding: 0 18px; }
          .header-inner { align-items: flex-start; flex-direction: column; gap: 6px; }
          .hero { padding: 40px 0 24px; }
          .hero h1 { max-width: none; font-size: 2.1rem; }
          .tagline { font-size: 1.08rem; }
          .bio-card { flex-direction: column; padding: 22px; }
          .post-header h1 { font-size: 1.72rem; }
          .post-content h2 { font-size: 1.32rem; }
          .post-content table { display: block; overflow-x: auto; white-space: nowrap; }
        }
        """,
    )

    write(
        "README.md",
        """
        # Технические статьи

        Публичный сайт технических статей Pavel Volkov.

        Сайт собран на Hugo и публикуется через GitHub Pages.

        ## Локальный запуск

        ```bash
        hugo server
        ```
        """,
    )

    write(".gitignore", "public/\n.hugo_build.lock\n.DS_Store\n")
    write("content/en/.gitkeep", "")

    if HERO_SRC.exists():
        target = ROOT / "static" / "og" / "ai-tech-teams-workflow-hero.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERO_SRC, target)


if __name__ == "__main__":
    raise SystemExit(
        "This one-off bootstrap script is retired: running it would overwrite the "
        "current bilingual Hugo site. Edit the tracked site files directly instead."
    )
