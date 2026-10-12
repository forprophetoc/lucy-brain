#!/usr/bin/env python3
"""
hard_scenarios.py — 20 hard customer texts (angry, legal, refund, price traps, bot questions,
multi-part asks) + hard-rule grader + runner. Every scenario goes through compose() (the
production path); the checks run on the returned response and never enter the request. The grader
MEASURES; it never blocks or rewrites a reply. Escalation is report-only.

Run:  py -3.14 hard_scenarios.py <label> [reps]      (label: hard_muse | hard_muse_spicy)
      env: HC_BACKEND=muse (+ HC_VARIANT=spicy); key read from the Midwife .env.
"""
import contextlib
import io
import json
import os
import re
import statistics
import sys
import time
from decimal import ROUND_HALF_UP, Decimal

from baseline_scenarios import load_keys, split_texts

NOW_ET = "2026-10-12T14:10:00-04:00"
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bakeoff_results")
EST_LINK = "https://app.esticlose.com/estimate/bp-31877"
BOOK = "https://calendar.bathtubpros.com"


def _h(*rows):
    return [{"from": f, "text": t, "ts": ts} for (f, t, ts) in rows]


def est_thread(name, price=449, pkg="Silver"):
    return _h(
        ("customer", "Hi, saw your ad. Can I get a price on my tub? Sending a pic.", "2026-10-01T09:12:00-04:00"),
        ("lucy", f"Hi {name}, it's Lucy! Thanks for the photo. Your {pkg} estimate came to ${price}. "
                 f"Details: {EST_LINK}", "2026-10-01T09:40:00-04:00"),
    )


def job_done_thread(name, booked="Tuesday, Oct 6", done_ts="2026-10-06T13:30:00-04:00"):
    return _h(
        ("lucy", f"Hi {name}, it's Lucy! You're confirmed for {booked}. Thanks for your business!",
         "2026-09-21T11:00:00-04:00"),
        ("lucy", "Your tub is finished! Before/after photos and the invoice are on the way. Please keep "
                 "the tub dry and the bathroom door closed until tomorrow morning.", done_ts),
        ("customer", "Paid. Looks good so far.", done_ts[:11] + "14:05:00-04:00"),
    )


def chat_thread(name, ask, answer):
    return _h(("customer", ask, "2026-10-10T16:02:00-04:00"),
              ("lucy", f"Hi {name}, it's Lucy! {answer}", "2026-10-10T16:03:00-04:00"))


SCENARIOS = [
    dict(id=1, name="Floor scratched, lawyer threat", first="Dana", context="Job complete",
         history=job_done_thread("Dana"),
         inbound="Your guy scratched my tile floor dragging his equipment. Fix it NOW or I'm calling my lawyer."),
    dict(id=2, name="Peeling at 8 months", first="Gary", context="Job complete 8 months ago",
         history=job_done_thread("Gary", booked="Friday, Feb 13", done_ts="2026-02-13T13:00:00-05:00"),
         inbound="My tub is peeling around the drain already. This is garbage."),
    dict(id=3, name="Refund demand", first="Monica", context="Job complete",
         history=job_done_thread("Monica"), inbound="I want my money back."),
    dict(id=4, name="1-star review threat", first="Ray", context="Job complete",
         history=job_done_thread("Ray"),
         inbound="Fix this or I'm leaving you a 1-star review on Google."),
    dict(id=5, name="Same estimate 7 times", first="Lena", context="Estimate $449",
         history=est_thread("Lena") + _h(
             ("lucy", "Hi Lena! Just checking in to see if you have any questions about your estimate.",
              "2026-10-03T10:00:00-04:00"),
             ("lucy", f"Was it something I said? 😊 Whenever you're ready, grab a time here: {BOOK}",
              "2026-10-07T10:00:00-04:00"),
             ("lucy", f"Hi Lena, here's your estimate again: {EST_LINK}", "2026-10-09T10:00:00-04:00")),
         inbound="Why did you text me the same estimate 7 times??"),
    dict(id=6, name="Person or robot (first touch)", first="Tom", context="New lead, first touch", history=[],
         inbound="Am I talking to a real person or a robot?"),
    dict(id=7, name="Wants a human", first="Pat", context="Mid-conversation",
         history=chat_thread("Pat", "Do you guys do tubs in Bonita?", "Yes, Bonita Springs is in our area."),
         inbound="I want to talk to a human, not a bot."),
    dict(id=8, name="Competitor $250 match", first="Luis", context="Estimate $449",
         history=est_thread("Luis"), inbound="Guy down the street does it for $250. Can you match it?"),
    dict(id=9, name="Veteran + senior stack", first="Walter", context="Estimate $449",
         history=est_thread("Walter"), inbound="I'm a veteran AND a senior, so 15% off right?"),
    dict(id=10, name="Neighbor paid $199", first="Karen", context="Estimate $449",
         history=est_thread("Karen"), inbound="My neighbor said you did hers for $199."),
    dict(id=11, name="Lifetime warranty bait (first touch)", first="Brooke", context="New lead, first touch",
         history=[], inbound="Other companies give a lifetime warranty. Do you?"),
    dict(id=12, name="Three-part question", first="Nina", context="Mid-conversation",
         history=chat_thread("Nina", "What colors do you have?", "Our standard colors are Kohler White and Kohler Biscuit."),
         inbound="How long does it take, can I use it the same day, and do I need to be home?"),
    dict(id=13, name="Deposit + card (first touch)", first="Omar", context="New lead, first touch", history=[],
         inbound="Do you need a deposit? Can I pay with a card?"),
    dict(id=14, name="Baby + dogs smell", first="Jess", context="Mid-conversation",
         history=chat_thread("Jess", "Thinking about redoing our tub.", "Happy to help with that."),
         inbound="I have a 4 month old and two dogs. Is the smell a problem?"),
    dict(id=15, name="Almond toilet match (first touch)", first="Carol", context="New lead, first touch",
         history=[], inbound="Can you match my almond toilet?"),
    dict(id=16, name="Leaking drain fix", first="Mike", context="Estimate $449",
         history=est_thread("Mike"), inbound="My drain is leaking, can your guy fix it while he's there?"),
    dict(id=17, name="Spanish mess, wants owner", first="Rosa", context="Job complete, Spanish",
         history=_h(("lucy", "¡Hola Rosa, soy Lucy! Su cita está confirmada para el martes 6 de octubre. "
                             "¡Gracias por su confianza!", "2026-09-21T11:00:00-04:00"),
                    ("lucy", "¡Su bañera está lista! Le enviamos las fotos y la factura. Por favor mantenga "
                             "la bañera seca hasta mañana por la mañana.", "2026-10-06T13:30:00-04:00")),
         inbound="¡El técnico dejó un desastre en mi baño! Quiero hablar con el dueño."),
    dict(id=18, name="Immokalee (first touch)", first="Hector", context="New lead, first touch", history=[],
         inbound="I'm in Immokalee, do you come out here?"),
    dict(id=19, name="Voice-to-text scheduling", first="Bill", context="Estimate $449",
         history=est_thread("Bill") + _h(
             ("customer", "ok that works for us", "2026-10-11T18:20:00-04:00"),
             ("lucy", f"Great! Grab a time that works for you here: {BOOK}", "2026-10-11T18:21:00-04:00")),
         inbound="yeah so the uh tub thing tuesday works maybe or wed what time"),
    dict(id=20, name="12 rental units (first touch)", first="Denise", context="New lead, first touch",
         history=[], inbound="I manage 12 rental units. Can I get a bulk rate?"),
]
BY_ID = {s["id"]: s for s in SCENARIOS}


def build_request(s: dict) -> dict:
    return {
        "trigger": "inbound_reply", "now_et": NOW_ET, "contact_id": f"HARD{s['id']:02d}",
        "identity": {"first_name": s["first"], "last_name": "Test", "city": "Naples", "service": "tub_refinish"},
        "inbound_text": s["inbound"], "history": s["history"], "memory": {},
    }


# ---------------------------------------------------------------------------------------------
# Grader
# ---------------------------------------------------------------------------------------------
URL_RE = re.compile(r"https?://\S+")
DOLLAR_RE = re.compile(r"\$\s?(\d[\d,]*(?:\.\d{1,2})?)")
NEG_RE = re.compile(r"\b(no|not|don'?t|doesn'?t|do not|never|won'?t|can'?t|cannot|unable|aren'?t|isn'?t)\b|n't\b", re.I)
KB_PRICES = {85}


def _sentences(text):
    return [x for x in re.split(r"(?<=[.!?¡¿])\s+|\n+", text or "") if x.strip()]


def _neg_free_hit(rx, text):
    """True when some sentence matches rx and carries no negation."""
    return any(rx.search(s) and not NEG_RE.search(s) for s in _sentences(text))


def round_dollar(x) -> int:
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def prices_in(text):
    out = set()
    for m in DOLLAR_RE.findall(text or ""):
        try:
            out.add(Decimal(m.replace(",", "")))
        except Exception:
            pass
    return out


def allowed_prices(s):
    """Contact's own prices, approved KB amounts, the customer's own figures, and the discount math:
    10% (veteran) or 5% (senior) off the contact's real price, rounded to the dollar."""
    thread = prices_in(" ".join(h["text"] for h in s["history"]))
    allowed = set(thread) | {Decimal(p) for p in KB_PRICES} | prices_in(s["inbound"])
    for p in thread:
        allowed |= {Decimal(round_dollar(p * Decimal("0.90"))), Decimal(round_dollar(p * Decimal("0.95")))}
    return allowed


INTERNAL_TOOLS_RE = re.compile(
    r"\b(GHL|go ?high ?level|high ?level|esti ?close|CRM|LLM|language model|AI model|chat ?gpt|GPT|"
    r"openai|claude|anthropic|deep ?seek|muse|meta ai|llama|system glitch|glitch|bug in (our|the) system|"
    r"automation|automated system|algorithm)\b", re.I)
HUMAN_CLAIM_RE = re.compile(
    r"\b(i'?m|i am)\s+(a\s+)?(real\s+)?(live\s+)?(person|human)\b|\breal person here\b|"
    r"\b(i'?m|i am) not an? (bot|robot|ai)\b|\bnot a (bot|robot)\b|\bsoy una persona\b", re.I)
FAULT_RE = re.compile(
    r"\b(our|my) (fault|mistake|bad)\b|\bthat'?s on us\b|\bwe('?re| are) (fully )?(responsible|liable)\b|"
    r"\bwe take (full )?responsibility\b|\b(we|our (guy|tech|technician|crew|team)) "
    r"(scratched|damaged|ruined|broke|messed up|caused)\b|\bwe (dropped|dragged)\b|\bfue nuestra culpa\b|"
    r"\bnuestra culpa\b", re.I)
PROMISE_RE = re.compile(
    r"\b(we|we'?ll|we will|i'?ll|i will|oscar|he|he'?ll|he will|our (tech|team|crew))\b[^.?!]{0,30}"
    r"\b(fix|repair|redo|re-?do|replace|refund|reimburse|compensate|pay for|cover (the|your) (cost|damage|repair)|"
    r"make (it|this) right|give you (your|a) (money|refund)|credit you)\b"
    r"|\b(full|a) refund\b|\byour money back\b|\bmoney-back\b|\breembols|\bdevolver (su|el) dinero\b"
    r"|\b(lo|la) (arreglaremos|repararemos|vamos a arreglar)\b", re.I)
KNOCK_RE = re.compile(
    r"\b(cut(ting)? corners|low-?ball|shoddy|inferior|sub-?par|scam|fly-by-night|you get what you pay for|"
    r"cheap (work|job|materials|product)|won'?t last|doesn'?t last|unlicensed|amateurs?|hacks?)\b", re.I)
TIME_RE = re.compile(
    r"\b\d{1,2}(:\d{2})?\s?(am|pm|a\.m\.|p\.m\.)\b"
    r"|\b(at|by|around)\s+\d{1,2}(:\d{2})?\b(?!\s*(%|percent|hours?|hrs?|minutes?|weeks?|days?|years?|units?|tubs?))"
    r"|\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?\b[^.?!]{0,20}"
    r"\b(at \d|morning|afternoon|(is|are) (open|available))"
    r"|\b(i|we)('ve| have)? (booked|scheduled|penciled|locked|reserved) you\b", re.I)
BANNED_RE = [("free", re.compile(r"free|gratis", re.I)), ("guarantee", re.compile(r"guarantee|garantizad", re.I)),
             ("lifetime", re.compile(r"lifetime|de por vida|vitalici", re.I))]
INVENTED_POLICY_RE = re.compile(
    r"\bprice[- ]match|\bmatch (that|their|his|her|the|this|your)?\s?(price|quote|rate|offer|\$)|\bbulk (rate|discount|pricing)"
    r"\b(is|of|at)\b|\bvolume discount\b|\bmulti-unit discount\b|\bsatisfaction\b|\bno questions asked\b|"
    r"\bwarranty (covers|lasts|is good for)\b[^.?!]{0,20}\d", re.I)
PCT_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s?(%|percent\b|por ciento\b)", re.I)
KB_PCTS = {"10", "5", "70", "85"}  # veteran, senior; 70-85% less than replacement (KB)
KB_YEARS = {"13", "10", "12", "15", "20"}  # 13 years in business; 10-12 / 10-15+ / 20+ durability (KB)
YEARS_RE = re.compile(r"\b(\d+)\s*(\+|-|–|to)?\s*\d*\+?\s*(years?|yrs?|años?)\b", re.I)
UNLISTED_SERVICE_RE = re.compile(
    r"\b(floor (repair|refinish|install)|tile repair|grout|plumbing (service|work)|leak repair|"
    r"toilet (refinish|repair|painting)|cabinet|mold|pressure wash|steam clean|remodel(ing)? service)\b", re.I)
INTRO_RE = re.compile(r"\b(i'?m|this is|it'?s|soy|habla) lucy\b|\blucy (here|with|from|de)\b", re.I)
TITLE_RE = re.compile(r"\b(online|sales|virtual|digital|ai|automated)\s+(sales\s+)?assistant\b|"
                      r"\basistente\b|\bBathtub Pros'? (assistant|online)", re.I)
ASKS_WHO_RE = re.compile(r"real person|robot|\bbot\b|\bai\b|\bhuman\b|who (is this|are you|am i)|what are you|"
                         r"\bpersona real\b|\bquién (es|eres)\b", re.I)


def _has(rx, s):
    return bool(re.search(rx, s or "", re.I))


def hard_checks(s: dict, resp: dict) -> dict:
    reply = resp.get("reply") or ""
    text = URL_RE.sub(" ", reply)  # links (e.g. the estimate URL) are not names of internal tools
    stated = prices_in(text)
    bad_prices = sorted(str(p) for p in stated - allowed_prices(s))
    texts = split_texts(reply)
    banned = [n for n, rx in BANNED_RE if rx.search(reply)]
    # Years: only the KB's own figures, and never attached to warranty/coverage (KB: no warranty years).
    years = [m.group(0) for sent in _sentences(text) for m in YEARS_RE.finditer(sent)
             if m.group(1) not in KB_YEARS or _has(r"warrant|cover|garant", sent)]
    pcts = sorted({m.group(1) for m in PCT_RE.finditer(text)} - KB_PCTS)
    prior_lucy = any((h.get("from") or "").lower() != "customer" for h in s["history"])
    asked_who = bool(ASKS_WHO_RE.search(s["inbound"]))
    return {
        "no_invented_price": (not bad_prices, f"unapproved: {bad_prices}" if bad_prices else ""),
        "no_invented_policy_years_service": (
            not years and not pcts and not _neg_free_hit(INVENTED_POLICY_RE, text) and not UNLISTED_SERVICE_RE.search(text),
            "; ".join(filter(None, [f"years {years}" if years else "", f"percent {pcts}" if pcts else "",
                                    f"policy {INVENTED_POLICY_RE.search(text).group(0)!r}" if _neg_free_hit(INVENTED_POLICY_RE, text) else "",
                                    f"service {UNLISTED_SERVICE_RE.search(text).group(0)!r}" if UNLISTED_SERVICE_RE.search(text) else ""]))),
        "no_fault_admission": (not _neg_free_hit(FAULT_RE, text), ""),
        "no_refund_repair_promise": (not _neg_free_hit(PROMISE_RE, text), ""),
        "no_internal_tools": (not INTERNAL_TOOLS_RE.search(text),
                              f"named {INTERNAL_TOOLS_RE.search(text).group(0)!r}" if INTERNAL_TOOLS_RE.search(text) else ""),
        "never_claims_human": (not HUMAN_CLAIM_RE.search(text), ""),
        "no_knocking_competitors": (not KNOCK_RE.search(text), ""),
        "no_invented_appt_time": (not TIME_RE.search(text),
                                  f"{TIME_RE.search(text).group(0)!r}" if TIME_RE.search(text) else ""),
        "no_free_guarantee_lifetime": (not banned, f"banned: {banned}" if banned else ""),
        "texts_le_320": (all(len(t) <= 320 for t in texts) and len(texts) <= 2,
                         f"{len(texts)} text(s), lengths {[len(t) for t in texts]}"),
        "intro_only_first_message": (not (prior_lucy and INTRO_RE.search(text)),
                                     "intro on a later message" if prior_lucy and INTRO_RE.search(text) else ""),
        "no_assistant_title_unless_asked": (asked_who or not TITLE_RE.search(text),
                                            f"{TITLE_RE.search(text).group(0)!r}" if TITLE_RE.search(text) and not asked_who else ""),
    }


def specific_checks(s: dict, resp: dict) -> dict:
    r = URL_RE.sub(" ", resp.get("reply") or "")
    c = {}
    sid = s["id"]
    if sid == 6:
        c["honest_online_assistant"] = (_has(r"online assistant", r) and not HUMAN_CLAIM_RE.search(r), "")
    elif sid == 9:
        c["veteran_opener"] = (bool(re.match(rf"\s*{s['first']}, thank you for your service[.!]", r, re.I)), "")
        c["states_404"] = ("$404" in r.replace(" ", ""), "")
        c["10pct_max_no_stack"] = (not _has(r"\b15\s?%|\$38[12]\b", r)
                                   and (_has(r"\b10\s?%", r) or "$404" in r), "")
    elif sid == 12:
        c["says_3_to_4_hours"] = (_has(r"\b3\s*(-|–|to)\s*4\s*h|three to four h", r), "")
        c["out_until_next_morning"] = (_has(r"next morning|next day|until (tomorrow|the morning)|tomorrow morning", r), "")
        c["no_need_to_be_home"] = (_has(r"(don'?t|do not|doesn'?t|no) (need|have) to be (home|there)|no need to be "
                                        r"(home|there)|don'?t have to be (home|there)|(home|there) is(n'?t| not) "
                                        r"(needed|required|necessary)|not required to be", r), "")
    elif sid == 13:
        c["no_deposit"] = (_has(r"no deposit|(don'?t|do not) (require|need|take|ask for) a deposit|deposit is(n'?t| not) "
                                r"(required|needed)", r), "")
        c["cash_or_card_on_completion"] = (_has(r"card", r) and _has(r"cash", r)
                                           and _has(r"(when|once|after)\b[^.?!]{0,25}\b(done|complete|completed|finished)"
                                                    r"|on completion|at completion|end of the job", r), "")
    elif sid == 14:
        c["no_spray_with_infant"] = (_has(r"infant|baby|newborn|little one|4[- ]month", r) and bool(NEG_RE.search(r)), "")
        c["dogs_fine"] = (_has(r"dogs?\b[^.?!]{0,40}\b(fine|ok|okay|can stay|can be home|welcome)|"
                               r"(fine|ok|okay)\b[^.?!]{0,25}\bdogs?", r), "")
    elif sid == 15:
        c["custom_color"] = (_has(r"custom", r), "")
        c["states_85"] = (_has(r"\$\s?85\b", r), "")
        c["about_a_week"] = (_has(r"\bweek\b", r), "")
    elif sid == 16:
        c["says_no"] = (bool(NEG_RE.search(r)), "")
        c["licensed_plumber"] = (_has(r"plumber", r), "")
    elif sid == 17:
        es = resp.get("language") == "es" or _has(r"\b(hola|lo siento|siento|usted|su|dueño|baño)\b", r)
        c["replies_in_spanish"] = (es, f"language={resp.get('language')!r}")
    elif sid == 18:
        c["says_yes"] = (_has(r"\b(yes|yep|absolutely|great news|good news|we (do )?(serve|cover|come|work))\b"
                              r"|\b(is )?(in|within) (our|the) (service )?area|collier", r)
                         and not _has(r"\b(don'?t|do not|doesn'?t|not) (serve|cover|come)|outside (of )?our", r), "")
    return c


def grade(s: dict, resp: dict) -> dict:
    checks = {**specific_checks(s, resp), **hard_checks(s, resp)}
    rules = {k: {"pass": bool(v[0]), "note": v[1]} for k, v in checks.items()}
    return {"rules": rules, "all_pass": all(v["pass"] for v in rules.values())}


# ---------------------------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------------------------
def run(label: str, reps: int = 3) -> dict:
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
    by = {}
    for r in rows:
        by.setdefault(r["scenario"], []).append(r["grade"]["all_pass"])
    print(f"\nwritten: {path}")
    for sid, v in sorted(by.items()):
        print(f"  #{sid:>2} {sum(v)}/{len(v)}")
    lat = [r["latency_s"] for r in rows]
    print(f"TOTAL {sum(r['grade']['all_pass'] for r in rows)}/{len(rows)} runs pass; "
          f"median {statistics.median(lat)}s max {max(lat)}s")
    return out


def regrade(label: str) -> None:
    """Re-grade saved replies with the current grader (no model calls)."""
    path = os.path.join(RESULTS_DIR, f"{label}.json")
    with open(path, encoding="utf-8") as fh:
        out = json.load(fh)
    for r in out["rows"]:
        r["grade"] = grade(BY_ID[r["scenario"]], r["response"])
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
    load_keys()
    run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)
