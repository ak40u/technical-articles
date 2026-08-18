---
title: "Choosing a Fallback LLM for Plan Review: Benchmarking 12 Models and Adopting Tencent Hunyuan 3"
date: 2026-08-18
description: "How we benchmarked 12 models to replace OpenAI Codex for plan reviews in Findrates, why Tencent Hunyuan 3 won, and how we engineered process safety in macOS."
author: "Pavel Volkov"
image: "og/sdd-in-production-hero-en.png"
---

In autonomous agent development (Agentic SDD), one of the most critical stages is **reviewing implementation plans and specs before writing any code**. If a logical defect slips past the planning stage, the implementing agent wastes dozens of minutes and API dollars implementing a broken architecture, while QA agents inherit false-positive test assertions.

Our primary engine for deep plan review is the **OpenAI Codex CLI** running at maximum reasoning effort (`reasoning_effort="xhigh"`). However, in fully autonomous overnight batches, we periodically hit token quotas and provider rate limits. Furthermore, single-vendor dependency represented a single point of failure.

Following the end of our Antigravity-Gemini subscription on July 14, 2026, we benchmarked **12 LLMs** on a real-world task to select an uncompromising fallback reviewer. The winner was **Tencent Hunyuan 3 (`tencent/hy3`)**.

Below is an analysis of Hunyuan 3's architecture, the benchmark methodology, comparative metrics against Codex and Claude Opus, and the implementation of our `codex-exec-safe.sh` execution harness.

![Fallback Architecture](fallback-architecture.svg)

---

## 1. The Reviewer Challenge: Why Reviewing Is Harder Than Coding

A plan reviewer performs the opposite task of code generation. Its goal is not to fill in implementation details, but to serve as an **adversarial auditor**:
1. Cross-examine plan assertions against the actual state of the repository (via read-only filesystem access).
2. Spot type mismatches, implicit environment assumptions, and hallucinated API endpoints.
3. Stress-test boundary conditions and verify that proposed tests fail on legacy code and pass on the target build.

Most lightweight models ("flash" and "mini" tiers) fail in this role: they default to agreeable consensus ("LGTM", suggesting minor stylistic polishes) without verifying the repository state.

---

## 2. Under the Hood of Tencent Hunyuan 3

Tencent has developed its Hunyuan family of LLMs since 2023, transitioning from dense architectures to a sparse Mixture-of-Experts (MoE) design in Hunyuan-Large and Hunyuan 3:

* **Shared + Specialized Experts Architecture:** Total parameter count is approximately 389B, with ~52B active parameters per token. In contrast to standard MoEs, Hunyuan assigns **1 continuously active Shared Expert** (retaining syntax and general language invariants) alongside **16 specialized experts** for narrow code and logic domains.
* **Expert-Specific Learning Rate (ES-LR):** To prevent routing collapse where a few experts dominate, learning rates scale dynamically per expert, maintaining uniform domain depth across all 16 experts.
* **Compiler-Verified Pretraining Synthetics:** Synthetic reasoning trajectories were validated using real compilers, typecheckers, and formal theorem provers, training the model to trace code like an AST interpreter.
* **KV-Cache Optimization (256k Context):** Multi-Head Latent Attention (MLA) combined with RoPE interpolation reduces KV-cache memory pressure by 60–75%, enabling full repository exploration without context degradation (100% Needle-in-a-Haystack).
* **Autonomous Backtracking (Long-CoT):** In high-reasoning mode, the model constructs explicit hypothesis trees and backtracks upon discovering boundary contradictions.

### Official Manufacturer Benchmarks (Tencent AI Lab)

In published evaluation reports, Hunyuan 3 demonstrates top-tier performance across mathematics, formal logic, and software engineering:

| Benchmark | Discipline | Hunyuan 3 Score | Context |
| :--- | :--- | :---: | :--- |
| **MATH-500** | Advanced Mathematical Reasoning | **86.4%** | On par with specialized reasoning models |
| **GSM8K** | Multi-step Arithmetic | **95.8%** | Near-ceiling accuracy |
| **HumanEval** | Python Code Generation & Analysis | **89.6%** | Outperforms standard open MoE baselines |
| **LiveCodeBench** | Contemporary Competitive Programming | **51.2%** | Resistant to dataset contamination |
| **SWE-bench Verified** | Repository-level Defect Resolution | **38.8%** | Zero-shot agentic setting |

In production, these strengths translate into methodical step-by-step verification: the model inspects dependency files, audits call signatures, and flags subtle contradictions.

---

## 3. The Testbed: Unimplemented Plan `tg-webhook-timeout`

Our first testbed wasn't honest, and it took a while to notice. We took three real **Findrates** backlog plans that had already shipped and merged, and ran the reviewers against current `HEAD`. Models racked up points for findings like "this phase is a no-op, it's already done" — a class of finding that never occurs in the live pipeline, because plan review always runs **before** implementation. Ranking on that testbed was misleading: Grok 4.5 scored 10 findings, GLM-5.2 scored 8 in 71 seconds, and both looked stronger than they turned out to be.

We rebuilt the decisive testbed around `tg-webhook-timeout` (the Telegram webhook intake budget and timeout plan — inbound message lock leasing, `message-id` dedup, and a "no silent 200 ACKs" invariant for both the voice and text paths), on a worktree pinned to commit `0bcafc42^` — the code state **before** this plan was implemented. All twelve models got the same prompt, the same checkout, and the same read-only access, including a symlink to `node_modules` so both sides could see inside `grammY` identically.

Manually verifying findings against the code surfaced three defect classes that different models caught:

1. **Missing caller abort signal:**
   The `parse_new` branch (`parse-quote-request.ts:166`) has no timeout on the calling side — the code itself carries a comment: "callWithFallback has no caller signal." The plan raises the wait bound to 50 seconds, but that turns the current redelivery into a silent 200 ACK — a direct violation of the plan's own "must-not 7." Claude Opus and Hunyuan 3 flagged this independently.
2. **Contract-test blind spot:**
   `telegram-webhook-contract.test.ts:46` imports the mutable route handler directly, so it falls outside the blast radius the plan declares — meaning the very test meant to catch a regression physically cannot catch it. Of twelve models, only Hunyuan 3 found this.
3. **Dedup running after the rate-limit check:**
   Message-id dedup runs **after** the rate-limit check, so a duplicate that arrives once the caller is already rate-limited still slips a second visible message to the client. Codex found this; Hunyuan 3 confirmed it independently.

A separate artifact of the testbed itself surfaced along the way: `opencode`'s `glob`/`grep` respect `.gitignore`, so `node_modules/` and `.claude/` are invisible to search even though a direct read at the full path works fine. Because of this, one model refused to verify `grammY` calls ("cannot check — search finds nothing"), and another declared a file "nonexistent" that actually exists in the main repository, just not in the isolated test worktree. We added a one-line fix for this blind spot to the review prompt.

![Model Benchmark Comparison](benchmark-matrix.svg)

---

## 4. Benchmark Results Across 12 Models

Each model received identical instructions, read-only repository permissions, and an isolated execution environment on the `0bcafc42^` worktree. Metrics:
* Findings per run and variance across repeat runs.
* Share of findings confirmed by manual code verification, and false positives.
* Runtime and cost by OpenRouter pricing, where the engine wasn't subscription-based.

### Comparative Evaluation Matrix

| Model | Findings (runs) | Variance | Runtime | Cost (Input / Output per 1M) | Role in Pipeline |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Tencent Hunyuan 3 (`hy3`)** | **9, 9, 9, 9** | **zero (4/4)** | 12–18 min | **$0.13 / $0.53** | **Chosen fallback for every review stage** |
| **OpenAI Codex (`xhigh`)** | 8 | 1 honest run | ~4.5 min | Codex Pro Tier | Primary workhorse engine |
| **Claude Opus** (Claude Code CLI) | 7, 7 | zero (2/2) | 11–14 min | subscription | Second-deepest, 3x slower than hy3 |
| **DeepSeek V4 Pro** | 7, 7, 7 | zero (3/3) | 4–9 min | $0.44 / $0.87 | Stable paid alternative |
| Kimi K3 | 6, 3 | 2x swing | 8–9 min | $3.00 / $15.00 | Too inconsistent to trust as a gate |
| GPT-5.6 Luna | 5 | 1 run | ~5 min | $0.10 / $0.60 | Cheap, but shallow |
| DeepSeek V4 Flash | 3, 3, 3, 4 | consistently weak | 12–30 min | $0.09 / $0.18 | Hits a model ceiling, not a harness issue |
| Grok 4.5 | 3 | 1 run | ~5.5 min | $2.00 / $6.00 | Didn't earn its price on the honest run |
| Xiaomi MiMo v2.5 | 3 | run timed out mid-pass | > 4 min | $0.14 / $0.28 | Fell short |
| GLM-5.2 | 2 | 1 run | ~4.5 min | not disclosed | Fast, but shallow on the honest run |
| Gemini 3.5 Flash | 2 | 1 run | ~3 min | $1.50 / $9.00 | Below the bar |
| Gemini 3.6 Flash | 2 | 1 run | ~3 min | $1.50 / $7.50 | Below the bar |

A thirteenth candidate, `qwen/qwen3.8-max`, doesn't appear in the table: every current Qwen release on our OpenRouter account hit the account's guardrail privacy policy ("No endpoints available matching your guardrail restrictions") and returned nothing at all — that's missing data, not a low score.

Arguably the single most important result of this testbed: **ranking on already-implemented versions of the same plans does not predict ranking on unimplemented ones.** Grok 4.5 scored 10 findings on the implemented plan and 3 on the honest one. Gemini Flash scored 7 and 2 respectively. Had we decided from the first, dishonest testbed, Grok would have shipped into the pipeline.

---

## 5. Why Hunyuan 3 Outperformed Flagship Models

1. **The one finding nobody else made:**
   Of twelve participants, only Hunyuan 3 noticed that the contract test `telegram-webhook-contract.test.ts:46` imports the mutable route handler directly and therefore falls outside the plan's declared blast radius — meaning the safety-net test physically can't catch the regression it was written to catch. Neither Codex, nor Opus, nor any of the paid contenders saw it.
2. **Reproducibility where everyone else drifted:**
   Four independent runs, four times exactly 9 findings. DeepSeek V4 Pro matched that zero variance, but at seven findings; Opus matched it too, but at seven findings and three times slower. Every other contender's runs swung by 2x or more.
3. **262k Token Context Window:**
   Large enough to load the entire plan, acceptance criteria, and related source modules and tests simultaneously.
4. **Economics:**
   At **$0.13 per 1M input tokens** and **$0.53 per 1M output tokens**, one exhaustive 12–18-minute reasoning pass costs a few cents — an order of magnitude cheaper than paid alternatives like DeepSeek V4 Pro or Kimi K3, and without eating into the subscription quota Codex and Opus share.
5. **The Latency Trade-off:**
   12–18 minutes is too slow for interactive code completion in an IDE, but **ideal for background autonomous pipelines**, where catching a flaw during planning saves hours of agentic rework and human debugging.

---

## 6. Engineering Harness: `codex-exec-safe.sh`

To integrate `hy3` as a seamless drop-in fallback for OpenCode/Codex, we built `~/.claude/bin/codex-exec-safe.sh`.

It resolves three infrastructure constraints:

### 1. Preventing PTY File Descriptor Leaks on macOS
Spawning LLM subagents from background orchestrators risks leaving orphaned `app-server` and MCP child processes. Each orphan holds open pseudo-terminal file descriptors (`/dev/ptmx`), eventually exhausting macOS's `kern.tty.ptmx_max=511` system limit.

The wrapper enforces deterministic tree termination (`kill_tree`) via an EXIT trap:

```bash
kill_tree() {
  local target="$1"
  [ -n "$target" ] || return 0
  local child
  for child in $(pgrep -P "$target" 2>/dev/null); do
    kill_tree "$child"
  done
  kill -TERM "$target" 2>/dev/null
}
```

### 2. Read-Only Perimeter for the Reviewer
An agent with write access often attempts to "fix" the repository rather than critiquing the plan. For `opencode`, a throwaway configuration is generated on each invocation with MCP disabled and strict tool restrictions:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openrouter/tencent/hy3",
  "permission": {
    "read": "allow", "grep": "allow", "glob": "allow", "list": "allow",
    "external_directory": "allow",
    "edit": "deny", "bash": "deny", "webfetch": "deny", "websearch": "deny"
  },
  "provider": {
    "openrouter": {
      "models": {
        "tencent/hy3": {
          "options": {
            "reasoning": { "effort": "high" }
          }
        }
      }
    }
  }
}
```

### 3. Single-Variable Engine Switching
Switching to Hunyuan 3 requires setting one environment variable:

```bash
CODEX_ENGINE=opencode codex-exec-safe.sh "<prompt>"
```

Unsetting it restores default execution through the primary engine — the Codex CLI at `reasoning_effort="xhigh"`.

---

## Key Takeaways

1. **Decouple generation from verification:** The model drafting code must never be the sole authority verifying its own assumptions.
2. **Never compromise on verification latency:** A 15-minute verification delay during planning pays for itself by eliminating downstream production regressions.
3. **Specialized reasoning models outperform general frontier models in niche tasks:** At $0.13/$0.53, Tencent Hunyuan 3 found more confirmed defects with less variance than Kimi K3 at $3/$15 per 1M, and out-found even the subscription-tier Codex and Opus — through relentless, unhurried reasoning.
