---
date: 2026-08-05
session: voice-rewrite
commit: 3f54998
status: completed
---

# Journal: 2026-08-05 — Rewriting published articles in the author's voice

## Context

The 18-day report was written against an explicit voice specification: short declaratives, varied sentence length, no filler openers, no AI tell-words. The three earlier articles predated that specification, so the publication read as two different authors. This session brought all four articles onto one voice.

## What happened

- Rewrote all six language versions of the three earlier articles: `ai-tech-teams-workflow`, `autonomous-digital-employee`, `claude-codex-concierge`.
- Preserved every structural element the site contract depends on: article titles (hardcoded in `EXPECTED_ARTICLE_TITLES`), diagram counts per bundle (3 / 2 / 0), tables, ASCII diagrams, code fences, block quotes, the external citation link, and all front matter fields.
- Preserved the facts. Every figure survived the rewrite unchanged: 15 runs over six days, 1.4 QA runs, 0.93 audits, 93 retrospectives, 790 → 1,732 lines, 300/400 size caps, 44 checks, 4 nonexistent helper functions, 15-minute state interval, 12 projects, 38 sessions, 4,246 decision records, 171 tests, 85 traders screened, 37 groups with 27 from one mechanic.
- Unified the pronoun for the digital employee across the English edition. The first article used "it", the 18-day report used "he". Everything is "it" now, so the series reads as one publication.
- Verified locally: article titles match the checker registry exactly, diagram counts per bundle are unchanged, no Cyrillic in any English bundle, all front matter fields present.

## Reflection

Rhythm measurements before and after, Russian editions: `ai-tech-teams-workflow` 12.3 → 11.7 words per sentence with short sentences rising 15% → 18%; `autonomous-digital-employee` 12.4 → 10.7 and 16% → 25%; `claude-codex-concierge` 11.8 → 10.8 and 9% → 16%. The English editions sit higher (13.0–14.2) because English syntax carries more words per clause and the rewrite did not force parity.

The risk in a voice pass is losing facts while chasing tone. Keeping the numbers in place was treated as a hard constraint and checked afterwards, not assumed.

Hugo is still not installed locally, so the full build and both checker scripts have not been run for this change either.

## Decisions

| Decision | Rationale | Impact |
| --- | --- | --- |
| Keep all article titles unchanged | Titles are hardcoded in the bilingual checker and carry recognition | No checker edits needed for this pass |
| Keep every diagram and table | The contract enforces per-bundle diagram counts | Rewrite is text-only, structure untouched |
| Unify on "it" in English | The series read as two authors with mixed pronouns | One voice across four articles |
| Treat figures as immutable | A voice pass must not become a facts pass | All numbers verified after rewriting |

## Next

- Run the full validation before merge: `hugo --gc --minify --printI18nWarnings --panicOnWarning`, then `check-bilingual-site.py` and the six `check-diagram-ux.py` invocations.
- Consider a second pass on the English editions if the higher average sentence length reads as a difference in voice rather than in language.
