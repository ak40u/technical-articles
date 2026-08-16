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

Once a task is selected, the Orchestrator agent takes over. Its job is to drive the feature from idea to staging without stopping. But writing the spec itself isn't just generating one big file; it's a strict multi-step process.

**Step 1. Isolation and Slicing (Preflight).** The Orchestrator spins up a clean git worktree to avoid crossing paths with neighbors and reads all comments on the task. Large features are never planned as a monolith. The Orchestrator forcibly slices the task into independent, ship-and-go increments (`plans/<feature-slug>-slices.md`). The specification is written for only one atomic increment at a time.

**Step 2. Independent Acceptance Criteria.** Agent Olga (the business analyst) forms `acceptance-criteria.md`. The golden rule is that she works independently from the code author to avoid cognitive anchoring. Olga explicitly writes both positive scenarios and "Must Not" invariants—things the code is strictly forbidden to do.

**Step 3. The Hard Plan.** Only now is the actual `plan.md` generated. This isn't just a feature description; it is a step-by-step algorithm for a robot: Phase 1 (create tables), Phase 2 (write DTOs), Phase 3 (integration). All architectural crossroads and chosen tradeoffs are forcibly documented in a separate `decisions.md` file. There are zero "on the fly" architectural decisions during coding.

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
