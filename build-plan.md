# BUILD PLAN — Claude Code task list (P0–P5)
*Execute in order; every task has acceptance tests (AT) that must pass before the next task starts. Builder NEVER reads the real dataset CSVs' row contents — all testing uses self-written synthetic fixtures (≤10 contacts). Spec of record: master-architecture.md.*

## P0 — Scaffold + environment asserts
1. Create `C:\bakeoff\` tree per architecture §2; copy lucy-persona.md verbatim into `shared\`; write `config\config.json` (ports 8701/8702/8703, phase:"phase1", compression:7, model:"sonnet").
2. `ctl.py` with: `status` (ports, job states, heartbeats), `kill` (create KILL file), `resume`, `watchdog`, `teardown` (stub).
3. Env-assert module used by every entry point (architecture §3).
4. **Billing smoke test**: one `claude -p` invocation ("return the JSON {\"ok\":true}"), `--output-format json --max-turns 1`, zero tools; record model, usage fields, and that auth came from the Max login. Pin the exact no-tools flag form from `claude --help` into config.

**AT-P0:** ctl status runs green; smoke returns valid JSON with usage numbers; negative test — `set ANTHROPIC_API_KEY=x` then any entry point → exits code 2 with the constraint message; `claude auth status` exit code propagates correctly.

## P1 — Loader + validators
1. `loader.py` per architecture §4: validation, SQLite seed, cabinet seed, B's contacts-seed.csv, live_routing (3/3 alternating), validation-report.txt (aggregates only).
2. Payload-builder column whitelist (expected_behavior structurally excluded).

**AT-P1:** synthetic fixture (8 contacts incl. 2 same-name pairs + 2 live flags, 20 events) loads clean; broken-FK fixture fails loudly; non-555 phone fails; 7-live-flags fixture fails; grep of all logs/outputs/seeds for a sentinel string planted in fixture `expected_behavior` finds ZERO hits; grep for a sentinel phone digit-string finds ZERO hits in every seed/store/cabinet (phone column dies at the loader); report contains counts only.

## P2 — Listener A + invoker + cabinet + output writer
1. `listener_a.py`: POST /event validate→queue→ack; GET /health; FIFO-per-contact worker, one global in-flight invocation.
2. `invoker.py`: prompt assembly (persona + profile + facts + thread tail ≤30 + event), bounded `claude -p` call, strict JSON parse + one repair retry, deterministic cabinet writes, output-A.csv row append (exact addendum §5 columns), saturation→queued_retry/15-min pause path.
3. D7 guards: proactive-window gate; opt-out regex latch.

**AT-P2:** fixture event POST → ack <1s with durable row; output row schema-validates (csv header exact); cabinet thread.md + facts.md updated; malformed-model-output simulation exercises repair-then-error path; burst of 5 events for one contact processes strictly in arc order; opt-out inbound latches contact and subsequent outbound is suppressed with note; a `scheduled_followup` at 22:00 ET produces draft marked window-blocked (no gateway call), while an `inbound_sms` at 03:00 processes normally.

## P3 — Drip-driver + Phase-1 compressed clock
1. `drip_driver.py` per architecture §5: schedule load, 7× mapping, first-75 cutoff, per-contact serialization, dual-POST with retry/backoff, driver-log.csv, heartbeat, kill-switch check, idempotent cursor.

**AT-P3:** 20-event fixture at 7× fires in order with correct compressed gaps (±2s); kill driver process mid-run, restart → zero double-fires (driver-log unique per event×harness), remaining events fire; one harness down → its rows error after 3 retries while the other harness's acks unaffected; KILL file → firing stops ≤5s, resume continues; simulated A-saturation queues without stalling B.

## P4 — Send gateway + kill switch + live path + inbound polling + reboot recovery
1. `send_gateway.py` per architecture §8: gate chain with per-gate logging, GHL upsert+send (env-var names only), sends ledger, sent_live confirmation back to harness, 30s inbound polling → live_inbound to owner (verify exact GHL read endpoint against LeadConnector v2 docs HERE — do not guess; if docs ambiguous, stop and report).
2. Register all five Task Scheduler jobs (architecture §10) with required flags; watchdog restart logic.
3. Provisioning (operator present, once): operator creates the 6 `ZZTEST-` test contacts in GHL (in-app, 2 minutes) or approves a one-time script; their GHL contact ids go into `config.live_contact_map`. Then end-to-end test: ONE message through one mapped contact (operator pre-warned; arrives on his phone).

**AT-P4:** gate-denial matrix test (phase1 / non-live contact / wrong owner / opted-out / out-of-window proactive each return the named gate); KILL blocks /send instantly; the single live test SMS arrives (operator confirms) and sent_live=TRUE row written; reply text from operator is captured by polling ≤60s and lands at owner harness only; **deliberate reboot**: machine restarted → all jobs auto-start, queued/missed events fire with late fired_at, watchdog log shows clean recovery, zero manual steps.

## P5 — Blind-merge script
1. `blind_merge.py` per architecture §11.

**AT-P5:** synthetic A+B outputs (incl. 2 LIVE- continuation rows) → audit-deck.csv has no harness column anywhere (header+grep), row count = A+B, audit_ids unique, join populates inbound_text/expected_behavior for dataset rows and flags continuations; blind-key.csv reconstructs the split exactly; key SHA256 printed.

## Phase 1 exit gate (operator review checklist — from addendum §2/§8)
- [ ] Both harnesses produced schema-valid output rows for the ~75-event window (structural check only — no quality reading)
- [ ] Zero contact-resolution errors on duplicate-name pairs in the window (cabinet spot-audit by contact_id)
- [ ] ZERO live SMS occurred (gateway sends ledger empty)
- [ ] expected_behavior leak grep: zero hits across all logs/outputs
- [ ] driver-log complete: every fired event has a row per harness (ack or error, nothing missing)
- [ ] A's saturation pauses / B's quota exhaustion windows logged as findings (if any occurred)
- [ ] Reboot recovery NOT yet demonstrated is acceptable here (P4 AT covered it; mid-week Phase-2 reboot still mandatory)
- [ ] Operator signs "GO PHASE 2" → config.phase flipped, driver rescheduled real-time, live path armed

## Run-week operator card (print this)
Machine: AC power, Sleep=Never, Windows Update paused. Emergency stop: file named `KILL` into `C:\bakeoff\killswitch\` (or `python C:\bakeoff\ctl.py kill`). Status: `python C:\bakeoff\ctl.py status`. Mid-week: one deliberate reboot, any day 3–5, just restart — touch nothing after.
