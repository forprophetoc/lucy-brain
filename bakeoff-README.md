# MIDWIFE BAKE-OFF — MASTER PACKAGE (read me first)

Five documents, one workflow. Date: June 10, 2026.

## The documents

1. **manus-dataset-brief.md** → paste into Manus. Builds contacts.csv + events.csv + build-summary.md. Nobody else sees these files.
2. **gpt-verification-prompt.md** → paste into GPT with Manus's three files. Returns numbers-only PASS/FAIL. ACCEPT = dataset locked. REJECT = paste correction list back to Manus. You never open the CSVs.
3. **simulation-spec-addendum.md** → goes to Cowork alongside midwife-rebuild-spec.md (v3). Defines the drip-driver, Phase 1 compressed clock, Phase 2 real-time 7-day run, contact-store isolation, the shared output CSV schema, and guardrails for both harnesses.
4. **fable-handoff-hermes-side.md** → opens a NEW Fable conversation that owns Harness B (Hermes on Gemini 2.5 free tier). Attach docs 1–3 + the rubric to that session.
5. **audit-scoring-rubric.md** → used only after Phase 2. Blind merge/shuffle, independent scoring, unblind, verdict. Headline metric: memory integrity on multi-touch arcs.

## Order of operations

1. Manus builds dataset → GPT verifies → ACCEPT
2. Cowork: simulation spec session (this also resolves the §7 open item from the main spec — Agent SDK plan billing vs. plain `claude -p`)
3. New Fable session: Harness B config plan via its handoff doc
4. Claude Code builds: Listener+Midwife (per main spec), drip-driver, Harness B config, loader, blind-merge script
5. Phase 1 smoke (~75 events, compressed clock, no live SMS) → gate review
6. Phase 2: 7 real days, live SMS to Oscar's phone for 6 contacts incl. the 3am slot, one deliberate mid-week reboot
7. Blind audit → audit-report.md → deployment decision (A, B, or split)

## Standing rules captured in this package

- Lucy persona identical across harnesses (lucy-persona.md, canonical).
- Inbound-triggered replies any hour; proactive sends 08:00–21:00 only.
- Harness A: Max plan only, no ANTHROPIC_API_KEY in env, ever.
- Harness B: Gemini 2.5 free tier only, no paid keys, US providers only (no Chinese-owned models/providers), skill whitelist, no AGENTS.md injection.
- Neither auditor (Oscar, Fable-Claude) reads the dataset before scoring moment.
- expected_behavior (written by Manus, verified by GPT) is the fixed scoring anchor.
