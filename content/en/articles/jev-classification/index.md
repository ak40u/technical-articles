---
title: "The Perfect Task for Jev: A Classification Model Lost to General-Purpose LLMs"
date: 2026-09-28
description: "I tested Jev, TypeSafe's decision model, on lead classification in my Derzhi Lida bot. On the very task Jev is built for, cheap general-purpose models were more accurate and no more expensive."
author: "Pavel Volkov"
image: "og/jev-classification-hero-en.png"
translationKey: "jev-classification"
---

I have a task that reads like a sales example for Jev.

My bot, Derzhi Lida (Russian for "grab the lead"), reads working chats in Telegram and looks for jobs for paid-ads and social media specialists. Regular expressions drop the obvious noise, and a model decides the rest. About 1,600 decisions a day. The answer is always one of three: a client request, a job opening, or irrelevant. Plus a list of ad platforms. Nothing to write, only something to choose.

That is exactly what Jev is sold for. I ran it on our tests next to three general-purpose models. It came last.

## What Jev is

Jev is a model from TypeSafe. It launched on OpenRouter on September 18, 2026 as `typesafe/jev-1.13`. TypeSafe calls this class of models System One. Their job is to make decisions. They do not write text.

Instead of a prompt and a reply, the model receives a state (any text or JSON) and a set of typed questions. There are three kinds:

- **choice** — pick one option from a list and return a probability for each;
- **noul** — answer yes or no and return the probability of yes;
- **score** — place the input on a scale you define.

No reasoning and no explanations, only values and probabilities. TypeSafe promises the probabilities are calibrated: 0.8 should mean being right about 80% of the time. The price is $0.042 per million input tokens, and output is free. The context window is 32 thousand tokens.

Jev runs on a separate Decisions API. The regular `/chat/completions` endpoint and the OpenAI client do not work with it, so you need your own request.

## Turning the task into questions

The bot has a system prompt several pages long. It holds rules that piled up from real mistakes: "looking for" means nothing on its own, what follows it decides; an agency that is hiring is relevant, an agency selling its services is not; a video editor is relevant only if the job includes publishing to social media; anything that looks like casino chat operators gets dropped.

For Jev I split this into nine questions:

```json
{
  "model": "typesafe/jev-1.13",
  "state": {"message": "Looking for a Yandex Direct specialist for an interior design studio, 40k+"},
  "questions": {
    "verdict": {
      "type": "choice",
      "instructions": "<every rule from the production prompt>",
      "criteria": {"lead": "...", "hiring": "...", "irrelevant": "..."}
    },
    "platform::Yandex Direct": {"type": "noul", "instructions": "...", "criteria": {"true": "...", "false": "..."}},
    "platform::VK": {"type": "noul", "...": "..."}
  }
}
```

One `choice` question decides what the message is. Eight `noul` questions decide which platforms are mentioned. I left the bot's analyzer alone and swapped only the model call; the spam filter and the regular expressions ran exactly as in production. The test set is 47 real messages: client requests, job openings, irrelevant posts, spam.

## First run: 40 out of 47

Five of the seven failures were Yandex Direct specialist openings. The prompt has a rule: if someone is looking for a Yandex Direct specialist, the platform is Yandex Direct even when it is not named. In the platform question I wrote the criterion "the platform is named explicitly in the text."

The two instructions contradicted each other. General-purpose models with the same prompt pass these tests: they pick the more specific rule. Jev took the criterion literally. Its probability for Yandex Direct on those openings ranged from 0.11 to 0.45.

The mistake was mine, not the model's. But it is telling. With Jev you no longer write a prompt, you design a questionnaire, and every criterion behaves like code. One imprecise line cost five tests.

After fixing the criterion: 45 out of 47, twice in a row.

## Results

All four models ran on the same day, on the same set, from identical containers on the bot's server. The runs were parallel, so the times compare only within this table.

| Model | Kind | Result | Suite time |
|---|---|---:|---:|
| DeepSeek V4.1 Flash | general-purpose | **47/47**, twice | 70–85 s |
| GLM 5.3 Flash | general-purpose | 46/47, twice | 157–244 s |
| Xiaomi MiMo v2.5 | general-purpose | 46/47 | 355 s |
| Jev 1.13 | decision model | 45/47, twice | 19–20 s |

Almost every model misses one case: a long post about "business transformation" that is really a job opening. The second miss was Jev's alone. The message "a clinic needs someone to shoot and edit videos for ads" is irrelevant under our rules: that is a videographer, not an ads specialist. The general-purpose models applied that rule. Jev did not.

The gap is one or two tests out of 47. Not a rout. But the model built for classification did not beat a single cheap general-purpose model at classification.

## Why it is not cheaper

The biggest surprise was the bill.

One Jev request averaged 7,700 input tokens. For the chat models, the whole prompt plus the message takes 3,200–3,600. I took it apart. The rules alone, 8,355 characters, cost 5,300 tokens in Jev: it has its own tokenizer, and Russian text comes out almost twice as expensive. The eight platform questions added about 1,900 more.

Free output does not help, because a chat model's answer here is only about a hundred tokens anyway.

| | Jev 1.13 | DeepSeek V4.1 Flash |
|---|---:|---:|
| Input, $ per million tokens | 0.042 | 0.035 |
| Output, $ per million tokens | 0 | 0.29 |
| Input tokens per decision | ~7,700 | ~3,500 |
| Cost per decision at list price | ~$0.00032 | ~$0.00015 |
| Median response time | 0.3 s | 1.5 s |
| Providers on OpenRouter | 1 | 27 |

Even without the platform questions, a Jev decision costs $0.00024. Still more. Price per million tokens is not price per decision.

Jev's speed really is impressive: 0.3 seconds against 1.5. But the bot works through a queue, and a second and a half costs nothing there. A speed win with nothing to spend it on.

## How Jev behaves beyond the tests

Apart from the bot, I put Jev through a separate series of checks on numeric data: 14 experiments, more than ten thousand requests. Here is what is worth knowing before you put it to work.

**It reads ready-made fields flawlessly.** When the answer sits in the state explicitly, such as "the value is above the threshold" or "the event is scheduled for today," Jev is right almost every time. A hint field lifted accuracy from 49% to 93%.

**It cannot calculate.** When the answer has to be derived from a series of numbers, the model fails. It got the sign of the change over a 20-value series right in 25% of cases. That is worse than a coin flip: it systematically flips the sign. Everything Jev needs to consider has to be passed in as ready-made features.

**Answers are not deterministic.** I sent 200 byte-identical requests twice. On the same model version, the decision at the 0.5 threshold changed in 13% of cases. In Derzhi Lida the two runs matched, but there are almost no borderline messages there.

**Wording changes the answer.** Answers to rephrased versions of the same question correlate with each other at only 0.50–0.57.

**The confidence field adds nothing.** It mirrors how far the probability is from 0.5, with a correlation of 0.999.

**Calibration is worse than a general-purpose model's.** On a thousand identical three-option questions I compared Jev with DeepSeek V4.1 Flash. The Brier score (lower means better calibrated) was 0.765 for Jev against 0.649. Calibration is Jev's headline promise, and that is exactly where it lost.

## Where Jev fits

Jev is strong when the answer follows directly from a fact you pass in. The type of a support ticket, the language of a message, whether the text contains a phone number, whether a required field is filled. Short question, unambiguous criteria, lots of decisions. There it is fast, typed, and cheap.

Lead classification looks the same but works differently. The decision is the application of a long rulebook with exceptions, and the message often has to be read twice: who is writing, whom they are looking for, what they are selling. A general-purpose model with a short reasoning pass handles that better. And since the rulebook is long, Jev also costs more.

Jev is specialized in the form of the answer, not in the substance of the task. A typed answer with probabilities is a convenient interface, not a guarantee of accuracy in your domain.

## What runs in production now

Derzhi Lida now runs on DeepSeek V4.1 Flash, with GLM 5.3 Flash as the fallback. After the switch I replayed 1,600 real messages from the day before through both the old and the new model. The old one approved 134, the new one 133, and the verdicts matched in 98.8% of cases. Median response time dropped from 24 seconds to a second and a half.

Jev did not go to production. My one takeaway: before you pick a model "built for the task," test it on your own data next to a cheap general-purpose one. The name of a model class says nothing about how it will handle your rules.
