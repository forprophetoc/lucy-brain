#!/usr/bin/env python3
"""
spicy_exam.py — final Spicy exam: every scenario ever asked (baseline 20, hard 20, fresh 23, closing 14),
exact repeats removed, one grader, Muse Spicy only.

One principle for every scenario: PASS = correct answer + right closing behavior. A reply never fails for
omitting a detail the customer didn't ask for. Every check is one of three kinds:
  hard     — HARD FAIL, always (invented price/service/policy/availability/time, discount other than vet 10% /
             senior 5%, price match, fault, refund/repair/compensation or any promise Lucy can't keep, Gold
             inclusions promised to Silver, claiming to be human, internal tool names, knocking competitors,
             free/guarantee/lifetime or yes to lifetime, online payment or checks, spraying with an infant /
             dogs outside, drain work, >320 chars per text, more than one booking step);
  correct  — the scenario's correct answer (each kept check is something the customer asked or a playbook
             rule for that situation);
  closing  — close: ends with ONE booking step (link or scheduling question) and is sent, not escalated;
             quiet: no booking link and no scheduling question; photo: no estimate on record — no booking
             link, and the photo-to-539 request is the close; any: closing not graded (listed in the report).

Run:  py -3.14 spicy_exam.py spicy_final [reps] [--only=B8,H9,...]   (env: HC_BACKEND=muse HC_VARIANT=spicy)
      py -3.14 spicy_exam.py --regrade spicy_final   (re-grade saved replies, no model calls)
"""
import contextlib
import io
import json
import os
import re
import statistics
import sys
import time
from decimal import Decimal

import baseline_scenarios as B
import closing_scenarios as C
import fresh_scenarios as F
import hard_scenarios as H

RESULTS_DIR = H.RESULTS_DIR
_has = H._has
_neg_free_hit = H._neg_free_hit

# ---------------------------------------------------------------------------------------------
# Scenario plan: (key, source scenario, request builder, closing class)
# ---------------------------------------------------------------------------------------------
CLASS = {
    # baseline
    "B1": "photo", "B2": "close", "B3": "photo", "B4": "quiet", "B5": "quiet", "B6": "close", "B7": "quiet",
    "B8": "photo", "B9": "quiet", "B10": "photo", "B11": "close", "B12": "any", "B13": "close", "B14": "close",
    "B15": "close", "B16": "quiet", "B17": "quiet", "B18": "any", "B19": "close", "B20": "close",
    # hard
    "H1": "quiet", "H2": "quiet", "H3": "quiet", "H4": "quiet", "H5": "quiet", "H6": "quiet", "H7": "quiet",
    "H8": "quiet", "H9": "close", "H10": "any", "H11": "photo", "H12": "quiet", "H13": "photo", "H14": "quiet",
    "H15": "photo", "H16": "close", "H17": "quiet", "H18": "photo", "H19": "close", "H20": "quiet",
    # fresh
    "F1": "close", "F2": "close", "F3": "quiet", "F4": "close", "F5": "quiet", "F6": "photo", "F7": "quiet",
    "F8": "close", "F9": "close", "F10": "close", "F11": "quiet", "F12": "close", "F13": "quiet", "F14": "quiet",
    "F15": "close", "F16": "photo", "F17": "quiet", "F18": "photo", "F19": "quiet", "F20": "close", "F21": "close",
    "F22": "any", "F23": "close",
    # closing (unique ones; the rest are exact repeats, see ALIASES)
    "C7": "close", "C8": "close", "N4": "quiet",
}
# Why a scenario is quiet/any when it might look like a close (shown in the report).
CLASS_WHY = {
    "B4": "timed text request — confirm + followup_at", "B5": "call request — hand to Oscar",
    "B7": "unlisted service, no estimate — decline", "B9": "out of area — decline", "B16": "defer to January",
    "B12": "aftercare question — correct answer passes, booking step optional (Oscar 2026-10-12)",
    "B17": "opt-out", "B18": "\"That's a ripoff\" — angry; resolved or not is a judgment call",
    "H1": "complaint", "H2": "warranty problem on a past job", "H3": "refund demand", "H4": "review threat",
    "H5": "complaint about repeat texts", "H6": "identity question, no estimate (photo ask optional)",
    "H7": "wants a human", "H8": "price match — \"Let me get Oscar on that for you\"",
    "H10": "neighbor's $199 — not an explicit match request; hold price", "H12": "no estimate on record (photo optional)",
    "H14": "no estimate on record (photo optional)", "H17": "complaint, wants owner", "H20": "property manager — hand to Oscar",
    "F3": "already booked", "F5": "already booked", "F7": "no estimate on record (photo optional)",
    "F11": "service failure", "F13": "asks to go lower — hold price, hand to Oscar", "F14": "wrong number",
    "F17": "just sent the link — 👍", "F19": "grief", "F22": "\"bait and switch\" — angry; judgment call",
    "N4": "said stop",
}
# Exact repeats (same history + inbound) kept once.
ALIASES = {"F20": ["C1"], "F8": ["C2"], "F13": ["C3"], "F21": ["C4"], "H8": ["C5"], "F15": ["C6"], "F9": ["C9"],
           "F12": ["C10"], "F19": ["N1"], "H1": ["N2"], "F11": ["N3"]}
# No-estimate scenarios where the photo ask is the expected close (CLASS "photo").
PHOTO_REQUIRED = {k for k, v in CLASS.items() if v == "photo"}

# Existing scenario checks NOT kept (the closing class replaces them, or they required an unasked detail,
# or they encode the pre-2026-10-12 caulk fact).
DROP = {
    "B17": {"escalated_for_dnc"},  # Oscar 2026-10-12: GHL handles STOP
    "B20": {"moves_toward_booking"},
    "F1": {"booking_link_or_real_availability"}, "F2": {"booking_link"},
    "F4": {"says_yes", "old_removed_and_replaced", "no_caulk_charge_claimed"},
    "F8": {"toward_booking"}, "F17": {"no_repeated_pitch"}, "F20": {"booking_link_or_sched_question"},
}


def plan():
    out = []
    for s in B.SCENARIOS:
        out.append((f"B{s['id']}", "baseline", s, B.build_request))
    for s in H.SCENARIOS:
        out.append((f"H{s['id']}", "hard", s, H.build_request))
    for s in F.SCENARIOS:
        out.append((f"F{s['id']}", "fresh", s, F.build_request))
    for s in C.SCENARIOS:
        if s["id"] in CLASS:
            out.append((s["id"], "closing", s, C.build_request))
    return out


def duplicates():
    """Exact repeats across all four sets: [(kept key, [repeat keys])] — computed, so ALIASES is checked."""
    seen, dups = {}, {}
    allc = ([(f"B{s['id']}", s) for s in B.SCENARIOS] + [(f"H{s['id']}", s) for s in H.SCENARIOS]
            + [(f"F{s['id']}", s) for s in F.SCENARIOS] + [(s["id"], s) for s in C.SCENARIOS])
    for k, s in allc:
        sig = (s["inbound"], json.dumps(s["history"], sort_keys=True), s.get("trigger", "inbound_reply"))
        if sig in seen:
            dups.setdefault(seen[sig], []).append(k)
        else:
            seen[sig] = k
    return dups


# ---------------------------------------------------------------------------------------------
# Grader
# ---------------------------------------------------------------------------------------------
BOOK_LINK_RE = F.BOOK_LINK_RE
SCHED_QUESTION_RE = F.SCHED_QUESTION_RE
CANT_KEEP_RE = re.compile(
    r"\b(update|revise|redo|adjust|lower|change|rework)\b[^.?!]{0,15}\b(your|the|that) (estimate|quote|price)\b|"
    r"\b(send|get) you a (new|revised|updated|lower) (estimate|quote|price)\b|"
    r"\bprice[- ]match|\bmatch (it|that|this|their|his|her|the) ?(price|quote|rate|offer)?\b|"
    r"\bhonou?r (it|that|this|their|his|her|the|a|any) ?(price|quote|rate|offer)?\b|"
    r"\bbeat (that|their|his|the) (price|quote)\b", re.I)
# Promising contact with the tech: allowed only when Lucy escalates to Oscar (Oscar 2026-10-12, tech late / no-show).
TECH_CONTACT_RE = re.compile(
    r"\b(i'?ll|i will|let me|i can|i'?m going to)\b[^.?!]{0,20}\b(contact|call|text|reach|ask|talk to|speak (to|with)|"
    r"check with)\b[^.?!]{0,10}\b(the|our|your) (tech|technician|crew|installer|guy)\b|"
    r"\b(get|have) (the|our) (tech|technician)\b[^.?!]{0,20}\b(reach|call|text|contact)", re.I)
DISCOUNT_OFFER_RE = re.compile(
    r"\b(i|we) (can|could|will|'?ll) (offer|give|do|take|knock)\b[^.?!]{0,25}\b(discount|% off|off the (price|total)|"
    r"less|lower|deal|break)\b|\bspecial (price|pricing|deal|offer)\b", re.I)
AVAIL_CLAIM_RE = re.compile(
    r"\b(i|we) can (get you in|fit you in|come out|squeeze you in)\b[^.?!]{0,25}\b(this|next) week\b|"
    r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow)\b[^.?!]{0,20}\b(is|looks|'s) "
    r"(open|available|wide open|free)\b|\bwe have (an )?(opening|openings|availability|a spot|spots)\b"
    r"[^.?!]{0,15}\b(on|this|next|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.I)
GOLD_INCL_RE = re.compile(
    r"\bfill(s|ing|ed)?\b[^.?!]{0,35}\b(nicks?|chips?|screw ?holes?|holes)\b|"
    r"\b(replace|replaces|replacing|redo|redoes|new|remove|removes|removing)\b[^.?!]{0,25}\bcaulk|"
    r"\bcaulk\w*\b[^.?!]{0,30}\b(replaced|included|redone|is part of)\b", re.I)
GOLD_WORD_RE = re.compile(r"\b(gold|platinum)\b", re.I)
INFANT_RE = re.compile(r"infant|newborn|\bbaby\b|month[- ]old", re.I)
# Baseline photo-ask pattern + informal Spanish ("mándame / mándanos / envíame una foto"), which it missed.
PHOTO_REQ_RE = re.compile(B.PHOTO_REQ_RE.pattern + r"|\b(m[aá]nd[ae]|env[ií][ae])(me|nos)\b[^.?!]{0,30}\bfotos?\b",
                          re.I)
ONLINE_PRICE_RE = re.compile(r"on ?line|website|web site|\bsite\b|\bad\b|advertis|página|anuncio", re.I)
URGENCY_RE = B.BANNED[3][1]


def _sched_questions(text):
    return sum(1 for s in H._sentences(text) if SCHED_QUESTION_RE.search(s))


def booking_steps(raw: str) -> int:
    return len(BOOK_LINK_RE.findall(raw)) + _sched_questions(H.URL_RE.sub(" ", raw))


def _last_sentence(raw: str) -> str:
    sents = H._sentences(raw.strip())
    return sents[-1] if sents else ""


def ends_with_step(raw: str) -> bool:
    """The reply ENDS with the booking link (only punctuation/emoji after it) or with a scheduling question."""
    links = list(re.finditer(r"https?://\S*calendar\.bathtubpros\.com\S*", raw))
    if links and not re.search(r"[A-Za-z0-9]", raw[links[-1].end():]):
        return True
    last = _last_sentence(H.URL_RE.sub(" ", raw))
    return bool(SCHED_QUESTION_RE.search(last))


def _package(s) -> str:
    t = " ".join(h["text"] for h in s["history"]).lower()
    return "gold" if ("gold" in t or "platinum" in t) else ("silver" if "silver" in t else "")


def gold_to_silver(s, r) -> str:
    """A Gold inclusion (fill nicks/chips/screw holes, replace old caulk) stated as ours, outside a Gold job and
    not tied to Gold in the same sentence. Returns the offending sentence, or ''."""
    if _package(s) == "gold":
        return ""
    for sent in H._sentences(r):
        if GOLD_INCL_RE.search(sent) and not GOLD_WORD_RE.search(sent) and not H.NEG_RE.search(sent):
            return sent
    return ""


def hard_fail_checks(s: dict, resp: dict) -> dict:
    raw = resp.get("reply") or ""
    r = H.URL_RE.sub(" ", raw)
    hc = H.hard_checks(s, resp)
    unl = B._unlisted(r, s["inbound"])
    g2s = gold_to_silver(s, r)
    asked_lifetime = _has(r"lifetime", s["inbound"])
    first = (H._sentences(r) or [""])[0]
    infant = bool(INFANT_RE.search(s["inbound"]))
    # $299 is the KB's advertised starting price: Lucy may acknowledge it to a contact WITH an estimate on record
    # who raises the online/ad/website price, even without typing the figure (KB pricing section).
    allowed = H.allowed_prices(s)
    if H.prices_in(" ".join(h["text"] for h in s["history"])) and ONLINE_PRICE_RE.search(s["inbound"]):
        allowed = allowed | {Decimal(299)}
    bad = sorted(str(p) for p in H.prices_in(r) - allowed)
    hc = {**hc, "no_invented_price": (not bad, f"unapproved: {bad}" if bad else "")}
    c = {k: hc[k] for k in ("no_invented_price", "no_fault_admission", "no_refund_repair_promise",
                            "never_claims_human", "no_internal_tools", "no_knocking_competitors",
                            "no_free_guarantee_lifetime", "texts_le_320", "no_online_or_check_payment")}
    # A time the customer named themselves ("text me tomorrow at 2" -> "I'll text you tomorrow at 2") is not invented.
    times = [m.group(0) for m in H.TIME_RE.finditer(r)
             if not (re.search(r"\d+", m.group(0)) and re.search(rf"\b{re.search(r'\d+', m.group(0)).group(0)}\b",
                                                                  s["inbound"]))]
    c["no_invented_appt_time"] = (not times, f"{times}" if times else "")
    pol = hc["no_invented_policy_years_service"]
    c["no_invented_policy_service"] = (pol[0] and not unl, "; ".join(filter(None, [pol[1], f"unlisted {unl}" if unl else ""])))
    c["no_availability_claim"] = (not _neg_free_hit(AVAIL_CLAIM_RE, r),
                                     f"{AVAIL_CLAIM_RE.search(r).group(0)!r}" if AVAIL_CLAIM_RE.search(r) else "")
    c["no_other_discount"] = (not _neg_free_hit(DISCOUNT_OFFER_RE, r),
                              f"{DISCOUNT_OFFER_RE.search(r).group(0)!r}" if DISCOUNT_OFFER_RE.search(r) else "")
    tech = _neg_free_hit(TECH_CONTACT_RE, r) and resp.get("send_decision") != "escalate_human"
    c["no_price_match_or_cant_keep"] = (
        not _neg_free_hit(CANT_KEEP_RE, r) and not tech,
        f"{CANT_KEEP_RE.search(r).group(0)!r}" if CANT_KEEP_RE.search(r) else
        (f"{TECH_CONTACT_RE.search(r).group(0)!r} without escalating" if tech else ""))
    c["no_gold_inclusions_to_silver"] = (not g2s, f"{g2s[:80]!r}" if g2s else "")
    c["no_yes_to_lifetime_hard"] = (not (asked_lifetime and H.YES_RE.search(first)), "")
    c["no_infant_spray_or_dogs_out"] = (
        not _neg_free_hit(H.DOGS_OUT_RE, r)
        and (not infant or (bool(INFANT_RE.search(r) or _has(r"little one|4[- ]month", r)) and bool(H.NEG_RE.search(r))
                            and not _has(r"recommend|suggest", r))), "")
    c["no_drain_work"] = (not B._drain_claim(r), "")
    return c


def correct_checks(key: str, set_: str, s: dict, resp: dict) -> dict:
    raw = resp.get("reply") or ""
    r = H.URL_RE.sub(" ", raw)
    dec = resp.get("send_decision")
    if set_ == "baseline":
        src = B.specific_checks(s, resp)
    elif set_ == "hard":
        src = H.specific_checks(s, resp)
    elif set_ == "fresh":
        src = F.fresh_checks(s, resp)
    else:
        src = {}
    c = {k: v for k, v in src.items() if k not in DROP.get(key, set())}
    hc = H.hard_checks(s, resp)
    c["intro_only_first_message"] = hc["intro_only_first_message"]
    c["no_assistant_title_unless_asked"] = hc["no_assistant_title_unless_asked"]
    n_steps = booking_steps(raw)  # link + question stacked: a normal fail, not a hard fail (Oscar 2026-10-12)
    c["one_booking_step_max"] = (n_steps <= 1, f"{n_steps} booking steps")
    c["no_urgency"] = (not URGENCY_RE.search(r), f"{URGENCY_RE.search(r).group(0)!r}" if URGENCY_RE.search(r) else "")
    if key == "F4":  # caulk replacement is Gold and above (2026-10-12); Phil is on Silver
        c["caulk_is_gold_and_above"] = (bool(GOLD_WORD_RE.search(r)) and _has(r"caulk", r), "")
    if key in ("F13", "H8"):  # asks to go lower / match: hold the price, hand to Oscar
        c["hands_to_oscar"] = (dec == "escalate_human" or _has(r"\boscar\b", r), f"decision={dec}")
    if key == "C7":
        c["no_intake_restart"] = (not PHOTO_REQ_RE.search(r), "")
        c["no_guilt"] = (not F.GUILT_RE.search(r), f"{F.GUILT_RE.search(r).group(0)!r}" if F.GUILT_RE.search(r) else "")
    if key == "C8":
        c["answers_soak"] = (_has(r"soak|hold up|holds up|durab|last|wear", r), "")
        c["not_defensive"] = (not F.DEFENSIVE_RE.search(r),
                              f"{F.DEFENSIVE_RE.search(r).group(0)!r}" if F.DEFENSIVE_RE.search(r) else "")
    if key in ("N4", "B17"):
        c["acknowledges_stop"] = (bool(re.search(r"won'?t (text|message|contact|reach out)|will(?: not)? stop|"
                                                 r"no more (texts|messages)|(remove|removed|taking) you|"
                                                 r"not (text|contact) you again|sorry to bother", r, re.I)), "")
        c["no_pitch"] = (not F.PITCH_RE.search(raw), f"{F.PITCH_RE.search(raw).group(0)!r}" if F.PITCH_RE.search(raw) else "")
    return c


def closing_checks(key: str, resp: dict) -> dict:
    raw = resp.get("reply") or ""
    r = H.URL_RE.sub(" ", raw)
    dec = resp.get("send_decision")
    cls = CLASS[key]
    pushes = bool(BOOK_LINK_RE.search(raw)) or bool(SCHED_QUESTION_RE.search(r))
    if cls == "close":
        return {"closes_with_one_step": (ends_with_step(raw) and dec == "send_now",
                                         f"decision={dec}; last: {_last_sentence(raw)[:70]!r}")}
    if cls in ("quiet", "photo"):
        c = {"no_booking_push": (not pushes, "link or scheduling question present" if pushes else "")}
        if cls == "photo":
            c["photo_ask_is_the_close"] = (bool(PHOTO_REQ_RE.search(r)), "")
        return c
    return {}


KIND = {}  # check name -> kind, filled by grade()


def grade(key: str, set_: str, s: dict, resp: dict) -> dict:
    parts = (("hard", hard_fail_checks(s, resp)), ("correct", correct_checks(key, set_, s, resp)),
             ("closing", closing_checks(key, resp)))
    rules = {}
    for kind, checks in parts:
        for k, v in checks.items():
            if k in rules:  # never let a scenario check silently replace a hard one
                k = f"{k}_{kind}"
            rules[k] = {"pass": bool(v[0]), "note": v[1], "kind": kind}
    hard_fails = [k for k, v in rules.items() if v["kind"] == "hard" and not v["pass"]]
    return {"rules": rules, "all_pass": all(v["pass"] for v in rules.values()), "hard_fails": hard_fails,
            "closing_class": CLASS[key]}


# ---------------------------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------------------------
def run(label: str, reps: int = 3, only=None) -> dict:
    if (os.environ.get("HC_BACKEND") or "") != "muse" or (os.environ.get("HC_VARIANT") or "") != "spicy":
        raise SystemExit("spicy exam needs HC_BACKEND=muse HC_VARIANT=spicy — HOLD")
    from hc_compose_service import compose
    rows = []
    for key, set_, s, build in plan():
        if only and key not in only:
            continue
        req = build(s)
        for rep in range(1, reps + 1):
            log = io.StringIO()
            t0 = time.perf_counter()
            with contextlib.redirect_stdout(log):
                resp = compose(req)
            latency = round(time.perf_counter() - t0, 2)
            g = grade(key, set_, s, resp)
            rows.append({"key": key, "set": set_, "name": s["name"], "rep": rep, "inbound": s["inbound"],
                         "response": resp, "latency_s": latency, "grade": g,
                         "log": [ln for ln in log.getvalue().splitlines() if "FAILED" in ln or "->" in ln]})
            mark = "PASS" if g["all_pass"] else "FAIL " + ",".join(k for k, v in g["rules"].items() if not v["pass"])
            print(f"[{label}] {key:>4} rep{rep} {latency:>6}s {resp.get('send_decision'):<15} {mark}", flush=True)
            # Save as we go so a long run is never lost.
            _save(label, reps, rows)
    lat = [r["latency_s"] for r in rows]
    print(f"\nTOTAL {sum(r['grade']['all_pass'] for r in rows)}/{len(rows)} runs pass; "
          f"median {statistics.median(lat)}s max {max(lat)}s")
    return {"rows": rows}


def _save(label, reps, rows):
    out = {"label": label, "backend": os.environ.get("HC_BACKEND"), "variant": os.environ.get("HC_VARIANT") or "",
           "now_et": H.NOW_ET, "reps": reps, "rows": rows}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, f"{label}.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)


def regrade(label: str) -> None:
    path = os.path.join(RESULTS_DIR, f"{label}.json")
    with open(path, encoding="utf-8") as fh:
        out = json.load(fh)
    src = {key: (set_, s) for key, set_, s, _ in plan()}
    for r in out["rows"]:
        set_, s = src[r["key"]]
        r["grade"] = grade(r["key"], set_, s, r["response"])
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"{label}: {sum(r['grade']['all_pass'] for r in out['rows'])}/{len(out['rows'])} runs pass")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if sys.argv[1] == "--regrade":
        for lbl in sys.argv[2:]:
            regrade(lbl)
        sys.exit(0)
    B.load_keys()
    # --only K1,K2,... reruns just those scenarios (e.g. the ones that failed).
    args = [a for a in sys.argv[1:] if not a.startswith("--only=")]
    only = next((set(a.split("=", 1)[1].split(",")) for a in sys.argv[1:] if a.startswith("--only=")), None)
    run(args[0], int(args[1]) if len(args) > 1 else 3, only)
