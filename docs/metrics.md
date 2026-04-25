# Metrics Reference — Lucy Syndrome Framework

> Phase 2 observability specification.  
> These 9 metrics measure whether functional scars are working — not just whether hooks fire.

---

## Core Metrics

### 1. `activation_rate`

**Definition:** Number of hook fires per scar per unit of time.  
**Formula:** `fires(scar_id, period) / days(period)`  
**Unit:** fires/week  
**Source:** `fires.jsonl` (automated)  
**Interpretation:** Zero for 30+ days → scar may be overconstrained or the error no longer occurs. Very high → consider whether the trigger is too broad.

---

### 2. `recurrence_rate`

**Definition:** Proportion of error opportunities where the same error recurs after the scar is active.  
**Formula:** `recurrences / total_error_opportunities`  
**Unit:** %  
**Source:** Manual operator label (`recurrence_post_scar: true` in log entry)  
**Interpretation:** H1 predicts ≥40% reduction vs pre-scar baseline. This metric closes or refutes H1.

---

### 3. `prevention_rate`

**Definition:** Proportion of hook fires followed by correct behavior (no error occurrence).  
**Formula:** `fires_where_outcome == "prevented" / total_fires`  
**Unit:** %  
**Source:** Manual operator label (`outcome: "prevented"` in log entry)  
**Note:** Complement of `leak_after_fire_rate`. Requires human review — a hook can fire and the model can still make the error.

---

### 4. `false_positive_rate`

**Definition:** Proportion of hook fires that were unnecessary (trigger activated but error was not imminent).  
**Formula:** `fires_where_false_positive == true / total_fires`  
**Unit:** %  
**Source:** Manual operator label (`false_positive: true` in log entry)  
**Critical threshold:** FP rate ≤ 2% over ≥50 fires is the prerequisite for escalating a scar from `warn` to `deny` severity. See [escalation-policy.md](escalation-policy.md).

---

### 5. `leak_after_fire_rate`

**Definition:** Proportion of cases where the error occurs even after the hook fires and delivers the warning.  
**Formula:** `fires_where_outcome == "leaked" / total_fires`  
**Unit:** %  
**Source:** Manual operator label (`outcome: "leaked"` in log entry)  
**Note:** `leaked` means the hook fired AND the error still happened. This is distinct from the hook not firing at all. High leak rate → the warning text is insufficient; the scar fix needs strengthening.

---

### 6. `latency_overhead`

**Definition:** Mean additional milliseconds per tool call due to hook execution.  
**Formula:** `mean(latency_ms)` across all fire events for a given hook  
**Unit:** ms  
**Source:** `fires.jsonl` field `latency_ms` (automated via hook timing)  
**Interpretation:** Should be <200ms. Hooks adding >500ms to every Write/Edit call are operationally disruptive.

---

### 7. `token_overhead`

**Definition:** Mean tokens added per session due to hook context injection (additionalContext + systemMessage).  
**Formula:** `sum(tokens_added)` per session, averaged across sessions  
**Unit:** tokens/session  
**Source:** `fires.jsonl` field `tokens_added` (automated)  
**Interpretation:** Track cumulative overhead. A system with 8 hooks firing frequently can add thousands of tokens per session, affecting cost and context window.

---

### 8. `operator_intervention_saved`

**Definition:** Number of human corrections avoided because the scar caught the error before the operator needed to intervene.  
**Formula:** Estimated count per week  
**Unit:** interventions/week  
**Source:** Manual estimate (`reviewed_by_human: true` + `outcome: "prevented"` in log)  
**Note:** This is the most meaningful ROI metric but requires operator judgment. One prevented `scar_001` fire (missing tildes in a DOCX) saves ~15 minutes of manual fix + client delivery delay.

---

### 9. `severity_adjusted_harm`

**Definition:** Sum of prevented errors weighted by scar criticality.  
**Formula:** `Σ (criticality_weight × 1)` per prevented error per week  
**Weights:** `critica` = 3, `alta` = 2, `media` = 1, `baja` = 0.5  
**Unit:** severity-adjusted points/week  
**Source:** `fires.jsonl` fields `criticidad` + `outcome`  
**Interpretation:** A week where two `critica` scars each prevent one error scores 6 points. Tracks whether the highest-risk scars are the ones doing the work.

---

## Derived Metrics

| Metric | Formula | Use |
|---|---|---|
| **Coverage** | `scars_with_hook / total_scars` | Currently 6/11 = 54.5%. Target: ≥80% |
| **Scar ROI** | `operator_intervention_saved / (latency_overhead_total + maintenance_hours)` | Justify ongoing investment |
| **Lucy Quotient** | `recurrence_rate × session_count × project_months` | From cross-analysis.md §6. Severity index of the syndrome |

---

## Implementation Notes

- All automated metrics (1, 6, 7) are populated from `fires.jsonl` via `analyze_fires.py` (to be built).
- Manual metrics (2, 3, 4, 5, 8, 9) require the operator to set `reviewed_by_human: true` and fill in `outcome`/`false_positive`/`notes` in the relevant log entry.
- Minimum viable tracking: implement metrics 1, 4, 6 first (fully automated). Add manual fields as overhead allows.
- Log schema: see [logging-schema.json](logging-schema.json).
- Escalation thresholds derived from these metrics: see [escalation-policy.md](escalation-policy.md).

---

*Specification derived from Deep Research report reviewed 2026-04-25. Compatible with Lucy Syndrome paper Zenodo v3 (DOI: 10.5281/zenodo.19555971).*

---

## Phase 3 Extension: Opportunity-Based Coverage

> Added 2026-04-25. Requires `opportunities.jsonl` (populated by `opportunity_observer`).

The Phase 2 "Coverage" metric (`scars_with_hook / total_scars`) measures **instrumentation** coverage — how many scars have hooks. It does not measure whether the hooks actually catch the errors they exist to catch.

Phase 3 replaces this with **recall-based coverage**:

### Updated: `coverage` (Phase 3)

**Definition:** Proportion of real opportunities where a fire was recorded.  
**Formula:** `confirmed_fires / (confirmed_fires + confirmed_missed_opportunities)`  
**Where:**  
  - `confirmed_fires` = fires where a matching opportunity was validated  
  - `confirmed_missed_opportunities` = opportunities where `validated=true` and `fired=false`  
**Unit:** %  
**Source:** `fires.jsonl` + `opportunities.jsonl` (semi-automated; requires operator validation)  
**Interpretation:** 100% means every real opportunity resulted in a fire. 60% means 40% of the time the scar context existed but the hook did not fire — a gap to close by broadening the trigger.

### New: `recall`

**Definition:** Of all contexts where a scar should apply, what fraction does the hook detect?  
**Formula:** `fires / total_opportunities` (unvalidated denominator)  
**Note:** Lower bound on true recall since `opportunities.jsonl` may not capture all contexts.

### New: `activation_rate` (Phase 3 re-definition)

In Phase 3, `activation_rate = fires / opportunities` (not fires/day).  
A rate of 0.3 means the hook fires on 30% of detected opportunities — useful for calibrating trigger breadth.

---

### Validation workflow

Opportunities start with `validated: null`. The operator validates them weekly:

```bash
python logging/validate_opportunities.py --stats          # see pending count
python logging/validate_opportunities.py --report         # generate Markdown review doc
python logging/validate_opportunities.py --validate <id> --result true|false
```

Only `validated=true` opportunities enter the coverage denominator,  
preventing the observer's false positives from inflating the missed count.

---

*Phase 3 extension — 2026-04-25. Backward-compatible: all Phase 2 metrics unchanged.*
