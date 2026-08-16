---
title: "Spec-Driven Development in Production: How We Build via Specs"
date: 2026-08-16
description: "Why canonical SDD turns into dead documentation, and how we built a working process based on a producer agent, adversarial model reviews, and TDD checks."
author: "Pavel Volkov"
image: "og/sdd-in-production-hero-en.png"
---

A colleague recently sent me a screenshot of a chat: "Have you read about SDD? Implement it for me."

In the Findrates.ai project, Spec-Driven Development runs every day. We have closed over 240 plans through this pipeline. And our approach is radically different from the beautiful conference slides that describe SDD as a silver bullet.

## The Evolution from Vibecoding to SDD

In the early days of AI programming, "vibecoding" ruled—an intuitive, chat-driven approach where a developer simply asks a bot to "build feature X." This worked for rapid prototypes, but on complex systems, it led to spaghetti code and context drift. The AI would forget requirements between sessions.

The industry's answer was Spec-Driven Development (SDD). The idea is to first write a strict, structured specification (e.g., in Markdown) that becomes the single source of truth. This specification is meant to be grounded in existing knowledge of the codebase and database, serving as an ironclad contract for the AI (in tools like Cursor or Claude) to execute.

## The Illusion of Canonical SDD

In theory, it sounds perfect. But how do vibecoders actually implement SDD in practice? A developer drafts a plan or asks an LLM to generate a spec, feeds it into Cursor, and hits "Apply."

The problem is that even if a human tries to ground the spec in reality, without systemic isolation and hard barriers, the specification is still written in a vacuum of partial context. The author (or their AI assistant) inevitably invents non-existent database methods and breaks the contracts of neighboring modules. When the AI writes tests for its own code, it merely verifies its own hallucinations. The endless `fix -> error -> fix` loop begins, the specification becomes obsolete two commits later, and unmanageable technical debt (drift) takes over.

We abandoned "trust-based" specs and built a rigorous, multi-layered pipeline.

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

A full SDD cycle (with reconnaissance, review, and TDD) is an expensive pipeline. The main mistake is feeding everything from the backlog into it blindly. Value in our project comes from real people: the Product Owner, business stakeholders, and platform operators file tasks in ClickUp (bugs and wishes), while researchers request new features.

To avoid burning the Orchestrator's resources on tasks that aren't needed right now, we created the Producer agent (the `producer` skill). Before a single line of spec is written, the Producer analyzes:
1. The full backlog (wishes and bugs from people).
2. The goals of the current release (MUST / SHOULD).
3. Lessons learned from past releases (`retro.md`).
4. Production signals (error alerts).

It applies a CPO-lens value filter and outputs the **Top-5 Tasks**. Every task must answer the question "why now?". If a task does not alleviate user pain, it gets deferred.

## Stage 1: Reconnaissance and Planning (The Orchestrator)

Writing the specification is not just generating one big Markdown file; it is a rigorous process of several isolated steps. The Orchestrator spins up a clean git worktree, reads all task comments, and begins reconnaissance.

**Step 1. Isolation and Slicing**
The Orchestrator forcibly slices the task into atomic increments (`plans/<feature-slug>-slices.md`). Planning is done for only one small slice at a time. If it's a bug fix, a mandatory *Baseline Repro* step is triggered: the QA agent (Marina) attempts to reproduce the bug on the current build. Writing a fix without a confirmed red E2E test is strictly prohibited.

**Step 2. Pre-plan Scout**
Before writing the plan, a read-only script scans the source code to gather exact file paths, dependencies, and current contracts. The plan is always grounded in real code, not LLM fantasies.

**Step 3. Independent Acceptance Criteria (Agent Olga)**
The business analyst agent forms `acceptance-criteria.md`. The golden rule is that she works independently of the code author (anti-anchoring). Olga explicitly writes positive scenarios and "Must Not" invariants—things the code is absolutely forbidden to do.

**Step 4. UX Contract (Agent Eva)**
If the slice touches the UI, the UX designer Eva steps in. She analyzes the project's existing design system and writes a strict UX contract: required states (loading, empty, error, success), components to reuse, and accessibility requirements.

**Step 5. The Hard Plan and Blind Jury**
Only now is the actual `plan.md` generated. This is a step-by-step execution algorithm for a robot.
The plan must include:
- **Foundations**: a list of concepts the feature expects from the core. If something is missing, it is recorded as architectural debt.
- **State Machine**: if entity statuses change, the Orchestrator writes a `state × event × guard × write` table. No status transitions without explicit condition checks.
- **Blind Jury**: for complex tasks, 2-3 alternative architectural solutions are generated (without stating preferences) and sent to a "blind" LLM judge to avoid anchoring on the first idea that comes to mind.

All architectural crossroads are forcibly documented in a separate `decisions.md` file. There are zero "on the fly" architectural decisions during coding. Finally, the finished plan goes through several rounds of adversarial review (Codex) until the judge says `NO ISSUES`.

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
