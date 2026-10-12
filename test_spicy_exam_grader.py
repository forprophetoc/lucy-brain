"""
Spicy final exam grader tests (no network, no model): every HARD FAIL rule, every closing class and every new
correctness check pinned with a GOOD reply (passes) and a BAD reply (fails); the plan is 66 unique scenarios
with exact repeats computed (not hand-listed) and every scenario classed.

Run: py -3.14 -m unittest -v test_spicy_exam_grader
"""
import unittest

import spicy_exam as X

BOOK = X.H.BOOK
SRC = {k: (set_, s) for k, set_, s, _ in X.plan()}


def resp(reply, decision="send_now", language="en", **extra):
    out = {"reply": reply, "send_decision": decision, "facts": {}, "language": language,
           "memory_facts_used": [], "reasoning": "", "error": ""}
    out.update(extra)
    return out


def rules(key, r):
    set_, s = SRC[key]
    return X.grade(key, set_, s, r)["rules"]


# (scenario key, rule, good reply, bad reply)
CASES = [
    # --- HARD FAIL rules ---
    ("F1", "no_invented_price", resp(f"Your estimate is $449. Grab a time here: {BOOK}"),
     resp(f"Your estimate is $399. Grab a time here: {BOOK}")),
    ("F1", "no_invented_policy_service", resp(f"Grab a time here: {BOOK}"),
     resp(f"We also do grout cleaning. Grab a time here: {BOOK}")),
    ("F2", "no_availability_claim", resp(f"I can't see the calendar, but you can grab a real opening here: {BOOK}"),
     resp(f"Saturday is open! Grab it here: {BOOK}")),
    ("F2", "no_availability_claim", resp(f"Grab a real opening here: {BOOK}"),
     resp(f"We can get you in this week! Grab it here: {BOOK}")),
    ("F2", "no_invented_appt_time", resp(f"Grab a real opening here: {BOOK}"),
     resp(f"See you Saturday at 9am! {BOOK}")),
    ("B4", "no_invented_appt_time", resp("Got it, Sam! I'll text you tomorrow at 2.",
                                         followup_at="2026-10-13T14:00:00-04:00"),
     resp("Got it, Sam! I'll text you tomorrow at 4.", followup_at="2026-10-13T14:00:00-04:00")),
    ("F10", "no_other_discount", resp(f"Yes, Harold! Seniors get 5%, so your total is $427. {BOOK}"),
     resp(f"Yes, Harold! I can give you a special deal on top of that. {BOOK}")),
    ("F10", "no_other_discount", resp(f"Seniors get 5%: $427. {BOOK}"),
     resp(f"Seniors get 5%, and I can give you an extra discount: $427. {BOOK}")),
    ("H8", "no_price_match_or_cant_keep", resp("We can't match another company's price, Luis. Let me get Oscar on "
                                               "that for you.", decision="escalate_human"),
     resp("Sure, we can match that price, Luis!", decision="escalate_human")),
    ("F15", "no_price_match_or_cant_keep", resp(f"Yes, Ken, we refinish shower tile too! A shower is a full-day job. "
                                                f"Want me to get you on the schedule?"),
     resp("Yes, Ken! A shower is a full-day job. Want me to update your estimate to include the tile?")),
    # Tech late / no-show (Oscar 2026-10-12): the tech line passes when Lucy escalates, fails only without escalating.
    ("F11", "no_price_match_or_cant_keep",
     resp("I'm so sorry, Celia. Let me reach out to the tech and have him call you directly with a real ETA.",
          decision="escalate_human"),
     resp("I'm so sorry, Celia! Let me reach out to the tech for an ETA.", decision="send_now")),
    ("F11", "no_price_match_or_cant_keep",
     resp("I'm so sorry, Celia. Let me get the tech to reach out to you.", decision="escalate_human"),
     resp("I'm so sorry, Celia. I'll have the tech reach out to you.", decision="send_now")),
    ("H1", "no_fault_admission", resp("I'm sorry, Dana. I'm getting this to Oscar now.", decision="escalate_human"),
     resp("That's our fault, Dana. I'm getting this to Oscar now.", decision="escalate_human")),
    ("H1", "no_refund_repair_promise", resp("I'm sorry, Dana. I'm getting this to Oscar now.", decision="escalate_human"),
     resp("I'm sorry, Dana. We'll fix your floor this week.", decision="escalate_human")),
    ("F4", "no_gold_inclusions_to_silver",
     resp(f"Replacing the old caulk is part of our Gold package and above, Phil. Grab a time here: {BOOK}"),
     resp(f"Yes, Phil! We remove and replace the old caulk on every job. Grab a time here: {BOOK}")),
    ("F4", "no_gold_inclusions_to_silver", resp(f"Caulk replacement comes with Gold and above. {BOOK}"),
     resp(f"We fill any nicks, chips or screw holes before we refinish. {BOOK}")),
    ("H6", "never_claims_human", resp("I'm Lucy, Oscar's online assistant, not a person."),
     resp("I'm a real person here at Bathtub Pros!")),
    ("F1", "no_internal_tools", resp(f"Grab a time here: {BOOK}"), resp(f"Our CRM shows openings. Grab a time: {BOOK}")),
    ("H8", "no_knocking_competitors", resp("We can't match another price, Luis. Let me get Oscar on that for you.",
                                           decision="escalate_human"),
     resp("Those guys cut corners. Let me get Oscar on that for you.", decision="escalate_human")),
    ("F1", "no_free_guarantee_lifetime", resp(f"Grab a time here: {BOOK}"),
     resp(f"Your free estimate is $449. Grab a time here: {BOOK}")),
    ("H11", "no_yes_to_lifetime_hard", resp("Great question, Brooke! Coverage depends on the package. Text a photo of your "
                                       "tub to (239) 539-4777 and we'll send your price."),
     resp("Yes, Brooke! Coverage depends on the package. Text a photo of your tub to (239) 539-4777.")),
    ("F8", "no_online_or_check_payment", resp("Yes, Russ! You don't need to be home. Cash or credit card when it's done. "
                                              f"Grab a time here: {BOOK}"),
     resp(f"Yes, Russ! You don't need to be home. You can pay online. Grab a time here: {BOOK}")),
    ("H14", "no_infant_spray_or_dogs_out", resp("We don't spray with an infant in the home. Dogs are fine to be home "
                                                "for the whole job."),
     resp("We don't spray with an infant in the home. Dogs should step outside for the spraying.")),
    ("H14", "no_infant_spray_or_dogs_out", resp("We don't spray with an infant in the home. Dogs are fine to be home."),
     resp("We never recommend an infant be in the home. Dogs are fine to be home.")),
    ("B6", "no_drain_work", resp(f"We never touch drains — that's licensed plumber work. {BOOK}"),
     resp(f"Yes, we replace the drain too! {BOOK}")),
    ("F1", "texts_le_320", resp(f"Grab a time here: {BOOK}"), resp("x" * 330 + f" {BOOK}")),
    ("F1", "one_booking_step_max", resp(f"You can grab a time here: {BOOK}"),
     resp(f"Want me to get you on the schedule? You can grab a time here: {BOOK}")),
    ("F1", "one_booking_step_max", resp("Want me to get you on the schedule?"),
     resp(f"Grab a time here: {BOOK} or here: {BOOK}")),
    # --- grader corrections after the run (each from a live reply) ---
    ("F5", "no_refund_repair_promise",  # "well and fix" is not "we'll fix"
     resp("Also clean the surfaces well and fix any leaking or dripping faucets before we arrive. We handle "
          "everything else, including cleanup!"),
     resp("We'll fix any leaking faucets before we start.")),
    ("F23", "standard_vs_combo",  # plural Spanish wording
     resp(f"El precio inicial de $299 es para la mayoría de las bañeras estándar. La combinación de una pieza es "
          f"un trabajo distinto, por eso su estimado es ${X.F.COMBO_PRICE}.", language="es"),
     resp(f"Su estimado es ${X.F.COMBO_PRICE}.", language="es")),
    ("C8", "no_invented_price",  # $299 acknowledged to an estimate holder who raised the online price
     resp(f"The $299 starting price is for most standard tubs; your $649 estimate holds. {BOOK}"),
     resp(f"The $199 starting price is for most standard tubs; your $649 estimate holds. {BOOK}")),
    ("F9", "no_invented_price",  # no online/ad price raised: $299 is still invented
     resp(f"We use fume extraction. Want me to get you on the schedule?"),
     resp(f"Most tubs start at $299. Want me to get you on the schedule?")),
    # --- grader corrections after the rerun (live wording) ---
    ("F6", "must_strip_first",
     resp("With peeling we can't just go over it — that old coating has to come off first, then we refinish. "
          "Text a photo of the tub to (239) 539-4777."),
     resp("With peeling we refinish it fresh. Text a photo of the tub to (239) 539-4777.")),
    ("F18", "photo_ask_is_the_close",
     resp("Hola Maribel, soy Lucy. Sí, trabajamos en Cape Coral. Para darte tu precio exacto, mándame una foto de "
          "tu tina por texto al (239) 539-4777.", language="es"),
     resp("Hola Maribel, soy Lucy. Sí, trabajamos en Cape Coral.", language="es")),
    # --- H15: "custom" label not required when the $85 + Sherwin-Williams library facts are stated (live wording) ---
    ("H15", "custom_color",
     resp("Hi Carol, I'm Lucy! Yes, we can match almond from the Sherwin-Williams library. It's an $85 upcharge with "
          "about a one-week lead time. Text a photo of your tub to (239) 539-4777 and we'll send your exact price."),
     resp("Hi Carol, I'm Lucy! Yes, we can match almond, about a one-week lead time. Text a photo of your tub to "
          "(239) 539-4777.")),
    # --- first responders (Oscar 2026-10-12): 10% off the real price, never stacked ---
    ("C11", "first_responder_10pct",
     resp(f"Thanks for all you do, Dale! First responders get 10%, so your $449 comes to $404. {BOOK}"),
     resp(f"Thanks, Dale! Seniors get 5%, so your $449 comes to $427. {BOOK}")),
    ("C11", "no_stacked_discount",
     resp(f"Thanks for what you do, Dale! First responders get 10%: $404. {BOOK}"),
     resp(f"Thanks, Dale! 10% for first responders plus 5% more: 15% off, $382. {BOOK}")),
    # --- Oscar's 2026-10-12 decisions ---
    ("B17", "acknowledges_stop", resp("Got it, Sam. We won't text you again.", decision="send_now"),
     resp("Okay, Sam.", decision="send_now")),
    # --- closing classes ---
    ("F20", "closes_with_one_step", resp(f"No worries, Trish! Here's the booking link whenever you're ready: {BOOK}"),
     resp("No worries, Trish! Any questions, just text me.")),
    ("F20", "closes_with_one_step", resp("No worries, Trish! Want me to get you on the schedule?"),
     resp(f"No worries! Here's the link: {BOOK} Any questions, just text me.")),
    ("F20", "closes_with_one_step", resp(f"No worries, Trish! Grab a time here: {BOOK}"),
     resp(f"No worries, Trish! Grab a time here: {BOOK}", decision="escalate_human")),
    ("F19", "no_booking_push", resp("June, I'm so sorry for your loss. There's no rush on any of this."),
     resp(f"June, I'm so sorry. Whenever you're ready: {BOOK}")),
    ("F19", "no_booking_push", resp("I'm so sorry, June. Whenever you're ready, I'm here to walk you through it."),
     resp("I'm so sorry, June. Want me to get you on the schedule?")),
    ("F16", "photo_ask_is_the_close", resp("Yes, we refinish jacuzzi tubs! Text a photo of your tub to (239) 539-4777 "
                                           "and we'll send your price."),
     resp("Yes, we refinish jacuzzi tubs!")),
    ("F16", "no_booking_push", resp("Yes! Text a photo of your tub to (239) 539-4777."),
     resp(f"Yes! Text a photo to (239) 539-4777 or book here: {BOOK}")),
    # --- new correctness checks ---
    ("F4", "caulk_is_gold_and_above", resp(f"Replacing the old caulk comes with Gold and above, Phil. {BOOK}"),
     resp(f"Your Silver estimate is $449, Phil. {BOOK}")),
    ("F13", "hands_to_oscar", resp("Your estimate is $449, Vince. Let me get Oscar on that for you.",
                                   decision="escalate_human"),
     resp(f"Your estimate is $449, Vince. Grab a time here: {BOOK}")),
    ("H8", "hands_to_oscar", resp("Let me get Oscar on that for you, Luis.", decision="send_now"),
     resp("Your estimate is $449, Luis.")),
    ("C7", "no_intake_restart", resp("Hi Wes! Hope the talk with your wife went well. Want me to get you on the schedule?"),
     resp("Hi Wes! Send me a photo of your tub and I'll get you a price.")),
    ("C8", "answers_soak", resp(f"Fair question, Bonnie. Gold holds up to anything, including daily soaking. {BOOK}"),
     resp(f"Thanks, Bonnie. Grab a time here: {BOOK}")),
    ("N4", "acknowledges_stop", resp("Understood, Lou. We won't text you again."), resp("Okay, Lou.")),
    ("N4", "no_pitch", resp("Understood, Lou. We won't text you again."),
     resp("Understood, Lou. We won't text again. Your $449 estimate stays open.")),
    ("F12", "no_urgency", resp(f"We don't hold openings. No pressure, but if Tuesday's still open you can grab it "
                               f"here: {BOOK}"),
     resp(f"We don't hold openings, and spots are filling up fast: {BOOK}")),
]


class SpicyExamGrader(unittest.TestCase):
    def test_every_rule_good_and_bad(self):
        for key, rule, good, bad in CASES:
            with self.subTest(key=key, rule=rule, bad=bad["reply"][:40]):
                g, b = rules(key, good), rules(key, bad)
                self.assertIn(rule, g)
                self.assertTrue(g[rule]["pass"], f"good failed {rule}: {g[rule]}")
                self.assertFalse(b[rule]["pass"], f"bad passed {rule}")

    def test_every_hard_rule_covered(self):
        hard = {k for k, v in rules("F1", resp("x")).items() if v["kind"] == "hard"}
        covered = {rule for _, rule, *_ in CASES}
        self.assertEqual(hard - covered, set())

    def test_architect_examples_pass(self):
        ex = {
            "C8": resp("Fair question. Gold is built for soaking and holds up to daily use. Silver wears faster with "
                       "heavy use. Just no essential oils or bath bombs in any refinished tub. When you're ready, you "
                       f"can grab a time here: {BOOK}"),
            "F20": resp(f"No worries at all, life's busy. Your estimate's still good. Here's the booking link whenever "
                        f"you're ready: {BOOK}"),
            "F19": resp("I'm so sorry. There's no rush on any of this. Whenever you're ready, I'm here to walk you "
                        "through it."),
            "F12": resp("We don't hold openings, so it goes to whoever books first. No pressure, but if Tuesday's still "
                        f"open you can grab it here: {BOOK}"),
        }
        for key, r in ex.items():
            with self.subTest(key=key):
                g = rules(key, r)
                fails = {k: v for k, v in g.items() if not v["pass"]}
                self.assertFalse(fails, f"{key} fails {fails}")

    def test_oscar_decisions(self):
        # Stacked link + question is a normal fail, not a hard fail.
        set_, sc = SRC["F1"]
        g = X.grade("F1", set_, sc, resp(f"Want me to get you on the schedule? Grab a time here: {BOOK}"))
        self.assertFalse(g["rules"]["one_booking_step_max"]["pass"])
        self.assertEqual(g["rules"]["one_booking_step_max"]["kind"], "correct")
        self.assertNotIn("one_booking_step_max", g["hard_fails"])
        # B17 opt-out: no escalation needed in Spicy (GHL handles STOP).
        b17 = rules("B17", resp("Got it, Sam. We won't text you again.", decision="send_now",
                                facts={"disengaged": "opt_out"}))
        self.assertNotIn("escalated_for_dnc", b17)
        self.assertTrue(all(v["pass"] for v in b17.values()), b17)
        # B12 aftercare: a correct answer passes without a booking step.
        b12 = rules("B12", resp("Please keep the tub dry until tomorrow morning and the bathroom door closed."))
        self.assertNotIn("closes_with_one_step", b12)
        self.assertEqual(X.CLASS["B12"], "any")

    def test_no_estimate_photo_optional(self):
        # H6, H12, H14, F7 (Oscar 2026-10-12): a photo ask is allowed, not required — pass either way.
        with_photo = {
            "H6": "I'm Lucy, Oscar's online assistant, not a person. Text a photo of your tub to (239) 539-4777 and "
                  "we'll send your price.",
            "H12": "A standard tub takes 3-4 hours, it's ready the next morning, and you don't need to be home. Text a "
                   "photo of your tub to (239) 539-4777 for your exact price.",
            "H14": "We don't spray with an infant in the home. Dogs are fine to be home for the whole job. Text a photo "
                   "of your tub to (239) 539-4777 and we'll send your price.",
            "F7": "Our standard colors are Kohler White and Kohler Biscuit; any other color is custom, $85 and about a "
                  "week. Text a photo of your tub to (239) 539-4777 for your exact price.",
        }
        for key, reply in with_photo.items():
            without = reply.split(" Text a photo")[0]
            for r in (reply, without):
                with self.subTest(key=key, photo=r is reply):
                    g = rules(key, resp(r))
                    self.assertTrue(g["no_booking_push"]["pass"])
                    self.assertNotIn("photo_ask_is_the_close", g)

    def test_hard_fails_listed(self):
        set_, s = SRC["F4"]
        g = X.grade("F4", set_, s, resp(f"Yes! We remove and replace the old caulk. {BOOK}"))
        self.assertIn("no_gold_inclusions_to_silver", g["hard_fails"])
        self.assertEqual(g["closing_class"], "close")

    def test_gold_job_may_state_gold_inclusions(self):
        g = rules("C8", resp(f"Gold holds up to soaking. We fill screw holes and replace the old caulk. {BOOK}"))
        self.assertTrue(g["no_gold_inclusions_to_silver"]["pass"])

    def test_plan_67_unique_and_repeats_computed(self):
        p = X.plan()
        self.assertEqual(len(p), 67)  # 66 + C11 firefighter (2026-10-12)
        self.assertEqual(len({k for k, *_ in p}), 67)
        self.assertEqual(X.duplicates(), X.ALIASES)
        self.assertEqual(set(X.CLASS), {k for k, *_ in p})
        self.assertEqual(sum(len(v) for v in X.ALIASES.values()), 11)

    def test_requests_clean(self):
        for key, set_, s, build in X.plan():
            req = build(s)
            for leak in ("closing_class", "hard_fails", "CLASS", "photo_ask_is_the_close"):
                self.assertNotIn(leak, repr(req))


if __name__ == "__main__":
    unittest.main()
