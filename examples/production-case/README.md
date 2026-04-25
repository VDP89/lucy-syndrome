# Production Case — Civil Engineering Operation

> The actual scars and hooks from a civil engineering firm running nine business areas
> through Claude Code. These are real operational files, not demonstration material.

---

## Context

**Operation**: DG Ingenieria SRL, Asuncion, Paraguay. Nine business areas: civil design, structural, aeronautical consulting, pavement analysis, vial infrastructure, urban planning, industrial plants, financial management, and digital communications. All areas operated via Claude Code, with an evolving knowledge base of 530+ markdown files.

**Dataset**: 163 findings extracted from 17 source files (15 Claude Code session logs + 2 ChatGPT memory exports), spanning August 2025 to April 2026. Findings are categorized into:
- **A** — Repeated errors (37 findings): mistakes that recurred after being corrected
- **B** — Successful corrections (55 findings): corrections that persisted across sessions
- **C** — False confidences (29 findings): the model was wrong and did not flag uncertainty
- **D** — Metacognitive frictions (42 findings): the model failed to apply a rule it already had

**Research**: the full dataset analysis is in [`../../research/`](../../research/).

---

## The 11 scars

| ID | Name | Severity | Hook | Origin |
|---|---|---|---|---|
| scar_001 | docx_tildes | medium | yes | Accents silently stripped from generated Word documents |
| scar_002 | code_review_absent | high | yes | 100% of generated code executed without source review |
| scar_003 | token_budget | medium | no | API plan exhausted from unmanaged MCP/model defaults |
| scar_004 | consult_kb_first | high | yes | Generating before reading the project knowledge base |
| scar_005 | validate_subagent_output | high | yes | Subagent silently omitted a file from a batch (14.8% data loss) |
| scar_006 | pre_deploy_audit | high | no | Website deployed with inconsistent content across pages |
| scar_007 | memory_update_session_close | high | no | Session closed without persisting discoveries to memory |
| scar_008 | no_fabricar_contenido | critical | no | External content fabricated without verifiable URL |
| scar_009 | verificar_dia_semana | critical | no | Day-of-week labels computed from memory, consistently wrong |
| scar_010 | definir_por_lo_que_somos | critical | yes | Brand copy defined products by what they are NOT |
| scar_011 | tildes_entregables | high | yes | Spanish deliverables (HTML, PDF, PPTX) written without accents |

---

## The 8 hooks

| File | Event | Matcher | Scar(s) |
|---|---|---|---|
| `hook_session_start.py` | `SessionStart` | — | Summary of all active scars |
| `hook_scar_001_docx.py` | `PreToolUse` | `Write\|Edit` | scar_001 |
| `hook_scar_002_size.py` | `PreToolUse` | `Write\|Edit` | scar_002 |
| `hook_scar_004_expand.py` | `UserPromptSubmit` | — | scar_004 (Etapa 0) |
| `hook_scar_005_subagent.py` | `PreToolUse` | `Task` | scar_005 |
| `hook_scar_010_no_cerrar_puertas.py` | `PreToolUse` | `Write\|Edit` | scar_010 |
| `hook_scar_011_tildes_entregables.py` | `PreToolUse` | `Write\|Edit` | scar_011 |
| `hook_dropbox_mirror_warn.py` | `SessionStart` | — | Infrastructure warning (Dropbox mirror) |

---

## Key findings from the dataset

**The RIALTO anomaly**: RIALTO is the project in the dataset with the highest density of findings — 21 findings from 373 lines (1 per 17.8 lines, vs. the dataset average of 1 per 34.6 lines). The reason: RIALTO had already implemented a manual scar-like system with 67+ numbered rules triple-anchored in memory, session logs, and workflow checklists. Its correction success rate was near 100%. This is the empirical validation of the framework proposed in the companion paper.

**RIALTO was also the file a subagent omitted** from the batch in Sesion 1 — which produced scar_005. The file with the most evidence of successful correction practices was the one silently dropped. The operator's follow-up question ("did you do the RIALTO re-pass?") is what recovered it, adding 21 findings (14.8% of the final dataset) and converting what would have been the paper's weakest section into its strongest case study.

**Rule shape predicts persistence**:

| Rule form | Escape rate |
|---|---|
| Binary (yes/no, specific value) | 17% |
| Structural (change to source document) | 10% |
| Proportional ("X% of Y") | 80% |
| Verbal without physical support | 100% |

**scar_004 is the pivotal scar**: the most frequent anti-pattern in the dataset — generating before reading — is the causal entry point for most repeated errors. If scar_004 works, the others are less needed.

---

## Notes on the files

- Files are included as-is from production. Spanish is the working language of the operation; English was used only for external-facing deliverables and the research paper.
- Phone numbers and other personal data have been redacted where present.
- The hooks contain hardcoded paths (e.g., `D:/DG-2026_OFFICE/`) that reflect the original environment. These paths do not affect the hook logic; they appear only in error messages and documentation strings.
- `hook_scar_004_expand.py` is the most complex hook in the set (~240 lines). It parses a memory index (MEMORY.md), extracts keywords, matches them against the user's prompt, and injects a list of files to read before generating. It is standard-library only.

---

## How the system evolved

| Date | Event |
|---|---|
| 2026-04-06 | Lab Sesion 1: 163 findings extracted. scar_001–005 codified. Hooks Fase 1. |
| 2026-04-07 | Hooks Fase 2 activated: SessionStart + PreToolUse Write\|Edit + PreToolUse Task |
| 2026-04-14 | scar_007–009 codified from recurring failures (calendar errors, fabricated content) |
| 2026-04-15 | scar_004 reincidence (A3.1): Etapa 0 added. hook_scar_004_expand.py deployed |
| 2026-04-18 | scar_010–011 codified from ERGON brand session. Hooks for both activated. |
| 2026-04-25 | Repository restructured as installable toolkit |
| 2026-04-25 | Phase 2 logging: all 8 hooks instrumented with log_scar_fire(). fires.jsonl now collects activation data. I5 closed. |
