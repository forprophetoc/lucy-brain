"""
Grader unit tests (no network, no model): every hard rule in baseline_scenarios.grade() is pinned
with a hand-written GOOD reply (rule passes) and a BAD reply (rule fails).

Run: python -m unittest -v test_baseline_grader
"""
import unittest

import baseline_scenarios as B

S = {s["id"]: s for s in B.SCENARIOS}


def resp(reply, decision="send_now", facts=None, followup_at=None, language="en"):
    r = {"reply": reply, "send_decision": decision, "facts": facts or {}, "language": language,
         "memory_facts_used": [], "reasoning": "", "error": ""}
    if followup_at:
        r["followup_at"] = followup_at
    return r


# (scenario, rule, good response, bad response)
CASES = [
    (1, "asks_photo_to_539",
     resp("Happy to help! Just text a photo of your tub to (239) 539-4777 and we'll send your exact price."),
     resp("Happy to help! A tub usually runs a few hundred dollars.")),
    (1, "no_price_or_range",
     resp("Text a photo of your tub to (239) 539-4777 and we'll send the exact price."),
     resp("Usually $299–$449. Text a photo of your tub to (239) 539-4777.")),
    (2, "states_449",
     resp("Your Gold estimate is $449, Sam!"),
     resp("Your estimate is in the link we sent.")),
    (3, "says_no_cost_to_you",
     resp("No cost to you, Sam! Any questions, just text me."),
     resp("Yes, it's on us!")),
    (3, "never_free",
     resp("No cost to you, Sam!"),
     resp("No cost to you, it's totally free!")),
    (4, "send_now",
     resp("You got it! I'll text you tomorrow at 2.", followup_at="2026-10-13T14:00:00-04:00"),
     resp("I'll pass this to Oscar.", decision="escalate_human")),
    (4, "followup_at_tomorrow_2pm",
     resp("You got it! I'll text you tomorrow at 2.", followup_at="2026-10-13T14:00:00-04:00"),
     resp("You got it! I'll text you tomorrow at 2.", followup_at="2026-10-13T10:00:00-04:00")),
    (5, "escalate",
     resp("I'll have Oscar give you a call.", decision="escalate_human"),
     resp("Sure, what time works?")),
    (6, "says_no",
     resp("We don't touch drains — that's licensed plumber work. We refinish right up to the edge."),
     resp("Great question! We refinish the whole tub.")),
    (6, "no_drain_removal_claim",
     resp("We never remove or replace drains; a licensed plumber handles that."),
     resp("Yes, we can replace the drain while we're there.")),
    (7, "says_no",
     resp("We don't offer steam cleaning, but we do refinish tubs and tile."),
     resp("Sure thing, we'll get that set up.")),
    (7, "no_unlisted_service",
     resp("We don't offer steam cleaning, but we do refinish tubs and tile."),
     resp("We don't do steam cleaning, but we can regrout your shower.")),
    (8, "names_tub_service",
     resp("We refinish tubs (including jacuzzi and soaking tubs), tub & tile, showers, sinks, and countertops."),
     resp("We do a little of everything!")),
    (8, "no_unlisted_service",
     resp("We refinish tubs, showers, sinks, countertops, plus chip repair and anti-slip."),
     resp("We refinish tubs and showers, and we also do cabinet painting.")),
    (9, "declines",
     resp("Sorry, Tampa is outside our service area — we cover Collier, Lee, Charlotte & Sarasota."),
     resp("Yes! We come out to Tampa.")),
    (10, "confirms_served",
     resp("Great news, Port Charlotte is in our service area!"),
     resp("Sorry, we don't serve Port Charlotte.")),
    (11, "says_3_to_4_hours",
     resp("A standard tub takes 3–4 hours."),
     resp("A tub takes about a day.")),
    (12, "out_until_next_morning",
     resp("The tub is out of service until the next morning."),
     resp("Sure, you can shower tonight!")),
    (12, "4h_only_if_unavoidable",
     resp("It's out of service until the next morning. If it's truly unavoidable, wait at least 4 hours."),
     resp("It's out until the next morning, or you can shower after 4 hours.")),
    (13, "offers_10pct",
     resp("Thank you for your service! Veterans get 10% off."),
     resp("Thank you for your service!")),
    (13, "not_combined",
     resp("Veterans get 10%; seniors get 5% — one or the other, not both."),
     resp("Veterans get 10% and seniors 5%, so you could get 15%!")),
    (14, "no_years_or_terms",
     resp("If our finish fails, it's covered; length depends on your package."),
     resp("You're covered for 5 years.")),
    (14, "no_guarantee_lifetime_nqa",
     resp("If our finish fails, it's covered."),
     resp("It comes with a lifetime warranty.")),
    (15, "no_spray_with_infant",
     resp("Congrats! We never spray while a newborn is in the home, so plan for baby to be out that day."),
     resp("Totally safe, no worries!")),
    (16, "send_now",
     resp("No problem! I'll check back in January.", facts={"followup_date": "2027-01-05"}),
     resp("", decision="escalate_human", facts={"followup_date": "2027-01-05"})),
    (16, "followup_in_january",
     resp("No problem! I'll check back in January.", facts={"followup_date": "2027-01-05"}),
     resp("No problem! I'll check back soon.", facts={"followup_date": "2026-11-01"})),
    (16, "no_pressure",
     resp("No problem! I'll check back in January. No pressure."),
     resp("Spots are filling up fast, so don't miss out!")),
    (17, "no_sales_content",
     resp("Understood, you won't hear from us again.", decision="escalate_human", facts={"disengaged": "opt_out"}),
     resp("Understood! Before you go, your $449 estimate is still good.", decision="escalate_human",
          facts={"disengaged": "opt_out"})),
    (17, "opt_out_flagged",
     resp("Understood, you won't hear from us again.", decision="escalate_human", facts={"disengaged": "opt_out"}),
     resp("Understood, you won't hear from us again.", decision="escalate_human")),
    (17, "escalated_for_dnc",
     resp("Understood, you won't hear from us again.", decision="escalate_human", facts={"disengaged": "opt_out"}),
     resp("Understood, you won't hear from us again.", facts={"disengaged": "opt_out"})),
    (18, "no_new_price",
     resp("I hear you. Your estimate is $449; it's smart to get 2–3 estimates."),
     resp("I hear you. I could do it for $399.")),
    (18, "calm",
     resp("I hear you, Sam. We're a fair price for a great product, no pressure."),
     resp("That is NOT a ripoff, we are the BEST.")),
    (19, "spanish_reply",
     resp("¡Hola Sam! Su presupuesto Gold es de $449.", language="es"),
     resp("Hi Sam! Your Gold estimate is $449.", language="en")),
    (19, "states_449",
     resp("¡Hola Sam! Su presupuesto es de $449.", language="es"),
     resp("¡Hola Sam! Está en el enlace.", language="es")),
    (19, "no_photo_ask",
     resp("¡Hola Sam! Su presupuesto es de $449.", language="es"),
     resp("¡Hola! Envíe una foto de su bañera.", language="es")),
    (20, "references_wife_answer",
     resp("Hi Sam! Did you get a chance to talk it over with your wife? Book here: https://calendar.bathtubpros.com"),
     resp("Hi Sam! Here's our booking page: https://calendar.bathtubpros.com")),
    (20, "moves_toward_booking",
     resp("Hi Sam! Did your wife have any questions? Grab a time here: https://calendar.bathtubpros.com"),
     resp("Hi Sam! Did your wife have any questions?")),
    (20, "sends",
     resp("Hi Sam! Did your wife have any questions? Book here: https://calendar.bathtubpros.com"),
     resp("", decision="escalate_human")),
    # common rules (any scenario)
    (2, "price_from_record",
     resp("Your Gold estimate is $449; custom colors are an $85 upcharge."),
     resp("Your Gold estimate is $449, or $599 for Platinum.")),
    (2, "no_banned_terms",
     resp("Your estimate is $449 — any questions, just text me."),
     resp("Your estimate is $449 — feel free to text me.")),
    (11, "no_banned_terms",
     resp("A standard tub takes 3–4 hours."),
     resp("A standard tub takes 3–4 hours, guaranteed.")),
    (11, "no_banned_terms",
     resp("A standard tub takes 3–4 hours."),
     resp("3–4 hours. Book today only for this spot, spots filling up!")),
    (14, "no_banned_terms",
     resp("If our finish fails, it's covered."),
     resp("Covered, no questions asked.")),
    (2, "texts_le_320",
     resp("Your estimate is $449.\n\n" + "a" * 300),
     resp("Your estimate is $449. " + "a" * 320)),
    (2, "texts_le_320",
     resp("Your estimate is $449."),
     resp("one\n\ntwo\n\nthree")),
    (11, "no_unlisted_service",
     resp("A standard tub takes 3–4 hours."),
     resp("3–4 hours. We also do mold remediation.")),
]


class GraderRules(unittest.TestCase):
    def test_every_rule_good_and_bad(self):
        for sid, rule, good, bad in CASES:
            with self.subTest(scenario=sid, rule=rule):
                g = B.grade(S[sid], good)["rules"]
                b = B.grade(S[sid], bad)["rules"]
                self.assertIn(rule, g)
                self.assertTrue(g[rule]["pass"], f"good reply failed {rule}: {g[rule]}")
                self.assertFalse(b[rule]["pass"], f"bad reply passed {rule}")

    def test_every_rule_has_a_case(self):
        covered = {(sid, rule) for sid, rule, _, _ in CASES}
        dummy = resp("x")
        for s in B.SCENARIOS:
            for rule in B.specific_checks(s, dummy):
                self.assertIn((s["id"], rule), covered, f"no good/bad case for #{s['id']} {rule}")
        common = {rule for _, rule, _, _ in CASES if rule in B.common_checks(S[2], dummy)}
        self.assertEqual(common, set(B.common_checks(S[2], dummy)))

    def test_all_pass_aggregates(self):
        good = resp("Your Gold estimate is $449, Sam!")
        self.assertTrue(B.grade(S[2], good)["all_pass"])
        self.assertFalse(B.grade(S[2], resp("It's free!"))["all_pass"])

    def test_twenty_scenarios_with_requests(self):
        self.assertEqual([s["id"] for s in B.SCENARIOS], list(range(1, 21)))
        for s in B.SCENARIOS:
            req = B.build_request(s)
            self.assertEqual(req["now_et"], "2026-10-12T14:10:00-04:00")
            blob = repr(req)
            for leak in ("asks_photo", "states_449", "expected"):
                self.assertNotIn(leak, blob)  # no grader text in the request
        self.assertEqual(B.build_request(S[20])["trigger"], "due_date_sweep")
        self.assertIn("$449", repr(B.build_request(S[2])["history"]))
        self.assertEqual(B.build_request(S[1])["history"], [])


if __name__ == "__main__":
    unittest.main()
