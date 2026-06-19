# MASTER ARCHITECTURE — Midwife Bake-Off
*Canonical build spec. Audience: Claude Code (builder). Author: Cowork (architect). Date: 2026-06-10.*
*This document ABSORBS the unexported midwife-rebuild-spec v3: where other docs cite "the main spec," this document is now the authority. Companions: simulation-spec-addendum.md (settled), audit-scoring-rubric.md (settled), fable-handoff-hermes-side.md (Harness B internals — not built here), lucy-persona.md (canonical persona), harness-b-contract.md (the only interface Harness B's owner builds against).*

## 0. Resolved decisions (final — do not reopen)

1. **Invocation: plain `claude -p`**, never the Agent SDK. Max-plan login only. `ANTHROPIC_API_KEY` present in the environment = startup build-failure (assert in every entry point).
2. **Contact store: local GHL-shaped mock.** No mock contact ever touches GHL. The 6 live-send contacts exist in GHL only as flagged test records (`ZZTEST-` name prefix + `bakeoff-test` tag) provisioned ONCE at P4 with the operator present, addressed thereafter only by GHL contact id, deleted at teardown.
3. **Machine stays awake** for the 7-day run. No wake timers. Power prerequisites (operator): AC power, Sleep = Never, display-off allowed, Windows Update paused for the run week. All services are Task Scheduler jobs with "run whether user is logged on," "run ASAP after missed start," restart-on-failure, plus at-startup triggers — the deliberate mid-week reboot must recover everything unattended.
4. **No phone number exists anywhere in this system (supersedes the kickoff's "substituted at load time" language).** GHL sends by contact id; the operator's number lives only inside GHL, where it already lives. The loader validates the dataset's 555 discipline, then DISCARDS the phone column — no store, seed, cabinet, log, payload, or output ever carries a tel. The gateway addresses the live six purely via `config.live_contact_map` (contact_id → GHL contact id). There is no `OPERATOR_PHONE` variable and no substitution step.
5. **Live-send ownership split:** the 6 live contacts are assigned 3-and-3 to Harness A and Harness B (alternating by load order, persisted in `live_routing`). Each live arc transmits via exactly ONE harness — otherwise both harnesses would double-text the operator on the same thread and his replies would be unattributable. The non-owner harness still processes every event for that contact draft-only. Latency stats for the 02:00–07:00 window come from ALL rows (draft + live), so both harnesses are still measured on the 3am test.

## 1. Component map

```
                          C:\bakeoff\dataset\contacts.csv + events.csv   (verified ACCEPT; nobody opens)
                                            │
                                      [1] loader.py  (validate → seed stores → strip expected_behavior)
                                            │
   ┌────────────────────────────────────────┼─────────────────────────────────────────┐
   ▼                                        ▼                                          ▼
harness-a\cabinet\ + midwife.db      harness-b contact seed                    driver.db (schedule)
                                                                                       │
                                      [2] drip_driver.py  ◄── killswitch ──────────────┤
                                            │  identical webhook POST, simultaneous    │
                            ┌───────────────┴────────────────┐                         │
                            ▼                                ▼                         │
              [3] listener_a.py :8701            Harness B listener :8702   (theirs — see contract)
                    │ ack 200, durable queue            │
              [4] invoker.py (claude -p, 1 event = 1 bounded call)
                    │ JSON out
              [5] cabinet writer + output-A.csv          output-B.csv (theirs)
                    │ live-eligible drafts                      │ live-eligible drafts
                    └────────────►  [6] send_gateway.py :8703  ◄┘
                                          │  ALL gates + GHL transmit + inbound polling
                                          ▼
                              GHL (real number) ──SMS──► operator phone ──reply──► gateway poll → owner harness
                    [7] watchdog (5-min health/restart)   [8] blind_merge.py (post-Phase-2 only)
```

## 2. Runtime layout (Windows)

Runtime root: **`C:\bakeoff\`** — deliberately OUTSIDE `Documents\` (OneDrive backup/sync can lock SQLite files and leak content to cloud; the operator's Documents shows OneDrive indicators). Specs remain in `Documents\Claude\Projects\Hermes\bakeoff\`; code + state live here.

```
C:\bakeoff\
  config\config.json          ports, paths, phase, compression, model — NO secrets ever
  dataset\                    contacts.csv, events.csv (read-only after ACCEPT; never printed)
  shared\lucy-persona.md      copied verbatim from the spec folder by P0 scaffold
  harness-a\
    listener_a.py  invoker.py  midwife.db
    cabinet\<contact_id>\profile.md | thread.md | facts.md
    out\output-A.csv            logs\a.log
  harness-b\out\output-B.csv  (B writes here; B internals live in C:\Users\test\hermes-work\ per its owner)
  driver\drip_driver.py  driver.db  out\driver-log.csv
  gateway\send_gateway.py  gateway.db  logs\gateway.log
  killswitch\                 presence of file named KILL = halt (see §9)
  merge\blind_merge.py  sealed\
  ctl.py                      start | stop | status | kill | resume | teardown
```

Python 3.14 (installed), stdlib + `flask` optional — builder may use stdlib `http.server` to keep dependencies zero. All times **America/New_York**, ISO 8601 with offset, everywhere.

## 3. Env asserts (run at the top of EVERY entry point)

1. `ANTHROPIC_API_KEY` is **unset** → else exit 2 "API key present — Max-plan-only constraint violated."
2. Harness A processes only: `claude auth status` exits 0 (logged-in Max account) → else exit 2.
3. Gateway only: `GHL_API_KEY` set (value never logged); `config.live_contact_map` present with exactly 6 entries (contact_id → GHL contact id), else live mode refuses to arm.
4. `C:\bakeoff\` not under a OneDrive/synced path (warn loud, proceed).
5. tzdata resolves America/New_York; system clock within 60s of NTP (warn only).

## 4. Loader / validator (`loader.py`) — P1

Input: the two dataset CSVs. The operator and Claude Code must never read row contents; loader output is aggregate-only.

Validation (hard fail on any): both CSVs parse; required columns present (`contacts`: contact_id, first_name, last_name, phone, language, live_send; `events`: event_id, contact_id, arc_step, event_type, scheduled_at, inbound_text, expected_behavior, plus any extra columns tolerated and preserved); every `events.contact_id` FK-matches a contact; all phones are `+1…555…` placeholders; exactly 6 contacts flagged live_send; `scheduled_at` parseable and non-decreasing per (contact_id, arc_step); event_id unique.

Seeding: per contact → SQLite `contacts` row + `cabinet\<contact_id>\profile.md` (name, language, live flag). Harness B seed: `harness-b\contacts-seed.csv` = contact_id, first_name, last_name, language, live_send. The phone column is validated (555 discipline) and then dropped — it exists nowhere downstream of the loader. Live routing table built here (alternating assignment).

**`expected_behavior` never leaves the dataset directory.** The driver reads events.csv but its payload builder has an explicit column whitelist; `expected_behavior` and `inbound_text` appear in no log line (bodies travel only inside payloads, cabinets, and output CSVs). `validation-report.txt` = counts, date range, arc histogram, duplicate-surname pair count — zero content.

## 5. Drip-driver (`drip_driver.py`) — P3

- Loads schedule from events.csv into `driver.db` once (`events_schedule`: event_id, contact_id, arc_step, event_type, scheduled_at, live_send, payload_json, a_status, b_status, fired_at, a_ack_at, b_ack_at). After load, the CSV is not re-read.
- **Phase 1 (compressed):** first 75 events by scheduled_at. `fire_wall = t0_wall + (scheduled_at − scheduled_at₀)/7`. **Phase 2 (real-time):** `fire_wall = scheduled_at`, all events.
- Loop: every 5s → kill-switch check → fire all events with `fire_wall ≤ now` not yet fired, oldest first, **serialized per contact_id** (arc order is sacred; global order best-effort).
- Fire = identical JSON POST (§6) to A `:8701/event` and B `:8702/event` (parallel threads). Per harness: ack timeout 10s; on connection-fail/5xx retry 1s/4s/16s then mark `error` and continue (a dead harness must never stall the other). 4xx = payload defect: log, mark, do NOT retry.
- **Idempotent resume:** status transitions persisted before/after POST; on restart, `firing`-state rows are re-checked against ack logs before refire; an acked event is never re-sent. Late events (machine was down) fire immediately on restart with true `fired_at` — the delay is test data, not an error.
- Rate-limit pause: if A's invoker signals saturation (§7), driver keeps firing B on schedule and queues A?? — NO: the LISTENER queues internally; the driver never pauses for harness slowness. Phase 1 Max-limit note from the addendum is handled inside Harness A's worker (slower than 7x is acceptable; events queue durably).
- `driver-log.csv`: event_id, harness, fired_at, ack_at, http_status, attempts.

## 6. Webhook payload (canonical, BOTH harnesses — the contract)

```json
{
  "schema_version": "bakeoff-1.0",
  "event_id": "E0417",
  "contact_id": "C0231",
  "arc_step": 3,
  "event_type": "inbound_sms",
  "scheduled_at": "2026-06-18T03:05:00-04:00",
  "fired_at": "2026-06-18T03:05:02-04:00",
  "inbound_text": "string or null",
  "live_send": false,
  "phase": 2
}
```

- `event_type` enum is whatever events.csv carries (expected family: inbound_sms, scheduled_followup, estimate_ready, job_complete; plus gateway-generated `live_inbound`). Harnesses must process unknown values as a generic trigger, never crash.
- `expected_behavior` is NEVER in a payload.
- Ack (both harnesses): HTTP 200 `{"received": true, "event_id": "E0417"}` returned only after durable local enqueue; processing is async. 4xx for malformed payloads. Health: GET `/health` → `{"ok": true, "queue_depth": n}`.

## 7. Harness A — Listener, invoker, cabinet

**Listener** (`listener_a.py`, 127.0.0.1:8701): validates payload → INSERT into `midwife.db events` (status=queued) → ack. Single worker thread drains FIFO **per contact** (one in-flight invocation globally — keeps Max usage smooth and ordering trivial).

**Invoker** (`invoker.py`) — one event = one bounded call:
1. Build prompt: `lucy-persona.md` (verbatim) + contact block (profile.md, facts.md, thread.md tail ≤ 30 messages) + event block (type, time, inbound_text) + output instructions.
2. Invoke: `claude -p --output-format json --max-turns 1 --model sonnet` with **zero tools enabled** (builder pins the exact no-tools flag form against `claude --help` at P0 — requirement: the call can read nothing and execute nothing; prompt via stdin). No web, no skills, no MCP (`--strict-mcp-config` with empty config if needed).
3. Required model output (strict JSON): `{"draft_message": str, "reasoning": str ≤3 sentences, "memory_facts_used": [str], "memory_updates": [str]}`. Parse failure → ONE repair retry (same context + "return only valid JSON") → else error row.
4. Deterministic post-steps (code, not model): append event + draft to `thread.md`; append `memory_updates` lines to `facts.md`; write output row; if draft is live-eligible (§8) POST it to the gateway.
5. Saturation handling: stderr/result indicating rate/usage limit → event → `queued_retry`, worker sleeps 15 min, resumes. Pause windows logged to `a.log` (parity with B's quota findings).

**Cabinet** = the memory under test. `profile.md` seeded identity; `thread.md` append-only conversation; `facts.md` durable agent-maintained facts (what `memory_facts_used` should cite). Contact resolution is ALWAYS by `contact_id` — never by name (duplicate-name pairs are seeded traps; cross-contamination = build defect).

**Output writer**: appends to `out\output-A.csv`, exact addendum §5 columns, `harness=A`, `cost_estimate` = `in=<input_tokens>;out=<output_tokens>` from the claude -p result JSON. Rows append in real time; `error` column carries timeout/refusal/parse-fail descriptions; ≥98% row coverage is the Phase 2 bar.

**D7 mechanical guards (code-level, belt under the persona):** proactive sends blocked outside 08:00–21:00 ET (inbound-triggered replies exempt — a reply to a 03:05 inbound IS allowed and is the whole point); STOP/opt-out intent regex on every inbound sets `contacts.opt_out=1` → all future outbound for that contact suppressed at the gateway and noted in output rows.

## 8. Send gateway (`send_gateway.py`, 127.0.0.1:8703) — the ONLY path to a real SMS

`POST /send {harness, contact_id, event_id, message}` → gates, in order, all logged per request: kill switch absent → phase == 2 → contact is live_send → requesting harness owns the contact (live_routing) → contact not opted out → window rule (proactive 08:00–21:00 ET; inbound-replies any hour) → transmit.

Transmit = GHL LeadConnector v2 (location `nABhWvCMp0bV0jtb6uLW`, `Version: 2021-07-28`, `Authorization: Bearer %GHL_API_KEY%`): resolve contact_id → GHL contact id via `config.live_contact_map`, then `POST /conversations/messages {type:"SMS", contactId, message}`. No contact creation, no phone handling — the webhook triggers the convo; GHL owns delivery. (The six `ZZTEST-` test contacts are provisioned once at P4 by the operator, in-app or via a one-time script he approves.) Result → `gateway.db sends`; success → harness's row gets `sent_live=TRUE` (gateway returns confirmation to the harness synchronously). Denials return the failed gate name so the harness logs an honest error/note.

**Inbound capture (operator replies, Phase 2):** gateway polls GHL every 30s for new inbound messages on the 6 ZZTEST contacts (cursor in gateway.db). New inbound → build `live_inbound` payload (`event_id: LIVE-<n>`, `arc_step: null` — owner harness derives next step from its thread and echoes its derived value), POST to the **owner** harness only, log to driver-log.csv. Builder verifies the exact GHL conversations read endpoint at P4 — pinned requirement is poll-based capture at ≤60s latency; no public URL, no tunnels (ngrok deliberately avoided: one less moving part to survive reboots).

**Teardown** (`ctl.py teardown`, post-audit): delete ZZTEST contacts from GHL; archive `C:\bakeoff\` state; print checklist.

## 9. Kill switch

Creating file `C:\bakeoff\killswitch\KILL` (any content) halts ALL sending instantly: driver stops firing (≤5s), gateway refuses /send and stops polling, invoker finishes in-flight call then parks queue. `ctl.py kill` creates it; deleting it + `ctl.py resume` continues from cursors (late fires logged). Operator instruction card: "Emergency stop = put a file named KILL in C:\bakeoff\killswitch — or run ctl kill."

## 10. Task Scheduler jobs (all: run whether logged on or not; run ASAP after missed start; restart on failure ×3; At-startup trigger)

| job | command | trigger |
|---|---|---|
| bakeoff-listener-a | `python C:\bakeoff\harness-a\listener_a.py` | startup |
| bakeoff-harness-b | start command supplied by B's owner (wrapper script slot) | startup |
| bakeoff-gateway | `python C:\bakeoff\gateway\send_gateway.py` | startup |
| bakeoff-driver | `python C:\bakeoff\driver\drip_driver.py` | startup |
| bakeoff-watchdog | `python C:\bakeoff\ctl.py watchdog` | every 5 min |

Watchdog: GET /health on :8701/:8702/:8703, driver heartbeat age < 60s (driver writes heartbeat row each loop); dead component → `schtasks /run` its job; every action appended to `logs\watchdog.log`. Reboot recovery = startup triggers + idempotent resume; the deliberate mid-week reboot needs zero manual steps and its delays are test data.

## 11. Blind-merge (`blind_merge.py`) — run only after Phase 2 completes

Per rubric §1, exactly: read output-A.csv + output-B.csv → union → strip `harness` into `merge\sealed\blind-key.csv` (script prints SHA256; file is not opened until rubric step 5) → assign `audit_id` = uuid4 → shuffle (os.urandom seed) → LEFT-join events.csv `inbound_text`,`expected_behavior` on event_id (rows for live continuations get blanks + `is_live_continuation=TRUE`) → emit `merge\audit-deck.csv`. The first human read of dataset content is the auditors opening audit-deck.csv at the scoring moment.

## 12. Standing constraints (carried from the package — enforced in code where possible)

Max plan only; no `ANTHROPIC_API_KEY` anywhere (assert). No web/tools/skills inside Midwife invocations (no-tools invocation). No production customer data near the simulation (separate GHL test records only; mock store local). Output CSV schema is fixed (addendum §5) — builder may not extend it. Dataset contents surface only via live SMS and the final CSVs. Everything survives unattended reboot. lucy-persona.md is shared verbatim; harness scaffolding must not alter her rules.

## 13. Known risks (flagged once, mitigations in design)

1. **Anthropic billing change 2026-06-15** (Agent SDK credit pool on Max; unclear whether `claude -p` is touched) — P0 smoke invocation proves headless billing on day one; invoker saturation-pause absorbs limit changes mid-run.
2. **Max weekly caps vs ~1,500 invocations** — single-turn Sonnet calls with tight contexts; thread tail capped; if limits bite, A queues and resumes (logged as findings, mirroring B's quota rules).
3. **GHL inbound read endpoint** — exact GET path verified at P4; capture design (polling) does not depend on webhooks/tunnels.
4. **Windows Update mid-run reboot** — pause updates for the week; recovery design makes a surprise reboot a logged event, not a failure.
