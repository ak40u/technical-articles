---
title: "How a Client Tested a Business Idea for $45,000 Instead of $1.6 Million"
translationKey: "business-idea-validation-savings"
date: 2026-08-08
description: "Five months of one engineer working with AI versus 120–190 person-months for a conventional team. A reverse estimate of the product, E2E system and supporting services without Git history."
summary: "The client paid $45,000 for five months of business-idea validation. Reproducing the full system with a conventional team would cost roughly $1.1–2.3 million. Here is the calculation and the point where AI began to stall."
tags: ["business validation", "AI development", "software cost", "E2E", "technical audit"]
image: "og/business-idea-validation-savings-hero-en.png"
---

Five months. $45,000. One engineer with AI:

One evening I messaged a friend with a rough calculation. The client had paid me $9,000 a month. Five months came to $45,000. A first reverse estimate put the work at about $450,000 for another AI-native team and as much as $1 million for a conventional one.

He replied, “So conventional development teams will soon disappear.”

I pushed back. AI was already stalling at this level of complexity.

Then I inspected the whole system instead of the main repository alone. One million dollars turned out to be low.

I have removed the names of the client, the product and everyone involved. The numbers remain.

## What the Client Bought for $45,000

The client needed an answer to a business hypothesis. A polished prototype would not supply one.

The test required a working B2B product: a staff office, a customer portal, several communication channels, document processing, money, statuses, permissions, background jobs and an audit trail. A user had to complete the journey. A staff member had to receive and process the result.

I worked alone, but the process was not solitary. AI engineering teams wrote modules, tests, migrations, interfaces and checks. I kept architecture, priorities and final decisions with me.

That boundary matters. An agent can produce a great deal of code overnight. In the morning, someone still has to decide whether it solves the problem and whether it is safe to put in front of people.

## The First Estimate Was Incomplete

I started with the core product. The estimate had one rule: ignore commit counts and dates.

Git history is a poor answer to “What would this cost to reproduce?” A repository can be moved. Ten commits can be squashed into one. A finished module can be imported in a single operation.

So I measured functionality and difficulty.

The main product contained about 166,000 lines of production TypeScript, 117 API routes, 33 database tables and 102 migrations. Its internal test system contributed roughly 270,000 more lines. It included transactions, queues, locks, redelivery, several external channels and substantial domain logic.

I estimated functional reproduction by a conventional team at 55–85 person-months. That produced the first range: roughly $500,000–1 million.

Then I remembered the second repository.

## The “Automated Tests” That Became a Product

The external E2E system lived outside the application. It entered the deployed test environment as a real user: messaging, sending email, opening the staff office, checking stored state and collecting evidence.

It contained 164,000 lines of test scenarios. With the harnesses, helpers and runners, the total reached 189,000 lines of executable Python. Static analysis put the lower bound above 900 checks.

There was a short smoke pack, a daily pack, a post-deployment pack and a full pre-release run. The system handled data cleanup, test identities, external-service noise and reviews of the verification itself.

Reproducing that layer adds 45–70 person-months. The familiar “add ten percent for QA” does not work here.

And the system was still larger.

## What Surrounded the Main Product

I went through the remaining directories and removed duplicates. Eleven folders were worktrees of the main product. Three more were temporary E2E worktrees. An old demo repeated functionality that the current product had replaced. Task archives, data exports and third-party boilerplate did not enter the estimate either.

What remained had independent purpose: out-of-band monitoring, a messaging proxy, CRM synchronization, a simulated counterparty, a contact-discovery pipeline, corporate services, reporting tools, the company site and local operations automation.

Together they added another 20–37 person-months. Their code was shorter than the core product. Their cost came from integrations, safety rails, deployment and knowledge extracted from real failures.

## What a Conventional Team Would Need

The final model looks like this:

| Part of the system | Conventional effort |
| --- | ---: |
| Core product and internal tests | 55–85 person-months |
| External E2E system | 45–70 person-months |
| Independent supporting services | 20–37 person-months |
| Total | **120–190 person-months** |

That amount of work would take roughly 14–20 months. The average team would carry 8–11 people and peak at 12–15: a technical lead, backend and frontend engineers, QA automation, infrastructure and product analysis.

I used a fully loaded business cost of $9,000–12,000 per person per month. That includes compensation, taxes, recruitment, management, replacements and the waiting time between people and stages.

The result is $1.1–2.3 million. The middle of the range sits near $1.6 million.

The client paid me $45,000 for five months. Comparing engineering labour alone, the avoided spend is roughly $1.0–2.2 million. The central estimate is the $1.6 million in the title. The calendar difference is about 9–15 months.

This is an estimate of avoided budget. It does not mean the client had two million dollars in an account and I returned the cash. It answers a narrower question: what would it cost to reproduce the same working functions, verification and supporting tools through a conventional route?

## Why the Difference Grew So Large

Code arrived faster. That was the obvious part.

Parallel work mattered more. While one agent investigated an integration, another wrote checks and a third looked for a hole in the plan. I moved between decisions instead of carrying every field by hand.

The distance from hypothesis to working journey became shorter. In a conventional team, an idea travels through specification, estimation, planning, implementation and a QA queue. Those stages remained. The gaps between them shrank.

Permission to throw work away helped too. A team that has already been hired naturally keeps building. My brief was different. Get an honest answer as cheaply as possible. When a hypothesis failed a real user journey, we did not purchase its next layer of architecture.

## Where AI Stalled

By the end of the fifth month, the codebase had become too large for effortless motion. Contexts swelled. One fix touched several channels. Temporary compatibility paths stayed alive. The test system grew large enough to require architecture of its own.

The pace slowed.

This is where developers say, “Anyone can build an MVP, but it will never reach production.” There is truth in that sentence. Production requires transactions, security, recovery, observability and checks across real user journeys.

The direction is still uncomfortable for a conventional team. Until recently, the production layer was its defence. One experienced engineer with AI can now cross a substantial part of that territory. The final stretch is slower and carries debt and difficult corners, but it is reachable.

AI cannot choose which business mistake a client can afford. It cannot accept liability for a data leak. It cannot decide when an idea should be stopped. A person still pays for those decisions with experience and reputation.

AI has not removed the need for a strong engineer. It gave one engineer the temporary size of a department.

The client needed an answer to a business idea. In the past, getting that answer meant building a small technology company first.

That first step is now optional.
