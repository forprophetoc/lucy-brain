#!/usr/bin/env python3
"""
closing_scenarios.py — the 14 closing scenarios (C1–C10 should close, N1–N4 should not push), as data.
Grading and running live in spicy_exam.py (one grader for every scenario ever asked).

Histories are reused where a scenario matches an earlier one, so these are exact repeats and spicy_exam keeps
only the original copy: C1=F20, C2=F8, C3=F13, C4=F21, C5=hard #8, C6=F15, C9=F9, C10=F12, N1=F19,
N2=hard #1, N3=F11. New here: C7 (proactive due-date sweep on the follow-up Lucy promised), C8 (Bonnie's two
texts as one inbound, Gold combo) and N4 ("Stop texting me" after one follow-up).
"""
import fresh_scenarios as F
import hard_scenarios as H

NOW_ET = H.NOW_ET
_h = F._h
COMBO = F.COMBO

BONNIE = ("I received it but considerably more than on line prices. I will be using the tub to soak so will that "
          "still hold up? I'm getting two estimates and hubby would want to talk about what you actually do as we "
          "would do but health issues won't permit right now")

SCENARIOS = [
    dict(id="C1", name="Back after 3 follow-ups", ref=("F", 20), context="Estimate $449, 3 unanswered follow-ups"),
    dict(id="C2", name="Snowbird away until December", ref=("F", 8), context="Estimate $449"),
    dict(id="C3", name="$400 cash?", ref=("F", 13), context="Estimate $449"),
    dict(id="C4", name="Website $299 vs combo quote", ref=("F", 21), context=f"Estimate ${F.COMBO_PRICE}, {COMBO}"),
    dict(id="C5", name="Guy down the street $250, match?", ref=("H", 8), context="Estimate $449"),
    dict(id="C6", name="Shower tile too, how long", ref=("F", 15), context="Estimate $449"),
    dict(id="C7", name="Promised follow-up after meeting wife (sweep)", first="Wes",
         context="Estimate $449 Silver; Lucy promised to text Monday (due_date_sweep)", trigger="due_date_sweep",
         history=F.quote_thread("Wes") + _h(
             ("customer", "Meeting my wife this weekend, will have an answer for you Monday.",
              "2026-10-08T17:20:00-04:00"),
             ("lucy", "Sounds good, Wes! I'll text you Monday.", "2026-10-08T17:22:00-04:00")),
         inbound=""),
    dict(id="C8", name="Bonnie: soak, two estimates, hubby", first="Bonnie",
         context=f"Estimate ${F.COMBO_PRICE} {COMBO}, Gold",
         history=F.quote_thread("Bonnie", price=F.COMBO_PRICE, pkg=f"Gold {COMBO}"), inbound=BONNIE),
    dict(id="C9", name="Toxic? Asthma", ref=("F", 9), context="Estimate $449"),
    dict(id="C10", name="Hold Tuesday for husband (gentle)", ref=("F", 12), context="Estimate $449"),
    dict(id="C11", name="Firefighter discount", first="Dale", context="Estimate $449 Silver",
         history=F.quote_thread("Dale"), inbound="I'm a firefighter, any discount?"),
    dict(id="N1", name="Widow, husband handled it", ref=("F", 19), context="Estimate $449"),
    dict(id="N2", name="Floor scratched, lawyer threat", ref=("H", 1), context="Job complete"),
    dict(id="N3", name="Tech no-show today", ref=("F", 11), context="Booked for today"),
    dict(id="N4", name="Stop texting me", first="Lou", context="Estimate $449 Silver, 1 follow-up",
         history=F.quote_thread("Lou") + _h(
             ("lucy", "Hi Lou! Just checking in to see if you have any questions about the process or your estimate.",
              "2026-10-09T10:15:00-04:00")),
         inbound="Stop texting me"),
]
for _s in SCENARIOS:
    if "ref" in _s:
        _src = F.BY_ID[_s["ref"][1]] if _s["ref"][0] == "F" else H.BY_ID[_s["ref"][1]]
        _s.update(first=_src["first"], history=_src["history"], inbound=_src["inbound"])
BY_ID = {s["id"]: s for s in SCENARIOS}


def build_request(s: dict) -> dict:
    return {
        "trigger": s.get("trigger", "inbound_reply"), "now_et": NOW_ET, "contact_id": f"CLOSE{s['id']}",
        "identity": {"first_name": s["first"], "last_name": "Test", "city": "Naples", "service": "tub_refinish"},
        "inbound_text": s["inbound"], "history": s["history"], "memory": {},
    }
