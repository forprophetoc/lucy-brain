# HARNESS B INTERFACE CONTRACT — one page
*For the Hermes-side Fable owner. Your internals (Gemini auth, skills, bloat controls) are yours per fable-handoff-hermes-side.md; everything on the wire is fixed here. Builder for both sides: Claude Code, same machine.*

## 1. What you receive

Drip-driver POSTs every event to **`http://127.0.0.1:8702/event`** (you own this listener):

```json
{
  "schema_version": "bakeoff-1.0",
  "event_id": "E0417",            // echo into your output row; LIVE-<n> for operator replies
  "contact_id": "C0231",          // resolve in YOUR seeded store — never by name
  "arc_step": 3,                  // null on live_inbound: derive from your thread, echo derived value
  "event_type": "inbound_sms",    // unknown values must process as generic trigger, never crash
  "scheduled_at": "2026-06-18T03:05:00-04:00",
  "fired_at":     "2026-06-18T03:05:02-04:00",
  "inbound_text": "string or null",
  "live_send": false,
  "phase": 2
}
```

Contact seed: `C:\bakeoff\harness-b\contacts-seed.csv` (contact_id, first_name, last_name, language, live_send) — produced by the shared loader before any run. You never receive `expected_behavior`, and no phone number exists anywhere in this system — GHL alone knows the destination; everything is keyed by contact_id.

## 2. What you must answer

- **Ack:** HTTP 200 `{"received": true, "event_id": "..."}` within **10s**, only after durable enqueue (process async). 4xx only for malformed payloads (driver will not retry those). Driver retries your 5xx/timeouts at 1s/4s/16s, then logs an error row against you — silence is a scored reliability failure, not a crash for anyone else.
- **Health:** GET `http://127.0.0.1:8702/health` → `{"ok": true, "queue_depth": n}` (watchdog restarts you when it fails).

## 3. What you must emit

Append one row per invocation, real-time, to **`C:\bakeoff\harness-b\out\output-B.csv`** — exact addendum §5 schema, `harness=B`, `cost_estimate` = tokens + free-tier quota consumed. `reasoning` (≤3 sentences) and `memory_facts_used` must come from the agent, not scaffolding. Errors/timeouts/refusals are rows with the `error` column filled — never silently dropped. Gemini quota exhaustion: queue, resume on reset, log the window (finding, not failure).

## 4. Live sends — you never touch GHL

For a `live_send: true` contact that YOUR side owns (3 of the 6 — ownership is told to you by the gateway response, you don't need the table), POST your final message to the shared send gateway:

`POST http://127.0.0.1:8703/send` `{"harness":"B","contact_id":"...","event_id":"...","message":"..."}`

Gateway applies every gate (kill switch, phase, ownership, opt-out, send-window) and transmits via the real GHL number. 200 → write `sent_live=TRUE`; denial returns the failed gate name → row stays draft with a note. Operator replies come back to you as `live_inbound` events at your listener — only for contacts you own.

## 5. Persona and survival

- Load `C:\bakeoff\shared\lucy-persona.md` VERBATIM; your scaffolding may add output-format instructions only — no rule changes.
- Your start command goes into the `bakeoff-harness-b` Task Scheduler wrapper (slot provided): after an unattended reboot your listener must return and resume its queue with zero manual steps. One deliberate mid-week reboot WILL happen.
- Phase 1 = compressed clock, same payloads, ~75 events, no live sends (gateway enforces; don't rely on that — your side shouldn't attempt them in phase 1).
- Timezone: all timestamps America/New_York ISO 8601; your `draft_ready_at` must be the same format or latency math breaks.

## 6. Timing expectations

No SLA on draft latency — it's scored data (median/p95, special cut for 02:00–07:00). Ack SLA is the only hard one (10s). Don't batch: process events as they arrive; the 3am events fire at 3am real time in Phase 2.
