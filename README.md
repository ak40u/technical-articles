# Technical Articles / Технические статьи

Pavel Volkov's bilingual technical publication. The Russian edition is served at the site root; the English edition is available under `/en/`.

Двуязычный сайт технических статей Pavel Volkov. Русская версия публикуется в корне сайта, английская — в `/en/`.

The site is built with Hugo and deployed through GitHub Pages.

## Local development / Локальный запуск

```bash
hugo server
```

Production-equivalent validation:

```bash
hugo --gc --minify --printI18nWarnings --panicOnWarning \
  --baseURL "https://ak40u.github.io/technical-articles/"
python3 scripts/check-bilingual-site.py public \
  "https://ak40u.github.io/technical-articles/"
python3 scripts/check-diagram-ux.py \
  public/articles/autonomous-digital-employee/index.html \
  assets/css/main.css
python3 scripts/check-diagram-ux.py \
  public/en/articles/autonomous-digital-employee/index.html \
  assets/css/main.css
```
