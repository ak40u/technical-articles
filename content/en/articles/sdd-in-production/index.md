---
title: "Spec-Driven Development in Production: How We Build via Specs"
date: 2026-08-16
description: "Why the textbook SDD fails, and how we built a working process based on adversarial model reviews and TDD verification."
summary: "A colleague asked about Spec-Driven Development. Our experience across 240+ plans in logicore-platform shows that a specification breaks without prior scouting and an adversarial review agent."
tags: ["SDD", "Spec-Driven Development", "AI development", "architecture", "logicore-platform"]
image: "og/sdd-in-production-hero-en.png"
translationKey: "sdd-in-production"
---

A colleague sent a screenshot of a conversation: “Have you read about SDD? Implement it for me.”

Spec-Driven Development works every day in `logicore-platform`. We have closed over 240 plans using this process. Our approach differs completely from canonical conference slides.

## The Illusion of Canonical SDD

Tutorials promise a straight path. You write a specification in OpenAPI, JSON Schema or Markdown. You hand it to an agent. The agent writes a ready service. The specification becomes the single source of truth.

On a live codebase, this process breaks immediately.

If an agent invents a specification from memory, it hallucinates database methods and breaks the contracts of neighbouring modules. When the same agent writes tests for its own code, it tests its own hallucination. The specification becomes obsolete after two commits. Drift begins.

We abandoned specifications generated from thin air.

## Scout Before Spec

A specification begins with fact gathering. A scout agent explores the codebase before creating the first line of the plan.

The scout builds a map of connections: file paths, line numbers, table schemas and current invariants. The result is saved in `scout-map.log`. Only then does the orchestrator move to the plan. You cannot describe a system without firmly attaching the description to the current state of the project.

## Anatomy of a Plan

In `logicore-platform`, a plan consists of a set of files in a `plans/` directory:

* `plan.md` — work steps with file paths and decision paths.
* `acceptance-criteria.md` — formal invariants (Must, Must Not, Should).
* `decisions.md` — recorded branches showing rejected alternatives.
* `failing-first-ledger.md` — tests that must fail before any code changes.
* `phase-XX-...md` — breakdown into independent steps.

A recent bug involving free container parking required a rewrite of the storage and parser. We did not fix the code blindly. The plan recorded the date calculation logic in `decisions.md` and described the failing tests in `failing-first-ledger.md`.

## Adversarial Review

The author of a plan does not review its own plan.

The drafted specification goes to an independent, opposing model — Codex, DeepSeek V4 Pro or Claude Opus. The reviewer looks for contract mismatches, phantom calls and missing migrations.

Checks run in a loop. Logs go to `codex-plan-review-roundX.log` and findings to `review-roundX-findings.md`. Development halts until the reviewer returns zero blocking remarks. On complex tasks, this takes two to four iterations.

## Code vs Plan and Drift

The specification is approved. The code is written. Next comes the verification gate: `code-vs-plan-round1-disposition.md`.

A separate agent compares the code against the original `acceptance-criteria.md`. Any deviation from the plan blocks the merge. TDD verification via `failing-first-ledger` proves that the tests failed before the edits, rather than being written to pass the finished code.

At the database level, runtime reconcile scripts run. They catch data discrepancies as the first sign of specification decay in production.

Making SDD work means building a pipeline of hard barriers. Without independent scouting and adversarial review, a specification remains dead text.
