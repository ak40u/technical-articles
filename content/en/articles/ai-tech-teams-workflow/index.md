---
title: "How I Built a Workflow for Autonomous AI Engineering Teams"
date: 2026-07-09
description: "How I separated roles, verification, and release so several AI teams could work in parallel without my constant supervision."
summary: "A practical breakdown of an autonomous AI engineering team system: roles, task queues, QA, audits, retrospectives, and the release pipeline."
tags: ["AI agents", "autonomous development", "QA", "architecture", "releases"]
image: "og/ai-tech-teams-workflow-hero-en.png"
translationKey: "ai-tech-teams-workflow"
---

*How I separated roles, verification, and release so several AI teams could work in parallel without my constant supervision.*

## In Brief

I stopped treating an AI agent as a lone executor that simply needs a good instruction and more context. That setup is too fragile: the agent comes up with the solution, writes the tests, trusts those tests, and then reports “done.”

Instead, I built a repeatable workflow for a small engineering team. One run takes a task, or a coherent part of one, breaks the work into pieces, separates responsibilities, and goes through a PR, CI, a staging environment, QA, and a QA audit. Only then does it return a result: done or blocked. The production release is automated too, but it lives outside the development loop.

Each run has six permanent AI roles: an orchestrator and tech lead, a plan reviewer, a QA agent, a QA auditor, a UX reviewer, and an environment engineer. They do not own the product; they own stages of the process. Product boundaries, disputed decisions, and starting the release autopilot remain my responsibility. Along the way, those roles bring in additional checks for security, accessibility, data, CI, browser journeys, and visual quality.

The main rule is simple: no “done” is accepted at face value. Authors do not verify their own work, a separate auditor checks QA, and a service check reads the files before the run can close. If a required verdict is missing or has the wrong type, the run stays open.

The system keeps its own run log. In the latest snapshot, there were 15 runs across six calendar days: one stopped and asked for my decision, and one bug still passed every check and became material for a new rule. A task took an average of 1.4 QA runs and 0.93 QA audits. The system has now completed 93 retrospectives. These numbers are not a comparison with human teams. They show something else: how much work the system completes without my manual involvement, where it stops on its own, and which errors still slip through.

## §1. Why I Went Down This Path

An agent is often perfectly capable of writing the code. The problem starts later, when it says “done.”

An autonomous developer has an unpleasant habit of verifying itself. It writes the code, writes the tests, runs them, gets a green result, and honestly concludes that it fixed the problem. But the tests may have repeated the same mistake as the implementation.

I had exactly that happen. A fix passed review, unit tests, and CI. On paper, everything looked clean. The staging environment told a different story: the corrected branch of the code was not reachable through the real user journey at all. Routing sent the flow elsewhere, and the fixed dialog never opened. The code was correct. The user could not reach it.

That made one thing clear: it is not enough to make an agent write code and run tests. You have to verify that the change is actually available to the user.

The second problem is more mundane but more painful: long autonomous processes die. The laptop goes to sleep, a background task stops, a notification gets lost, or the context runs out. From the outside, it looks like the agent silently stopped and everything is stalled until you ask, “So, how is it going?” Autonomy that needs constant supervision quickly becomes another job.

The third problem is the boundary of independent decision-making. An agent either asks about every small detail or, at the other extreme, makes a decision that should have come to me. Both destroy the point of automation.

That is how the engineering-team system emerged: not one all-powerful agent and not an instruction for every possible case, but a repeatable team template. It has roles, evidence, recovery after failure, and a formal boundary between “decide for yourself” and “stop.”

## §2. Not One Agent, but a Team

One agent with a large context is still a single point of failure. It may be smart, fast, and careful, but one question remains at the end: who checked its work?

I approached the problem from the opposite direction: I stopped trying to build one perfect agent. Instead, I assembled a small autonomous engineering team. It has roles, separate state, locks, reports, a message queue, and a clear rule for where the team decides on its own and where it stops and calls me.

The team's job is broader than writing code. It must bring a change to a verified state on the staging environment and leave a trail behind it: a plan, checks, verdicts, screenshots, decisions, and errors.

So the main question is not how quickly code is typed, but how trust is designed. Who proposes a solution, who checks it, where the evidence lives, what happens after a process crashes, how several teams avoid getting in one another's way, and how a rule born from a single incident avoids becoming a mandatory but useless procedure.

This led to four basic rules.

1. **The author and the verifier are separate.** If the orchestrator writes the plan, another agent reviews it. If the team writes the code, an outside reviewer compares it with the plan. QA checks the product separately, and a QA auditor separately checks the QA work itself. Different models are useful here not because the diagram looks impressive, but because they fail in different ways.

2. **Evidence matters more than statements.** A QA verdict does not remain in a chat. It is written to a structured file inside the run report. The same applies to the QA audit and the UX verdict. The final check reads files, not the tone of a model's response.

3. **Every rule needs a reason.** The protocol was not invented in advance. It grew out of retrospectives. Every rule has an incident label: why it exists and which class of error it is meant to prevent.

4. **Escalation to me must not depend on the agent's mood.** Before asking me, the agent checks whether the decision is reversible, the consequences are limited, and the task remains within the agreed scope. If all three are true, the team decides for itself and records the decision in the log. If the product meaning changes, the cost of error is high, or several attempts have already failed, the run stops and asks for a decision.

The distrust extends to the task description itself. A task provides a symptom and acceptance criteria. Any named files, presumed root cause, and proposed fix are treated as hypotheses. This is especially important when the text was already written with a large language model: invented APIs and very confident but incorrect explanations appear there regularly.

Sometimes the team argues with me too. If a task looks like polishing for the sake of polishing, it sends it back with a question about its value. An autonomous team that can make a reasoned objection is more useful than one that silently executes everything.

## §3. One Engineering Team: Permanent Roles and Temporary Checks

One system run is not “an agent with a large context,” but a small team with roles and separate communication channels. When a batch of tasks arrives, it is distributed among teams like these instead of being crammed into one endless conversation.

The table below is not there to make the org chart look impressive. It shows the boundaries of responsibility: who plans, who reviews the plan, who looks at the product through the user's eyes, who checks the check itself, and who owns the environment.

| Role | Responsibility | Environment | What It Leaves Behind |
| --- | --- | --- | --- |
| Orchestrator | Plan, code, PR, execution loop, notifications | Claude | Plan, changes, PR, reports |
| Plan reviewer | Plan review and code-to-plan verification | Codex | Findings on the plan and changes |
| QA agent | Real user journey on the staging environment | Codex, with Gemini as a fallback | QA verdict, test plan, screenshots |
| QA auditor | QA quality review | Codex | Audit verdict |
| UX reviewer | UX agreement before implementation and screenshot review after QA | Claude | UX agreement, UX verdict |
| Environment engineer | Worktrees, locks, resources, cleanup | Claude | Environment status report |

That is the top layer. Below it is a second layer: temporary checks inside supporting tools and methods. At one step, the orchestrator works as a migration engineer; at another, as an integrator. The reviewer can activate a security check. QA becomes a browser operator. The UX reviewer temporarily turns into an accessibility auditor.

Temporary checks do not have their own channels in the queue, and they do not close a stage themselves. They provide a specialized perspective where it is needed. So I would not say that “six agents do everything.” More precisely, six permanent roles bring in the checks they need as the work progresses.

The QA agent is deliberately not limited to reading code. It follows the real user journey on the staging environment, records observations, collects screenshots, and attaches evidence.

There is a message queue between the roles. This matters more than it may seem. If everyone shares one common instruction, their independence is decorative: they all see the same reasoning and absorb the same assumptions. With a queue, the QA auditor sees QA's evidence, not a draft of its reasoning. A verifier who has already read the author's explanation is a worse verifier.

```text
                    ┌────────────────┐
        plan ──────►│ Plan reviewer  │ findings
                    └────────────────┘──────┐
                                            ▼
┌────────────────┐    message queue     ┌────────────────┐
│ Orchestrator   │◄────────────────────►│ QA agent       │
│ plan/code/PR   │                      │ staging        │
└───────┬────────┘                      └───────┬────────┘
        │                                       │ QA verdict
        │ screenshots                           ▼
        ▼                               ┌────────────────┐
┌────────────────┐                      │ QA auditor     │
│ UX reviewer    │                      │ QA audit       │
└────────────────┘                      └────────────────┘
```

At the end, a service check closes the run. It requires a positive QA verdict, a positive QA audit, and, for UI tasks, a positive UX verdict. It cannot be persuaded. This is what makes parallel work possible: I do not have to personally inspect every team before it closes. I look at the result and the evidence instead of manually rereading the entire journey.

## §4. How One Run Works

The stages did not appear for the sake of a nice diagram. They serve two purposes. First, a run can recover after a process failure. Second, each stage leaves evidence, not just a verbal “I did it.”

```text
0 preflight → 1 framing (1b reproduce the bug before the fix)
→ 2 plan (2b blind option comparison · 2c UX agreement)
→ 3 plan review (3b change-scope claim · 3c criteria → task)
→ 4 implementation → 5 tests → 5.5 plan alignment
→ 6 PR / CI / merge → 7 deploy to staging
→ 8 QA until approval → 8.5 QA audit → 8.6 UX review
→ 9 confirmation → 10 final check
→ 11 retrospective → 12–13 cleanup
```

What follows is not the complete protocol, but the logic of a single pass.

### 4.1 Preflight

Stage 0 checks the things that are better discovered before work begins: deployment access, external CLI limits, forgotten background processes, and the availability of QA windows. It also creates a dedicated worktree and sets a lock for the run.

The point is simple: it is better to stop before starting than at stage seven, when there is already a PR, a queue, and other people's expectations.

### 4.2 Framing and Splitting

One run takes a coherent piece of work: deployment to the staging environment plus QA approval. If a task has multiple phases, the team breaks it into parts itself. This was a deliberate decision: if I decide where to split every task, I become a manual coordinator again.

The split is written immediately to a durable Markdown file: work parts, decisions made, and the resume protocol. A session's context may run out, background tasks may die, but the file remains. A new session reads it and continues from the last point.

### 4.3 Reproduce the Bug First

For bug fixes, the QA agent first reproduces the bug on the current staging environment. This happens before the code and, where possible, before the fix plan.

This protects against three unpleasant possibilities. The bug may be a phantom. After the fix, the team may accidentally test a similar but different scenario. And the code may look wrong even though the user never reaches that branch at all. The last possibility is exactly what happened with the green but useless fix at the beginning of this article.

### 4.4 Planning and Comparing Options

If a task has several possible approaches, the orchestrator first writes several architecture options. They reach the plan reviewer in a random order, with no hint about the preferred option. Each has roughly the same level of detail. If one sketch is half as detailed as the others, that is already a hint.

After an approach is chosen, the plan goes through review. I capped it at three rounds. After the third, we continue only for a serious or critical finding. In practice, fourth and fifth rounds mostly catch cosmetic issues that are cheaper to catch later.

A separate rule came from a silly incident: before putting helper-function names into a plan, check them in the code. Once, a plan confidently cited four functions. Not one of them existed.

For UI tasks, a UX agreement is created before implementation: interface states, reusable patterns, accessibility requirements, and a mobile-first view. The plan reviewer reviews the plan together with this agreement, rather than an abstract instruction to “make it look good.”

### 4.5 Code, Tests, and an Outside View

Implementation follows the plan. Tests are written from the specification, not from the finished code. Internal modules are not mocked in BDD tests: only external SDKs may be mocked. The local database is real and is reset predictably before each run.

Before the merge, there is a separate comparison: the reviewer checks whether the code matches the plan. This catches quiet drift, where the implementation went in a different direction even though everything builds and the tests pass.

### 4.6 Deployment: A Green Status Proves Very Little

After deployment, the team confirms that the staging environment is actually running the intended build. A green infrastructure status proves very little on its own: it may mean only that some deployment finished.

This rule appeared after two similar cases. One run reported a deployment, but the staging environment had a different commit. Another updated only part of the system: infrastructure was green, but the affected client service was still on the old version. QA rejected it with a simple diagnosis: the change was not there.

That is why the report before QA uses careful language: “deployed for verification,” not “fixed.” The team earns the right to say “verified” only after all checks are complete.

### 4.7 The QA Loop

The orchestrator sends the QA agent a concise brief: the change, acceptance criteria, build version, and affected parts of the code. A finding blocks the run if it is a regression caused by the current PR. Existing problems on the affected screens are recorded separately. Without this boundary, the first round quickly drowns in unrelated old problems.

When QA rejects a run, the team does not immediately rush to change the code. First, it determines what actually happened:

| No. | Hypothesis | What the Team Does |
| --- | --- | --- |
| 0 | Broken environment | Checks the health of the staging environment |
| 1 | Real bug | Fixes it, opens a PR, runs CI, merges, redeploys, and reruns QA |
| 2 | False finding | Responds with a reference to the specification and requests another check |
| 3 | Overly strict test | Fixes the test, then gets confirmation from the QA auditor |

Item zero appeared after a useless investigation in the wrong place. Integration tests passed, the staging environment was silent, and the team dug into business logic. Since then, the environment is always checked first.

There is protection against endless repair loops: if QA rejects the run twice for the same reason, a third attempt using the same class of solution is forbidden. The team has to move up one level. For example, instead of editing the instruction again, it should make the behavior predictable in code. If that still does not help, an architectural change is needed.

For UI work, the orchestrator performs a quick self-check before QA: a service check measures specific numbers and states without opening a browser. Broken layout should be caught in 30 seconds, not consume a full QA round.

### 4.8 The QA Auditor

QA approval is always followed by a QA audit. This is not distrust of a particular agent; it protects against a shared blind spot, because a verifier can check the wrong thing too. An exception for “low-risk work that can skip this step” once let an under-verified piece of work through, so that exception no longer exists.

The QA auditor derives the expected set of checks from the specification, compares it with the actual coverage, reviews the evidence, and looks for a scenario QA may have missed. Sometimes it performs a spot check on the staging environment. The result is simple: approve or return for more work.

Importantly, the auditor does not command the orchestrator directly. It sends a signal. A false critical finding is closed with an evidence-based response. A real gap is fixed and sent back for another audit. The system cannot close “with reservations.”

For UI work, the UX reviewer joins after the QA audit. It compares screenshots with the UX agreement. Critical and serious problems block closure. Medium and minor issues go into notes and the retrospective. A matter of taste comes to me after two rounds.

### 4.9 The Final Check

After QA, the audit, and UX review, one last question remains: can the run be considered closed? The final check answers it. It verifies the presence and contents of the evidence: a positive QA verdict, approval from the QA auditor, and approval from the UX reviewer for UI runs. A nonzero exit code means there is no closure.

The check itself was also subjected to distrust. An audit found two bugs where a rejection was mistakenly treated as approval. In one case, a negative verdict passed because of a matching substring. In the other, a mixed verdict passed because it included the word “success.” The final check gained its own regression tests after that.

For UI tasks, the rule is stricter: a UX verdict is required by default. Unless the run is explicitly marked as work without an interface, the check requires a UX verdict. Forget the flag and the check fails. That is the correct behavior: an earlier UI change shipped without either UX stage precisely because skipping them had been allowed by default.

After the final check, QA publishes its comment, the tech lead closes the task, “not now” items become new tasks, and I receive the outcome: done or blocked. Then comes cleanup: worktrees, locks, background processes, and branches.

## §5. How a Run Continues After a Failure

Autonomy does not fail only on difficult architectural decisions. Sometimes it is simpler: the machine goes to sleep, a process dies, or a notification gets lost. So a separate part of the system is responsible for resuming work after ordinary, everyday failures.

Normally, a run moves forward through events. A review, CI job, deployment, or QA run finishes, a notification arrives, and the orchestrator continues to the next step.

But an event can be lost. A background task can be killed. The machine can sleep. So there is a safety net: every 15 minutes, the system rereads the run state, finds the current stage, checks whether the background step is alive, and either resumes the work or repairs the failure.

I tried a four-minute interval. During a 30-minute QA run, that produced around seven unnecessary returns to the run. Each return pulled the protocol and state back into context. Fifteen minutes turned out to be a reasonable compromise: idle time is bounded, but context is not burned for nothing.

The statuses “killed,” “failed,” and “timeout” have a separate rule: each is an anomaly that cannot be answered with a no-op. The agent must read the output, inspect the signals for that specific step, and decide whether to repair it or escalate it to me. This rule came from a run that stopped on a killed step and waited for me to look in on it.

For this to work, critical state lives outside the model: the run card, current stage, next check time, parts table, verdicts, and task queue. A new session recovers from the files. A guard prevents closure while the queue still contains unfinished tasks.

There is a reverse side too: the timer has to be removed. On “done” and “blocked,” it is deleted; otherwise it would keep returning to a run that is already waiting for my decision. The same rule applies to locks, worktrees, and processes: if you create a resource, clean it up.

## §6. How Several Teams Work in Parallel

The next question is how to run several such teams rather than one. I do not need a system where one enormous run drags the entire queue behind it. I want to hand it a batch of tasks: 12 bugs, 5 UI polish items, and 3 integration-debt items. The queue then distributes them among autonomous engineering teams.

```text
task batch
   │
   ▼
queue ──► team A ──► PR → staging window → QA → result
   │      team B ──► PR → staging window → QA → result
   │      team C ──► PR → staging window → QA → result
   └────► team N ──► PR → staging window → QA → result
```

Of course, “unlimited numbers” do not repeal physics. There are CI, the staging environment, model limits, QA windows, storage systems, and queues. But the important shift is elsewhere: infrastructure becomes the bottleneck instead of my attention. Add a worktree, isolated storage, a queue, and a QA window, and you get another autonomous team.

Parallelism immediately creates a new problem: teams can interfere with one another. With one team, there is almost no need for coordination. With several, you need to know in advance which parts of the project each one will touch.

Each run holds a lock for its task and, after planning, records its change scope: the directories and product domains it will touch. A check looks for overlap with other active teams. Overlap does not always block the work, but it cannot be ignored. The team must read the other claim and choose whether to change its plan, wait for the merge, or consciously accept the risk.

The staging environment also became a window instead of a rental for the entire run. The first version held it for 4–8 hours even though it was needed for only part of that time. Now the team takes the environment before deployment, holds it through QA and the auditor's spot check, and then releases it. If a fix is required, the window is released during development. While one team writes code, another can run QA.

The environments are isolated without elaborate infrastructure. Each worktree receives its own storage, queue index, and port. Parallel BDD runs stopped overwriting one another. A separate status screen shows queues, locks, declared change scopes, and when each team last updated its state.

So scaling turned out not to be model magic but ordinary engineering work: preventing teams from overwriting one another's queues, preserving claims when locks are reacquired, and recording session state separately. This layer now has its own test suite: 44 checks pass.

## §7. How the Process Learns from Mistakes

Every run ends with a stage that improves the process itself. This is an important part of the system: without it, all that remains is a folder of instructions that gradually go stale.

The retrospective collects review logs, QA verdicts, the audit, friction notes, the orchestrator's memories, and my corrections. The file has a required “honest mistakes” section: places where the agent was wrong even though rules already existed.

Obvious fixes go into the process immediately. If a run reveals an outdated identifier, a missing instruction, or a proven safeguard, it is corrected in the same pass. The agent has limited permission to make such automatic commits: only team protocols, the process, and personal configuration. Product code always goes through the full cycle.

But self-learning cannot be left without controls either. It quickly developed two failure modes.

The first was bloat. For five weeks, every lesson became a new paragraph in the protocol. The core instruction grew from 790 to 1,732 lines and began consuming too much context every time the system re-entered a run, even when nothing had happened.

The remedy was mundane. A lesson is recorded as a short, 2–4-line rule with an incident label. It goes into the handbook for the stage where it is needed. The core changes only when a foundational system rule changes. Before anything is added, the system searches for a similar rule: extend the existing one instead of creating twins. Size limits are checked automatically: up to 300 lines for the core and 400 for a handbook. If a file exceeds its limit, that becomes a retrospective finding in its own right.

The second failure mode was self-blindness. An agent that completed a run tends to turn a one-off case into an eternal law. So not every finding becomes a rule immediately. Unless it needs an immediate fix, it waits for a second occurrence. After the second, it becomes a rule.

New and generalized rules go through external review: is this a recurring problem or a one-off, is the rule written too broadly, does it conflict with an existing rule, and is the new QA check worth its cost on every run? If the evidence is insufficient, the rule does not become active yet.

Rules can die. If a new check increases the number of QA rounds, creates false rejections, or conflicts with another finding, the rule is sent for review. If it is removed, the protocol keeps a short record of why, so the next run does not reopen the same debate from scratch.

Escaped bugs are tracked separately: those discovered after QA approval and the auditor's approval. Each one gets a short analysis built around one question: what check would have caught this class of bug? That check is added to the QA protocol. The bug fix and the process fix remain separate files.

```text
run ──► retrospective ──► obvious fix?
                             │ yes              │ no, but recurring
                             ▼                  ▼
                      external review     wait for second case
                        │ accept               │ second case
                        ▼                      ▼
                 rule in handbook ◄────── promotion
                        │
                        ▼
             log + rule value check ──► remove rule
```

## §8. What Actually Limits Parallel Work

Several engineering teams consume context and compute. So I try to spend those resources where they create quality, not where an agent is simply waiting.

Most of the context remains with the orchestrator. Heavy checks are moved outside: QA runs, audits, and reviews. By the time of final confirmation, the orchestrator does not manually recheck everything. It reads the auditor's verdict and confirms that the evidence is present. Otherwise the audit becomes theater: a separate role may exist, but no one truly uses its result.

The fallback path is defined in advance too. If Codex capacity is unavailable, the team can switch to Gemini, but with caveats. It handles narrow, single-step tasks well enough. On complex repository changes, it often loses track or hits the time limit. This is documented as a limitation, not hidden behind the phrase “there is a fallback.”

The protocol saves context too. That is why there are file-size limits, a state check every 15 minutes instead of every four minutes, and a rule to read only the handbook for the current stage. When re-entering a run, the system does not need to reload the entire process description every time.

Speed appears where stages can run in parallel without losing checks. Code review runs alongside CI, but the merge waits for both results. The concise QA brief is prepared while deployment is being polled. While one team goes through CI, deployment, and QA, another is already working on the next piece up to the PR.

There are two things I do not shorten: real CI and the QA → QA audit chain. First comes the check, then the check of that check.

My attention is still the most expensive resource. So notifications are reduced to end-state signals: “done” with a report or “blocked” with the specific decision required. A separate notification arrives for the retrospective. Routine events stay quiet: a flaky CI run that was restarted, a review finding that was resolved, an intermediate stage.

If ten teams ask three questions each, autonomy is over. So before every question, a team first has to determine whether it can decide for itself.

## §9. What You Can Take from This

If I were building a similar system from scratch, I would not start with model selection or a long instruction. I would start with the boundaries of trust: where evidence is required, who checks the checker, and what happens when a run fails.

- **Evidence instead of a confident tone.** Every verdict must be written to a file with a clear schema. “I checked it” does not count without a file.
- **A final check.** A service check closes the run by inspecting the required evidence. It needs tests of its own.
- **Dangerous omissions fail closed.** UX review is required for UI tasks unless the run is explicitly marked as work without an interface.
- **The author and reviewer are separate.** Preferably on another model, or at least in another context.
- **A QA audit.** A second verifier evaluates the quality of the verification: coverage, evidence, and missed classes of scenarios.
- **A reviewer signals rather than commands.** The team must be able to reject a false finding with evidence. A real one must be fixed and submitted for review again.
- **Reproduce the bug first.** For a bug fix, reproduce it on the live staging environment before fixing it.
- **Blind option comparison.** Several architecture options in a random order help prevent attachment to the first idea.
- **Round limits.** Reviews, QA, and audits have maximums. After a repeated failure of the same class, change the approach instead of going in circles.
- **Periodic state checks.** The run normally moves through events, and a scheduler protects against lost events. Choose an interval that does not re-enter the run too often without a reason.
- **State outside the context.** The stage, work parts, verdicts, and queue must be recoverable from files, not from the model's memory.
- **A lesson as a short rule.** Not half a page of history, but 2–4 lines with an incident label and a protocol size limit.
- **A rule is not born from one case.** Sometimes it needs a second similar incident or external review.
- **Track escaped bugs separately.** A bug that passed every check must lead to a new QA check.
- **A staging window instead of renting the environment.** Hold a shared resource only for deployment and verification.
- **Careful language.** Before QA, the team says “deployed for verification.” “It works” appears only after the verdicts.

## §10. Where the Boundaries Are

This system has boundaries, and they matter. I do not see it as a universal replacement for an engineering team or for the product owner's own decisions.

The production release is automated, but it lives in a separate pipeline. The engineering team's work ends at “verified on staging and queued for release.” I then start the release autopilot separately: it has its own protocol, its own checks, and the right to stop. The boundary matters: the team does not deploy to production by itself. It prepares a verified candidate, and the release pipeline brings it to the production environment after a separate decision.

Taste is not automated either. The UX reviewer catches inaccessible controls, missing states, broken mobile layouts, and a custom-built pattern where the system's standard should have been used. But if the debate reaches “I just don't like it,” it comes to me after two rounds.

I treat the numbers carefully. Ninety-three retrospectives are enough to identify recurring errors and improve the process. But the latest metrics snapshot covers only 15 runs across six calendar days, so it cannot support loud claims such as “the system became twice as good.” I use the numbers more modestly: to see whether repeat QA rounds are increasing, whether there are more stops, and whether new rules have started getting in the way.

Bugs still slip through. Two bugs passed every check. Both were visual: the functional checks did not cover them. That led to a visual test pass and a bug-class coverage matrix. I do not claim that the system guarantees zero misses. It promises something else: every miss should produce a barrier for the entire class of similar errors.

The Gemini fallback is weaker than the primary path. It helps with narrow tasks when limits are reached, but it is worse at handling complex repository changes. It is better to document that in the protocol than pretend all models are equivalent.

The system is personal. The roles, rules for escalating to me, tracker rules, comment discipline, and round limits are all tuned to a particular person and product. You can adopt the general approach, but you will have to grow the checks and thresholds out of your own incidents.

And the most unpleasant source of errors is the orchestrator itself. Most retrospectives are about how it made a lazy decision within otherwise correct rules: it trusted a summary, failed to reread a file, or cut a check short. The final check compensates for this in part, but it does not cure it. The process makes the errors visible. That is already a lot.

## Conclusion

When I talk about this system, I often hear: “So the agent writes code instead of you?” No. That is far too narrow.

Code is only the middle of the chain. The full unit of work looks like this: framing, planning, review, implementation, tests, PR, CI, staging, QA, QA audit, fixes, closure, retrospective. The gain does not come from the model typing faster. It comes from parallelism, independent roles, a final check, and the absence of manual management at every step.

I like that the eventual solution turned out to be an old engineering toolkit: separation of duties, witnesses, evidence, locks, loop limits, recovery after failure, shared-resource management, and retrospectives. Large models might find that slightly insulting: a smarter model does not remove the need for a process.

The engineering-team system does not turn agents into people or make them infallible engineers. But it makes their confidence verifiable. That turned out to be enough for me to hand the system batches of tasks and review the evidence rather than the tone of its response.

In the end, this is not a story about “AI writing code for me.” It is a story about the engineering system around AI: a compact protocol, stage-specific handbooks, service checks with their own tests, a run log, coordination across several teams, and 93 retrospectives. The incidents are real. Each one left behind a rule.
