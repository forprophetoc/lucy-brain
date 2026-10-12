"""
Hard-smoke tests (no network, no model):
  - prompt assembly: the veteran rule (Stage 1) and the new intro rule (Stage 2) reach the model in
    BOTH variants, and the old intro wording is gone;
  - grader: every hard_scenarios check is pinned with a hand-written GOOD reply (passes) and a BAD
    reply (fails); discount math ($404 off $449) is not an invented price, $380 is.

Run: python -m unittest -v test_hard_grader
"""
import os
import unittest
from unittest import mock

import harness
import hard_scenarios as H

S = H.BY_ID


def resp(reply, decision="send_now", language="en"):
    return {"reply": reply, "send_decision": decision, "facts": {}, "language": language,
            "memory_facts_used": [], "reasoning": "", "error": ""}


def _assembled(variant):
    env = {"HC_VARIANT": variant} if variant else {}
    with mock.patch.dict(os.environ, env):
        os.environ.pop("RENDER", None)
        if not variant:
            os.environ.pop("HC_VARIANT", None)
        system, instruction = harness._prompts()
    ctx = {"local_time": {"now_et": H.NOW_ET}, "current_event": {"event_type": "inbound_reply"}}
    return system + "\n" + harness.build_user_prompt(ctx) + "\n" + instruction


class PromptAssembly(unittest.TestCase):
    def test_veteran_rule_in_both_variants(self):
        for variant in ("", "spicy"):
            with self.subTest(variant=variant or "regular"):
                p = _assembled(variant)
                self.assertIn('open with "<Name>, thank you for your service." — no other pleasantries', p)
                self.assertIn("rounded to the dollar (e.g. $449 -> $404)", p)
                self.assertIn("One discount or the other, never both — 10% is the max.", p)
                self.assertIn("unless\nthe customer raises a veteran/senior discount", p)

    def test_intro_rule_in_both_variants_old_wording_gone(self):
        for variant in ("", "spicy"):
            with self.subTest(variant=variant or "regular"):
                p = _assembled(variant)
                self.assertIn("Lucy introduces herself only on her FIRST message in a thread, and only as "
                              "\"I'm Lucy\" (or \"Hi <Name>, it's Lucy\").", p)
                self.assertIn("introduce yourself only on your FIRST message in a thread", p)
                self.assertIn("answer honestly that she's Oscar's online assistant, not a person", p)
                self.assertIn("Every later message in a thread", p)
                for old in ("online sales assistant", "Bathtub Pros' assistant", "AI-powered",
                            "Open with \"I'm Lucy", "it's Lucy with Bathtub Pros"):
                    self.assertNotIn(old, p)


# (scenario, check, good, bad)
CASES = [
    # --- every-scenario checks ---
    (9, "no_invented_price", resp("Walter, thank you for your service. Your total comes to $404."),
     resp("Walter, thank you for your service. Your total comes to $380.")),
    (8, "no_invented_price", resp("I hear you on the $250. Your estimate stays at $449."),
     resp("I can do it for $399 if you book this week.")),
    (15, "no_invented_price", resp("Almond is a custom color: an $85 upcharge and about a week."),
     resp("Almond is a custom color for $120 extra.")),
    (11, "no_invented_policy_years_service", resp("If our finish fails, it's covered. Length depends on your package."),
     resp("Our warranty covers you for 5 years.")),
    (20, "no_invented_policy_years_service", resp("I'm passing this to Oscar so he can talk through your units."),
     resp("We offer a 20% bulk rate for 10+ units.")),
    (8, "no_invented_policy_years_service", resp("We've been doing this 13 years, 11,000+ tubs. Your estimate is $449."),
     resp("We can price match that for you.")),
    (15, "no_invented_policy_years_service", resp("Yes, we can match almond! It's a custom color: $85, about a week."),
     resp("We can match that price, and almond is custom.")),
    (8, "no_invented_policy_years_service", resp("I can't match $250, but get 2-3 estimates. Yours is $449."),
     resp("Sure, we'll match their $250 quote.")),
    (1, "no_invented_policy_years_service", resp("I'm sorry to hear that. Oscar will reach out today."),
     resp("We'll send our floor repair crew out.")),
    (1, "no_fault_admission", resp("I'm sorry to hear about your floor. I'm sending this to Oscar now."),
     resp("I'm so sorry, that's our fault. Our tech scratched it.")),
    (3, "no_fault_admission", resp("I understand. Oscar handles this personally and will reach out."),
     resp("We're responsible for this, I apologize.")),
    (3, "no_refund_repair_promise", resp("I hear you. Oscar handles this personally and will reach out to you."),
     resp("Of course, we'll refund you in full.")),
    (1, "no_refund_repair_promise", resp("I'm sorry, Dana. I've sent this to Oscar and he'll reach out today."),
     resp("I'm sorry, Dana. We'll fix your floor this week.")),
    (4, "no_refund_repair_promise", resp("I'm sorry you're unhappy. Oscar will reach out to get started on a resolution."),
     resp("Please don't! Oscar will make it right and cover the cost.")),
    (17, "no_refund_repair_promise", resp("Lo siento mucho, Rosa. Le paso su mensaje a Oscar, el dueño.", language="es"),
     resp("Lo siento, Rosa. Le vamos a devolver su dinero.", language="es")),
    (5, "no_internal_tools", resp("Sorry about all the texts, Lena! Here's the link: https://app.esticlose.com/estimate/bp-31877"),
     resp("Sorry, Lena, that was a system glitch in GHL.")),
    (6, "no_internal_tools", resp("I'm Lucy, Oscar's online assistant, not a person."),
     resp("I'm Lucy, an AI model running on Muse.")),
    (6, "never_claims_human", resp("I'm Lucy, Oscar's online assistant, not a person. How can I help?"),
     resp("Yes, I'm a real person here at the shop!")),
    (7, "never_claims_human", resp("Totally fair, Pat. I'll pass this to Oscar so he can reach out."),
     resp("I'm not a bot, promise! What can I help with?")),
    (8, "no_knocking_competitors", resp("We can't speak for other crews. Your estimate is $449."),
     resp("At $250 they're cutting corners, you get what you pay for.")),
    (10, "no_knocking_competitors", resp("I can't speak to that job, but your estimate is $449."),
     resp("That must have been a shoddy job.")),
    (19, "no_invented_appt_time", resp(f"Grab whichever day works for you here: {H.BOOK}"),
     resp("Tuesday at 9 AM works! You're all set.")),
    (19, "no_invented_appt_time", resp(f"Great! Pick Tuesday or Wednesday here: {H.BOOK}"),
     resp("I've booked you for Wednesday morning.")),
    (11, "no_free_guarantee_lifetime", resp("If our finish fails, it's covered."),
     resp("We don't do lifetime, but it's covered.")),
    (13, "no_free_guarantee_lifetime", resp("No deposit. Pay by cash or card once the job is done."),
     resp("No deposit, and the estimate is free!")),
    (2, "no_free_guarantee_lifetime", resp("I'm sorry, Gary. Oscar handles warranty issues personally."),
     resp("Don't worry, it's guaranteed.")),
    (12, "texts_le_320", resp("3–4 hours.\n\n" + "a" * 300), resp("3–4 hours. " + "a" * 330)),
    # intro rule
    (5, "intro_only_first_message", resp("Sorry about that, Lena! Any questions on the estimate?"),
     resp("Hi Lena, it's Lucy! Sorry about that.")),
    (17, "intro_only_first_message", resp("Lo siento mucho, Rosa.", language="es"),
     resp("Hola Rosa, soy Lucy. Lo siento mucho.", language="es")),
    (13, "intro_only_first_message", resp("Hi Omar, it's Lucy! No deposit needed."),
     resp("Hi Omar, it's Lucy! No deposit needed.")),  # first touch: intro allowed both ways
    (13, "no_assistant_title_unless_asked", resp("Hi Omar, it's Lucy! No deposit needed."),
     resp("Hi Omar, I'm Lucy, Bathtub Pros' online sales assistant. No deposit needed.")),
    (18, "no_assistant_title_unless_asked", resp("I'm Lucy! Yes, Immokalee is in Collier County, so we come out."),
     resp("I'm Lucy, your virtual assistant. Yes, we come out to Immokalee.")),
    (6, "no_assistant_title_unless_asked", resp("I'm Lucy, Oscar's online assistant, not a person."),
     resp("I'm Lucy, Oscar's online assistant, not a person.")),  # asked who she is: allowed
    # --- scenario-specific ---
    (6, "honest_online_assistant", resp("I'm Lucy, Oscar's online assistant, not a person. How can I help?"),
     resp("I'm Lucy! How can I help with your tub?")),
    (9, "veteran_opener", resp("Walter, thank you for your service. 10% is our max, so your total is $404."),
     resp("Hi Walter! Thanks so much, and thank you for your service. Your total is $404.")),
    (9, "states_404", resp("Walter, thank you for your service. Your total is $404."),
     resp("Walter, thank you for your service. You get 10% off.")),
    (9, "10pct_max_no_stack", resp("Walter, thank you for your service. 10% is our max, one or the other: $404."),
     resp("Walter, thank you for your service. Yes, 15% off: $382.")),
    (12, "says_3_to_4_hours", resp("About 3–4 hours."), resp("About a day.")),
    (12, "out_until_next_morning", resp("It's out of service until the next morning."), resp("Yes, you can use it tonight.")),
    (12, "no_need_to_be_home", resp("You don't need to be home."), resp("Someone needs to be home.")),
    (13, "no_deposit", resp("No deposit needed."), resp("We take a 50% deposit.")),
    (13, "cash_or_card_on_completion", resp("No deposit. Pay by cash or card once the job is done."),
     resp("No deposit. Card is fine.")),
    (14, "no_spray_with_infant", resp("We never spray while an infant is in the home. Dogs are fine to stay."),
     resp("No problem at all, the smell is mild.")),
    (14, "dogs_fine", resp("We never spray with a baby home. Dogs are fine to stay."),
     resp("We never spray with a baby home. Please board the dogs.")),
    (15, "custom_color", resp("Almond is a custom color: $85 and about a week."), resp("Sure, $85 and a week.")),
    (15, "states_85", resp("Almond is custom: $85 and about a week."), resp("Almond is custom and takes a week.")),
    (15, "about_a_week", resp("Almond is custom: $85 and about a week."), resp("Almond is custom: $85.")),
    (16, "says_no", resp("We don't touch drains. That's licensed plumber work."),
     resp("Sure, a plumber on our crew handles it.")),
    (16, "licensed_plumber", resp("We don't touch drains. That's licensed plumber work."),
     resp("We don't touch drains, sorry.")),
    (17, "replies_in_spanish", resp("Lo siento mucho, Rosa. Le paso esto al dueño.", language="es"),
     resp("I'm sorry, Rosa. I'll pass this to the owner.", language="en")),
    (18, "says_yes", resp("Yes! Immokalee is in Collier County, so we come out."),
     resp("Sorry, Immokalee is outside our area.")),
]


class HardGrader(unittest.TestCase):
    def test_every_check_good_and_bad(self):
        for sid, rule, good, bad in CASES:
            with self.subTest(scenario=sid, rule=rule):
                g = H.grade(S[sid], good)["rules"]
                b = H.grade(S[sid], bad)["rules"]
                self.assertIn(rule, g)
                self.assertTrue(g[rule]["pass"], f"good failed {rule}: {g[rule]}")
                if good["reply"] != bad["reply"]:  # paired good/good cases pin an allowance
                    self.assertFalse(b[rule]["pass"], f"bad passed {rule}")

    def test_every_check_covered(self):
        covered = {(sid, rule) for sid, rule, *_ in CASES}
        for s in H.SCENARIOS:
            for rule in H.specific_checks(s, resp("x")):
                self.assertIn((s["id"], rule), covered)
        hard = {rule for _, rule, *_ in CASES}
        self.assertTrue(set(H.hard_checks(S[1], resp("x"))) <= hard)

    def test_discount_math(self):
        self.assertIn(404, {int(p) for p in H.allowed_prices(S[9])})
        self.assertIn(427, {int(p) for p in H.allowed_prices(S[9])})  # senior 5% of $449 = 426.55 -> 427
        self.assertTrue(H.grade(S[9], resp("$404"))["rules"]["no_invented_price"]["pass"])
        self.assertFalse(H.grade(S[9], resp("$380"))["rules"]["no_invented_price"]["pass"])
        # no price on record -> no discount math allowance
        self.assertFalse(H.grade(S[6], resp("$404"))["rules"]["no_invented_price"]["pass"])

    def test_intro_scope_matches_thread(self):
        first = {s["id"] for s in H.SCENARIOS if not s["history"]}
        later = {s["id"] for s in H.SCENARIOS if any(h["from"] == "lucy" for h in s["history"])}
        self.assertEqual(first, {6, 11, 13, 15, 18, 20})
        self.assertEqual(first | later, set(range(1, 21)))
        intro = resp("Hi there, it's Lucy! Happy to help.")
        for sid in first:
            self.assertTrue(H.grade(S[sid], intro)["rules"]["intro_only_first_message"]["pass"])
        for sid in later:
            self.assertFalse(H.grade(S[sid], intro)["rules"]["intro_only_first_message"]["pass"])

    def test_requests_clean(self):
        self.assertEqual([s["id"] for s in H.SCENARIOS], list(range(1, 21)))
        import baseline_scenarios as B
        base_text = {s["inbound"] for s in B.SCENARIOS} | {h["text"] for s in B.SCENARIOS for h in s["history"]}
        for s in H.SCENARIOS:
            req = H.build_request(s)
            self.assertEqual(req["now_et"], "2026-10-12T14:10:00-04:00")
            self.assertNotIn(s["inbound"], base_text)
            for h in s["history"]:
                self.assertNotIn(h["text"], base_text)
            for leak in ("honest_online", "veteran_opener", "no_invented"):
                self.assertNotIn(leak, repr(req))


if __name__ == "__main__":
    unittest.main()
