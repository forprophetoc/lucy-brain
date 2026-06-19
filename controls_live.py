"""controls_live.py — LIVE control-lane runner.

Runs the EXACT control suite from controls.py through the real engine, scores each
control the same way, and then — on each control's asserting event only — fires a
real SMS via the proven live_send adapter IFF the decision is a send (send_now),
the contact is a CONTROL_ contact, and every live_send gate passes.

controls.py stays a pure checker (no send path). This runner is the live wrapper.

Safety:
  * Transmission requires run.toml [live_send].enabled = true AND killswitch disarmed.
  * Cap enforced by live_send.gate via data/.live_count (shared, persistent).
  * HARD HALT (stop the whole run) on a GHL error OR any non-CONTROL_ send attempt.
  * Phone numbers never appear: we send by GHL contactId only. No number is logged.
  * Durable audit trail: one JSONL line per control is appended to
    data/live-send-log.jsonl AS the run progresses (and a successful send is logged
    the instant transmit() returns), so a later crash can never lose the record of
    what was actually sent. The message body is logged; no phone number ever is.

Run:  python controls_live.py     (ANTHROPIC_API_KEY must be unset — harness guards it)
"""
import sys
import json
import time
import urllib.error
from datetime import datetime

# Windows consoles default to cp1252; model drafts (and our glyphs) can contain
# characters it can't encode -> force UTF-8 so printing the report never crashes.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from harness import run_bakeoff
from controls import CONTROLS, CONTACT_COLS, EVENT_COLS, _to_csv
import live_send


LOG_PATH = live_send.COUNTER.parent / "live-send-log.jsonl"  # data/live-send-log.jsonl


def _log(record):
    # Append one JSON line and flush immediately — durable against a later crash.
    # ensure_ascii=False keeps message text readable; never contains a phone number.
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()


def _run_engine():
    contacts, events = [], []
    for c in CONTROLS:
        contacts.extend(c["contacts"])
        events.extend(c["events"])
    out = run_bakeoff(_to_csv(contacts, CONTACT_COLS), _to_csv(events, EVENT_COLS),
                      backend="claude", num_smoke_test_events=len(events))
    return {r["event_id"]: r for r in out["results"]}


def run_live():
    rows = _run_engine()
    report = []          # (control_id, passed, sent_live, decision, draft, note)
    halted = None

    run_id = datetime.now().strftime("%Y%m%dT%H%M%S")
    _log({"run_id": run_id, "event": "run_start", "ts": time.time(),
          "enabled": live_send._cfg().get("enabled"),
          "killswitch_armed": live_send.KILL_FILE.exists(),
          "count_start": live_send._count(),
          "cap": live_send._cfg().get("max_live_sends", 16)})

    for c in CONTROLS:
        cid = c["control_id"]
        # Per-control audit record, written durably in `finally` (or earlier on a
        # successful send). Whatever happens to this iteration, one line is recorded.
        rec_log = {"run_id": run_id, "event": "control", "ts": time.time(),
                   "control_id": cid, "sent_live": False, "_written": False}
        try:
            row = rows.get(c["assert_event"])
            if row is None:
                note = f"NO RESULT for {c['assert_event']}"
                rec_log.update(decision="-", passed=False, note=note)
                report.append((cid, False, False, "—", "", note))
                continue

            rec = row["recommendation"]
            contact_id = row["contact_id"]
            decision = rec["send_decision"]
            draft = rec["suggested_customer_message"] or ""
            rec_log.update(contact_id=contact_id, decision=decision, message=draft)

            # --- score exactly as the checker does ---------------------------
            try:
                passed = bool(c["assert_fn"](rec))
                evidence = c["evidence_fn"](rec)
            except Exception as e:
                passed, evidence = False, f"assert error: {e}"
            rec_log["passed"] = passed

            # --- live send on the asserting event ----------------------------
            sent_live, note = False, evidence
            is_send = decision in live_send.SEND_DECISIONS  # {"send_now"}

            if halted:
                note = f"{evidence} | SKIPPED (run halted)"
            elif not is_send:
                note = f"{evidence} | dark (decision={decision!r})"
            else:
                # Tripwire: a send decision from a non-CONTROL_ contact must HALT.
                if not contact_id.startswith("CONTROL_"):
                    halted = f"non-CONTROL_ send attempt: {contact_id}"
                    note = f"{evidence} | HALT — {halted}"
                    rec_log.update(note=note, halt=halted)
                    report.append((cid, passed, False, decision, draft, note))
                    break
                allowed, ghl_id, reasons = live_send.gate(contact_id, decision, draft)
                if not allowed:
                    note = f"{evidence} | gate_blocked={reasons}"
                    rec_log["gate_reasons"] = reasons
                else:
                    try:
                        status, data = live_send.transmit(ghl_id, draft)
                    except (urllib.error.HTTPError, urllib.error.URLError) as e:
                        code = getattr(e, "code", "URLERR")
                        halted = f"GHL error {code} on {cid}"
                        note = f"{evidence} | HALT — GHL error {code} (nothing sent for this control)"
                        rec_log.update(note=note, halt=halted, ghl_error=str(code))
                        report.append((cid, passed, False, decision, draft, note))
                        break
                    # SENT. Record it durably NOW, before touching anything else, so a
                    # crash can never leave a sent text unlogged. Then bump the counter.
                    sent_live = True
                    note = (f"{evidence} | status={status} "
                            f"msgId={data.get('messageId')} count={live_send._count() + 1}")
                    rec_log.update(sent_live=True, ghl_status=status, note=note,
                                   ghl_message_id=data.get("messageId"),
                                   ghl_conversation_id=data.get("conversationId"),
                                   count_after=live_send._count() + 1, _written=True)
                    _log(rec_log)
                    live_send.COUNTER.write_text(str(live_send._count() + 1))

            rec_log.setdefault("note", note)
            report.append((cid, passed, sent_live, decision, draft, note))
        finally:
            # Exactly one durable line per control: the successful-send path already
            # wrote (_written=True); every other path (dark, blocked, no-result, halt,
            # or an unexpected exception) gets recorded here.
            if not rec_log.get("_written"):
                rec_log["_written"] = True
                _log(rec_log)

    _log({"run_id": run_id, "event": "run_end", "ts": time.time(),
          "sent_this_run": sum(1 for r in report if r[2]),
          "count_end": live_send._count(), "halt": halted})
    return report, halted


def print_report(report, halted):
    print("\n" + "=" * 120)
    print("LUCY CONTROL LANE — LIVE")
    print("=" * 120)
    print(f"{'control_id':<34} | {'CHK':<4} | {'SENT_LIVE':<9} | {'decision':<12} | message")
    print("-" * 120)
    real = [r for r in report if "deliberate" not in r[0]]
    for cid, passed, sent_live, decision, draft, note in report:
        chk = "PASS" if passed else "FAIL"
        msg = (draft or "").replace("\n", " ").strip()
        print(f"{cid:<34} | {chk:<4} | {str(sent_live).upper():<9} | {decision[:12]:<12} | {msg[:120]!r}")
        print(f"{'':<34} | {'':<4} | {'':<9} | {'':<12} | -> {note}")
    print("-" * 120)

    real_pass = sum(1 for r in real if r[1])
    sent_total = sum(1 for r in report if r[2])
    canary = next((r for r in report if "deliberate" in r[0]), None)

    print(f"Real controls: {real_pass}/{len(real)} passed.")
    if canary is not None:
        print(f"Canary (must FAIL): {'OK — checker bites' if canary[1] is False else 'BROKEN — canary passed!'}"
              f"  (sent_live={str(canary[2]).upper()})")
    print(f"Total LIVE texts sent this run: {sent_total}  |  persistent count={live_send._count()}/"
          f"{live_send._cfg().get('max_live_sends', 16)}")
    print(f"Killswitch: {'ARMED' if live_send.KILL_FILE.exists() else 'DISARMED'}  |  "
          f"live_send.enabled={live_send._cfg().get('enabled')}")
    print(f"HALT: {halted if halted else 'none'}")
    print("=" * 120)


if __name__ == "__main__":
    rep, halt = run_live()
    print_report(rep, halt)
