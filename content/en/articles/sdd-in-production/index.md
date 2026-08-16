---
title: "Spec-Driven Development in the AI Era: Forcing Agents to Write Code by Contract"
date: 2026-08-16
description: "Why canonical SDD turns into dead documentation, and how we built a working process based on production signals, adversarial model reviews, and TDD checks."
author: "Pavel Volkov"
image: "og/sdd-in-production-hero.png"
---

In Findrates.ai, Spec-Driven Development runs every day: we have closed over 240 plans through this pipeline. Our actual process differs significantly from conference slides where SDD is presented as an effortless silver bullet.

## The Limits of Vibecoding

With the rise of LLMs, developers initially relied on "vibecoding"—prompting a chatbot to "build feature X." For quick scripts and prototypes, this was enough. On an existing codebase, however, vibecoding quickly caused loss of context: models forgot constraints between sessions, broke neighboring modules, and generated unmanaged technical debt.

To regain control over architecture, teams started adopting Spec-Driven Development (SDD): first writing a Markdown specification defining all requirements, then having an agent in Cursor or Claude implement it step by step.

## Why Canonical SDD Fails in Practice

On paper, the workflow looks straightforward: a developer writes a spec, feeds it to an agent, and clicks "Apply."

In practice, a specification written by a human or generated in a single chat session is disconnected from the real codebase. The author inevitably references non-existent database methods and ignores contracts of adjacent modules. When the AI generates code and writes its own tests, it simply verifies its own hallucinations. The project gets trapped in a `fix -> error -> fix` loop, and the specification becomes obsolete within two commits.

We abandoned "trust-based" specs and built a pipeline where agents are strictly isolated and cross-check results at every stage.

![SDD Pipeline](/en/articles/sdd-in-production/sdd-pipeline.svg)

Theory vs. Production:

| Parameter | Canonical SDD (in tutorials) | SDD in Findrates.ai (in production) |
| :--- | :--- | :--- |
| **Source of Value** | Static task description from customer | Backlog from business, product, and operators + Producer filter |
| **Reconnaissance** | Code written from scratch or assumptions | Orchestrator isolates context in a worktree and slices tasks (`<slug>-slices.md`) |
| **Acceptance Criteria** | Written by the code author | Written by an independent analyst (Agent Olga) with Must-Not rules |
| **Plan Review** | Manual skimming of Markdown | Adversarial review by independent LLMs until all issues are resolved |
| **Verification (TDD)** | Tests written after implementation | Strict BDD before implementation + mutation testing (Stryker) |
| **QA and Deployment** | Manual handoff to a QA engineer | Autonomous QA loop by Marina: up to 5 rounds of `fix -> retest` (prod is manual) |

---

## Value Filter: Preventing Wasteful Runs

A full SDD cycle is resource-intensive. Running a single slice costs $2–$6 in API tokens and takes 15–25 minutes of model compute. That is cheaper than an hour of senior engineer time, but feeding backlog items indiscriminately into the pipeline wastes compute budget on low-priority tasks.

In Findrates.ai, tasks arrive in ClickUp from the Product Owner, business stakeholders, platform operators, and researchers. To filter out noise before triggering the heavy pipeline, we use the Producer agent (the `producer` skill).

Before any specification is drafted, the Producer analyzes:
1. The active backlog.
2. Release goals (MUST / SHOULD).
3. Lessons learned from previous releases (`retro.md`).
4. Production telemetry and error alerts.

The Producer evaluates product impact and selects the **Top-5 tasks**. If a task does not address an immediate platform problem, it is deferred.

## How the Specification is Formed

Once a task is selected, the Orchestrator initiates specification preparation. Rather than drafting a single document, it executes a step-by-step requirements workflow:

*Agent names (Olga, Eva, Marina) represent architectural isolation of context and prompt instructions. The acceptance criteria agent cannot view source code to prevent bias (anti-anchoring), while the QA agent has no access to backend code, testing the application strictly as a black box.*

**1. Isolation and Slicing**  
The Orchestrator spins up an isolated git worktree and divides the feature into independent slices (`plans/<feature-slug>-slices.md`). Only one atomic increment is planned at a time. For bug fixes, a strict rule applies: Agent Marina must first reproduce the defect on the current build (Baseline Repro). No fix is written without a confirmed red E2E test.

**2. Codebase Reconnaissance (Pre-plan Scout)**  
A read-only script scans the repository for target files, imports, data types, and method signatures. The plan relies on actual codebase structure rather than LLM assumptions.

**3. Independent Acceptance Criteria (Agent Olga)**  
The business analyst agent creates `acceptance-criteria.md`, defining positive test cases and mandatory constraints (Must-Not):

```markdown
### Acceptance Criteria
- [ ] When currency changes, recalculate rate using Central Bank rate on request creation date.
- [ ] Display currency indicator in rate card and comparison table.

### Must-Not Invariants
- [ ] MUST NOT finalize request with status EXPIRED.
- [ ] MUST NOT invoke `recalculateTotal()` without operator permissions check.
```

**4. UX Contract (Agent Eva)**  
For frontend tasks, designer Eva produces a contract based on the design system: defining required states (loading, empty, error, success), reusable components, and accessibility requirements.

**5. Structured Plan (Tech-Lead)**  
The Tech-Lead compiles the final `plan.md` and divides it into phases (`phase-1.md`, `phase-2.md`). The plan contains no implementation code—only algorithms, dependency verification, and architectural choices. This verified document serves as the specification.

Required sections:
- **Foundations:** Core system entities assumed to exist. Missing entities are logged to the architectural debt registry.
- **State Machine:** When entity states change, a transition table is required: `state × event × guard condition × DB write`.
- **Blind Jury:** For ambiguous architectural choices, 2–3 unlabeled alternatives are generated and evaluated by an independent LLM judge.

All trade-offs are recorded in `decisions.md`. Architectural choices are never made on the fly during coding.

## From Plan to Implementation and Verification

The plan author is not permitted to review their own plan.

The completed plan is sent to an independent reviewer model (Codex, Tencent Hunyuan 3, or Claude Opus). The reviewer checks for mismatched types, missing functions, and unhandled DB migrations. Implementation is blocked until all issues are resolved.

Sample finding from `codex-plan-review.log`:
```markdown
[CRITICAL] Phantom DB method in Phase 2.
Call `db.rates.updateStatus()` does not exist in `src/db/rates.ts`. 
Existing method requires explicit `tenantId`. The plan will break build on step 3.
```

Only after plan approval does the Orchestrator generate code. We enforce BDD (Behavior-Driven Development): tests are written to the specification before implementation. Mutation testing (Stryker) verifies test quality—if code changes pass without failing tests, the build is rejected. After code generation, the `code-vs-plan` gate validates the implementation against Olga's criteria.

The code is then deployed to local staging. Agent Marina executes E2E scenarios via Telethon and Playwright. The pipeline has a hard limit of **5 repair rounds**. If tests fail after 5 `fix -> retest` cycles, execution stops and alerts an engineer on Telegram.

Across **240+ closed plans**:
- **~84% of tasks** pass through the pipeline fully autonomously to verified staging.
- **~16% of tasks** require human intervention (due to undocumented legacy debt, third-party API divergences, or ambiguous ticket requirements).

Production deployment is always executed manually by a human engineer. The pipeline automates development and verification while keeping release authority with the team.

## Key Takeaway

Effective SDD in the AI era is not about writing Markdown documents, but establishing mutual verification between isolated models. Without codebase reconnaissance, independent criteria definition, and adversarial review, specifications quickly drift from production reality. A pipeline with strict verification gates turns specifications into enforceable contracts, making AI-driven development predictable and safe.
