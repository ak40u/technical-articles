---
title: "Spec-Driven Development in Production: How We Build via Specs"
date: 2026-08-16
description: "Why canonical SDD turns into dead documentation, and how we built a working process based on a producer agent, adversarial model reviews, and TDD checks."
author: "Pavel Volkov"
image: "og/sdd-in-production-hero-en.png"
---

A colleague recently sent me a screenshot of a chat: "Have you read about SDD? Implement it for me."

In the Findrates.ai project, Spec-Driven Development runs every day. We have closed over 240 plans through this pipeline. And our approach is radically different from the beautiful conference slides that describe SDD as a silver bullet.

## The Illusion of Canonical SDD

Tutorials promise a straightforward path. You write a specification in OpenAPI, JSON Schema, or Markdown. You hand it to an AI agent. The agent writes a ready-made service. The specification becomes the single source of truth.

On a live, legacy codebase, this process breaks immediately.

If an agent (or a human programmer) conjures a specification "out of thin air," they invent database methods and break the contracts of neighboring modules. When that same agent writes tests for its own code, it verifies its own hallucinations. The specification becomes obsolete two commits later, and unmanageable technical debt (drift) begins.

We abandoned specs from thin air and built a rigorous, multi-layered pipeline.

![SDD Pipeline](/en/articles/sdd-in-production/sdd-pipeline.svg)

## Canonical SDD vs Our Reality

To understand the chasm between theory and practice, look at this table:

| Characteristic | Canonical SDD (in articles) | SDD in Findrates.ai (reality) |
| :--- | :--- | :--- |
| **Source of Value** | The client provides a ready task and spec | Backlog from business, PO, and operators + Producer's filter |
| **Reconnaissance** | Code is written from scratch or by guessing | The Orchestrator isolates context and slices the task (`<slug>-slices.md`) |
| **Writing Criteria** | Written by the code author (self-checking) | Written by an independent analyst (Agent Olga) |
| **Plan Review** | A human skims the Markdown | Adversarial review by Codex/Opus down to zero findings |
| **Verification (TDD)** | Tests are written post-implementation | Strict BDD before code + Stryker (mutation testing) |
| **QA and Deploy** | Manual handoff to a tester | Marina's QA loop: 5 rounds of `fix -> retest` autonomously |

---

## Stage 0: Finding Value (The Producer Agent)

The main problem with SDD is writing a perfect specification for a feature that nobody needs. Value in our project comes from real people: the Product Owner, business stakeholders, and platform operators file tasks in ClickUp (bugs and wishes), while researchers request new features.

To avoid taking everything into work blindly, we created the Producer agent (the `producer` skill). Before a single line of spec is written, the Producer analyzes:
1. The full backlog (wishes and bugs from people).
2. The goals of the current pilot (MUST / SHOULD).
3. Lessons learned from past releases (`retro.md`).
4. Production signals (error alerts).

It applies a CPO-lens value filter and outputs the **Top-5 Tasks**. Every task must answer the question "why now?". If a task does not alleviate user pain, it gets deferred.

## Stage 1: Reconnaissance and Planning (The Orchestrator)

Once a task is selected, the Orchestrator agent takes over. Its job is to drive the feature from idea to staging without stopping.

The specification starts with context isolation and decomposition (Preflight). The Orchestrator spins up a clean git worktree to avoid crossing paths with neighbors, and slices the task into independent increments (`plans/<feature-slug>-slices.md`). You cannot describe a system entirely — planning is only done for one small, independent slice at a time.

Next, Agent Olga (the business analyst) independently forms `acceptance-criteria.md`. She writes not only what should work, but also "Must Not" lists — things the code is strictly forbidden to do.

Only then is `plan.md` born — a document with rigid execution phases and a `decisions.md` file, where all architectural crossroads are recorded (why we chose option A instead of B).

## Stage 2: Adversarial Review

The author of the plan never checks their own plan. That is a strict rule.

The finished specification text goes to an independent opposing model (Codex, Tencent Hunyuan 3, or Claude Opus). The reviewer looks for contract inconsistencies, phantom calls, and missing database migrations.

A cycle of checks begins. Development halts until the reviewer issues zero blocking findings. On complex tasks, this takes two to four iterations.

Here is a real fragment of a reviewer's log (`review-round1-findings.md`):
```markdown
[CRITICAL] Phantom DB method in Phase 2.
The call `db.invoices.updateStatus()` does not exist in `src/db/invoices.ts`. 
The existing method requires passing a `tenantId`. The plan will break the build at step 3.
```

## Stage 3: Code Verification and TDD

The specification is approved. The Orchestrator writes the code.

Here, strict BDD (Behavior-Driven Development) and Stryker come into effect. We do not allow writing tests "from code" — they are written strictly according to the specification before implementation. And mutation testing (Stryker) ensures the tests aren't empty shells: if the logic can be broken but the tests remain green, the build fails.

After writing, the `code-vs-plan` barrier triggers. A separate agent verifies the finished code against Olga's original criteria. Any deviation from the plan blocks branch merging.

## Stage 4: Marina's QA Loop

If the code passes all gates, the Orchestrator deploys it to local staging and passes the baton to Agent Marina (QA skill).

Marina runs e2e scenarios (Telethon, Playwright). If she finds a bug, she returns it to the Orchestrator. The Orchestrator has a limit — **5 rounds to fix it**. If the feature does not run cleanly after 5 `fix -> retest` iterations, the Orchestrator surrenders and pages a human on Telegram.

## Conclusion

Making SDD work in the AI era means building a pipeline of rigid barriers. Without a Producer, independent reconnaissance, and adversarial review, a specification remains dead text. But with them, it becomes an executable contract that drives the business forward.
