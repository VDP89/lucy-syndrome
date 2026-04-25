---
id: scar_example_002
name: verify_before_claiming
severity: critical
created: 2026-04-25
status: example
---

# scar_example_002 — Factual claims without verifiable sources

> **Example scar.** This file is a domain-independent template derived from the production case.
> Adapt the trigger, fix, and metrics to your own environment.
> The originating incidents are documented in `examples/production-case/scars/scar_008_no_fabricar_contenido.md`
> and `examples/production-case/scars/scar_009_verificar_dia_semana.md`.

---

## What happened (origin)

Two related failures, both rooted in the same mechanism:

**Fabricated content.** During a daily news curation task, when no real Reddit thread was found on a target topic, the model combined an academic paper (real URL) with the format and framing of a Reddit post (not real) and presented the composite item as a community discussion. The operator requested the link. There was no link. This happened repeatedly across multiple sessions despite a written rule prohibiting it.

**Incorrect day-of-week.** The model was asked to reschedule calendar events across three weeks. It assigned day-of-week labels (Monday, Thursday, Saturday) to specific dates. All three were wrong. Documented errors in a single session:

| Date | Model said | Actual |
|---|---|---|
| April 14 | Monday | Tuesday |
| April 16 | Wednesday | Thursday |
| April 18 | Friday | Saturday |

Both failures share the same root: the model *believed it knew* and did not verify. In the first case, the belief was that a plausible item is the same as an existing item. In the second case, the belief was that mental date arithmetic is reliable.

## Where it applies (trigger)

**For external content:**
- Any output that includes a post, thread, article, or tweet from an external platform
- Any daily digest, news curation, or research summary task
- Any recommendation to reply to or engage with external community content

**For date and time:**
- Any output that assigns a day-of-week label to a specific date
- Any scheduling, calendar, or planning task involving concrete dates
- Any agenda or communication that names a day and a date together

## Why it gets forgotten (root cause)

**External content fabrication:**
- Pressure to fill all sections of a structured output creates incentive to "complete" even without real content
- The model confuses "this topic is relevant to this community" with "a post about this topic exists in this community"
- Academic papers found during search get reformatted as community posts without the model verifying the post exists
- The rule says "include the URL" but the model generates the item before finding (or failing to find) the URL

**Date arithmetic:**
- The model believes it can compute day-of-week from date. It cannot, reliably.
- There is no friction before writing "Monday April 14" — it outputs automatically
- The error is not caught until the operator checks a calendar

## Scar (fix)

### Rule 1 — No URL = item does not exist

For any external content item:
1. Find the URL first
2. If no URL exists → do not include the item. Do not rephrase it as "active topic" or "community discussion"
3. Declare explicitly: "No verified posts found today in [platform/community]"
4. If adjacent content exists (a paper on the topic, not a community post) → include it with its real URL and correct source label. Never present it as if it were a post in the wrong platform.

**Every content item must have: (a) a direct clickable URL, (b) a verified date, (c) the correct platform/source label. Missing any of the three → omit the item.**

### Rule 2 — Never compute day-of-week from memory

For any date that requires a day-of-week label:
1. Find an anchor date in the current context (today's date, if provided)
2. Count forward or backward from the anchor with simple arithmetic
3. If the date is more than 7 days away from the anchor → verify with a Bash `date` command or web search
4. Never write "Monday April X" without having counted from the anchor

**Self-check before sending any output with dates: for each date+day pair, "did I count from the anchor, or did I recall it?"**

## How to verify

- Every external content item in the output has a direct URL that resolves to the described content
- If the operator requests a link and the answer is "I cannot find one" → scar failure
- For dates: if the operator corrects a day-of-week → scar failure; log and review whether the anchor-counting step ran

## Metrics

- Activations: 0
- Success: 0 (N/A — adapt to your own environment)
- Last applied: never
- Post-scar recurrences: 0
- Notes: No hook currently; behavioral protocol only. A `UserPromptSubmit` hook that detects task types involving external content or date labeling would strengthen this scar.
