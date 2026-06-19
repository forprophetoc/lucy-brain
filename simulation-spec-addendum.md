# SIMULATION SPEC ADDENDUM — "Midwife Bake-Off" Test Harness

*Companion to: midwife-rebuild-spec.md (v3). Audience: Cowork (architect). Builder: Claude Code.*

## 0. Purpose

Run the identical 500-contact / ~1,500-event mock dataset through TWO harnesses and produce comparable output CSVs for a blind human audit:

- **Harness A — "Midwife"**: Claude Code headless (`claude -p`) on Max plan. Per main spec: Listener, single bounded invocation per event, markdown filing cabinet + SQLite. **Constraint #1 unchanged: no ANTHROPIC_API_KEY anywhere in the environment.**
- **Harness B — "Hermes-side"**: the existing Hermes build, reconfigured to run on **Google Gemini 2.5 (free tier)**. Owned by a separate Fable agent (see fable-handoff-hermes-side.md). Harness B must consume the same events.csv and emit the same output schema (§5).

This is a system-vs-system comparison (flat-rate Claude Code system vs. free-tier Hermes system), not a model-vs-model benchmark. Both harnesses run the **identical Lucy persona prompt** (§6) so voice is controlled even though the engine differs.

## 1. Inputs

- `contacts.csv` and `events.csv` per manus-dataset-brief.md, verified ACCEPT by the GPT compliance audit (gpt-verification-prompt.md). The operator and auditors have NOT read these files; the harness build must not surface their contents to the operator outside of the live-send SMS and the final output CSVs.
- Before any run: a loader validates both CSVs parse and FK-match, then seeds each harness's contact store (GHL is NOT used for mock contacts — see §3).

## 2. Two phases

### Phase 1 — compressed clock (~1 day wall time, smoke test)

- Virtual clock at ~7x. The drip-driver maps each event's scheduled_at onto compressed wall time, preserving order and relative gaps.
- Scope: first ~75 events only (by scheduled_at). Purpose: catch systemic failures cheap — memory file not written, wrong contact resolved, timezone math, malformed output rows.
- NO live SMS in Phase 1. live-send contacts are drafted-only in this phase.
- Exit gate: operator reviews Phase 1 output CSVs for structural sanity (not message quality). Both harnesses must produce schema-valid output before Phase 2 is authorized.
- Max-plan note: compressed time bunches invocations; if rolling limits are hit, the driver pauses and resumes — accept slower than 7x rather than dropping events.

### Phase 2 — real time (7 consecutive days, the scored run)

- The drip-driver fires every event at its literal scheduled_at (America/New_York). 3am events fire at 3am.
- Live-send contacts (6, phone placeholder replaced with the operator's number at load time): their outbound messages ACTUALLY SEND as SMS via the GHL number, at natural times including the 02:30–03:30 slot. All other contacts: draft-only, send step mocked but latency-stamped.
- The operator may reply to live-send SMS from his phone; those inbound replies route into the harness as real inbound events and are logged as additional rows (arc_step continues).
- Machine resilience is in scope: Task Scheduler must recover both harnesses and the drip-driver after reboot/sleep with no manual steps. At least one deliberate reboot is performed mid-week and logged.

## 3. Contact store isolation

- Mock contacts NEVER enter the production GHL account as real contacts. Architect picks: GHL sandbox sub-account, or local mock of the GHL contact API with identical request/response shapes. Live-send SMS still transmits via the real GHL number (the 6 contacts may exist as flagged test contacts in a sandbox/sub-account if required for sending).
- Production customer data and the simulation must be fully separated. A kill switch halts all sending instantly.

## 4. Drip-driver (new component)

- Local service, Task Scheduler-managed, reads events.csv, fires each event as a webhook-shaped POST to BOTH harness listeners (identical payload, simultaneous).
- Idempotent and resumable: persists a cursor; after crash/reboot it resumes without double-firing. Late events (machine asleep at fire time) fire on wake and the delay is recorded — that is itself test data.
- Logs per event per harness: fired_at, ack_at, harness HTTP status.

## 5. Output CSV schema (BOTH harnesses, exact)

One row per agent invocation:

| column | content |
|---|---|
| harness | `A` or `B` |
| event_id, contact_id, arc_step | echo from events.csv |
| event_fired_at | drip-driver actual fire time (ISO 8601) |
| draft_ready_at | when the proposed message was complete |
| latency_seconds | draft_ready_at − event_fired_at |
| draft_message | Lucy's proposed SMS, verbatim |
| reasoning | agent's stated reasoning for the draft (≤3 sentences, produced by the agent) |
| memory_facts_used | semicolon list of prior-arc facts the agent claims it used (empty if none) |
| sent_live | TRUE only for live-send actual transmissions |
| cost_estimate | Harness A: invocation token counts; Harness B: tokens + free-tier quota consumed. Field present for both |
| error | empty, or error/timeout/refusal description |

Rows append in real time to per-harness CSVs; final deliverables are `output-A.csv` and `output-B.csv` plus the drip-driver log.

## 6. Persona parity

A single canonical `lucy-persona.md` (identity: "Lucy, Oscar's online assistant" at Bathtub Pros; always self-introduces on first touch of a thread; never claims to be human; "online assistant" IS the disclosure; inbound-triggered replies any hour, proactive sends 08:00–21:00 only; pivot-to-booking bias; coating/package facts per main spec). BOTH harnesses load this verbatim. Any harness-specific prompt scaffolding must not alter Lucy's rules.

## 7. Guardrails

- Harness A: Max login only; per-invocation max-turn and output bounds per main spec; presence of ANTHROPIC_API_KEY in env is a build-failure condition (assert at startup).
- Harness B: Gemini free tier; if quota exhausts mid-week, the harness queues events and resumes on quota reset — exhaustion timestamps are recorded as findings, not failures. NO paid keys of any kind in Harness B. Provider restriction per fable-handoff-hermes-side.md §Constraints.
- Neither harness may browse the web, call non-essential tools, or load skills beyond what the event requires. Harness B specifically: skill whitelist only (esticlose-irrelevant skills excluded), no AGENTS.md auto-injection (launch outside repo dir or config-disabled).

## 8. Definition of done

- Phase 1: both harnesses produce schema-valid output for ~75 events; zero contact-resolution errors on the duplicate-name pairs present in that window.
- Phase 2: 7-day run completes; ≥98% of events produce a row (errors logged, not silently dropped); all 6 live-send arcs transmitted including the 3am slot; reboot recovery demonstrated; output-A.csv, output-B.csv, and driver log delivered to the audit step.
