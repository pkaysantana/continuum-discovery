# Gemini SAP handoff

1. Open Gemini Pro / Deep Think and select the highest reasoning setting available in your account.
2. Upload `GEMINI_SAP_HANDOFF.md`. It contains the complete revision task followed by all 15 Markdown source documents, including Claude's exact review. Read the opening task before the source documents: it records the user's latest scope clarification and identifies the latest v2 reanalysis draft as the revision target.
3. If file attachments permit, also supply `inputs/reports/HLM_HH_QUALIFIER_CROSSTAB.json` for all 187 paired records. The matrix, individual ambiguous cases and exact counts are already in the combined Markdown.
4. Ask Gemini to return the replacement SAP as a prospective amendment for a new analysis, explicitly disclosing prior modelling. Do not ask it to run code or inspect model performance.
5. Check that the revision preserves that history and distinguishes a holdout untouched by the new analysis from data never previously evaluated. The requested READY_TO_FREEZE status applies to the new amendment, not retroactively to earlier results.

`REVISION_TASK.md` is the standalone instruction. `inputs/` contains exact source snapshots. `INPUT_MANIFEST.json` identifies every source version and SHA-256. The ZIP contains this complete directory, including supplementary JSON evidence. Use the combined Markdown when attaching many files is inconvenient.

The SAP was independently updated during packaging. Its latest v2 reanalysis version is the target; the earlier draft is preserved as PRE_HANDOFF_SNAPSHOT for review context. The source files were not modified by this packaging task.

Suggested message to Gemini:

> Follow the opening revision task in the attached GEMINI_SAP_HANDOFF.md. Produce the complete revised SAP for the new analysis amendment, with prior modelling disclosed, using Claude's adversarial review and the verified qualifier cross-tab. Revise the latest v2 draft, retaining correct amendments already made. Do not run any analysis. Flag any consequential source conflict or missing freeze detail rather than inventing an implementation choice.

The handoff has not been submitted to Gemini. No performance outputs are included.
