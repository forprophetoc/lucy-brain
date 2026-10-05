"""
Timed follow-up smoke (real model). Runs six scripted customer inbounds through compose() — the
exact path V4 calls — with now_et = 2026-10-05T14:10:00-04:00, and grades each decision.

Run:  HC_BACKEND=deepseek python timed_smoke.py [--runs N] [--only 1,3]
Exit code 0 only when every run passes.
"""
import argparse
import re
import sys

from hc_compose_service import compose

NOW_ET = "2026-10-05T14:10:00-04:00"  # Monday
NOW_UTC = "2026-10-05T18:10:00.000Z"
WHITELIST = {679, 449, 299, 59, 29}
PRICE_RE = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)")
FREE_RE = re.compile(r"free", re.I)  # any form: free, feel free, carefree, iso-free...

THREAD = [
    {"from": "lucy", "text": "Hi Sam, it's Lucy from Bathtub Pros! Your tub refinishing estimate is ready: "
                             "https://app.esticlose.com/estimate/bathtub-pros/sam-1005 Any questions, just text me.",
     "ts": "2026-10-05T13:40:00-04:00"},
    {"from": "customer", "text": "Thanks, looks good. How long does the job take?", "ts": "2026-10-05T13:55:00-04:00"},
    {"from": "lucy", "text": "A standard tub takes about 3-4 hours, and it's ready to use the next morning.",
     "ts": "2026-10-05T13:56:00-04:00"},
]

SCENARIOS = {
    1: "Can you reach out to me at 4pm today?",
    2: "Text me tomorrow morning, I'm slammed today",
    3: "Call me at 5",
    4: "Can Oscar call me around 5:30 so my wife can be on too?",
    5: "Hit me up next week sometime",
    6: "Is the estimate free?",
}


def _prices_ok(reply):
    bad = []
    for m in PRICE_RE.finditer(reply or ""):
        amt = round(float(m.group(1).replace(",", "")))
        if amt not in WHITELIST:
            bad.append(amt)
    return bad


def grade(n, r):
    reply, dec, at = r.get("reply") or "", r.get("send_decision"), r.get("followup_at", "")
    if n == 1:
        return dec == "send_now" and at == "2026-10-05T16:00:00-04:00", "send + 16:00 today"
    if n == 2:
        return dec == "send_now" and at == "2026-10-06T10:00:00-04:00", "send + 10:00 tomorrow"
    if n in (3, 4):
        return dec == "escalate_human" and not at, "escalate, no followup_at"
    if n == 5:
        if dec == "send_now" and re.fullmatch(r"2026-10-1[2-6]T10:00:00-04:00", at or ""):
            return True, "send + next-week weekday 10:00 (scheduled)"
        if dec == "send_now" and not at and "?" in reply:
            return True, "send + asked which day"
        return False, "send + next-week 10:00, or a reply asking which day"
    if n == 6:
        bad = _prices_ok(reply)
        ok = dec == "send_now" and not FREE_RE.search(reply) and not bad
        return ok, f"send, no 'free', no invented price{' (bad: ' + str(bad) + ')' if bad else ''}"
    raise ValueError(n)


def run_one(n):
    req = {"trigger": "inbound_reply", "now": NOW_UTC, "now_et": NOW_ET, "contact_id": f"SMOKE{n}",
           "identity": {"first_name": "Sam", "last_name": "Rivera", "city": "Naples", "service": "tub_refinish"},
           "inbound_text": SCENARIOS[n], "history": THREAD, "memory": {}}
    return compose(req)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    which = [int(x) for x in a.only.split(",") if x] or sorted(SCENARIOS)
    rows, passed = [], 0
    for run in range(1, a.runs + 1):
        for n in which:
            r = run_one(n)
            ok, expect = grade(n, r)
            passed += ok
            rows.append((run, n, ok, expect, r))
            print(f"[{'PASS' if ok else 'FAIL'}] run {run} #{n} {SCENARIOS[n]!r}\n"
                  f"    send_decision={r.get('send_decision')} followup_at={r.get('followup_at', '')!r} "
                  f"error={r.get('error')!r}\n    expect: {expect}\n    reply: {r.get('reply')!r}\n"
                  f"    reasoning: {r.get('reasoning')!r}", flush=True)
    print(f"\nSUMMARY: {passed}/{len(rows)} PASS")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
