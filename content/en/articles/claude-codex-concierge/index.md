---
title: "How I Built a Concierge for Claude Code and Codex"
translationKey: "claude-codex-concierge"
date: 2026-07-31
description: "Why dozens of AI sessions force you to delegate not just tasks but their management: a Telegram concierge, a memory of decisions, routing, and result tracking."
summary: "A practical breakdown of a personal AI concierge for Claude Code and Codex: how it understands incoming requests, resumes the right sessions, tracks assignments, and returns results."
tags: ["AI agents", "Claude Code", "Codex", "Telegram", "project management"]
image: "og/claude-codex-concierge-hero-en.png"
---

The more I use AI, the faster each individual task moves. Then the acceleration hits the most primitive part of the system. Me.

Claude Code writes code, Codex reviews the changes, a third session hunts a failure, a fourth waits for review. They can work in parallel. My brain cannot. Working memory holds a few independent items at once; research usually puts the number near four [meaningful chunks](https://pubmed.ncbi.nlm.nih.gov/11515286/). The exact limit depends on the task and on how well information is grouped. It is nowhere near dozens of live sessions.

I started losing track of which agent I had answered, what each one was waiting for, and where the finished result was sitting. The sessions did not forget their tasks. I did.

My first attempt was Agent Dashboard, a separate Electron application showing projects, sessions and recent events. At the computer it took some load off: ten windows became one screen.

Then I connected a Telegram bot to it. From a phone it is easier to ask one question: "What is happening with Logicore?" Or to forward a colleague's message with "pass this to the project". I expected a mobile entry point into the same dashboard to be enough.

The first prototype exposed the difference between access to events and understanding of work. Once I asked the bot what was happening in a project. It looked at the timestamp of the last entry and confidently reported the session had been stuck for an hour and a half. At that moment my Mac screen said `2 running tasks`. Another time I delegated work through the same bot. The agent finished, the result was already in the dashboard, and Telegram stayed silent. Twenty minutes later I wrote: "Well?"

I did not need a mobile log viewer. I needed an assistant that remembers the agents for me: knows who is doing what, resumes the right session, passes in new information, and comes back with the result on its own.

That is how the Concierge appeared.

## When delegating tasks is no longer enough

The first stage of working with AI looks the same for almost everyone. You take a task, describe it to an agent, get the result. Better instructions and tools mean larger units of work go out whole.

On one project this is pure acceleration. I still remember why each session is open, what it already knows, and which answer needs checking. Management stays invisible because it costs less time than the work.

Then there are ten projects and hundreds of tasks. Execution keeps getting cheaper, but a new cost appears: choosing the next task, finding the right context, not starting a duplicate, noticing a blocker, waiting for the result, recalling a decision from last week.

I had delegated execution and kept all the dispatch work. AI sped up task production so much that I became the bottleneck.

The next move is one level up. Agents take over not only work inside a project but a large part of its operational management: intake, routing, resuming previous sessions, tracking unfinished turns, scheduled checks, summaries.

The human keeps the portfolio level. I decide why a project exists, where it goes, how much risk is acceptable, which irreversible actions are allowed. The Concierge keeps work moving between those decisions.

An ordinary company grows the same way. The founder first hires people to get more work done. Then discovers the whole day goes to assigning tasks and asking for status. At that point another individual contributor is not the answer. A management loop is.

![Two levels of delegation: a person manages individual tasks or hands the operational project loop to a concierge](delegation-levels.svg "When tasks number in the hundreds, the main constraint is no longer execution but the queue, context, and control.")

## Why I needed a separate agent

The Concierge lives in Telegram and accepts messages only from me. Text, voice, a screenshot, a document, a fragment of a forwarded conversation.

Its work starts before any project agent is called. It has to work out which project the request belongs to, find the previous session, keep its context, and decide whether anything needs doing at all. Sometimes I only want a summary. Sometimes I want the work continued. Sometimes I forward a message with no verb — then offering choices beats acting.

The Concierge must not fix the project itself. I caught it trying to help quickly several times: connecting over SSH, opening a database, reading a repository directly. That saved time on the first step only. After that, roles, permissions and work history got mixed together.

The rule is simple now. The Concierge interprets and coordinates. Work inside a project stays in that project's session.

The same rule settled the model choice. At first we routed by stereotype: code to Codex, operational work to Claude. Continuity turned out to matter more. If a project already lives in Claude Code, that session holds instructions, skills, an open branch and memory of past decisions. Opening Codex because a request contains the word "code" throws all of it away.

So the Concierge looks for an existing session and resumes it. It creates a new one only when there is nothing to continue. The provider for a new session is inherited from the project's history too.

## The path of one request

Suppose I forward a curator's question to Telegram. A second earlier I manage to write a separate line: "this is our curator".

An early version grabbed the first sentence immediately and replied that it did not know who I meant. Now adjacent messages enter a short collection window. Caption, forwarded message and attachment reach the model as one ordered package.

Next the Concierge compares the mentions against dashboard projects and its working memory. Reliable match — it proposes the action straight away. Weak context — Telegram shows two or three buttons: pass the request to the matched session, create a separate assignment, or just save the information. Nothing changes before I choose.

After the choice the task goes to the project agent and one status message stays in the chat. Its text changes as work proceeds: the agent reads data, runs a command, edits files, checks the result. It is a service message and must not crowd out the substantive reply.

When the project session finishes its turn, a separate watcher notices the final state and wakes the Concierge. The result arrives as a new message. Long logs and engineering details stay behind a "Technical report" button.

The new message matters. Edit the old one and Telegram often shows no notification. Formally the answer was delivered; the person never saw it.

![The path of an assignment from Telegram to a verifiable result in an existing or new project session](request-lifecycle.svg "The model understands and routes the request. Delivery, observation, and retries run separately.")

## What runs without a model

A pinned Claude Code session on Sonnet handles understanding. It does not close after every answer. The process waits for the next message on standard input: idle time burns no tokens, and a new request does not pay to start another session.

Everything related to reliability I gradually moved out of the language model.

A local outbox holds a finished reply until Telegram confirms delivery. A network failure retries the send, not Sonnet's reasoning. The scheduler computes the next run itself. The watcher tracks assignments without continuous AI polling. A watchdog restarts the service after a failure with the same session ID.

Inside, it came out as a few simple parts:

| Component | Responsibility |
|---|---|
| Telegram bot | Mobile input and reply delivery |
| Pinned Sonnet session | Intent understanding and conversational context |
| Agent Dashboard | Projects, Claude/Codex sessions, and events |
| Task watcher | Progress, stalled starts, and final results |
| Project Brain | Facts, decisions, and open questions for each project |
| Scheduler | Recurring assignments and run history |
| Decision corpus | Search for similar choices in old sessions |

Sonnet has Full Access: Chrome, skills, plugins, connected MCP servers. An interceptor still blocks shell commands and direct project-file access from the Concierge session. A written promise to stay out of projects was not enough.

## The failures that shaped the architecture

The first version started a new Claude session per request. The bot replied, exited, forgot the conversation. "Check again" naturally produced a question back: check what? One pinned session fixed the context and cut response time.

Then it turned out that dispatching a task is not enough. Claude Code has no event that makes a model, once it has replied, speak again when another session finishes. That is why the independent watcher exists. I no longer write "Well?" to find a result that is already done.

The next failure looked mysterious: some replies "did not render". Telegram's log said everything succeeded. The initial reply and the progress tracker were editing the same `message_id`; whoever wrote last stayed on screen. We reserved the old message for progress and started sending substantive replies separately. We also added a technical delivery log: API method, result ID, attempt number, fallback, text hash. The text itself is not logged.

Another bug pushed an internal exception to the user:

```text
Claude returned an invalid intake proposal
```

The cause was mundane. The model parsed the request correctly but invented a button label longer than 48 characters. Those fields are normalised locally first now. If the structure is still invalid, the service asks the model to repair it once. The final fallback offers safe read-only actions instead of an exception trace.

Write permissions needed their own investigation. The Concierge had two separate restrictions: normal authorisation to mutate data, and an extra confirmation for dangerous operations. Both returned a similar refusal, so even the agent could not explain why adjacent requests behaved differently.

Authorisation is now issued for one specific Telegram message, expires quickly, and carries a risk scope: read-only, reversible mutation, dangerous action. A refusal includes a reason code and the risky fragment that was found. Repeating the same forbidden call does not push it through.

## What it remembers about me

A long chat history makes poor memory. Words are easy to find in it; the moment a person actually made a choice is not.

The Concierge indexes my decisions from local Claude and Codex sessions separately. Each record keeps the preceding conversation, my formulation, the agent's next reply, and the names of the tools used. Command arguments and tool results stay out of the index.

For example, I once said firmly: "ai-panel is a different project. Do not touch it." A later request about a new interface found that precedent and produced a useful recommendation: create a separate repository instead of bolting the feature onto a project with a similar name.

This search does not turn the model into a copy of me. It lets the model make a prediction and show its basis: which past decisions look similar, how close they are, what information is missing now. After I make the actual choice, the prediction gets calibrated.

Project Brain sits next to the general index. A short memory per project: confirmed facts, recent decisions, the usual provider, open questions. Daily summaries no longer depend on the last ten lines of the newest session.

## Assignments that return on their own

I do not use slash commands in ordinary conversation. A recurring assignment is created with a sentence:

> Send me a Logicore summary at ten on weekdays until September 1.

Or:

> Check the migration every three hours, eight times in total.

Before saving, the Concierge shows how it understood the interval, the repeat limit and the next runs. The same conversational route changes the schedule, pauses it, runs it now, or deletes it.

The schedule database lives on the Mac and survives service restarts. A missed day does not produce a queue of obsolete runs. A task cannot run in parallel with itself. After three persistent failures it stops and reports the reason.

For publishing, payments, deletion or a production deployment, a permanent schedule is not permanent consent. Every such run asks again.

## Where the system stands now

On July 31, 2026, a local installation check shows one live pinned Sonnet session. The dashboard sees 12 projects and 38 Claude and Codex sessions. The index holds 4,246 decision records from three source types. The current suite of 171 tests passes.

The numbers will age fast. The limits will not.

The Mac and Agent Dashboard have to be running, or the Concierge cannot reach project sessions. Another session may stop because of the network, authorisation, or a missing tool. A forwarded screenshot without explanation can genuinely be ambiguous. The decision model finds analogues; it does not read minds.

I tested local models too. Some sounded convincing in ordinary conversation, but quality dropped on routing, strict tool schemas and dangerous scenarios. Sonnet stays the central dispatcher for now. Speech recognition, storage, search, scheduling and observation run locally.

I can now leave home without the laptop, forward a task to the Concierge, and get an answer from the same project session I worked with that morning. The agent is stuck — I see it in Telegram. It finished — the result arrives on its own.

That was the point.
