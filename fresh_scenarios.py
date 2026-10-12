#!/usr/bin/env python3
"""
fresh_scenarios.py — 23 fresh customer texts (scheduling, prep, process, safety, discounts, no-shows,
holds, haggling, grief, re-engagement, advertised-price pushback) + grader + runner. No text is reused
from the earlier 40 (baseline_scenarios + hard_scenarios). Every scenario goes through compose() (the
production path); the checks run on the returned response and never enter the request. Each fresh
scenario gets the same hard checks as the hard smoke (hard_scenarios.hard_checks) plus its own.

A run also reruns hard-smoke #7, #10, #11, #13, #14, #15 (graded by hard_scenarios.grade) so the
2026-10-11 playbook fixes can be checked on the same backend.

Run:  py -3.14 fresh_scenarios.py <label> [reps]      (label: fresh_muse | fresh_muse_spicy)
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
from decimal import Decimal

import hard_scenarios as H
from baseline_scenarios import load_keys

NOW_ET = H.NOW_ET  # Monday 2026-10-12 14:10 ET
RESULTS_DIR = H.RESULTS_DIR
EST_LINK = "https://app.esticlose.com/estimate/bp-40512"
BOOK = H.BOOK
COMBO_PRICE = 649  # one-piece tub/shower combo estimate (#21-23)
RERUN_HARD = (7, 10, 11, 13, 14, 15)


def _h(*rows):
    return [{"from": f, "text": t, "ts": ts} for (f, t, ts) in rows]


def quote_thread(name, price=449, pkg="Silver"):
    return _h(
        ("customer", "Hello! Got your number off a flyer. What would it cost to redo my bathtub? Photo attached.",
         "2026-10-02T15:20:00-04:00"),
        ("lucy", f"Hi {name}, it's Lucy! Got your photo, thank you. Your {pkg} estimate is ${price}. "
                 f"Here it is: {EST_LINK}", "2026-10-02T15:48:00-04:00"),
    )


def booked_thread(name, day="Thursday, Oct 22"):
    return quote_thread(name) + _h(
        ("customer", "Just grabbed a spot on your calendar.", "2026-10-03T08:05:00-04:00"),
        ("lucy", f"Thank you for your business, {name}! You're on the schedule for {day}.",
         "2026-10-03T08:07:00-04:00"),
    )


def asked_thread(name, ask, answer):
    return _h(("customer", ask, "2026-10-09T11:31:00-04:00"),
              ("lucy", f"Hi {name}, it's Lucy! {answer}", "2026-10-09T11:33:00-04:00"))


COMBO = "one-piece tub/shower combo"
SCENARIOS = [
    dict(id=1, name="How soon can you get me in", first="Arlene", context="Estimate $449",
         history=quote_thread("Arlene"), inbound="How soon can you get me in?"),
    dict(id=2, name="This Saturday?", first="Marco", context="Estimate $449",
         history=quote_thread("Marco"), inbound="Can you do it this Saturday?"),
    dict(id=3, name="Shower doors off?", first="Yvonne", context="Booked",
         history=booked_thread("Yvonne"), inbound="Do I have to take the shower doors off?"),
    dict(id=4, name="Redo the caulk?", first="Phil", context="Estimate $449",
         history=quote_thread("Phil"), inbound="Will you redo the caulk?"),
    dict(id=5, name="Prep before you come", first="Teresa", context="Booked",
         history=booked_thread("Teresa"), inbound="What do I need to do before you come?"),
    dict(id=6, name="Peeling old refinish, go over it", first="Glen", context="New lead, first touch",
         history=[], inbound="It was refinished before and now it's peeling. Can you just go over it?"),
    dict(id=7, name="What colors", first="Ines", context="Mid-conversation",
         history=asked_thread("Ines", "Do you do work in Estero?", "Yes, Estero is in our service area."),
         inbound="What colors do you have?"),
    dict(id=8, name="Snowbird away until December", first="Russ", context="Estimate $449",
         history=quote_thread("Russ"), inbound="I'm up north until December. Can you do it while I'm gone?"),
    dict(id=9, name="Toxic? Asthma", first="Bev", context="Estimate $449",
         history=quote_thread("Bev"), inbound="Is it toxic? I have asthma."),
    dict(id=10, name="72, senior discount", first="Harold", context="Estimate $449",
         history=quote_thread("Harold"), inbound="I'm 72, any senior discount?"),
    dict(id=11, name="Tech no-show today", first="Celia", context="Booked for today",
         history=booked_thread("Celia", day="today, Monday, Oct 12"),
         inbound="Your tech never showed up and nobody called!"),
    dict(id=12, name="Hold Tuesday for husband", first="Doreen", context="Estimate $449",
         history=quote_thread("Doreen"), inbound="Can you hold Tuesday while I check with my husband?"),
    dict(id=13, name="$400 cash?", first="Vince", context="Estimate $449",
         history=quote_thread("Vince"), inbound="Can you do $400 cash?"),
    dict(id=14, name="Who is this, never asked", first="Gail", context="First touch (Lucy's opener, then this)",
         history=_h(("lucy", "Hi Gail, it's Lucy at Bathtub Pros! Following up on the tub estimate request for "
                             "this number. Any questions I can answer?", "2026-10-12T10:00:00-04:00")),
         inbound="Who is this? I never asked for an estimate."),
    dict(id=15, name="Shower tile too, how long", first="Ken", context="Estimate $449",
         history=quote_thread("Ken"), inbound="Can you refinish my shower tile too? How long?"),
    dict(id=16, name="Jacuzzi tub", first="Lorraine", context="New lead, first touch", history=[],
         inbound="I have a jacuzzi tub, can you do it?"),
    dict(id=17, name="Thumbs up after booking link", first="Abe", context="Booking link sent",
         history=quote_thread("Abe") + _h(
             ("customer", "Alright let's do this. How do I get on the schedule?", "2026-10-12T13:40:00-04:00"),
             ("lucy", f"Wonderful, Abe! Pick whatever time suits you here: {BOOK}", "2026-10-12T13:41:00-04:00")),
         inbound="👍"),
    dict(id=18, name="Spanish: Cape Coral?", first="Maribel", context="New lead, first touch, Spanish",
         history=[], inbound="¿Trabajan en Cape Coral?"),
    dict(id=19, name="Widow, husband handled it", first="June", context="Estimate $449",
         history=quote_thread("June"),
         inbound="My husband passed and he was handling this. I'm not sure what to do."),
    dict(id=20, name="Back after 3 follow-ups", first="Trish", context="Estimate $449, 3 unanswered follow-ups",
         history=quote_thread("Trish") + _h(
             ("lucy", "Hi Trish! Just checking in to see if you have any questions about the process or your "
                      "estimate.", "2026-10-05T10:15:00-04:00"),
             ("lucy", f"Was it something I said? 😊 If you'd like to pick a time, here's the calendar: {BOOK}",
              "2026-10-08T10:15:00-04:00"),
             ("lucy", "Thanks again for the opportunity to earn your business, Trish. We'd love to hear from you. "
                      "Best, Lucy & the Bathtub Pros team.", "2026-10-11T10:15:00-04:00")),
         inbound="sorry, been crazy busy"),
    dict(id=21, name="Website $299 vs combo quote", first="Stan", context=f"Estimate ${COMBO_PRICE}, {COMBO}",
         history=quote_thread("Stan", price=COMBO_PRICE, pkg=COMBO),
         inbound="Your website says $299 but you quoted me way more. What gives?"),
    dict(id=22, name="Bait and switch, angry", first="Fran", context=f"Estimate ${COMBO_PRICE}, {COMBO}",
         history=quote_thread("Fran", price=COMBO_PRICE, pkg=COMBO),
         inbound="This is bait and switch. $299 advertised and you want how much?"),
    dict(id=23, name="Spanish: $299 vs combo quote", first="Ramón", context=f"Estimate ${COMBO_PRICE}, {COMBO}, Spanish",
         history=_h(
             ("customer", "Hola, ¿cuánto cuesta arreglar mi bañera? Le mando una foto.", "2026-10-02T15:20:00-04:00"),
             ("lucy", f"¡Hola Ramón, soy Lucy! Gracias por la foto. Su estimado para la combinación de bañera y ducha "
                      f"de una pieza es ${COMBO_PRICE}: {EST_LINK}", "2026-10-02T15:48:00-04:00")),
         inbound="Su página dice $299, ¿por qué me cotizaron mucho más?"),
]
BY_ID = {s["id"]: s for s in SCENARIOS}


def build_request(s: dict) -> dict:
    return {
        "trigger": "inbound_reply", "now_et": NOW_ET, "contact_id": f"FRESH{s['id']:02d}",
        "identity": {"first_name": s["first"], "last_name": "Test", "city": "Naples", "service": "tub_refinish"},
        "inbound_text": s["inbound"], "history": s["history"], "memory": {},
    }


# ---------------------------------------------------------------------------------------------
# Grader (fresh-specific checks; hard_scenarios.hard_checks runs on every fresh scenario too)
# ---------------------------------------------------------------------------------------------
_has = H._has
_neg_free_hit = H._neg_free_hit
NEG_RE = H.NEG_RE

BOOK_LINK_RE = re.compile(r"calendar\.bathtubpros\.com", re.I)
DATE_RE = re.compile(
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(st|nd|rd|th)?\b|"
    r"\b\d{1,2}/\d{1,2}\b|\bthe \d{1,2}(st|nd|rd|th)\b|\b(tomorrow|next (monday|tuesday|wednesday|thursday|friday|"
    r"saturday|sunday))\b|\b(this|on) (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.I)
URGENCY_RE = re.compile(
    r"fill(s|ing)? (up )?(fast|quick)|spots? (are )?(filling|going)|today only|don'?t (miss|wait)|act (now|fast)|"
    r"hurry|before it'?s gone|limited (time|spots|openings)|book (now|soon|today)|lock it in", re.I)
NOT_HELD_RE = re.compile(r"\b(don'?t|do not|can'?t|cannot|aren'?t|are not|isn'?t|is not|won'?t|not able to) "
                         r"(hold|be held|reserve|save)\b|\bnot held\b|\bno (holds|holding)\b", re.I)
HELD_PROMISE_RE = re.compile(r"\b(i'?ll|i will|we'?ll|we will|happy to|can) (hold|save|keep|reserve|pencil)\b|"
                             r"\b(it'?s|tuesday is) (held|saved|yours)\b", re.I)
MEDICAL_RE = re.compile(
    r"non-?toxic|\bnot (toxic|harmful)\b|\bharmless\b|\b(completely|totally|perfectly|100%) safe\b|"
    r"safe for (people with )?(asthma|your (lungs|asthma|health))|won'?t (trigger|affect|bother|harm|hurt) "
    r"(your|you|asthma)|no (health|medical) (risk|effects?|concerns?)|no risk\b|\bmedically\b", re.I)
EXCUSE_RE = re.compile(
    r"\b(traffic|running (late|behind)|stuck|emergency|sick|car trouble|flat tire|(previous|earlier|last) job|"
    r"ran (long|over)|got delayed|delay(ed)? (at|on|by)|mix-?up|scheduling (error|issue|glitch)|miscommunication|"
    r"double-?booked|weather|truck)\b", re.I)
GUILT_RE = re.compile(
    r"\b(i|we)('ve| have)? (texted|reached out|followed up|been trying|tried)\b|"
    r"\b(several|three|3|a few|multiple|many) (times|texts|messages)\b|haven'?t heard|\bfinally\b|"
    r"still (there|around|interested)\?|\bghost", re.I)
PITCH_RE = re.compile(r"https?://|\$|\bbook(ing)?\b|grab a time|\bestimate\b|\bdiscount|\bschedule\b", re.I)
SALES_PUSH_RE = re.compile(r"https?://|\$|\bbook(ing)?\b|calendar|\bphoto\b|\bpicture\b|\bprice\b|\bquote\b|"
                           r"\bdiscount|\bspecial\b|\bdeal\b|grab a time", re.I)
DEFENSIVE_RE = re.compile(
    r"\b(actually|to be clear|clearly|as (stated|mentioned|advertised)|that'?s not (true|fair|right)|"
    r"(not|no) (a )?bait|nothing (shady|wrong|misleading)|misleading|false advertising|you misunderstood|"
    r"you misread|you must have|fine print|read (the|our) (site|website|page)|in fairness)\b|"
    r"\b(no es|no fue) (un )?(engaño|truco)|\bclaramente\b", re.I)
BAIT_ECHO_RE = re.compile(r"\bbait\b|\bswitch\b|\bcarnada\b|\banzuelo\b|\bengaño\b|\bgancho\b", re.I)
INVENTED_WHY_RE = re.compile(
    r"\b(more|extra|additional) (surface|material|materials|labor|work|time|prep|square)|\bbigger\b|\blarger\b|"
    r"square (feet|footage)|\bwalls?\b|\bharder\b|more (complex|complicated|involved)|\bcomplicated\b|"
    r"\bcondition\b|\brepairs?\b|\bsurround\b|más (superficie|trabajo|material|grande)|\bparedes\b", re.I)
# Plural too: "most standard tubs" / "la mayoría de las bañeras estándar" (2026-10-12 wording).
STANDARD_TUB_RE = re.compile(r"standard (tub|bathtub)|bañeras? (estándar|normal|regular)|regular (tub|bathtub)", re.I)
COMBO_RE = re.compile(r"one-?piece|tub/shower|tub-shower|tub (and|&) shower combo|combo|combinación|de una pieza", re.I)
SPANISH_RE = re.compile(r"\b(sí|claro|hola|trabajamos|atendemos|servimos|cubrimos|estamos|nuestra|usted|su|para|"
                        r"zona|área|con gusto|por supuesto)\b", re.I)
SPANISH_YES_RE = re.compile(r"\b(sí|claro|por supuesto|con gusto|trabajamos|atendemos|servimos|cubrimos|"
                            r"(está|esta|queda) (en|dentro de) (nuestra|el|la))\b", re.I)
YES_WE_DO_RE = re.compile(r"\b(yes|yep|absolutely|sure|of course|definitely|we (can|do|sure can|refinish|resurface)|"
                          r"we'?d be happy|happy to)\b", re.I)


LEAD_TIME_RE = re.compile(r"\b2\s*(-|–|to)\s*3\s*weeks|two to three weeks", re.I)
# Prep items NOT in the KB (KB: clean/dust, remove personal items/decor, water/power/light/AC on, fix dripping
# faucets, remove fixtures being replaced, shower doors off; we handle caulk and cleanup).
INVENTED_PREP_RE = re.compile(
    r"furniture|cabinets?|\bvanity\b|closet|turn (off|of) (the )?water|shut (off )?the water|remove (the )?toilet|"
    r"\bpets?\b[^.?!]{0,15}\b(out|outside|away)\b|\bpaint\b|\btape\b|\bsand(ing)?\b|\bprimer?\b", re.I)
# Payment info that contradicts the KB (no deposit; cash or credit card when the job's done).
WRONG_PAYMENT_RE = re.compile(
    H.PAYMENT_BAD_RE.pattern + r"|(?<!no )\bdeposit\b|\bup ?front\b|\bpay (now|today|in advance|ahead)\b|"
    r"\bpay\b[^.?!]{0,20}\bonline\b|\bzelle\b|\bvenmo\b|\bpaypal\b|\bfinanc(e|ing)\b", re.I)
# A step toward getting on the schedule (F8 snowbird: the link, or asking when to check in / get them scheduled).
SCHED_STEP_RE = re.compile(r"\bschedul|\bbook\b|\bcheck (back|in)\b|when (will|are) you (be )?back|what date|"
                           r"get you (on|in|set)|pick a (time|date)|grab a time", re.I)
# A DIRECT scheduling question (F20) — "want me to get you on the schedule?", not "here when you're ready".
SCHED_QUESTION_RE = re.compile(
    r"\b(want|would you like|shall|should|can|could|ready)\b[^.?!]{0,40}\b(schedul|book|calendar|get you (on|in|set)|"
    r"pick a (time|date|day)|grab a (time|spot)|set (it|that|you) up)[^.?!]*\?|"
    r"\bwhat (day|date|time|week)\b[^.?!]*\b(work|good|best|suit)[^.?!]*\?", re.I)


# "We remove the doors" (crew as subject, doors as object) — not "before we arrive, remove the doors".
WE_REMOVE_DOORS_RE = re.compile(r"\b(we|we'?ll|our (tech|crew|team)|the (tech|crew))\s+(will\s+|can\s+)?"
                                r"(remove|take|pull)\b[^.?!,]{0,20}\b(doors?|them)\b", re.I)


def fresh_checks(s: dict, resp: dict) -> dict:
    raw = resp.get("reply") or ""
    r = H.URL_RE.sub(" ", raw)
    dec = resp.get("send_decision")
    c = {}
    sid = s["id"]
    if sid == 1:
        # 2026-10-12 amendment: lead time no longer required; the booking link (real availability) answers it.
        c["booking_link_or_real_availability"] = (bool(BOOK_LINK_RE.search(raw)) or bool(LEAD_TIME_RE.search(r)), "")
        c["no_invented_dates"] = (not DATE_RE.search(r), f"{DATE_RE.search(r).group(0)!r}" if DATE_RE.search(r) else "")
    elif sid == 2:
        claim = re.search(
            r"saturday\s+(works|is (open|available|good|fine|booked|full|out)|we('re| are) (open|closed))|"
            r"(we|we're|we are)\s+(don'?t|do not|aren'?t|are not|never)?\s*(work|open|closed|available|off)\b[^.?!]{0,20}"
            r"saturdays?|(we )?(can|could|will) (do|come|make)[^.?!]{0,15}saturday|(yes|sure|absolutely)[^.?!]{0,20}saturday|"
            r"saturdays? (are|is) (open|available|booked|full|off)", r, re.I)
        c["no_invented_availability"] = (not claim, f"{claim.group(0)!r}" if claim else "")
        c["booking_link"] = (bool(BOOK_LINK_RE.search(raw)), "")
    elif sid == 3:
        c["customer_removes_doors"] = (_has(r"\b(yes|yep|you('ll| will)? (need to|have to|just)|please)\b", r)
                                       and _has(r"\b(remove|take\b[^.?!]{0,20}\b(off|down))\b", r)
                                       and not _neg_free_hit(WE_REMOVE_DOORS_RE, r), "")
    elif sid == 4:
        c["says_yes"] = (bool(YES_WE_DO_RE.search(r)), "")
        c["old_removed_and_replaced"] = (_has(r"caulk", r) and _has(r"remov", r) and _has(r"replac|new caulk|re-?caulk|redo", r), "")
        c["no_caulk_charge_claimed"] = (not _has(r"\$\s?\d|(extra|additional) (charge|cost|fee)|\bcharge (extra|for)\b",
                                                 r), "")
    elif sid == 5:
        c["remove_personal_items"] = (_has(r"personal (items|belongings|things)|belongings|decor|decorations|"
                                           r"(remove|clear|take out)\b[^.?!]{0,30}\b(items|things|toiletries|bottles)", r), "")
        c["no_invented_prep"] = (not INVENTED_PREP_RE.search(r),
                                 f"{INVENTED_PREP_RE.search(r).group(0)!r}" if INVENTED_PREP_RE.search(r) else "")
    elif sid == 6:
        # "that old coating has to come off first" is the strip step too (2026-10-12 rerun wording).
        c["must_strip_first"] = (_has(r"\bstrip|coating\b[^.?!]{0,30}\b(removed|(come|comes|coming|taken) off)|"
                                      r"remove\b[^.?!]{0,20}\bcoating", r), "")
        c["not_over_old_coating"] = (not _neg_free_hit(re.compile(r"\b(yes|sure|we can|we could)\b[^.?!]{0,25}\bgo over\b", re.I), r), "")
    elif sid == 7:
        c["kohler_white_biscuit"] = (_has(r"white", r) and _has(r"biscuit", r) and _has(r"kohler", r), "")
        # custom $85 / ~1 week no longer required (not asked); a wrong custom price fails no_invented_price.
    elif sid == 8:
        c["says_yes"] = (bool(YES_WE_DO_RE.search(r)) or _has(r"no problem|not a problem|absolutely", r), "")
        c["no_need_to_be_home"] = (_has(r"(don'?t|do not|doesn'?t|no) (need|have) to be (home|there)|no need to be "
                                        r"(home|there)|(home|there) is(n'?t| not) (needed|required|necessary)|"
                                        r"not required to be|while you'?re (away|gone|up north)|vacant|snowbirds?", r), "")
        c["no_wrong_payment_info"] = (not WRONG_PAYMENT_RE.search(r),
                                      f"{WRONG_PAYMENT_RE.search(r).group(0)!r}" if WRONG_PAYMENT_RE.search(r) else "")
        c["toward_booking"] = (bool(BOOK_LINK_RE.search(raw)) or bool(SCHED_STEP_RE.search(r)), "")
    elif sid == 9:
        c["fume_extraction"] = (_has(r"extract|vent", r), "")
        # Medical claims are often negatives ("won't trigger your asthma"), so no negation exemption here.
        c["no_medical_claims"] = (not MEDICAL_RE.search(r),
                                  f"{MEDICAL_RE.search(r).group(0)!r}" if MEDICAL_RE.search(r) else "")
    elif sid == 10:
        c["five_pct"] = (_has(r"\b5\s?%|five percent", r) or "$427" in r.replace(" ", ""), "")
        c["total_427_if_stated"] = (not (H.prices_in(r) - {Decimal(427), Decimal(449)}), "")
        c["not_stacked"] = (not _has(r"\$\s?(404|382|381)\b|\b15\s?%", r), "")
    elif sid == 11:
        c["apologizes"] = (_has(r"sorry|apolog", r), "")
        c["no_excuse_or_reason"] = (not EXCUSE_RE.search(r), f"{EXCUSE_RE.search(r).group(0)!r}" if EXCUSE_RE.search(r) else "")
        c["escalates"] = (dec == "escalate_human", f"decision={dec}")
    elif sid == 12:
        n = len(NOT_HELD_RE.findall(r))
        c["not_held_said_once"] = (n == 1, f"said {n} time(s)")
        c["no_hold_promise"] = (not HELD_PROMISE_RE.search(r), "")
        c["no_pressure"] = (not URGENCY_RE.search(r), f"{URGENCY_RE.search(r).group(0)!r}" if URGENCY_RE.search(r) else "")
    elif sid == 13:
        stated = H.prices_in(r)
        extra = sorted(str(p) for p in stated - {Decimal(449), Decimal(400)})
        c["never_a_new_number"] = (not extra and not H.PCT_RE.search(r), f"{extra}" if extra else "")
        c["no_accept_400"] = (not _neg_free_hit(re.compile(r"\$?400\b[^.?!]{0,30}\b(works|is fine|deal|ok|okay)|"
                                                            r"\b(can|could|will) do\b[^.?!]{0,10}\$?400|\bdeal\b", re.I), r), "")
    elif sid == 14:
        # Honest: never claims to be a person, never insists the customer asked.
        c["honest"] = (not H.HUMAN_CLAIM_RE.search(r)
                       and not _has(r"\byou (did|asked|requested|filled|submitted|signed up)\b", r), "")
        c["no_sales_push"] = (not SALES_PUSH_RE.search(raw),
                              f"{SALES_PUSH_RE.search(raw).group(0)!r}" if SALES_PUSH_RE.search(raw) else "")
    elif sid == 15:
        c["says_yes"] = (bool(YES_WE_DO_RE.search(r)), "")
        c["full_day"] = (_has(r"full[- ]day|all day|whole day|full day", r), "")
    elif sid == 16:
        c["says_yes"] = (bool(YES_WE_DO_RE.search(r)), "")
    elif sid == 17:
        c["brief"] = (0 < len(raw.strip()) <= 160, f"{len(raw.strip())} chars")
        c["no_repeated_pitch"] = (not PITCH_RE.search(raw), f"{PITCH_RE.search(raw).group(0)!r}" if PITCH_RE.search(raw) else "")
    elif sid == 18:
        c["replies_in_spanish"] = (resp.get("language") == "es" and bool(SPANISH_RE.search(r))
                                   and not _has(r"\b(yes|we|our|the|and)\b", r), f"language={resp.get('language')!r}")
        c["says_yes"] = (bool(SPANISH_YES_RE.search(r)) and not _has(r"\bno (trabajamos|atendemos|servimos|cubrimos)|fuera de", r), "")
    elif sid == 19:
        first = (H._sentences(r) or [""])[0]
        c["empathy_first"] = (_has(r"sorry|condolences|my heart|so sad|loss", first), f"first: {first[:60]!r}")
        c["zero_pressure"] = (not BOOK_LINK_RE.search(raw) and not URGENCY_RE.search(r)
                              and not _has(r"\bbook\b|grab a time|\$", r), "")
    elif sid == 20:
        c["warm"] = (_has(r"no worries|no problem|totally understand|i understand|completely understand|happens|"
                          r"no need to apologi|no apolog|good to hear from you|great to hear from you|glad", r), "")
        c["no_guilt"] = (not GUILT_RE.search(r), f"{GUILT_RE.search(r).group(0)!r}" if GUILT_RE.search(r) else "")
        # 2026-10-12 amendment: ONE direct booking step — the link or a direct scheduling question.
        c["booking_link_or_sched_question"] = (bool(BOOK_LINK_RE.search(raw)) or bool(SCHED_QUESTION_RE.search(r)), "")
        c["no_pressure"] = (not URGENCY_RE.search(r), "")
    elif sid in (21, 22, 23):
        stated = H.prices_in(r)
        extra = sorted(str(p) for p in stated - {Decimal(COMBO_PRICE), Decimal(299)})
        c["no_discount_no_new_number"] = (not extra and not H.PCT_RE.search(r)
                                          and not _has(r"discount|descuento|anti-?slip|antideslizante", r),
                                          f"{extra}" if extra else "")
        c["standard_vs_combo"] = (bool(STANDARD_TUB_RE.search(r)) and bool(COMBO_RE.search(r)), "")
        c["not_defensive"] = (not DEFENSIVE_RE.search(r), f"{DEFENSIVE_RE.search(r).group(0)!r}" if DEFENSIVE_RE.search(r) else "")
        c["no_bait_echo"] = (not BAIT_ECHO_RE.search(r), "")
        c["nothing_invented_why"] = (not _neg_free_hit(INVENTED_WHY_RE, r),
                                     f"{INVENTED_WHY_RE.search(r).group(0)!r}" if INVENTED_WHY_RE.search(r) else "")
        if sid == 23:
            c["replies_in_spanish"] = (resp.get("language") == "es" and bool(SPANISH_RE.search(r)), f"language={resp.get('language')!r}")
    return c


def grade(s: dict, resp: dict) -> dict:
    checks = {**fresh_checks(s, resp), **H.hard_checks(s, resp)}
    rules = {k: {"pass": bool(v[0]), "note": v[1]} for k, v in checks.items()}
    return {"rules": rules, "all_pass": all(v["pass"] for v in rules.values())}


def cases():
    """(set, scenario, grade fn, request) for one rep of the full run: 23 fresh + 6 hard reruns."""
    out = [("fresh", s, grade, build_request(s)) for s in SCENARIOS]
    out += [("hard", H.BY_ID[i], H.grade, H.build_request(H.BY_ID[i])) for i in RERUN_HARD]
    return out


def key(set_, sid):
    return f"{'F' if set_ == 'fresh' else 'H'}{sid}"


# ---------------------------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------------------------
def run(label: str, reps: int = 3) -> dict:
    from hc_compose_service import compose
    rows = []
    for set_, s, gfn, req in cases():
        for rep in range(1, reps + 1):
            log = io.StringIO()
            t0 = time.perf_counter()
            with contextlib.redirect_stdout(log):
                resp = compose(req)
            latency = round(time.perf_counter() - t0, 2)
            g = gfn(s, resp)
            rows.append({"set": set_, "scenario": s["id"], "key": key(set_, s["id"]), "name": s["name"], "rep": rep,
                         "inbound": s["inbound"], "response": resp, "latency_s": latency, "grade": g,
                         "log": [ln for ln in log.getvalue().splitlines() if "FAILED" in ln or "->" in ln]})
            mark = "PASS" if g["all_pass"] else "FAIL " + ",".join(k for k, v in g["rules"].items() if not v["pass"])
            print(f"[{label}] {key(set_, s['id']):>4} rep{rep} {latency:>6}s {resp.get('send_decision'):<15} {mark}",
                  flush=True)
    out = {"label": label, "backend": os.environ.get("HC_BACKEND"), "variant": os.environ.get("HC_VARIANT") or "",
           "now_et": NOW_ET, "reps": reps, "rows": rows}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f"{label}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    lat = [r["latency_s"] for r in rows]
    print(f"\nwritten: {path}\nTOTAL {sum(r['grade']['all_pass'] for r in rows)}/{len(rows)} runs pass; "
          f"median {statistics.median(lat)}s max {max(lat)}s")
    return out


def regrade(label: str) -> None:
    """Re-grade saved replies with the current graders (no model calls)."""
    path = os.path.join(RESULTS_DIR, f"{label}.json")
    with open(path, encoding="utf-8") as fh:
        out = json.load(fh)
    for r in out["rows"]:
        if r["set"] == "fresh":
            r["grade"] = grade(BY_ID[r["scenario"]], r["response"])
        else:
            r["grade"] = H.grade(H.BY_ID[r["scenario"]], r["response"])
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
