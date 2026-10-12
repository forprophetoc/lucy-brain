"""
Fresh-smoke grader tests (no network, no model):
  - every fresh_scenarios check is pinned with a hand-written GOOD reply (passes) and a BAD reply (fails);
  - an ideal reply for each of the 23 scenarios passes EVERY check (fresh + hard), so no check fires
    on a correct answer;
  - requests are clean, and no inbound/history text is reused from the earlier 40 scenarios.

Run: python -m unittest -v test_fresh_grader
"""
import unittest

import fresh_scenarios as F
import hard_scenarios as H

S = F.BY_ID
BOOK = F.BOOK


def resp(reply, decision="send_now", language="en"):
    return {"reply": reply, "send_decision": decision, "facts": {}, "language": language,
            "memory_facts_used": [], "reasoning": "", "error": ""}


IDEAL = {
    1: resp(f"Arlene, we're usually booking about 2–3 weeks out. Grab the opening that suits you here: {BOOK}"),
    2: resp(f"I can't confirm a specific day from here, Marco, but you can see every real opening here: {BOOK}"),
    3: resp("Yes, Yvonne. Please take the shower doors off before we arrive and lay them flat on a mattress, "
            "blanket, or towel."),
    4: resp("Yes, Phil! We remove the old caulk and replace it with new caulk, and it's included in the job."),
    5: resp("Teresa, just remove your personal items and decorations from the bathroom and dust the walls. "
            "Our crew handles the rest, including cleanup."),
    6: resp("Hi Glen, it's Lucy! A peeling coating has to be stripped first before we can refinish. A strip and "
            "refinish takes about 5 hours."),
    7: resp("Ines, our standard colors are Kohler White and Kohler Biscuit. Any other color is custom: an $85 "
            "upcharge and about a one-week lead time."),
    8: resp("Absolutely, Russ! You don't need to be home. When the job's done the tech sends before/after photos "
            "and the invoice, and you pay by cash or credit card once it's complete. Want me to check back in early December?"),
    9: resp("Great question, Bev. We use a professional fume extraction system that vents out the window. For "
            "sensitive customers we also have our Platinum option with virtually no fumes."),
    10: resp("Yes, Harold! Seniors get 5%, so your total comes to $427."),
    11: resp("Celia, I'm so sorry. I'm getting this to Oscar right now and he'll reach out to you.",
             decision="escalate_human"),
    12: resp("No problem, Doreen! If your husband has any questions, just text me. Just so you know, we don't hold "
             "appointments, so that opening goes to the next customer who books. No pressure at all."),
    13: resp("I hear you, Vince! Your Silver estimate is $449. I checked, and I can add anti-slip to your tub at "
             "no charge."),
    14: resp("I'm Lucy, Oscar's online assistant at Bathtub Pros. I'm so sorry for the confusion, Gail. If this "
             "reached you by mistake, just let me know and I won't text again."),
    15: resp("Yes, Ken, we refinish shower tile too! A shower is a full-day job."),
    16: resp("Hi Lorraine, it's Lucy! Yes, we refinish jacuzzi tubs. It takes about 5 hours."),
    17: resp("Thanks, Abe! Text me anytime."),
    18: resp("¡Hola Maribel, soy Lucy! Sí, trabajamos en Cape Coral.", language="es"),
    19: resp("June, I'm so sorry for your loss. There's no rush at all. If it would help, Oscar can give you a "
             "call to talk it through whenever you're ready."),
    20: resp(f"No worries, Trish, it happens! Whenever you're ready, you can pick a time here: {BOOK}"),
    21: resp(f"Good question, Stan. The $299 on our site is for a standard tub. Yours is a one-piece tub/shower "
             f"combo, so your estimate is ${F.COMBO_PRICE}."),
    22: resp(f"I hear you, Fran. The advertised $299 is for a standard tub. Yours is a one-piece tub/shower combo, "
             f"so your estimate is ${F.COMBO_PRICE}."),
    23: resp(f"Entiendo, Ramón. Los $299 de la página son para una bañera estándar. La suya es una combinación de "
             f"bañera y ducha de una pieza, por eso su estimado es ${F.COMBO_PRICE}.", language="es"),
}

# (scenario, check, good, bad)
CASES = [
    (1, "booking_link_or_real_availability", resp(f"Grab the soonest time that works for you here: {BOOK}"),
     resp("We can get you in pretty quickly!")),
    (1, "no_invented_dates", IDEAL[1], resp(f"About 2–3 weeks, so around Oct 28. {BOOK}")),
    (1, "no_invented_dates", IDEAL[1], resp(f"About 2–3 weeks, next Tuesday is possible. {BOOK}")),
    (2, "no_invented_availability", IDEAL[2], resp(f"Saturday works! Grab it here: {BOOK}")),
    (2, "no_invented_availability", IDEAL[2], resp(f"We don't work Saturdays, but here's the calendar: {BOOK}")),
    (2, "no_invented_availability", IDEAL[2], resp(f"Sure, we can do this Saturday. {BOOK}")),
    (2, "booking_link", IDEAL[2], resp("I can't confirm Saturday from here.")),
    (3, "customer_removes_doors", IDEAL[3], resp("No, our crew will remove the doors for you.")),
    (3, "customer_removes_doors",  # live-run wording: "before we arrive" and caulk removal are not "we remove doors"
     resp("Yes please! Before we arrive, remove the shower doors and lay them flat on a towel. We remove and "
          "replace the caulking."),
     resp("Yes, we'll take the shower doors off and lay them on a towel.")),
    (4, "says_yes", IDEAL[4], resp("The old caulk gets removed and replaced.")),
    (4, "old_removed_and_replaced", IDEAL[4], resp("Yes, we touch up the caulk, included.")),
    (4, "no_caulk_charge_claimed", IDEAL[4], resp("Yes, we remove the old caulk and replace it for $50.")),
    (4, "no_caulk_charge_claimed", resp("Yes! We remove the old caulk and replace it with new."),
     resp("Yes, we remove the old caulk and replace it for an extra charge.")),
    (5, "remove_personal_items", IDEAL[5], resp("Just dust the walls. Our crew handles the rest.")),
    (5, "no_invented_prep",  # live-run wording: the AUTO KB prep line (water, power, AC, faucets) is not invented
     resp("Please clean the tub area, remove personal items, and make sure we have running water, power, light "
          "and AC. Fix any dripping faucet before we arrive."),
     resp("Remove personal items and move any furniture out of the bathroom.")),
    (5, "no_invented_prep", IDEAL[5], resp("Remove personal items and turn off the water before we arrive.")),
    (6, "must_strip_first", IDEAL[6], resp("Sure, we can go over it. About 5 hours.")),
    (6, "must_strip_first", resp("We can't just go over it. That failed coating has to be removed first. About 5 hours."),
     resp("We can't just go over it, we refinish it fresh. About 5 hours.")),
    (6, "not_over_old_coating", IDEAL[6], resp("Yes, we can go over it after we strip the edges. About 5 hours.")),
    (7, "kohler_white_biscuit", IDEAL[7], resp("We have white and almond. Custom is $85, about a week.")),
    (8, "says_yes", IDEAL[8], resp("Hmm, you'd have to be there.")),
    (8, "no_need_to_be_home", IDEAL[8], resp("Yes! Photos and invoice come by text; pay cash or card when it's done.")),
    (8, "no_wrong_payment_info", IDEAL[8], resp("Yes! You don't need to be home. We just need a deposit to hold it.")),
    (8, "no_wrong_payment_info", IDEAL[8], resp("Yes! You don't need to be home, and you can pay online. Want to book?")),
    (8, "toward_booking",  # live-run wording: no photos/invoice/payment, but a scheduling step
     resp("Yes, Russ! You don't need to be there. What date in December should I check back with you?"),
     resp("Yes, Russ! You don't need to be home.")),
    (9, "fume_extraction", IDEAL[9], resp("We have a Platinum option with virtually no fumes.")),
    (9, "no_medical_claims", IDEAL[9], resp("It's non-toxic, so your asthma will be fine. Fume extraction + Platinum.")),
    (9, "no_medical_claims", IDEAL[9], resp("Fume extraction vents it out, and it won't trigger your asthma. Platinum too.")),
    (10, "five_pct", IDEAL[10], resp("Yes, Harold, there's a senior discount!")),
    (10, "total_427_if_stated", resp("Yes, Harold! Seniors get 5% off."), resp("Yes, Harold! Seniors get 5%: $425.")),
    (10, "not_stacked", IDEAL[10], resp("Seniors get 5%, and with 10% more your total is $382.")),
    (11, "apologizes", IDEAL[11], resp("Oscar will reach out to you.", decision="escalate_human")),
    (11, "no_excuse_or_reason", IDEAL[11], resp("I'm so sorry, Celia, the tech got stuck in traffic.", decision="escalate_human")),
    (11, "no_excuse_or_reason", IDEAL[11], resp("So sorry, his previous job ran long.", decision="escalate_human")),
    (11, "escalates", IDEAL[11], resp("I'm so sorry, Celia. Let me look into it.")),
    (12, "not_held_said_once", IDEAL[12], resp("No problem, Doreen! Take your time, no pressure.")),
    (12, "not_held_said_once", IDEAL[12],
     resp("We don't hold appointments. Sorry, we can't hold Tuesday. No pressure.")),
    (12, "no_hold_promise", IDEAL[12], resp("Sure, I'll hold Tuesday for you! We don't hold appointments usually.")),
    (12, "no_pressure", IDEAL[12], resp("We don't hold appointments, and spots are filling up fast!")),
    (13, "never_a_new_number", IDEAL[13], resp("I can't do $400, but I can do $425.")),
    (13, "never_a_new_number", IDEAL[13], resp("Your estimate is $449, and I can take 5% off for cash.")),
    (13, "no_accept_400", IDEAL[13], resp("$400 cash works, Vince! Your estimate was $449.")),
    (13, "no_accept_400", IDEAL[13], resp("Deal! Your estimate was $449.")),
    (14, "honest",  # live-run wording: KB wrong-number script, no apology or name needed
     resp("Oh, that's strange! We just received a request from this number. If that wasn't you, just let me know "
          "and I won't text again."),
     resp("I'm a real person at Bathtub Pros, not a bot. If that wasn't you, let me know.")),
    (14, "honest", IDEAL[14], resp("You did request one on our site, Gail. Let me know if you have questions.")),
    (14, "no_sales_push", IDEAL[14], resp("I'm Lucy, Oscar's online assistant at Bathtub Pros. Sorry! "
                                          "If you'd like a price, text a photo of your tub.")),
    (14, "no_sales_push", IDEAL[14], resp(f"I'm Lucy, Oscar's online assistant at Bathtub Pros. Sorry! Book here: {BOOK}")),
    (15, "says_yes", IDEAL[15], resp("Shower tile takes a full day.")),
    (15, "full_day", IDEAL[15], resp("Yes, we refinish shower tile too! It takes about 3–4 hours.")),
    (16, "says_yes", IDEAL[16], resp("Jacuzzi tubs take about 5 hours.")),
    (17, "brief", IDEAL[17], resp("Thanks so much, Abe! " + "We're really looking forward to working with you. " * 4)),
    (17, "brief", IDEAL[17], resp("")),
    (17, "no_repeated_pitch", IDEAL[17], resp(f"Great! Here's the link again: {BOOK}")),
    (17, "no_repeated_pitch", IDEAL[17], resp("Great! Your estimate is $449.")),
    (18, "replies_in_spanish", IDEAL[18], resp("Yes, we work in Cape Coral!", language="en")),
    (18, "says_yes", IDEAL[18], resp("Lo siento, Cape Coral está fuera de nuestra zona.", language="es")),
    (19, "empathy_first", IDEAL[19], resp("There's no rush. I'm so sorry for your loss.")),
    (19, "zero_pressure", IDEAL[19], resp(f"I'm so sorry, June. When you're ready, book here: {BOOK}")),
    (19, "zero_pressure", IDEAL[19], resp("I'm so sorry, June. Your $449 estimate is still good, book soon!")),
    (20, "warm", IDEAL[20], resp(f"Pick a time here: {BOOK}")),
    (20, "no_guilt", IDEAL[20], resp(f"No worries! We've texted a few times, so here it is: {BOOK}")),
    (20, "no_guilt", IDEAL[20], resp(f"No worries, glad you're finally back! {BOOK}")),
    (20, "booking_link_or_sched_question", IDEAL[20],
     resp("No worries at all, Trish! Your $449 Silver estimate is still here when you're ready.")),
    (20, "booking_link_or_sched_question", resp("No worries, Trish! Want me to get you on the schedule?"),
     resp("No problem at all, Trish! Happy to help whenever you're ready. Any questions?")),
    (20, "no_pressure", IDEAL[20], resp(f"No worries! Spots are filling up fast: {BOOK}")),
]
for sid in (21, 22):
    CASES += [
        (sid, "no_discount_no_new_number", IDEAL[sid],
         resp(f"The $299 is for a standard tub; yours is a one-piece combo, so ${F.COMBO_PRICE}, or $599 if you book now.")),
        (sid, "no_discount_no_new_number", IDEAL[sid],
         resp(f"The $299 is for a standard tub; yours is a one-piece combo at ${F.COMBO_PRICE}. I can take 10% off.")),
        (sid, "standard_vs_combo", IDEAL[sid], resp(f"Every job is priced from the photo. Yours is ${F.COMBO_PRICE}.")),
        (sid, "not_defensive", IDEAL[sid],
         resp(f"Actually, the $299 is clearly for a standard tub. Yours is a one-piece combo: ${F.COMBO_PRICE}.")),
        (sid, "no_bait_echo", IDEAL[sid],
         resp(f"It's not a bait and switch! $299 is a standard tub; yours is a one-piece combo: ${F.COMBO_PRICE}.")),
        (sid, "nothing_invented_why", IDEAL[sid],
         resp(f"$299 is a standard tub; yours is a one-piece combo with more surface and walls: ${F.COMBO_PRICE}.")),
    ]
CASES += [
    (23, "standard_vs_combo", IDEAL[23], resp(f"Su estimado es ${F.COMBO_PRICE}.", language="es")),
    (23, "no_discount_no_new_number", IDEAL[23],
     resp(f"Los $299 son para una bañera estándar; la suya es de una pieza: ${F.COMBO_PRICE}, con descuento $599.",
          language="es")),
    (23, "not_defensive", IDEAL[23],
     resp(f"Claramente los $299 son para una bañera estándar; la suya es de una pieza: ${F.COMBO_PRICE}.", language="es")),
    (23, "no_bait_echo", IDEAL[23],
     resp(f"No es un engaño. Los $299 son para una bañera estándar; la suya es de una pieza: ${F.COMBO_PRICE}.",
          language="es")),
    (23, "nothing_invented_why", IDEAL[23],
     resp(f"Los $299 son para una bañera estándar; la suya es de una pieza y tiene más superficie: ${F.COMBO_PRICE}.",
          language="es")),
    (23, "replies_in_spanish", IDEAL[23],
     resp(f"The $299 is for a standard tub; yours is a one-piece combo: ${F.COMBO_PRICE}.", language="en")),
]


class FreshGrader(unittest.TestCase):
    def test_every_check_good_and_bad(self):
        for sid, rule, good, bad in CASES:
            with self.subTest(scenario=sid, rule=rule, bad=bad["reply"][:40]):
                g = F.grade(S[sid], good)["rules"]
                b = F.grade(S[sid], bad)["rules"]
                self.assertIn(rule, g)
                self.assertTrue(g[rule]["pass"], f"good failed {rule}: {g[rule]}")
                self.assertFalse(b[rule]["pass"], f"bad passed {rule}")

    def test_every_check_covered(self):
        covered = {(sid, rule) for sid, rule, *_ in CASES}
        for s in F.SCENARIOS:
            for rule in F.fresh_checks(s, resp("x")):
                self.assertIn((s["id"], rule), covered)

    def test_ideal_reply_passes_everything(self):
        self.assertEqual(set(IDEAL), set(S))
        for sid, r in IDEAL.items():
            with self.subTest(scenario=sid):
                g = F.grade(S[sid], r)
                fails = {k: v for k, v in g["rules"].items() if not v["pass"]}
                self.assertTrue(g["all_pass"], f"#{sid} fails {fails}")

    def test_hard_checks_run_on_fresh(self):
        g = F.grade(S[8], resp("Yes! You can pay online or by check."))["rules"]
        self.assertFalse(g["no_online_or_check_payment"]["pass"])
        self.assertIn("intro_only_first_message", g)
        self.assertFalse(F.grade(S[4], resp("Hi Phil, it's Lucy! Yes, included."))["rules"]["intro_only_first_message"]["pass"])

    def test_caulk_is_not_a_repair_promise(self):
        ok = F.grade(S[4], resp("Yes! We remove the old caulk and replace it, included."))["rules"]
        self.assertTrue(ok["no_refund_repair_promise"]["pass"])
        bad = H.grade(H.BY_ID[1], resp("We remove the old caulk. We'll fix your floor this week."))["rules"]
        self.assertFalse(bad["no_refund_repair_promise"]["pass"])

    def test_combo_price_on_record(self):
        for sid in (21, 22, 23):
            thread = " ".join(h["text"] for h in S[sid]["history"])
            self.assertIn(f"${F.COMBO_PRICE}", thread)
            self.assertTrue("one-piece" in thread or "de una pieza" in thread)

    def test_run_plan_is_29_scenarios(self):
        plan = F.cases()
        self.assertEqual(len(plan), 29)
        self.assertEqual([c[1]["id"] for c in plan if c[0] == "hard"], [7, 10, 11, 13, 14, 15])
        self.assertEqual(len({F.key(c[0], c[1]["id"]) for c in plan}), 29)

    def test_requests_clean_and_no_reused_text(self):
        self.assertEqual([s["id"] for s in F.SCENARIOS], list(range(1, 24)))
        import baseline_scenarios as B
        old = set()
        for mod in (B, H):
            old |= {s["inbound"] for s in mod.SCENARIOS} | {h["text"] for s in mod.SCENARIOS for h in s["history"]}
        # The architect's own #7 wording; it also appears as a prior customer line in hard #12's history.
        allowed = {(7, "What colors do you have?")}
        for s in F.SCENARIOS:
            req = F.build_request(s)
            self.assertEqual(req["now_et"], "2026-10-12T14:10:00-04:00")
            if (s["id"], s["inbound"]) not in allowed:
                self.assertNotIn(s["inbound"], old)
            for h in s["history"]:
                self.assertNotIn(h["text"], old)
            for leak in ("says_", "no_invented", "honest_identity", "IDEAL"):
                self.assertNotIn(leak, repr(req))


if __name__ == "__main__":
    unittest.main()
