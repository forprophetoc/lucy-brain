#!/usr/bin/env python3
"""
baseline_scenarios.py — 20-scenario bake-off set + hard-rule grader + runner.

Every scenario goes through hc_compose_service.compose() (the production path). The checks live
here and run on the returned response; nothing from them enters the request. The grader MEASURES,
it never blocks or rewrites a reply.

Run:  py -3.14 baseline_scenarios.py <label> [reps]      (label: deepseek | muse | muse_spicy)
      env: HC_BACKEND (+ HC_VARIANT) select the brain; keys are read from the Midwife .env.
"""
import json
import os
import re
import statistics
import sys
import time

NOW_ET = "2026-10-12T14:10:00-04:00"
PHONE = "(239) 539-4777"
EST_URL = "https://app.esticlose.com/estimate/bp-20417"
BOOKING = "https://calendar.bathtubpros.com"
ENV_PATH = r"C:\Users\test\Documents\Claude\Projects\Midwife\profit\.env"
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bakeoff_results")


def _h(*pairs):
    return [{"from": f, "text": t, "ts": ts} for (f, t, ts) in pairs]


# A $449 Gold estimate on record, as V4 would replay it (estimate link + price in the thread).
EST_449 = _h(
    ("lucy", f"Hi! It's Lucy with Bathtub Pros. Your Gold estimate for your tub is ready: $449. "
             f"Here it is: {EST_URL}", "2026-10-08T10:02:00-04:00"),
)

# Price whitelist beyond the contact's own thread: approved KB amounts Lucy may state.
KB_PRICE_WHITELIST = {85}

# ---------------------------------------------------------------------------------------------
# Scenarios. `estimate` = the price on record in the thread (None = no estimate on record).
# ---------------------------------------------------------------------------------------------
SCENARIOS = [
    dict(id=1, name="New lead price ask", estimate=None, package=None, history=[],
         inbound="How much to refinish a tub?"),
    dict(id=2, name="Price recall", estimate=449, package="gold", history=EST_449,
         inbound="What's my price again?"),
    dict(id=3, name="Is the estimate free", estimate=None, package=None, history=[],
         inbound="Is the estimate free?"),
    dict(id=4, name="Timed text request", estimate=449, package="gold", history=EST_449,
         inbound="Can you text me tomorrow at 2?"),
    dict(id=5, name="Call request", estimate=449, package="gold", history=EST_449,
         inbound="Can Oscar call me?"),
    dict(id=6, name="Drain replacement", estimate=449, package="gold", history=EST_449,
         inbound="Do you replace the drain too?"),
    dict(id=7, name="Unlisted service", estimate=None, package=None, history=[],
         inbound="Do you do tile steam cleaning?"),
    dict(id=8, name="Service list", estimate=None, package=None, history=[],
         inbound="What services do you offer?"),
    dict(id=9, name="Out of area (Tampa)", estimate=None, package=None, history=[],
         inbound="Do you come out to Tampa?"),
    dict(id=10, name="In area (Port Charlotte)", estimate=None, package=None, history=[],
         inbound="I'm in Port Charlotte"),
    dict(id=11, name="Job duration", estimate=449, package="gold", history=EST_449,
         inbound="How long does a tub take?"),
    dict(id=12, name="Shower tonight", estimate=449, package="gold", history=EST_449,
         inbound="Can we shower tonight?"),
    dict(id=13, name="Veteran discount", estimate=449, package="gold", history=EST_449,
         inbound="I'm a veteran, any discount?"),
    dict(id=14, name="Warranty", estimate=449, package="gold", history=EST_449,
         inbound="What's the warranty?"),
    dict(id=15, name="Newborn safety", estimate=449, package="gold", history=EST_449,
         inbound="We have a newborn, is it safe?"),
    dict(id=16, name="Defer to January", estimate=449, package="gold", history=EST_449,
         inbound="Not ready till January"),
    dict(id=17, name="Opt-out", estimate=449, package="gold", history=EST_449,
         inbound="Stop texting me"),
    dict(id=18, name="Price pushback", estimate=449, package="gold", history=EST_449,
         inbound="That's a ripoff"),
    dict(id=19, name="Spanish price", estimate=449, package="gold",
         history=_h(("lucy", f"¡Hola! Soy Lucy de Bathtub Pros. Su presupuesto Gold para la bañera "
                             f"está listo: $449. Aquí está: {EST_URL}", "2026-10-08T10:02:00-04:00")),
         inbound="¿Cuánto cuesta?"),
    dict(id=20, name="Promised follow-up (sweep)", estimate=449, package="gold", trigger="due_date_sweep",
         history=EST_449 + _h(
             ("customer", "Thanks. I'm meeting my wife tonight, will have an answer for you after that.",
              "2026-10-09T17:40:00-04:00"),
             ("lucy", "Sounds good! I'll check back in with you Monday afternoon.",
              "2026-10-09T17:42:00-04:00")),
         inbound="",
         followup={"touch": 2, "estimate_viewed": True, "estimate_url": EST_URL, "booking_link": BOOKING}),
]


def build_request(s: dict) -> dict:
    trig = s.get("trigger", "inbound_reply")
    req = {
        "trigger": trig,
        "now_et": NOW_ET,
        "contact_id": f"BAKE{s['id']:02d}",
        "identity": {"first_name": "Sam", "last_name": "Rivera", "city": "Fort Myers",
                     "service": "tub_refinish"},
        "inbound_text": s["inbound"],
        "history": s["history"],
        "memory": {},
    }
    if s.get("followup"):
        req["followup"] = s["followup"]
    return req


# ---------------------------------------------------------------------------------------------
# Grader
# ---------------------------------------------------------------------------------------------
PHOTO_REQ_RE = re.compile(
    r"\b(send|text|share|upload|snap|attach|get|grab|take|env[ií]e|m[aá]nde)\b[^.?!]{0,40}"
    r"\b(photo|photos|picture|pictures|pic|pics|image|images|foto|fotos)\b"
    r"|\b(photo|photos|picture|pictures|pic|pics|image|images|foto|fotos)\b[^.?!]{0,30}"
    r"\b(of (the|your)|so (i|we) can|to (get|quote|start|see|confirm|give)|to get you)\b", re.I)
DOLLAR_RE = re.compile(r"\$\s?(\d[\d,]*(?:\.\d{2})?)")
RANGE_RE = re.compile(r"\b\d{3}\s*(?:-|–|to)\s*\$?\d{3}\b")
BANNED = [
    ("free", re.compile(r"free|gratis", re.I)),
    ("guarantee", re.compile(r"guarantee", re.I)),
    ("no questions asked", re.compile(r"no questions asked", re.I)),
    ("urgency", re.compile(r"spots? (are )?filling|today only|don'?t miss|act now|limited time|"
                           r"before (it'?s|they'?re) gone|book (now|today) (to|before)", re.I)),
]
# Services NOT on the approved list. A term the customer used in their own message may be echoed
# (e.g. "we don't do steam cleaning"); any other unlisted service named fails.
UNLISTED_SERVICES = [
    ("steam cleaning", r"steam"), ("tile cleaning", r"tile clean"), ("grout", r"grout"),
    ("tile replacement", r"(replace|install)\w*\s+(the\s+|new\s+)?tiles?\b|tile (replacement|install)"),
    ("cabinets", r"cabinet"), ("flooring", r"floor(ing)? (install|refinish)"), ("toilets", r"toilet (install|refinish|repair)"),
    ("vanities", r"vanit(y|ies)"), ("mold remediation", r"mold"), ("pressure washing", r"pressure wash"),
    ("pools", r"\bpools?\b"), ("remodeling", r"(full|bath(room)?|kitchen) remodel"),
    ("glass/doors", r"(shower )?(glass|door) install"), ("walk-in tubs", r"walk-in tub"),
    ("tub liners", r"liner"), ("appliances", r"appliance"),
]
NEG_RE = re.compile(r"\b(no|not|don'?t|doesn'?t|do not|never|won'?t|can'?t|cannot|unfortunately|"
                    r"aren'?t|isn'?t|only|outside|sorry)\b|\bn't\b", re.I)


def split_texts(reply: str):
    return [t.strip() for t in re.split(r"\n\s*\n", reply or "") if t.strip()]


def _amounts(text: str):
    out = set()
    for m in DOLLAR_RE.findall(text or ""):
        try:
            out.add(int(float(m.replace(",", ""))))
        except ValueError:
            pass
    return out


def _thread_text(s: dict) -> str:
    return " ".join(h["text"] for h in s.get("history") or [])


def _unlisted(reply: str, inbound: str):
    hits = []
    for name, pat in UNLISTED_SERVICES:
        rx = re.compile(pat, re.I)
        if rx.search(reply) and not rx.search(inbound):
            hits.append(name)
    return hits


def common_checks(s: dict, resp: dict) -> dict:
    reply = resp.get("reply") or ""
    allowed = _amounts(_thread_text(s)) | KB_PRICE_WHITELIST
    stated = _amounts(reply)
    texts = split_texts(reply)
    banned = [n for n, rx in BANNED if rx.search(reply)]
    unlisted = _unlisted(reply, s["inbound"])
    return {
        "price_from_record": (not stated - allowed, f"stated {sorted(stated)} allowed {sorted(allowed)}"),
        "no_banned_terms": (not banned, f"banned: {banned}" if banned else ""),
        "texts_le_320": (all(len(t) <= 320 for t in texts) and len(texts) <= 2,
                         f"{len(texts)} text(s), lengths {[len(t) for t in texts]}"),
        "no_unlisted_service": (not unlisted, f"unlisted: {unlisted}" if unlisted else ""),
    }


def _has(rx, s):
    return bool(re.search(rx, s or "", re.I))


def _drain_claim(reply: str) -> bool:
    """True when a sentence says BP removes/replaces/installs drains (without a negation)."""
    for sent in re.split(r"(?<=[.!?])\s+|\n", reply):
        if re.search(r"\b(we|we'll|we will|we can|i can|our (tech|team|crew))\b[^.?!]{0,30}"
                     r"\b(remove|replace|swap|install|change)\w*\b[^.?!]{0,30}\bdrains?\b", sent, re.I):
            if not NEG_RE.search(sent):
                return True
        if re.search(r"^\s*(yes|yep|yeah|absolutely|sure)\b", sent, re.I) and _has(r"drain", sent):
            return True
    return False


def specific_checks(s: dict, resp: dict) -> dict:
    r = resp.get("reply") or ""
    dec = resp.get("send_decision")
    facts = resp.get("facts") or {}
    fu_at = resp.get("followup_at") or ""
    sid = s["id"]
    c = {}
    if sid == 1:
        c["asks_photo_to_539"] = (bool(PHOTO_REQ_RE.search(r)) and "539-4777" in r, "")
        c["no_price_or_range"] = (not DOLLAR_RE.search(r) and not RANGE_RE.search(r), "")
    elif sid == 2:
        c["states_449"] = ("449" in r, "")
    elif sid == 3:
        c["says_no_cost_to_you"] = (_has(r"no cost to you", r), "")
        c["never_free"] = (not _has(r"free", r), "")
    elif sid == 4:
        c["send_now"] = (dec == "send_now", f"decision={dec}")
        c["followup_at_tomorrow_2pm"] = (fu_at == "2026-10-13T14:00:00-04:00", f"followup_at={fu_at!r}")
    elif sid == 5:
        c["escalate"] = (dec == "escalate_human", f"decision={dec}")
    elif sid == 6:
        c["says_no"] = (bool(NEG_RE.search(r)) and _has(r"plumber|drain", r), "")
        c["no_drain_removal_claim"] = (not _drain_claim(r), "")
    elif sid == 7:
        c["says_no"] = (bool(NEG_RE.search(r)), "")
    elif sid == 8:
        c["names_tub_service"] = (_has(r"\btubs?\b|bathtub", r), "")
    elif sid == 9:
        c["declines"] = (bool(NEG_RE.search(r)) and not _has(r"^\s*(yes|yep|absolutely|sure)\b", r), "")
    elif sid == 10:
        c["confirms_served"] = (_has(r"\b(yes|yep|absolutely|great news|good news|we (do )?(serve|cover|come|work))"
                                     r"|\b(you'?re|is) (in|within) (our|the) (service )?area", r)
                                and not _has(r"\b(don'?t|do not|doesn'?t|not) (serve|cover|come)|outside (of )?our", r), "")
    elif sid == 11:
        c["says_3_to_4_hours"] = (_has(r"\b3\s*(-|–|to)\s*4\s*h|three to four h", r), "")
    elif sid == 12:
        c["out_until_next_morning"] = (_has(r"next morning|next day|until (tomorrow|the morning)|tomorrow morning", r), "")
        c["4h_only_if_unavoidable"] = (not _has(r"4 hours|four hours", r)
                                       or _has(r"unavoidable|have to|must|at (the )?least|if you (really|absolutely)", r), "")
    elif sid == 13:
        c["offers_10pct"] = (_has(r"\b10\s?%|10 percent|ten percent", r), "")
        c["not_combined"] = (not _has(r"\b15\s?%", r)
                             and (not _has(r"\b5\s?%|senior", r)
                                  or _has(r"not both|one or the other|can'?t (be )?combin|not combin|either|only one|isn'?t combin", r)), "")
    elif sid == 14:
        c["no_years_or_terms"] = (not _has(r"\b\d+\s*[- ]?\s*(years?|yrs?)\b|\b(one|two|three|five|ten|fifteen)[- ]years?\b", r), "")
        c["no_guarantee_lifetime_nqa"] = (not _has(r"guarantee|lifetime|no questions asked", r), "")
    elif sid == 15:
        c["no_spray_with_infant"] = (_has(r"newborn|infant|baby|little one", r) and bool(NEG_RE.search(r)), "")
    elif sid == 16:
        jan = (facts.get("followup_date") or "").startswith("2027-01") or fu_at.startswith("2027-01")
        c["send_now"] = (dec == "send_now", f"decision={dec}")
        c["followup_in_january"] = (jan, f"followup_date={facts.get('followup_date')!r} followup_at={fu_at!r}")
        c["no_pressure"] = (not BANNED[3][1].search(r), "")
    elif sid == 17:
        c["no_sales_content"] = (not _has(r"\$|calendar\.|book|estimate|discount|%|schedule|deal", r), "")
        c["opt_out_flagged"] = (facts.get("disengaged") == "opt_out", f"disengaged={facts.get('disengaged')!r}")
        c["escalated_for_dnc"] = (dec == "escalate_human", f"decision={dec}")
    elif sid == 18:
        c["no_new_price"] = (_amounts(r) <= {449}, f"stated {sorted(_amounts(r))}")
        c["calm"] = (not re.search(r"\b[A-Z]{4,}\b", re.sub(r"\b(SW|USA|AI)\b", "", r))
                     and not _has(r"\d+\s?% off|discount", r), "")
    elif sid == 19:
        es = resp.get("language") == "es" or _has(r"\b(hola|su|usted|presupuesto|bañera|gracias)\b", r)
        c["spanish_reply"] = (es, f"language={resp.get('language')!r}")
        c["states_449"] = ("449" in r, "")
        c["no_photo_ask"] = (not PHOTO_REQ_RE.search(r), "")
    elif sid == 20:
        c["references_wife_answer"] = (_has(r"wife|talk(ed)? (it )?over|chat with|answer|decid|discuss", r), "")
        c["moves_toward_booking"] = (_has(r"book|schedul|calendar\.|ready|move forward|grab a (time|spot)", r), "")
        c["sends"] = (dec == "send_now", f"decision={dec}")
    return c


def grade(s: dict, resp: dict) -> dict:
    """{rule: {"pass": bool, "note": str}} plus "all_pass"."""
    checks = {**specific_checks(s, resp), **common_checks(s, resp)}
    rules = {k: {"pass": bool(v[0]), "note": v[1]} for k, v in checks.items()}
    return {"rules": rules, "all_pass": all(v["pass"] for v in rules.values())}


# ---------------------------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------------------------
def load_keys():
    """Read exactly the DEEPSEEK_API_KEY and MUSE_API_KEY lines (never printed)."""
    try:
        with open(ENV_PATH, encoding="utf-8") as fh:
            for line in fh:
                k, _, v = line.strip().partition("=")
                if k in ("DEEPSEEK_API_KEY", "MUSE_API_KEY") and v and not os.environ.get(k):
                    os.environ[k] = v.strip().strip('"').strip("'")
    except OSError:
        pass


def run(label: str, reps: int = 3) -> dict:
    import contextlib
    import io
    from hc_compose_service import compose
    rows = []
    for s in SCENARIOS:
        for rep in range(1, reps + 1):
            log = io.StringIO()
            t0 = time.perf_counter()
            with contextlib.redirect_stdout(log):
                resp = compose(build_request(s))
            latency = round(time.perf_counter() - t0, 2)
            g = grade(s, resp)
            rows.append({"scenario": s["id"], "name": s["name"], "rep": rep, "inbound": s["inbound"],
                         "response": resp, "latency_s": latency, "grade": g,
                         "log": [ln for ln in log.getvalue().splitlines() if "FAILED" in ln or "->" in ln]})
            mark = "PASS" if g["all_pass"] else "FAIL " + ",".join(k for k, v in g["rules"].items() if not v["pass"])
            print(f"[{label}] #{s['id']:>2} rep{rep} {latency:>6}s {resp.get('send_decision'):<15} {mark}", flush=True)
    out = {"label": label, "backend": os.environ.get("HC_BACKEND"), "variant": os.environ.get("HC_VARIANT") or "",
           "now_et": NOW_ET, "reps": reps, "rows": rows}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f"{label}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"\nwritten: {path}")
    summarize(out)
    return out


def summarize(out: dict) -> None:
    rows = out["rows"]
    by = {}
    for r in rows:
        by.setdefault(r["scenario"], []).append(r["grade"]["all_pass"])
    for sid, v in sorted(by.items()):
        print(f"  #{sid:>2} {sum(v)}/{len(v)}")
    lat = [r["latency_s"] for r in rows]
    print(f"TOTAL {sum(r['grade']['all_pass'] for r in rows)}/{len(rows)} runs pass; "
          f"median {statistics.median(lat)}s max {max(lat)}s")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    load_keys()
    run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)
