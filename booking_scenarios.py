#!/usr/bin/env python3
"""
booking_scenarios.py — BUILD LOOP (BRAIN) Stage 2: the "let's book" reply (Oscar 2026-10-02).

Three booking scenarios — BOK1 "let's book", BOK2 "ok I'm ready, let's do it", BOK3
"Let's do the 9:30 on the 15th" (with availability). Grader: the thank-you is in the FIRST
sentence, the booking link is present, the day-before reminder + on-our-way line is mentioned,
the customer's name is used, every text is <=320 chars, and the FULL hard rule set
(spicy_exam.hard_fail_checks: prices, banned terms, invented times, ...) still passes.

Runner: `reps` runs per scenario on HC_BACKEND=muse, BOTH variants (HC_VARIANT unset = normal
Lucy, then =spicy). Every reply is printed for Oscar's voice check.

Run:  py -3.14 booking_scenarios.py booking [reps]     (env: HC_BACKEND=muse)
      py -3.14 booking_scenarios.py --regrade booking   (re-grade saved replies, no model calls)
"""
import contextlib
import io
import json
import os
import re
import statistics
import sys
import time

import baseline_scenarios as B
import fresh_scenarios as F
import hard_scenarios as H
import spicy_exam as SE

NOW_ET = H.NOW_ET
RESULTS_DIR = B.RESULTS_DIR

SCENARIOS = [
    dict(id="BOK1", first="Mia", context="Estimate $449 Silver",
         history=F.quote_thread("Mia"), inbound="let's book"),
    dict(id="BOK2", first="Dan", context="Estimate $449 Silver",
         history=F.quote_thread("Dan"), inbound="ok I'm ready, let's do it"),
    dict(id="BOK3", first="Sarah", context="Estimate $449 Silver; the 9:30 on the 15th IS in availability",
         history=F.quote_thread("Sarah"), inbound="Let's do the 9:30 on the 15th",
         availability=[{"label": "Thu Oct 15, 9:30 AM", "start_iso": "2026-10-15T09:30:00-04:00"}]),
]
BY_ID = {s["id"]: s for s in SCENARIOS}


def build_request(s: dict) -> dict:
    req = {
        "trigger": "inbound_reply", "now_et": NOW_ET, "contact_id": f"BOOK{s['id']}",
        "identity": {"first_name": s["first"], "last_name": "Test", "city": "Naples",
                     "service": "tub_refinish"},
        "inbound_text": s["inbound"], "history": s["history"], "memory": {},
    }
    if s.get("availability"):
        req["availability"] = s["availability"]
    return req


# ---------------------------------------------------------------------------------------------
# Grader
# ---------------------------------------------------------------------------------------------
THANK_RE = re.compile(r"thank|appreciat", re.I)
REMINDER_RE = re.compile(r"remind", re.I)
ON_OUR_WAY_RE = re.compile(r"on (our|the) way", re.I)


def _opening_sentence(r: str) -> str:
    """Sentence that must carry the thank-you. A one-word opener ("Excellent!") is an
    interjection, not the first sentence — the rule is about the first real sentence."""
    sents = H._sentences(r) or [""]
    if not THANK_RE.search(sents[0]) and len(sents) > 1 and len(sents[0]) <= 15:
        return sents[1]
    return sents[0]


def booking_checks(s: dict, resp: dict) -> dict:
    raw = resp.get("reply") or ""
    r = H.URL_RE.sub(" ", raw)
    first = _opening_sentence(r)
    name = re.escape(s["first"])
    c = {
        "thank_you_first": (bool(THANK_RE.search(first)), f"opening sentence: {first[:70]!r}"),
        "booking_link": (bool(F.BOOK_LINK_RE.search(raw)), "no calendar link in reply"),
        "reminder_promised": (bool(REMINDER_RE.search(r)), "no day-before reminder mention"),
        "on_our_way_promised": (bool(ON_OUR_WAY_RE.search(r)), "no on-our-way mention"),
        "name_used": (bool(re.search(rf"\b{name}\b", r, re.I)), f"{s['first']} not in reply"),
    }
    return c


def grade(s: dict, resp: dict) -> dict:
    rules = {k: {"pass": bool(v[0]), "note": v[1], "kind": "booking"} for k, v in booking_checks(s, resp).items()}
    hard = SE.hard_fail_checks(s, resp)
    for k, v in hard.items():
        if k in rules:
            k = f"{k}_hard"
        rules[k] = {"pass": bool(v[0]), "note": v[1], "kind": "hard"}
    hard_fails = [k for k, v in rules.items() if v["kind"] == "hard" and not v["pass"]]
    return {"rules": rules, "all_pass": all(v["pass"] for v in rules.values()), "hard_fails": hard_fails}


# ---------------------------------------------------------------------------------------------
# Runner — reps per scenario, BOTH variants in one process (HC_VARIANT is read per request).
# ---------------------------------------------------------------------------------------------
def run(label: str, reps: int = 3) -> dict:
    if (os.environ.get("HC_BACKEND") or "").strip() != "muse":
        raise SystemExit("booking scenarios need HC_BACKEND=muse — HOLD")
    from hc_compose_service import compose
    rows = []
    for variant in ("regular", "spicy"):
        if variant == "spicy":
            os.environ["HC_VARIANT"] = "spicy"
        else:
            os.environ.pop("HC_VARIANT", None)
        for s in SCENARIOS:
            req = build_request(s)
            for rep in range(1, reps + 1):
                log = io.StringIO()
                t0 = time.perf_counter()
                with contextlib.redirect_stdout(log):
                    resp = compose(dict(req))
                latency = round(time.perf_counter() - t0, 2)
                g = grade(s, resp)
                rows.append({"key": s["id"], "variant": variant, "rep": rep, "inbound": s["inbound"],
                             "response": resp, "latency_s": latency, "grade": g,
                             "log": [ln for ln in log.getvalue().splitlines() if "FAILED" in ln or "->" in ln]})
                mark = "PASS" if g["all_pass"] else "FAIL " + ",".join(k for k, v in g["rules"].items() if not v["pass"])
                print(f"[{label}] {variant:>7} {s['id']} rep{rep} {latency:>6}s "
                      f"{resp.get('send_decision'):<15} {mark}", flush=True)
                print(f"  REPLY: {resp.get('reply')!r}", flush=True)
                _save(label, reps, rows)
    lat = [r["latency_s"] for r in rows]
    print(f"\nTOTAL {sum(r['grade']['all_pass'] for r in rows)}/{len(rows)} runs pass; "
          f"median {statistics.median(lat)}s max {max(lat)}s")
    return {"rows": rows}


def _save(label, reps, rows):
    out = {"label": label, "backend": os.environ.get("HC_BACKEND"),
           "variant": "both", "now_et": NOW_ET, "reps": reps, "rows": rows}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, f"{label}.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)


def regrade(label: str) -> None:
    """Re-grade saved replies after a grader fix — no model calls."""
    path = os.path.join(RESULTS_DIR, f"{label}.json")
    with open(path, encoding="utf-8") as fh:
        out = json.load(fh)
    for r in out["rows"]:
        r["grade"] = grade(BY_ID[r["key"]], r["response"])
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"{label}: {sum(r['grade']['all_pass'] for r in out['rows'])}/{len(out['rows'])} runs pass")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    B.load_keys()
    if len(sys.argv) > 1 and sys.argv[1] == "--regrade":
        for lbl in sys.argv[2:]:
            regrade(lbl)
        sys.exit(0)
    run(sys.argv[1] if len(sys.argv) > 1 else "booking", int(sys.argv[2]) if len(sys.argv) > 2 else 3)
