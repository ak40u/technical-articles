---
date: 2026-07-21
session: russian-telegram-cta
commit: faa05c4
status: completed
---

# Journal: 2026-07-21 — Russian Telegram CTA

## Context

The bilingual Hugo site needed one consistent path from every Russian article to the author's Telegram channel, without adding that promotion to English pages or Russian shell pages.

## What happened

- Added a shared CTA to the article footer in `layouts/_default/single.html`, gated by Russian language and article-page context. The localized sentence lives in `i18n/ru.toml`; presentation stays in `assets/css/main.css`.
- Extended `scripts/check-bilingual-site.py` with a dynamic link contract: discover generated article pages, require exactly one Telegram link and CTA on every Russian article, require zero on every English article and on the Russian home, about, and article-index pages, and verify safe link attributes.
- Proved the guard with temporary negative mutations. Removing a Russian CTA failed with the expected cardinality errors; injecting the link into an English article failed with the language-boundary error.
- Shipped commit `faa05c4` (`feat(site): link Russian articles to Telegram`) to `main`.
- Verified the live site: both Russian articles return HTTP 200 with exactly one CTA; both English articles and all three Russian shell pages return HTTP 200 with none.

## Reflection

Putting the CTA in the shared footer avoided duplicating editorial content across articles. The stronger result was turning placement into a generated-site contract: new articles inherit both the CTA and its verification automatically. Negative mutations and live checks prevented a green local build from being mistaken for proof of the published behavior.

## Decisions

| Decision | Rationale | Impact |
| --- | --- | --- |
| Render from the shared article template | One source of truth for current and future articles | No per-article maintenance |
| Keep the CTA Russian-only | The channel promotion belongs to the Russian publication context | English and shell pages remain clean |
| Enforce exact cardinality and safe attributes | Presence alone would not catch duplicates, leakage, or unsafe external links | The build fails closed on contract drift |
| Verify production after deployment | Publication is not complete until the live artifact matches the build | Commit, deployment, and user-visible behavior are tied together |

## Next

- No unresolved work for this change.
- If the Telegram URL or copy changes, update the template/localization and checker contract in the same commit.
