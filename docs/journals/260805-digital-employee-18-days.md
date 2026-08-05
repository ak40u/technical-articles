---
date: 2026-08-05
session: digital-employee-18-days
commit: 86b1152
status: completed
---

# Journal: 2026-08-05 — Digital employee 18-day report

## Context

The autonomous digital employee article published on 2026-07-21 described the design. Eighteen days of operation produced measurable outcomes worth a follow-up: fifty shift runs, eleven hypotheses, the project's first profitable month, and two limits the employee refused to cross without the owner. The follow-up had to enter the site under the same contract as existing articles, not as a loose page.

## What happened

- Added the bilingual page bundle `content/{ru,en}/articles/digital-employee-18-days/` with a shared `translationKey`, full frontmatter, and one page-bundle diagram (`hypothesis-fate.svg`) in each language.
- Drew the diagram in the site palette rather than generating it with Mermaid: the subject is a distribution of eleven outcomes, which reads better as fixed geometry than as a flow graph. The English copy carries no Cyrillic, per the site contract.
- Rendered the 1920x1080 hero pair with `rsvg-convert` in the visual language of the first article's hero, so the two reports look like a series.
- Extended `scripts/check-bilingual-site.py` with the new routes: `PAGE_PAIRS`, `EXPECTED_ARTICLE_TITLES`, `EN_DIAGRAMS`, `BUNDLE_DIAGRAM_COUNTS`, expected OG assets, and the `page_og` map. Without those entries the article would have been published outside every guarantee the checker provides.
- Registered the diagram UX check for both language versions in `.github/workflows/hugo.yml` and in the README validation block.
- Verified what is verifiable without a local Hugo binary: both SVGs parse as XML, the English bundle contains no Cyrillic, both front matters carry all seven required fields with a matching `translationKey`, both referenced OG files exist and are non-empty, each language contains exactly one diagram, the workflow file stays valid YAML, and the checker still compiles.

## Reflection

The checker's registries are hardcoded per article, so adding content silently means adding it without verification. Editing the registries in the same commit as the article keeps publication and its guarantees in one change instead of two.

Numbers were corrected against the source of truth before writing. The draft said the employee had closed eight hypotheses; the backlog shows seven closed outright and an eighth with its main branch killed and the remainder waiting for data. The article and the diagram now carry the second version.

Hugo is not installed on this machine, so the full build, the bilingual contract, and the diagram UX checks have not been run locally. That gap is real and is stated rather than papered over.

## Decisions

| Decision | Rationale | Impact |
| --- | --- | --- |
| Hand-drawn SVG instead of Mermaid | The content is a fixed distribution of outcomes, not a process graph | One diagram, no Mermaid font rules to enforce |
| One diagram instead of three | The report has a single structural claim worth a picture | Lower verification surface for a follow-up article |
| Update the checker in the same commit | Registries are hardcoded per route | The new article inherits every existing guarantee |
| State the missing local build | A green partial check is not a green build | Reviewer knows exactly what remains unproven |

## Next

- Run the full validation before merge: `hugo --gc --minify --printI18nWarnings --panicOnWarning`, then `check-bilingual-site.py` and both `check-diagram-ux.py` invocations for the new routes.
- The Telegram CTA is rendered by the shared template, so the Russian page should inherit exactly one; the checker confirms it on a real build.
