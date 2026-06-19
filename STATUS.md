# Lucy / Midwife — STATUS
_Source of truth. Read first; update on evidence. GREEN only on a passing control/log — never on "done."_

## Verified (green on evidence)
- [x] Brain wired (HC -> Claude, Sonnet 4.6) — smoke test produces real drafts, not NOT_BUILT.
- [x] Gate layer — inbound->send_now; never-silent floor (empty inbound -> escalate Oscar, proven stubbed); opt-out = GHL-owned.
- [x] Audit fields — language + memory_facts_used recorded by live model.
- [x] Control suite (13 + canary) — 13/13 pass, canary FAILs. controls.py.
- [x] Live send (GHL Conversations) — single + full lane landed on phone; whitelist + cap + kill switch held.

## In progress
- [~] Crash-proof per-run log + CONTROLS-REVIEW export (verifiability).

## To build
- [ ] Inbound reply routing (GHL "Customer Replied" -> webhook -> HC).
- [ ] Brain on API key for production (flip off no-key guard; subscription is testing-only, not permitted for prod).
- [ ] Lucy memory fields in GHL.
- [ ] Snowbird due-date sweep (HC-owned; not a GHL trigger).

## Decisions locked
- Model: Sonnet 4.6 (Opus overkill; Haiku only if it passes the gauntlet).
- GHL = communicator, HC = only brain (GHL sends HC's exact text).
- Inbound = webhook; proactive = HC-owned sweep.
- Opt-out = GHL DND + natural-language opt-out -> acknowledge + flag Oscar.
- Cost: testing on subscription free/allowed; production = metered API (small at this volume).

## Risks / watch
- GHL inbound trigger reliability — text bodies exposed ({{message.body}}); fallback = poll Conversations API.
- Latency — API fixes the 13-16s cold-spawn.
- Spec duplication — Hermes/bakeoff is canonical (has harness.py); Midwife/ is a partial copy.
- Verification trust — never accept a stubbed/faked test as proof.
