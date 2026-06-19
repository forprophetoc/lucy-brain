"""Live-send adapter — the ONLY code path that transmits a real SMS via GHL.

Every gate must pass or it MOCKS (sent_live=False). Phone numbers never touch a
row / log / memory: we send by GHL contactId only, resolved from data/live-map.json.
Reads ONLY the GHL_API_KEY line from the .env (never loads it into os.environ, so
the harness no-key guard on ANTHROPIC_API_KEY stays intact).
"""
import json
import pathlib
import tomllib
import urllib.request
import urllib.error

from harness import run_bakeoff

BASE = pathlib.Path(__file__).parent
ENV_PATH = r"C:\Users\test\Documents\Claude\Projects\Hermes\profit\.env"
KILL_FILE = BASE / "STOP"
COUNTER = BASE / "data" / ".live_count"
GHL_MSG_URL = "https://services.leadconnectorhq.com/conversations/messages"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
SEND_DECISIONS = {"send_now"}  # escalate_human / silent / defer are NOT auto-sends


def _ghl_key():
    for line in open(ENV_PATH, encoding="utf-8"):
        s = line.strip()
        if s.startswith("GHL_API_KEY="):
            return s.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _cfg():
    return tomllib.loads((BASE / "run.toml").read_text()).get("live_send", {})


def _live_map():
    return json.loads((BASE / "data" / "live-map.json").read_text())


def _count():
    if COUNTER.exists():
        try:
            return int(COUNTER.read_text().strip() or "0")
        except ValueError:
            return 0
    return 0


def gate(contact_id, send_decision, draft):
    # Returns (allowed, ghl_contact_id|None, reasons[]). ALL must pass to transmit.
    cfg, lm = _cfg(), _live_map()
    ghl_id = lm.get(contact_id, {}).get("ghl_contact_id")
    reasons = []
    if not cfg.get("enabled"):
        reasons.append("live_send.disabled")
    if not contact_id.startswith("CONTROL_"):
        reasons.append("not_CONTROL_contact")
    if ghl_id is None:
        reasons.append("contact_not_in_live_map")
    if KILL_FILE.exists():
        reasons.append("killswitch_armed")
    if _count() >= int(cfg.get("max_live_sends", 16)):
        reasons.append("counter_exhausted")
    if send_decision not in SEND_DECISIONS:
        reasons.append(f"not_a_send:{send_decision}")
    if not (draft or "").strip():
        reasons.append("empty_draft")
    return (not reasons), ghl_id, reasons


def transmit(ghl_contact_id, message):
    body = json.dumps({"type": "SMS", "contactId": ghl_contact_id,
                       "message": message}).encode()
    req = urllib.request.Request(
        GHL_MSG_URL, data=body, method="POST",
        headers={"Authorization": f"Bearer {_ghl_key()}", "Version": "2021-07-28",
                 "Content-Type": "application/json", "Accept": "application/json",
                 "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode())


def draft_for(contact_id, text):
    # Run the seeded inbound through the REAL engine to get Lucy's draft.
    contacts = ("contact_id,first_name,last_name,phone,city,service,package,"
                "estimate_amount,tags,persona_note\n"
                f"{contact_id},Oscar,Owner,+10000000000,Naples,tub_refinish,gold,451,,n\n")
    events = ("event_id,contact_id,arc_step,event_type,scheduled_at,inbound_text,"
              "expected_behavior\n"
              f"LIVE1,{contact_id},step1,inbound_reply,2026-06-16T12:00:00-04:00,{text},x\n")
    return run_bakeoff(contacts, events, backend="claude",
                       num_smoke_test_events=1)["results"][0]["recommendation"]


def fire(contact_id="CONTROL_LIVE", text="Hi can I get an estimate on my tub?"):
    rec = draft_for(contact_id, text)
    draft = rec["suggested_customer_message"] or ""
    allowed, ghl_id, reasons = gate(contact_id, rec["send_decision"], draft)
    if not allowed:
        print(f"MOCKED sent_live=FALSE | contact={contact_id} | gate_blocked={reasons}")
        print(f"  draft would have been: {draft[:160]!r}")
        return False
    try:
        status, data = transmit(ghl_id, draft)
    except urllib.error.HTTPError as e:
        print(f"GHL ERROR {e.code}: {e.read().decode()[:200]} | sent_live=FALSE (nothing sent)")
        return False
    COUNTER.write_text(str(_count() + 1))
    print(f"sent_live=TRUE | status={status} | contact={contact_id} (ghl {ghl_id})")
    print(f"  ghl messageId={data.get('messageId')} conversationId={data.get('conversationId')}")
    print(f"  live_send_count={_count()}")
    print(f"  message sent: {draft[:200]!r}")
    return True


if __name__ == "__main__":
    import sys
    cid = sys.argv[1] if len(sys.argv) > 1 else "CONTROL_LIVE"
    fire(cid)
