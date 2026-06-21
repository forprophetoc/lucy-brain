#!/usr/bin/env python3
"""
sweep_proof.py — proves the PROACTIVE due-date sweep through /compose.

The daily sweep wakes the brain for a contact whose follow-up date is DUE (the date math
is deterministic CODE on the TS side — see the vitest test lucyDueDateSweep.test.ts; the
due/not-due SKIP is proven there, NOT here). This proof exercises the BRAIN half: given a
due contact and the remembered timeline in `history`, does the brain draft a grounded
re-engagement that USES that timeline?

  DUE contact: history says the customer will be ready "in January"; now = a January date
  (so they are due). compose(trigger="due_date_sweep") must return a NON-EMPTY customer
  message that references the January / ready timeline, with a usable send_decision.

  CONTROL: a contact with NO timeline and no due context — the brain must NOT invent a
  follow-up date (facts.followup_date stays empty). Sanity that proactive ≠ hallucinate.

Real brain (claude -p subscription), inference-only, no send, no GHL, no network mutation.
"""
import re

from hc_compose_service import compose

JAN_NOW = "2027-01-10T10:00:00-05:00"  # a January date — the remembered "January" is now due
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _mentions_timeline(text: str) -> bool:
    t = (text or "").lower()
    return ("january" in t) or ("jan" in t) or ("ready" in t) or ("new year" in t)


def main():
    print("=" * 80)
    print("PROACTIVE DUE-DATE SWEEP THROUGH /compose — proof")
    print("=" * 80)
    print("NOTE: the due/not-due SKIP is proven deterministically in the TS test")
    print("      (server/_core/lucyDueDateSweep.test.ts). This proves the BRAIN draft.\n")

    # --- DUE contact: the remembered timeline lives ONLY in history. ---
    history = [
        {"from": "customer",
         "text": "We're snowbirds — we won't be ready until January when we're back. Reach out then?",
         "ts": "2026-11-15T14:00:00-05:00"},
        {"from": "lucy",
         "text": "Absolutely — I'll circle back in January when you're settled. Talk then!",
         "ts": "2026-11-15T14:02:00-05:00"},
    ]
    due_req = {
        "trigger": "due_date_sweep",
        "now": JAN_NOW,
        "contact_id": "SWEEP_DUE",
        "identity": {"first_name": "Pat", "last_name": "Lee", "city": "Naples",
                     "service": "tub_refinish"},
        "inbound_text": "",  # proactive — no customer message
        "history": history,
    }
    due = compose(due_req)
    reply = due.get("reply") or ""

    print("--- DUE contact ---")
    print(f"now:           {JAN_NOW}  (the remembered 'January' is now due)")
    print("history (the remembered timeline, passed into the brain):")
    for h in history:
        print(f"   [{h['from']}] {h['text']!r}")
    print(f"inbound_text:  {due_req['inbound_text']!r}  (empty — proactive)")
    print(f"\nreply:         {reply!r}")
    print(f"send_decision: {due.get('send_decision')!r}")
    print(f"facts:         {due.get('facts')}")
    print(f"memory_facts:  {due.get('memory_facts_used')}")
    print(f"error:         {due.get('error')!r}")

    non_empty = bool(reply.strip())
    grounded = _mentions_timeline(reply)
    decision_usable = due.get("send_decision") in ("send_now", "escalate_human")
    due_pass = non_empty and grounded and decision_usable and not due.get("error")

    print(f"\nnon-empty re-engagement?            {non_empty}")
    print(f"references the January/ready timeline? {grounded}")
    print(f"send_decision usable?               {decision_usable}")

    # --- CONTROL: no timeline, no due context — must NOT invent a date. ---
    ctrl_req = {
        "trigger": "due_date_sweep",
        "now": JAN_NOW,
        "contact_id": "SWEEP_CTRL",
        "identity": {"first_name": "Sam", "last_name": "Roe", "city": "Naples",
                     "service": "tub_refinish"},
        "inbound_text": "",
        "history": [
            {"from": "customer", "text": "Thanks for the quote, I'll think about it.",
             "ts": "2026-12-01T09:00:00-05:00"},
            {"from": "lucy", "text": "Of course — here whenever you're ready.",
             "ts": "2026-12-01T09:01:00-05:00"},
        ],
    }
    ctrl = compose(ctrl_req)
    ctrl_fud = (ctrl.get("facts") or {}).get("followup_date", "")
    ctrl_no_invented_date = (ctrl_fud == "")

    print("\n--- CONTROL contact (no stated timeline) ---")
    print(f"reply:         {ctrl.get('reply')!r}")
    print(f"send_decision: {ctrl.get('send_decision')!r}")
    print(f"facts:         {ctrl.get('facts')}")
    print(f"error:         {ctrl.get('error')!r}")
    print(f"\nno invented follow-up date? {ctrl_no_invented_date}  (facts.followup_date={ctrl_fud!r})")

    passed = due_pass and ctrl_no_invented_date
    print("\n" + "-" * 80)
    print(f"DUE re-engagement grounded in timeline? {due_pass}")
    print(f"CONTROL did not invent a date?          {ctrl_no_invented_date}")
    print(f"RESULT: {'PASS' if passed else 'FAIL'}")
    print("=" * 80)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
