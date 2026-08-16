---
title: "Spec-Driven Development in Production: How We Build via Specs"
date: 2026-08-16
description: "Why canonical SDD turns into dead documentation, and how we built a working process based on a producer agent, adversarial model reviews, and TDD checks."
author: "Pavel Volkov"
image: "og/sdd-in-production-hero-en.png"
---

A colleague recently sent me a screenshot of a chat: "Have you read about SDD? Implement it for me."

In the `logicore-platform` project, Spec-Driven Development runs every day. We have closed over 240 plans through this pipeline. And our approach is radically different from the beautiful conference slides that describe SDD as a silver bullet.

## The Illusion of Canonical SDD

Tutorials promise a straightforward path. You write a specification in OpenAPI, JSON Schema, or Markdown. You hand it to an AI agent. The agent writes a ready-made service. The specification becomes the single source of truth.

On a live, legacy codebase, this process breaks immediately.

If an agent (or a human programmer) conjures a specification "out of thin air," they invent database methods and break the contracts of neighboring modules. When that same agent writes tests for its own code, it verifies its own hallucinations. The specification becomes obsolete two commits later, and unmanageable technical debt (drift) begins.

We abandoned specs from thin air and built a rigorous, multi-layered pipeline.

![SDD Pipeline](/en/articles/sdd-in-production/sdd-pipeline.svg)

## Canonical SDD vs Our Reality

To understand the chasm between theory and practice, look at this table:

| Characteristic | Canonical SDD (in articles) | SDD in `logicore-platform` (reality) |
| :--- | :--- | :--- |
| **Source of Value** | The client provides a ready task and spec | The Producer agent scans the backlog and error logs |
| **Reconnaissance** | Code is written from scratch or by guessing | The Scout agent builds a `scout-map.log` before planning |
| **Writing Criteria** | Written by the code author (self-checking) | Written by an independent analyst (Agent Olga) |
| **Plan Review** | A human skims the Markdown | Adversarial review by Codex/Opus down to zero findings |
| **Verification (TDD)** | Tests are written post-implementation | `failing-first-ledger.md`: tests MUST fail before code |
| **QA and Deploy** | Manual handoff to a tester | Marina's QA loop: 5 rounds of `fix -> retest` autonomously |

---

## Stage 0: Finding Value (The Producer Agent)

The main problem with SDD is writing a perfect specification for a feature that nobody needs. To avoid this, we created the Producer agent (the `producer` skill).

Before a single line of spec is written, the Producer analyzes:
1. The full backlog (hundreds of tasks).
2. The goals of the current pilot (MUST / SHOULD).
3. Lessons learned from past releases (`retro.md`).
4. Production signals (error alerts).

It applies a CPO-lens value filter and outputs the **Top-5 Tasks**. Every task must answer the question "why now?". If a task does not alleviate user pain, it gets deferred.

## Stage 1: Reconnaissance and Planning (Autopilot)

Once a task is selected, the Orchestrator agent (the `autopilot` skill) takes over. Its job is to drive the feature from idea to staging without stopping.

The specification starts with gathering facts. A Scout agent explores the codebase before creating the first line of the plan. It builds a map of relationships: file paths, line numbers, table schemas, and current invariants. The result settles in the `scout-map.log` artifact. You cannot describe a system without being tightly bound to the project's current state.

Next, Agent Olga (the business analyst) independently forms `acceptance-criteria.md`. She writes not only what should work, but also "Must Not" lists — things the code is strictly forbidden to do.

Only then is `plan.md` born — a document with rigid execution phases and a `decisions.md` file, where all architectural crossroads are recorded (why we chose option A instead of B).

## Stage 2: Adversarial Review

The author of the plan never checks their own plan. That is a strict rule.

The finished specification text goes to an independent opposing model (Codex, DeepSeek V4 Pro, or Claude Opus). The reviewer looks for contract inconsistencies, phantom calls, and missing database migrations.

A cycle of checks begins. Development halts until the reviewer issues zero blocking findings. On complex tasks, this takes two to four iterations.

Here is a real fragment of a reviewer's log (`review-round1-findings.md`):
```markdown
[CRITICAL] Phantom DB method in Phase 2.
The call `db.invoices.updateStatus()` does not exist in `src/db/invoices.ts`. 
The existing method requires passing a `tenantId`. The plan will break the build at step 3.
```

## Stage 3: Code Verification and TDD

The specification is approved. The Orchestrator writes the code.

Here, `failing-first-ledger.md` comes into effect. A TDD check guarantees that the written tests failed *before* edits were made to the main code, rather than being written to fit an already completed implementation. If a test is instantly green, the code is rolled back.

After writing, the `code-vs-plan` barrier triggers. A separate agent verifies the finished code against Olga's original criteria. Any deviation from the plan blocks branch merging.

## Stage 4: Marina's QA Loop

If the code passes all gates, Autopilot deploys it to local staging and passes the baton to Agent Marina (QA skill).

Marina runs e2e scenarios (Telethon, Playwright). If she finds a bug, she returns it to Autopilot. Autopilot has a limit — **5 rounds to fix it**. If the feature does not run cleanly after 5 `fix -> retest` iterations, Autopilot surrenders and pages a human on Telegram.

## Conclusion

Making SDD work in the AI era means building a pipeline of rigid barriers. Without a Producer, independent reconnaissance, and adversarial review, a specification remains dead text. But with them, it becomes an executable contract that drives the business forward.
