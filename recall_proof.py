#!/usr/bin/env python3
"""
recall_proof.py — proves RECALL THROUGH /compose (Seam 1).

A 2-step arc:
  step1: Lucy tells the customer a price ($617). We capture her reply.
  step2: a NEW inbound ("what was my price again?") is sent through compose() with
         `history` carrying the step1 turns. The price appears ONLY in `history` —
         NOT in identity/contact fields. We assert step2's reply contains "617".

Recall must come from the passed history, not identity. Real brain (claude -p), no send.
"""
import re

from hc_compose_service import compose

PRICE = "617"  # unusual value, present ONLY in history (never in identity)


def main():
    # --- Step 1: Lucy states the price. History is empty; identity has NO amount. ---
    step1_req = {
        "trigger": "inbound_reply",
        "now": "2026-06-15T15:00:00-04:00",
        "contact_id": "RECALL_PROOF",
        "identity": {"first_name": "Pat", "last_name": "Lee", "city": "Naples",
                     "service": "tub_refinish"},
        "inbound_text": (
            f"Hi, can you confirm my quote? Oscar told me the gold package is ${PRICE} "
            f"for my tub refinish."
        ),
        "history": [],
    }
    step1 = compose(step1_req)
    lucy_turn1 = step1["reply"]

    # --- Step 2: new inbound asks to recall the price. The price lives ONLY in history. ---
    history = [
        {"from": "customer", "text": step1_req["inbound_text"],
         "ts": "2026-06-15T15:00:00-04:00"},
        {"from": "lucy", "text": lucy_turn1, "ts": "2026-06-15T15:01:00-04:00"},
    ]
    step2_req = {
        "trigger": "inbound_reply",
        "now": "2026-06-16T11:00:00-04:00",
        "contact_id": "RECALL_PROOF",
        # Identity deliberately carries NO price/amount — recall must come from history.
        "identity": {"first_name": "Pat", "last_name": "Lee", "city": "Naples",
                     "service": "tub_refinish"},
        "inbound_text": "what was my price again?",
        "history": history,
    }
    step2 = compose(step2_req)
    reply2 = step2["reply"]

    # --- Guards: price must NOT be in identity (so recall can only be from history). ---
    identity_blob = " ".join(str(v) for v in step2_req["identity"].values())
    price_in_identity = PRICE in identity_blob

    print("=" * 80)
    print("RECALL THROUGH /compose — proof")
    print("=" * 80)
    print(f"\nPRICE under test: ${PRICE} (present ONLY in history, NOT identity)")
    print(f"price_in_identity? {price_in_identity}  (must be False)")
    print("\n--- Step1 inbound:", step1_req["inbound_text"])
    print("--- Step1 Lucy reply:", repr(lucy_turn1))
    print("\n--- Step2 request.history (passed into the brain) ---")
    for h in history:
        print(f"   [{h['from']}] {h['text']!r}")
    print("\n--- Step2 inbound:", repr(step2_req["inbound_text"]))
    print("--- Step2 reply:", repr(reply2))
    print("--- Step2 memory_facts_used:", step2.get("memory_facts_used"))
    print("--- Step2 send_decision:", step2.get("send_decision"))
    print("--- Step2 error:", repr(step2.get("error")))

    recalled = PRICE in (reply2 or "")
    passed = recalled and not price_in_identity
    print("\n" + "-" * 80)
    print(f"price recalled in step2 reply? {recalled}")
    print(f"RESULT: {'PASS' if passed else 'FAIL'}")
    print("=" * 80)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
