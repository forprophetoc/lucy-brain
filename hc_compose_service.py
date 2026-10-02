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

Fidelity note: processes the current inbound as a single `inbound_reply` event through
the EXACT run_bakeoff path the control gauntlet validates. `history` is replayed VERBATIM
into the brain's transcript (oldest->newest) via run_bakeoff(seed_history=...) so prior
facts are recallable; the current inbound is the only scored turn. `memory` is accepted
(contract honored) but not replayed.
"""
import csv
import hmac
import io
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from harness import run_bakeoff, BRAIN_MODEL

CONTACT_COLS = ["contact_id", "first_name", "last_name", "phone", "city",
                "service", "package", "estimate_amount", "tags", "persona_note"]
EVENT_COLS = ["event_id", "contact_id", "arc_step", "event_type",
              "scheduled_at", "inbound_text", "expected_behavior", "followup_json"]


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
    # Proactive due-date sweep (TS-decided who's due; date math is NOT the brain's job).
    # A non-inbound event_type means harness skips enforce_inbound_timing's never-silent
    # floor (INBOUND_EVENT_TYPES = {"inbound_reply"}), so the brain's OWN send_decision
    # governs a proactive draft. The inbound_reply path below stays byte-equivalent.
    trigger = (req.get("trigger") or "inbound_reply").strip()
    is_sweep = trigger in ("due_date_sweep", "proactive")
    # Stage 5: thread V4's proactive follow-up context ({touch, estimate_viewed, estimate_url,
    # booking_link}) to the brain as a JSON string on the event. Sweep-only; "" for inbound.
    followup_json = json.dumps(req.get("followup")) if (is_sweep and req.get("followup")) else ""
    if is_sweep:
        event = {
            "event_id": "E_COMPOSE", "contact_id": cid, "arc_step": "step1",
            "event_type": "due_date_followup", "scheduled_at": _now_iso(req),
            "inbound_text": "", "expected_behavior": "", "followup_json": followup_json,
        }
    else:
        event = {
            "event_id": "E_COMPOSE", "contact_id": cid, "arc_step": "step1",
            "event_type": "inbound_reply", "scheduled_at": _now_iso(req),
            "inbound_text": str(req.get("inbound_text") or ""), "expected_behavior": "",
        }
    # Seam 1 — recall: replay the passed history VERBATIM into the brain's transcript
    # (oldest->newest), so prior facts (e.g. a price stated earlier) are recallable.
    # Recall comes from history ONLY, never from identity/contact fields.
    history = req.get("history") or []
    seed_history = {cid: history} if history else None
    out = run_bakeoff(_csv([contact], CONTACT_COLS), _csv([event], EVENT_COLS),
                      backend=os.environ.get("HC_BACKEND", "claude"), num_smoke_test_events=1,
                      seed_history=seed_history)
    results = out.get("results") or []
    if not results:
        return {"reply": "", "send_decision": "escalate_human", "facts": {},
                "language": "", "memory_facts_used": [], "reasoning": "",
                "error": "no result from brain"}
    rec = results[0]["recommendation"]
    reply = (rec.get("suggested_customer_message") or "").strip()
    # Never-silent floor: clean send_now-with-reply -> send_now; anything else -> escalate_human.
    escalate = bool(rec.get("escalate_oscar")) or rec.get("send_decision") != "send_now" or not reply
    # Seam 2 — scheduling: surface facts.followup_date from the brain when it resolved a
    # stated timeline; omit (empty facts) when the brain emitted none. Inference-only; no send.
    followup_date = (rec.get("followup_date") or "").strip()
    first_name = (rec.get("first_name") or "").strip()
    scope_raw = (rec.get("scope") or "").strip()
    scope = scope_raw if scope_raw in ("Tub", "Tub and Tile") else ""  # exact options only; else omit
    # Stage 5: surface the terminal disengagement signal (V4 STOPS the follow-up cadence on it).
    disengaged_raw = (rec.get("disengaged") or "").strip()
    disengaged = disengaged_raw if disengaged_raw in ("opt_out", "not_interested") else ""
    facts = {}
    if followup_date:
        facts["followup_date"] = followup_date
    if first_name:
        facts["first_name"] = first_name
    if scope:
        facts["scope"] = scope
    if disengaged:
        facts["disengaged"] = disengaged
    return {
        "reply": reply,
        "send_decision": "escalate_human" if escalate else "send_now",
        "facts": facts,
        "language": rec.get("language") or "",
        "memory_facts_used": list(rec.get("memory_facts_used") or []),
        "reasoning": rec.get("rationale") or "",
        "error": rec.get("error") or "",
    }


def _err(msg):
    return {"reply": "", "send_decision": "escalate_human", "facts": {}, "language": "",
            "memory_facts_used": [], "reasoning": "", "error": msg}


def _secret_ok(headers) -> bool:
    """Stage 5 — when HC_COMPOSE_SECRET is set, /compose requires a matching X-HC-Secret
    (constant-time compare). Unset secret -> open (local/dev default)."""
    expected = os.environ.get("HC_COMPOSE_SECRET") or ""
    if not expected:
        return True
    got = headers.get("X-HC-Secret") or ""
    return hmac.compare_digest(got, expected)


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)  # contract: compose errors ride in the body, not the status
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Health check for Render — always 200, no auth, no brain call.
        if self.path.rstrip("/") == "/health":
            self._json({"ok": True, "model": BRAIN_MODEL})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path.rstrip("/") != "/compose":
            self.send_response(404)
            self.end_headers()
            return
        if not _secret_ok(self.headers):
            self._json({"error": "unauthorized"}, status=401)
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
    backend = (os.environ.get("HC_BACKEND") or "claude").strip()
    # Conditional refusal (Stage 5): ANTHROPIC_API_KEY is only allowed in api mode. The
    # subscription brain (default) still refuses it, so a stray key can never meter the sub path.
    if os.environ.get("ANTHROPIC_API_KEY") and backend != "api":
        raise SystemExit("ANTHROPIC_API_KEY set but HC_BACKEND != 'api' — refusing (subscription-only brain).")
    host = os.environ.get("HC_HOST") or "127.0.0.1"
    port = int(os.environ.get("HC_PORT") or "8787")
    secret_on = "yes" if os.environ.get("HC_COMPOSE_SECRET") else "no"
    print(f"[HC] brain model pinned: {BRAIN_MODEL} (backend={backend})")
    print(f"[HC] /compose on http://{host}:{port}/compose + GET /health (backend={backend}, "
          f"secret={secret_on}, no-send)")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
