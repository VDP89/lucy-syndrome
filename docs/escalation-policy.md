# Escalation Policy — Lucy Syndrome Framework

> When and how to escalate a scar's severity level from `warn` to `confirm` or `deny`.

---

## The Escalation Ladder

```
warn  →  confirm  →  deny
 ↑                    ↓
 └──── refine/archive ←──── no fires for 30–45 days
```

### Level 1: `warn` (default for all new scars)

**Behavior:** Hook fires and injects a reminder message. The model decides whether to follow it.  
**When to use:** Always start here. No data required.  
**Rationale:** A warn that fires on a false positive creates noise that can be refined. A deny that fires on a false positive stalls the workflow. Start with warn.

---

### Level 2: `confirm`

**Behavior:** Hook fires and requires explicit human operator confirmation before the tool call proceeds.  
**Conditions to escalate from `warn`:**
- Scar has `criticidad: alta` or `criticidad: critica`
- The trigger pattern is reasonably specific (low expected false positive rate)
- The scar has accumulated some activation data (≥5 fires) showing the trigger is valid

**When NOT to use confirm:**
- Scars that fire on almost every Write call (would require constant interruption)
- Scars where the "confirmation" cannot be meaningfully given by the operator in context

---

### Level 3: `deny`

**Behavior:** Hook blocks the tool call entirely. The operator must take an explicit override action to proceed.  
**Conditions to escalate from `confirm` or `warn`:**
- **≥ 50 fires** with outcome data over the measurement period, AND
- **FP rate ≤ 2%** (false positives ≤ 1 per 50 fires), verified over those fires

Both conditions must be met simultaneously.

**Why these thresholds?**
- 50 fires provides statistical confidence that the filter pattern is reliable
- FP ≤ 2% means at most 1 false block per 50 hook activations — operationally acceptable
- Without verified FP data, moving to deny is a bet. The cost of a false deny is a stalled workflow; the cost of a false warn is a line of extra context.

**What `deny` looks like in practice:**
- The hook returns a non-zero exit code, causing Claude Code to reject the tool call
- The operator sees an error message and must either fix the condition or manually override
- Use only for actions that are irreversible and where the scar's trigger is highly precise

---

### Refine or Archive

**When:** 30–45 days without a single fire on an active scar  
**Options:**
1. **Refine the trigger:** the filter may be too narrow. Broaden the pattern or check if the error still occurs in current workflows.
2. **Archive:** mark as `estado: archivada` in the scar file. The error the scar was designed to prevent may no longer occur. Append-only — do not delete the file.

---

## Escalation Decision Tree

```
New scar
   ↓
Start at warn
   ↓
Accumulate fires data (fires.jsonl)
   ↓
After ≥5 fires: is FP rate acceptable?
   ├── FP rate > 10%: refine filter (return to warn with better pattern)
   └── FP rate ≤ 10%: continue at warn
   ↓
After ≥50 fires: is FP rate ≤ 2%?
   ├── Yes + scar is critica/alta: consider escalating to deny
   └── No: stay at warn, continue refining
   ↓
30–45 days with zero fires: refine or archive
```

---

## Current Scar Severity Map

| Scar | Criticidad | Current Severity | Hook Exists | Notes |
|---|---|---|---|---|
| scar_001 | media | warn | Yes | Hook fires on DOCX generation scripts |
| scar_002 | alta | warn | Yes | Hook fires on code >200 lines |
| scar_003 | media | warn | No | Guideline only — fix requires operator action |
| scar_004 | alta | warn | Yes | Second-generation hook after 2026-04-15 incident |
| scar_005 | alta | warn | Yes | Always fires on Task tool calls |
| scar_006 | alta | warn | No | Phase 1 only — no hook yet |
| scar_007 | alta | warn | No | Phase 1 only — no hook yet |
| scar_008 | critica | warn | No | URL verification not automatable via regex hook |
| scar_009 | critica | warn | No | Feasible: datetime comparison hook ~1–2h to build |
| scar_010 | critica | warn | Yes | Negation patterns in public copy |
| scar_011 | alta | warn | Yes | Missing tildes in Spanish deliverables |

**Current coverage:** 6/11 scars have hooks (54.5%). Target before any `deny` escalation: ≥80% with ≥4 weeks of fires data.

---

## Why Not Deny By Default for Critical Scars?

The paper (Part V §3) argues deliberately against `deny` as a default, even for critical scars:

> "A blocking hook that fires on a false positive creates an incident; a warn-severity hook that fires on a false positive creates noise, and noise can be refined out of existence by tightening the filter."

> "I wanted the right to iterate on the hooks without fear that a bad filter would break real work."

The escalation policy here operationalizes this reasoning: earn `deny` with 50 fires and 2% FP. Don't assume it.

---

*Policy derived from Lucy Syndrome paper (Zenodo DOI: 10.5281/zenodo.19555971) and Deep Research report, 2026-04-25.*
