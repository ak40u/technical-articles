---
title: "Choosing a Fallback LLM for Plan Review: Benchmarking 12 Models and Adopting Tencent Hunyuan 3"
date: 2026-08-18
description: "How we benchmarked 12 models to replace OpenAI Codex for plan reviews in Findrates, why Tencent Hunyuan 3 won, and how we engineered process safety in macOS."
author: "Pavel Volkov"
image: "og/sdd-in-production-hero-en.png"
---

In autonomous agent development (Agentic SDD), one of the most critical stages is **reviewing implementation plans and specs before writing any code**. If a logical defect slips past the planning stage, the implementing agent wastes dozens of minutes and API dollars implementing a broken architecture, while QA agents inherit false-positive test assertions.

Our primary engine for deep plan review is **OpenAI Codex powered by flagship GPT-5.6-sol** running at maximum reasoning effort (`reasoning_effort="xhigh"`). However, in fully autonomous overnight batches, we periodically hit token quotas and provider rate limits. Furthermore, single-vendor dependency represented a single point of failure.

Following the end of our Antigravity-Gemini subscription on July 14, 2026, we benchmarked **12 LLMs** on a real-world task to select an uncompromising fallback reviewer. The winner was **Tencent Hunyuan 3 (`tencent/hy3`)**.

Below is an analysis of Hunyuan 3's architecture, the benchmark methodology, comparative metrics against GPT-5.6-sol, and the implementation of our `codex-exec-safe.sh` execution harness.

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

## 3. The Testbed: Unimplemented Plan `86cb2ckwe`

We evaluated candidates on an authentic task from the **Findrates** backlog: `plans/86cb2ckwe-parser-option-loss/` (remedying commercial offer option loss in inbound email parsing).

The plan contained **9 documented defect vectors** across database contracts, input validation, and boundary conditions. Three specific traps proved decisive:

1. **Non-discriminating anchor test:**
   In Phase 2, the test-anchor instructed an SDK fake to "return one option per `Option N` block in received text". However, in the test fixture, `Option 3` began at character position 1909, while `truncateInput` in production code truncated input at exactly 2000 characters. The `Option 3` header was present in the prompt on *both* legacy and target builds, causing the test to pass unconditionally without proving the fix.
2. **Hidden payload truncation:**
   The parser received the `Option 3` header, but the tariff schedule payload was truncated, creating empty database rate records without raising errors.
3. **Idempotency contract breakage on resend:**
   The plan proposed updating rate records using an incomplete composite key, overwriting valid previously saved options.

The remaining 6 defects covered unhandled SDK exceptions, schema type mismatches, and missing transaction rollback cleanups.

![Model Benchmark Comparison](benchmark-matrix.svg)

---

## 4. Benchmark Results Across 12 Models

Each model received identical instructions, read-only repository permissions, and an isolated execution environment. Metrics:
* Verified defect detection count (Ground Truth: 9 confirmed flaws).
* False positive rate.
* Consistency across 4 independent evaluation runs.
* Runtime duration and token cost.

### Comparative Evaluation Matrix

| Model | Flaws Detected (of 9) | Consistency (4 runs) | Runtime | Cost (Input / Output per 1M) | Role in Pipeline |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Tencent Hunyuan 3 (`hy3`)** | **9 / 9** | **100% (9 on all 4)** | 12–18 min | **$0.13 / $0.53** | **Primary Plan Review Fallback** |
| **OpenAI Codex (GPT-5.6-sol, `xhigh`)** | 8 / 9 | 100% | 4–7 min | Codex Pro Tier | Primary Workhorse Engine |
| **DeepSeek V4 (Reasoning)** | 6 / 9 | 75% | 2–4 min | $0.14 / $0.28 | Fast Pre-filter |
| **Anthropic Claude Sonnet 4.6** | 7 / 9 | 75% | 1–2 min | $3.00 / $15.00 | Cost-prohibitive for high-volume fallback |
| **Google Gemini 2.5 Pro** | 6 / 9 | 50% | 1–3 min | $1.25 / $5.00 | Legacy Fallback (pre-July) |
| **Qwen 2.5 Coder / Qwen 3 (235B)** | 5 / 9 | 50% | 2–3 min | $0.20 / $0.60 | Missed character offset boundaries |
| **Mistral Large / Codestral** | 5 / 9 | 50% | 1–2 min | $2.00 / $6.00 | Biased toward approving proposed plans |
| *Remaining Evaluated Candidates* | ≤ 4 / 9 | < 50% | — | — | Failed strictness bar |

---

## 5. Why Hunyuan 3 Outperformed Flagship Models

1. **Character-offset and boundary rigor:**
   Hunyuan 3 was the only model that computed the exact length of the fixture text, compared it with the `truncateInput(2000)` constant in `parse-ai-json.ts`, and reported: *"Option 3 header begins at character 1909; it survives truncation, creating an illusion of data presence while the payload is lost."* Even GPT-5.6-sol initially treated this as expected truncation behavior.
2. **262k Token Context Window:**
   Large enough to load the entire plan, acceptance criteria, related source modules, and historical test fixtures simultaneously.
3. **Economics:**
   At **$0.13 per 1M input tokens** and **$0.53 per 1M output tokens**, a 15-minute exhaustive reasoning pass costs less than $0.02.
4. **The Latency Trade-off:**
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

Unsetting it restores default execution through `Codex (GPT-5.6-sol)`.

---

## Key Takeaways

1. **Decouple generation from verification:** The model drafting code must never be the sole authority verifying its own assumptions.
2. **Never compromise on verification latency:** A 15-minute verification delay during planning pays for itself by eliminating downstream production regressions.
3. **Specialized reasoning models outperform general frontier models in niche tasks:** At $0.13/$0.53, Tencent Hunyuan 3 achieved superior defect detection over $15/1M models through relentless methodical reasoning.
