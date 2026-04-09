---
id: scar_001
name: docx_tildes
severity: medium
date_detected: 2026-04-04
date_codified: 2026-04-06
status: active
---

# scar_001 — DOCX generated without accents

## What happened (origin)

Technical specification documents I was generating with a Python
script (via the `docx-js` wrapper library) consistently came out with
missing accents and tildes on uppercase headings unless the source code
used manual Unicode escapes for every diacritic character. A document
delivered to a client had "CAPITULO" rendered as "CAPITULO" and
"ESPECIFICACION" as "ESPECIFICACION" across every section header,
because the library's default code path strips diacritics from
uppercased strings at render time.

This was caught on visual inspection before delivery — but only
because I happened to look. The error was purely cosmetic, which
made it exactly the kind of thing that slides through a "does it
run?" quality gate.

## Where it applies (trigger)

- Editing any Python file that contains `from docx` or imports
  `docx-js` or any docx-producing library.
- Any script whose filename matches `*generate*.py`, `*generador*.py`,
  `*build_doc*.py` and which outputs `.docx`.
- Immediately after regenerating a DOCX, **before** handing it to
  anyone downstream of you (a human reader, a PDF pipeline, an
  archival system).

## Why it gets forgotten (root cause)

- **Low technical friction.** Nothing in the generation pipeline
  prevents the bug. The DOCX file writes fine, opens fine, and looks
  fine — until a human reads the headings.
- **Post-hoc rule.** "Run the tilde fixer after generation" is an
  addendum, not a step in the pipeline. It depends on memory, which
  is exactly what the Lucy Syndrome breaks.
- **Cosmetic, not functional.** The script exits clean, tests pass,
  no exception is raised. The model's "task complete" signal fires
  on a document that is wrong.

## Scar (fix)

1. After regenerating any DOCX, run a tilde/accent post-processor.
   In my environment this is a small Python script that walks the
   document, re-inserts the Unicode characters into any all-caps
   string that should have carried a diacritic, and writes the file
   back in place:

   ```bash
   python scripts/fix_tildes.py <path_to_docx>
   ```

   You can write your own version in ~60 lines of `python-docx` plus
   a dictionary of your language's uppercase-with-diacritic words.
   The pattern is simple: iterate `doc.paragraphs`, for each run
   check `.text` against your dictionary, and rewrite the run if
   there's a match. The tricky part is that `python-docx` splits
   text into multiple runs when formatting changes mid-word, so the
   replacement has to rebuild runs from the paragraph text and lose
   character-level formatting. For pure headings this is fine.

2. Verify visually that the known-problem words on the first and last
   pages are correct. Do not trust a grep — trust your eyes, once.

3. If the fix script does not exist yet or fails on your document,
   **stop** and fix the script before delivering. Do not ship a
   document with the known defect just because the fix tool is
   missing.

## How to verify

- Open the DOCX and search for the canonical problem words in your
  language (Spanish: `CAPITULO`, `ESPECIFICACION`, `PAVIMENTO`,
  `SECCION`). They must appear with their correct diacritics.
- If you are opening the file programmatically with `python-docx`,
  `doc.paragraphs[i].text` should contain the expected Unicode
  codepoints (`\u00cd` for *Í*, `\u00d3` for *Ó*, etc.).

## Metrics (from the originating environment)

- Activations: 4
- Successes: 4 (all regenerations passed through the fix before
  delivery; no accent-related corrections needed post-delivery)
- Last applied: a production run in April 2026 that touched four
  docx-producing scripts in a single session
- Recurrences after scar was installed: 0

## Notes

The hook (`hooks/hook_scar_001_docx.py`) is intentionally dumb: it
fires on any Python file that mentions `docx`, including files that
merely discuss docx without producing it. This generates occasional
false positives (for example, when you're editing a README about
docx, or editing the scar hook itself). That is an acceptable trade-
off: a warn-severity false positive costs nothing, and the alternative
— trying to detect *only* files that actively produce docx — is hard
to do reliably from static analysis at write time.
