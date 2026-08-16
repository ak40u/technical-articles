---
title: "Spec-Driven Development in the AI Era: Forcing Agents to Write Code by Contract"
date: 2026-08-16
description: "Why canonical SDD turns into dead documentation, and how we built a working process based on production signals, adversarial model reviews, and TDD checks."
author: "Pavel Volkov"
image: "og/sdd-in-production-hero.png"
---

In the Findrates.ai project, Spec-Driven Development runs every day: we have closed over 240 plans through this pipeline. But our real-world process is radically different from the pristine conference slides that present SDD as a silver bullet.

## The Death of Vibecoding

In the early days of AI programming, "vibecoding" ruled—an intuitive, chat-driven approach where a developer simply asks a bot to "build feature X." For rapid prototypes, this worked brilliantly. But on complex legacy systems, vibecoding quickly led to spaghetti code and context drift. The models would forget requirements between sessions, and the developer lost control of the architecture.

As an answer to this chaos, engineers began shifting toward Spec-Driven Development (SDD). The idea is simple: first, write a strict, structured specification (e.g., in Markdown) that becomes the "single source of truth." This specification is grounded in existing knowledge of the codebase and database, serving as an ironclad contract for the AI (in tools like Cursor or Claude) to execute mechanically.

## The Illusion of Canonical SDD

In theory, it sounds perfect. But how do vibecoders actually implement SDD in practice? A developer drafts a plan, feeds it into Cursor, and hits "Apply."

The problem is that even if a human sincerely tries to ground the spec in reality, without systemic isolation and hard barriers, the specification is still written in a vacuum of partial context. The author (or their AI assistant) inevitably invents non-existent database methods and breaks the contracts of neighboring modules. When the AI then writes tests for its own code, it merely validates its own hallucinations. The endless `fix -> error -> fix` loop begins, the specification becomes obsolete two commits later, and the project drowns in technical debt.

We abandoned "trust-based" specs and built a rigorous, multi-layered pipeline where agents keep each other in check.

![SDD Pipeline](/en/articles/sdd-in-production/sdd-pipeline.svg)

To understand the chasm between theory and practice, look at this table:

| Characteristic | Canonical SDD (in tutorials) | SDD in Findrates.ai (in reality) |
| :--- | :--- | :--- |
| **Source of Value** | The client provides a ready-made task and spec | Backlog from business, product, and operators + Producer's filter |
| **Reconnaissance** | Code is written from scratch or guesswork | Orchestrator isolates context and slices the task (`<slug>-slices.md`) |
| **Acceptance Criteria** | Written by the code author (checking themselves) | Written by an independent analyst (Agent Olga) with Must-Not lists |
| **Plan Review** | A human skims the Markdown | Adversarial review by independent LLMs down to zero findings |
| **Verification (TDD)** | Tests are written after implementation | Strict BDD before code + Stryker (mutation testing) |
| **QA and Deploy** | Manual handoff to a tester | Marina's QA cycle: up to 5 rounds of `fix -> retest` (prod is manual only) |

---

## The Value Filter: Don't Burn the Machine

A full SDD cycle (with reconnaissance, adversarial review, mutation testing, and E2E QA) is a resource-intensive pipeline. A single slice execution consumes between $2 and $6 in API tokens and takes 15–25 minutes of model run-time. That is an order of magnitude cheaper and faster than an hour of senior engineer time, but feeding the whole backlog into it indiscriminately is the fastest way to burn your compute budget on tasks nobody needs.

Value in Findrates.ai comes from real people: the Product Owner, business stakeholders, and platform operators file tasks in ClickUp, while researchers request new features. To avoid taking everything into work blindly, we created the Producer agent (the `producer` skill).

Before a single line of spec is written, the Producer analyzes:
1. The full backlog.
2. The goals of the current release (MUST / SHOULD).
3. Lessons learned from past releases (`retro.md`).
4. Production signals (error alerts).

It applies a value filter (CPO-lens) and yields the **Top-5 tasks**. Every task must answer the question "why now?". If a task does not solve an acute platform pain, it is deferred.

## How the Contract is Actually Born

Once a task is selected, the Orchestrator agent takes over. Writing the specification is not just generating one big Markdown file; it is a rigorous, isolated process of five steps.

> **A Note on Agent Personas:** Names like "Olga", "Eva", or "Marina" are not roleplay. They represent strict architectural isolation of contexts and prompt rubrics. The AC agent knows nothing about code to prevent expectation bias (anti-anchoring), while the QA agent has zero access to backend source files, ensuring the system is tested as a strict "black box."

**1. Isolation and Slicing**
The Orchestrator spins up a clean git worktree to avoid crossing paths with neighbors and forcibly slices the task into atomic increments (`plans/<feature-slug>-slices.md`). Planning is always done for only one small slice at a time. If it's a bug fix, a mandatory *Baseline Repro* step is triggered: the QA agent (Marina) attempts to reproduce the bug on the current build. Writing a fix without a confirmed red E2E test is strictly prohibited.

**2. Pre-plan Scout**
Before writing the plan, a read-only script scans the source code to gather exact file paths, dependencies, and current contracts. The plan is always grounded in real code, not LLM fantasies.

**3. Independent Acceptance Criteria (Agent Olga)**
The business analyst agent forms `acceptance-criteria.md`. The golden rule is that she works independently of the code author (anti-anchoring). Olga explicitly writes positive scenarios and mandatory "Must Not" invariants:

```markdown
### Acceptance Criteria
- [ ] When currency changes, recalculate rate using Central Bank rate on creation date.
- [ ] Display currency indicator in rate card and comparison table.

### Must-Not Invariants
- [ ] MUST NOT finalize request with status EXPIRED.
- [ ] MUST NOT invoke `recalculateTotal()` without operator permissions check.
```

**4. UX Contract (Agent Eva)**
If the slice touches the UI, the UX designer Eva steps in. She analyzes the project's existing design system and writes a strict UX contract: required states (loading, empty, error, success), components to reuse, and accessibility requirements.

**5. The Hard Plan and Blind Jury**
Only now does the Tech-Lead agent (a sub-persona of the Orchestrator) generate the actual `plan.md`. The plan is physically split into phase files (`phase-1.md`, `phase-2.md`) to artificially isolate context during future coding. 
The plan contains zero code—only the algorithm, research, and red-team analysis. This rigorous, verified contract is the very core of SDD in our understanding; programming becomes merely the mechanical execution of the specification.

The plan must include:
- **Foundations**: a list of business concepts the feature expects from the core. If something is missing, it is explicitly recorded as architectural debt rather than hacked together.
- **State Machine**: if entity statuses change, the Tech-Lead writes a `state × event × guard × write` table. No status transitions without explicit condition checks.
- **Blind Jury**: for complex tasks, 2-3 alternative architectural solutions are generated (without stating preferences) and sent to an independent "blind" LLM judge to avoid anchoring on the first idea that comes to mind.

All architectural crossroads are forcibly documented in a separate `decisions.md` file. There are zero "on the fly" architectural decisions during coding.

## Running the Gauntlet: From Plan to Staging

The specification is written, but the author of the plan never verifies their own plan. That is the law.

The finished text goes to an independent opposing model (Codex, Tencent Hunyuan 3, or Claude Opus). The reviewer looks for contract mismatches, phantom calls, and missing DB migrations. Development halts until the reviewer issues zero blocking findings.

Here is a real snippet from the reviewer log `codex-plan-review.log`:
```markdown
[CRITICAL] Phantom DB method in Phase 2.
Call `db.rates.updateStatus()` does not exist in `src/db/rates.ts`. 
Existing method requires explicit `tenantId`. The plan will break build on step 3.
```

Only after the specification is approved does the Orchestrator write code. Here, strict BDD (Behavior-Driven Development) and Stryker come into play. We do not allow writing tests "to the code"—they are written strictly to the specification before implementation. Mutation testing (Stryker) ensures the tests aren't empty shells: if the logic can be broken and the tests are still green, the build fails. Once the code is written, a separate `code-vs-plan` gate checks the finished code against Olga's original criteria. Any deviation blocks the branch merge.

Finally, the code is deployed to local staging, and Agent Marina (QA) takes the baton. She runs E2E scenarios (Telethon, Playwright). The Orchestrator has a hard limit—**5 rounds to fix it**. If the feature doesn't run cleanly after 5 iterations of `fix -> retest`, the pipeline stops and calls a human in Telegram.

Across **240+ closed plans**, our operational metrics show:
- **~84% of tasks** converge entirely autonomously from backlog to staging-verified state.
- **~16% of tasks** require human escalation (predominantly due to undocumented legacy debt, third-party API mismatches, or ambiguous product decisions).

Deploying to production **remains a strictly manual human action**. Autonomy liberates developers from the tedious prep and verification loop, but the team retains ultimate accountability for the product.

## Conclusion

Making SDD work in the AI era means moving beyond writing Markdown files. It requires building a pipeline of hard barriers where agents keep each other in check. Without the Producer, independent reconnaissance, and adversarial review, a specification remains dead text. But with them, it transforms into an executable contract that moves the business forward without accumulating debt.
