#!/usr/bin/env python3
"""
schedule_proof.py — proves SCHEDULING THROUGH /compose (Seam 2).

An inbound stating a timeline ("ready in January") is sent through compose() with a
known `now` (mid-June 2026). We assert the brain emits facts.followup_date as a
canonical YYYY-MM-DD that lands in January (of the next occurrence, 2027-01).

Real brain (claude -p), inference-only, no send.
"""
import re

from hc_compose_service import compose

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def main():
    now = "2026-06-21T10:00:00-04:00"  # known anchor; January is the NEXT January (2027-01)
    inbound = "We won't be ready until January — can you reach back out to me then?"

    req = {
        "trigger": "inbound_reply",
        "now": now,
        "contact_id": "SCHED_PROOF",
        "identity": {"first_name": "Pat", "last_name": "Lee", "city": "Naples",
                     "service": "tub_refinish"},
        "inbound_text": inbound,
        "history": [],
    }
    resp = compose(req)
    facts = resp.get("facts") or {}
    fud = facts.get("followup_date", "")

    print("=" * 80)
    print("SCHEDULING THROUGH /compose — proof")
    print("=" * 80)
    print(f"\nnow:     {now}")
    print(f"inbound: {inbound!r}")
    print(f"\nfacts:        {facts}")
    print(f"reply:        {resp.get('reply')!r}")
    print(f"send_decision:{resp.get('send_decision')!r}")
    print(f"error:        {resp.get('error')!r}")

    well_formed = bool(DATE_RE.match(fud or ""))
    in_january = well_formed and fud[5:7] == "01"
    passed = well_formed and in_january

    print("\n" + "-" * 80)
    print(f"followup_date: {fud!r}")
    print(f"matches /^\\d{{4}}-\\d{{2}}-\\d{{2}}$/? {well_formed}")
    print(f"lands in January (month == 01)?       {in_january}")
    print(f"RESULT: {'PASS' if passed else 'FAIL'}")
    print("=" * 80)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
