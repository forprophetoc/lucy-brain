#!/usr/bin/env python3
"""
hc_compose_service.py — HTTP wrapper around Lucy's brain (harness.run_bakeoff).

POST /compose
  req:  { trigger, now, contact_id,
          identity:{first_name,last_name,city,service},
          inbound_text, history:[{from,text,ts}], memory:{followup_date?} }
  resp: { reply, send_decision:"send_now"|"escalate_human", facts:{followup_date?},
          language, memory_facts_used:[], reasoning, error }

The brain runs on the `claude` CLI subscription (claude -p) via harness — NO API key
(harness guards ANTHROPIC_API_KEY). This service performs INFERENCE ONLY: it never
sends SMS, never calls GHL, never transmits. The TS orchestrator owns send/escalate and
stays DARK until Oscar flips LUCY_LIVE.

Never-silent floor preserved: an inbound that is not a clean send_now-with-reply maps to
escalate_human (never silent), matching the engine's own gate.

v1 fidelity note: processes the current inbound as a single `inbound_reply` event through
the EXACT run_bakeoff path the control gauntlet validates. `history` / `memory` are accepted
(contract honored) but not yet replayed into the brain context — documented follow-up, not
a silent drop.
"""
import csv
import io
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from harness import run_bakeoff

CONTACT_COLS = ["contact_id", "first_name", "last_name", "phone", "city",
                "service", "package", "estimate_amount", "tags", "persona_note"]
EVENT_COLS = ["event_id", "contact_id", "arc_step", "event_type",
              "scheduled_at", "inbound_text", "expected_behavior"]


def _csv(rows, cols):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in cols})
    return buf.getvalue()


def _now_iso(req):
    now = (req.get("now") or "").strip()
    if now.endswith("Z"):
        now = now[:-1] + "+00:00"  # harness uses datetime.fromisoformat
    return now or "2026-01-01T12:00:00-05:00"


def compose(req: dict) -> dict:
    ident = req.get("identity") or {}
    cid = (str(req.get("contact_id") or "").strip()) or "compose_contact"
    contact = {
        "contact_id": cid,
        "first_name": ident.get("first_name") or "",
        "last_name": ident.get("last_name") or "",
        "phone": "+1",
        "city": ident.get("city") or "",
        "service": ident.get("service") or "tub_refinish",
        "package": "", "estimate_amount": "", "tags": "", "persona_note": "",
    }
    event = {
        "event_id": "E_COMPOSE", "contact_id": cid, "arc_step": "step1",
        "event_type": "inbound_reply", "scheduled_at": _now_iso(req),
        "inbound_text": str(req.get("inbound_text") or ""), "expected_behavior": "",
    }
    out = run_bakeoff(_csv([contact], CONTACT_COLS), _csv([event], EVENT_COLS),
                      backend="claude", num_smoke_test_events=1)
    results = out.get("results") or []
    if not results:
        return {"reply": "", "send_decision": "escalate_human", "facts": {},
                "language": "", "memory_facts_used": [], "reasoning": "",
                "error": "no result from brain"}
    rec = results[0]["recommendation"]
    reply = (rec.get("suggested_customer_message") or "").strip()
    # Never-silent floor: clean send_now-with-reply -> send_now; anything else -> escalate_human.
    escalate = bool(rec.get("escalate_oscar")) or rec.get("send_decision") != "send_now" or not reply
    return {
        "reply": reply,
        "send_decision": "escalate_human" if escalate else "send_now",
        "facts": {},  # brain schema has no followup_date output yet (documented)
        "language": rec.get("language") or "",
        "memory_facts_used": list(rec.get("memory_facts_used") or []),
        "reasoning": rec.get("rationale") or "",
        "error": rec.get("error") or "",
    }


def _err(msg):
    return {"reply": "", "send_decision": "escalate_human", "facts": {}, "language": "",
            "memory_facts_used": [], "reasoning": "", "error": msg}


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)  # contract: errors ride in the body, not the HTTP status
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path.rstrip("/") != "/compose":
            self.send_response(404)
            self.end_headers()
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            req = json.loads(self.rfile.read(n) or b"{}")
            self._json(compose(req))
        except Exception as e:  # never crash the loop; surface in the error field
            self._json(_err(f"compose service error: {e}"))

    def log_message(self, *a):
        pass  # quiet


if __name__ == "__main__":
    if os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY set — refusing (subscription-only brain).")
    port = int(os.environ.get("HC_PORT") or "8787")
    print(f"[HC] /compose on http://127.0.0.1:{port}/compose (brain=claude -p, subscription, no-send)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
